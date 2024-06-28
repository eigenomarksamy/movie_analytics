import os
import gc
import sys
import math
import time
import argparse
from typing import Tuple
import queue
import threading
from analytics.summary import Summary
from analytics.cache_rw import CacheRW
from analytics.directory_manager import DirectoryMgr
from analytics.mp4_handler import get_video_info
from analytics.utils import (get_total_size_gb,
                             convert_duration_to_str,
                             convert_size_to_str,
                             convert_resolution_to_str,
                             convert_size_mb_to_str)
from visualization import generate_visualization
from ui import get_user_inputs, show_progress_window
from cli_displayers import display_progress, display_table

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Create movie info')
    parser.add_argument('--dest', type=str, dest='input_directory',
                        help='Input directory path')
    parser.add_argument('--proj', type=str, default="", dest='proj_name',
                        help='Input project name')
    parser.add_argument('--proc-speed', type=float, default=0.1,
                        dest='proc_speed',
                        help='Processing speed (GB/s)')
    parser.add_argument('--exec-time', type=float, default=60,
                        dest='max_exec_time',
                        help='Allowed time to execute (s)')
    parser.add_argument('--quiet', '-q', action='store_true', dest='quiet',
                        help='Hide detailed output')
    parser.add_argument('--ui', action='store_true', dest='use_ui',
                        help='Use the UI')
    return parser.parse_args()

def process_args(args: argparse.Namespace) -> Tuple[os.PathLike, str,
                                                    str, float, float]:
    def prepare_values(dest_dir, proj_name, proc_speed, max_exec_time, quiet_mode):
        separator = '/'
        if dest_dir.find('\\') != -1:
            separator = '\\'
        if proj_name == "":
            proj_name = dest_dir.replace(separator, '_')
        if dest_dir[-1] != separator:
            dest_dir += separator
        max_size_batch = proc_speed * (max_exec_time - 10)
        verbose = not quiet_mode
        return dest_dir, proj_name, separator, max_size_batch, proc_speed, verbose, args.use_ui

    defaults_dict = {}

    if args.input_directory:
        defaults_dict['dest_dir'] = str(args.input_directory)

    if args.proj_name:
        defaults_dict['proj_name'] = str(args.proj_name)

    defaults_dict['proc_speed'] = str(args.proc_speed)
    defaults_dict['exec_time'] = str(int(args.max_exec_time))

    if args.use_ui:
        user_inputs = get_user_inputs(defaults_dict)
        dest_dir = user_inputs['destination']
        proj_name = user_inputs['project_name']
        proc_speed = user_inputs['proc_speed']
        exec_time = user_inputs['exec_time']
        quiet_mode = user_inputs['quiet_mode']
    else:
        dest_dir = args.input_directory
        proj_name = args.proj_name
        proc_speed = float(defaults_dict['proc_speed'])
        exec_time = int(defaults_dict['exec_time'])
        quiet_mode = args.quiet

    return prepare_values(dest_dir, proj_name, proc_speed,
                          exec_time, quiet_mode)

def exec(dest_dir: os.PathLike, proj_name: str, separator: str,
         max_size_batch: float, proc_speed: float,
         verbose: bool, use_ui: bool) -> int:
    start_time = time.time()
    initialization_time_start = time.time()
    cache_obj = CacheRW(proj_name, verbose)
    dir_mgr_obj = DirectoryMgr(dest_dir, cache_obj)
    summary_obj = Summary()
    total_list = dir_mgr_obj.get_list_of_files()
    total_list_size = dir_mgr_obj.get_total_size_gb_of_files()
    remaining_list = dir_mgr_obj.get_remaining_list_files()
    remaining_list_size = dir_mgr_obj.get_total_size_gb_of_remaining_files()
    processed_list_size = dir_mgr_obj.get_total_size_gb_of_processed_files()
    if len(remaining_list) == 0:
        raw_csv_data = cache_obj.read_raw_csv_file()
        full_summary = summary_obj.generate_full_summary(raw_csv_data)
        cache_obj.write_full_summary_file(full_summary)
        path_name, file_name = os.path.split(cache_obj.csv_raw_file)
        generate_visualization(path_name + '/', file_name)
        return 0
    working_list = dir_mgr_obj.get_working_batch_list_files(remaining_list,
                                                            max_size_batch)
    actual_processed = []
    total_size_gb = get_total_size_gb(working_list)
    working_list_count = len(working_list)
    expected_total_processing_time = total_size_gb / proc_speed
    csv_dict = []
    csv_raw = []
    progress_queue = queue.Queue()
    initial_table = {
        "Destination": dest_dir,
        "Project": proj_name,
        "Files csv": cache_obj.csv_clean_file,
        "Files csv (raw)": cache_obj.csv_raw_file,
        "Summary (wip)": cache_obj.summary_file,
        "Temporary summary": cache_obj.tmp_summary_file,
        "Final summary": cache_obj.full_summary_file,
        "Analytics graphs": cache_obj.out_dir_visualization,
        "Full list": cache_obj.file_list_full_file,
        "Processed list": cache_obj.file_list_processed_file,
        "Processing speed": proc_speed,
        "Allowed execution time": (max_size_batch / proc_speed),
        "Number of total files": len(total_list),
        "Number of processed files": len(total_list) - len(remaining_list),
        "Number of remaining files": len(remaining_list),
        "Number of batch files": working_list_count,
        "Total size": f'{total_list_size:.2f} GB',
        "Batch size": convert_size_mb_to_str(total_size_gb * 1024),
        "Remaining list size (incl batch)": f'{remaining_list_size:.2f} GB',
        "Processed list size": f'{processed_list_size:.2f} GB',
        "Already processed": f'{processed_list_size * 100 / total_list_size:.2f}%',
        "Expected progress":
            f'{(processed_list_size + total_size_gb) * 100 / total_list_size:.2f}%',
        "Expected time": convert_duration_to_str(20 * working_list_count),
        "Expected remaining list size": f'{remaining_list_size - total_size_gb:.2f} GB',
        "Expected remaining list count":
            f'{len(remaining_list) - working_list_count}',
        "Expected remaining runs (at this proc speed)":
            math.ceil(remaining_list_size / total_size_gb)
    }
    if use_ui:
        ui_thread = threading.Thread(target=show_progress_window,
                                     args=(initial_table, progress_queue))
        ui_thread.start()
    if verbose:
        print("Initialization done.")
        display_table(table=initial_table, headers=["Information", "Value"])
        print("Execution initiated.")
        print("Progress")
    initialization_time_end = time.time()
    initialization_time_taken = initialization_time_end - initialization_time_start
    step_times = []
    for file in working_list:
        step_time_start = time.time()
        try:
            mp4_file = get_video_info(f'{file}')
            summary_obj.step(file.split(separator)[-1], mp4_file['encoding'],
                             mp4_file['size'] / (1024 ** 2),
                             mp4_file['duration'] / 60,
                             mp4_file['creation_time'],
                             mp4_file['time_taken'])
            progress_text = (f"{summary_obj.count_files}/{working_list_count}\t\t"
                             f"{summary_obj.total_size_gb:.2f}/{total_size_gb:.2f} GB\t\t"
                             f"{(summary_obj.total_size_gb*100)/total_size_gb:.2f}%\t\t"
                             f"~{convert_duration_to_str((working_list_count - summary_obj.count_files) * 20)}")
            if use_ui:
                progress_queue.put((int((summary_obj.count_files / working_list_count) * 100),
                                    progress_text))
            if verbose:
                display_progress(working_list_count,
                                 summary_obj.count_files,
                                 progress_text)
            csv_dict.append({
                "file": file.split(separator)[-1],
                "encoding": mp4_file['encoding'],
                "size": convert_size_to_str(mp4_file['size']),
                "duration": convert_duration_to_str(mp4_file['duration']),
                "creation date": mp4_file['creation_time'],
                "resolution": convert_resolution_to_str(
                    mp4_file['resolution_width'],
                    mp4_file['resolution_height']),
                "processing time": mp4_file['time_taken']
            })
            csv_raw.append({
                "file": file.split(separator)[-1],
                "encoding": mp4_file['encoding'],
                "size (MB)": mp4_file['size'] / (1024 ** 2),
                "duration (mins)": mp4_file['duration'] / 60,
                "creation date": mp4_file['creation_time'],
                "resolution (h)": mp4_file['resolution_height'],
                "processing time": mp4_file['time_taken']
            })
            actual_processed.append(file)
        except Exception as e:
            print(f"Error processing file {file}: {e}")
        finally:
            gc.collect()
        step_time_end = time.time()
        step_times.append(step_time_end - step_time_start)
    step_time_avg = sum(step_times) / len(step_times)
    finalization_time_start = time.time()
    summary_obj.finalize()
    summary = summary_obj.get_summary_lines()
    cache_obj.write_processed_files_list(actual_processed)
    cache_obj.write_summary_file(summary)
    cache_obj.write_csv_clean_file(csv_dict)
    cache_obj.write_csv_raw_file(csv_raw)
    raw_csv_data = cache_obj.read_raw_csv_file()
    tmp_summary = summary_obj.generate_full_summary(raw_csv_data)
    cache_obj.write_tmp_summary_file(tmp_summary)
    if verbose:
        print("All output files were generated.")
    finalization_time_end = time.time()
    finalization_time_taken = finalization_time_end - finalization_time_start
    end_time = time.time()
    total_time = end_time - start_time
    timetable = {
        "Initialization":
            f'{initialization_time_taken:.2f} secs',
            "Steps total / steps length":
            f'{convert_duration_to_str(sum(step_times))} / '
            f'{len(step_times)}',
            "Step average":
            convert_duration_to_str(step_time_avg),
            "Finalization":
            f'{finalization_time_taken:.2f} secs',
            "Total execution":
            convert_duration_to_str(total_time),
            "Average execution per item":
            convert_duration_to_str(total_time / len(step_times))
    }
    if use_ui:
        progress_queue.put((100, str(timetable)))
    if verbose:
        display_table(table=timetable, headers=["Timing", "Value"])
        print("End of execution.")
    progress_queue.put(None)
    return 0

def main(args: argparse.Namespace) -> int:
    dest_dir, proj_name, separator, max_size_batch, \
        proc_speed, verbose, use_ui = process_args(args)
    return exec(dest_dir, proj_name, separator,
                max_size_batch, proc_speed, verbose, use_ui)

if __name__ == '__main__':
    sys.exit(main(parse_arguments()))
