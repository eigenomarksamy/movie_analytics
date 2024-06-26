import os
import gc
import sys
import math
import time
import argparse
from typing import Tuple
from tabulate import tabulate
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
from ui import get_user_inputs

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
        return dest_dir, proj_name, separator, max_size_batch, proc_speed, verbose

    if args.use_ui:
        user_inputs = get_user_inputs()
        dest_dir = user_inputs['destination']
        proj_name = user_inputs['project_name']
        proc_speed = user_inputs['proc_speed']
        exec_time = user_inputs['exec_time']
        quiet_mode = user_inputs['quiet_mode']
    else:
        dest_dir = args.input_directory
        proj_name = args.proj_name
        proc_speed = args.proc_speed
        exec_time = args.max_exec_time
        quiet_mode = args.quiet

    return prepare_values(dest_dir, proj_name, proc_speed, exec_time, quiet_mode)

def display_progress(total_count: int,
                     processed_count: int,
                     total_size: float,
                     processed_size: float) -> None:
    progress_bar = ['-'] * 100
    for i in range(int(processed_count * 100 / total_count)):
        progress_bar[i] = '+'
    print(f"{''.join(progress_bar)}\t\t"
          f"{processed_count}/{total_count}\t\t"
          f"{processed_size:.2f}/{total_size:.2f} GB\t\t"
          f"{(processed_size*100)/total_size:.2f}%\t\t"
          f"~{convert_duration_to_str((total_count - processed_count) * 15)}")

def display_initial_info(exp_proc_time: float, batch_files_count: int,
                         batch_size: float, proc_speed: float,
                         rem_list_count: int, total_list_count: int,
                         total_list_size: float, rem_list_size: float,
                         proc_list_size: float, destination: str,
                         project: str, allowed_exec_time: float,
                         out_dir_csv: str, out_dir_csv_raw: str,
                         out_dir_summary_wip: str, out_dir_summary_tmp: str,
                         out_dir_summary_final: str, out_dir_list_full: str,
                         out_dir_list_proc: str, out_dir_visualization: str) -> None:
    print("Initialization done.")
    table = {
        "Destination": destination,
        "Project": project,
        "Files csv": out_dir_csv,
        "Files csv (raw)": out_dir_csv_raw,
        "Summary (wip)": out_dir_summary_wip,
        "Temporary summary": out_dir_summary_tmp,
        "Final summary": out_dir_summary_final,
        "Analytics graphs": out_dir_visualization,
        "Full list": out_dir_list_full,
        "Processed list": out_dir_list_proc,
        "Processing speed": proc_speed,
        "Allowed execution time": allowed_exec_time,
        "Number of total files": total_list_count,
        "Number of processed files": total_list_count - rem_list_count,
        "Number of remaining files": rem_list_count,
        "Number of batch files": batch_files_count,
        "Total size": f'{total_list_size:.2f} GB',
        "Batch size": convert_size_mb_to_str(batch_size * 1024),
        "Remaining list size (incl batch)": f'{rem_list_size:.2f} GB',
        "Processed list size": f'{proc_list_size:.2f} GB',
        "Already processed": f'{proc_list_size * 100 / total_list_size:.2f}%',
        "Expected progress":
            f'{(proc_list_size + batch_size) * 100 / total_list_size:.2f}%',
        "Expected time": convert_duration_to_str(15 * batch_files_count),
        "Expected remaining list size": f'{rem_list_size - batch_size:.2f} GB',
        "Expected remaining list count":
            f'{rem_list_count - batch_files_count}',
        "Expected remaining runs (at this proc speed)":
            math.ceil(rem_list_size / batch_size)
        }
    print(tabulate(table.items(), tablefmt="pretty", stralign="left",
                   headers=["Information", "Value"]))
    print("Execution initiated.")

def exec(dest_dir: os.PathLike, proj_name: str, separator: str,
         max_size_batch: float, proc_speed: float, verbose: bool) -> int:
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
    if verbose:
        display_initial_info(exp_proc_time=expected_total_processing_time,
                             batch_files_count=working_list_count,
                             batch_size=total_size_gb, proc_speed=proc_speed,
                             rem_list_count=len(remaining_list),
                             total_list_count=len(total_list),
                             total_list_size=total_list_size,
                             rem_list_size=remaining_list_size,
                             proc_list_size=processed_list_size,
                             destination=dest_dir, project=proj_name,
                             allowed_exec_time=(max_size_batch / proc_speed),
                             out_dir_csv=cache_obj.csv_clean_file,
                             out_dir_csv_raw=cache_obj.csv_raw_file,
                             out_dir_summary_wip=cache_obj.summary_file,
                             out_dir_summary_tmp=cache_obj.tmp_summary_file,
                             out_dir_summary_final=cache_obj.full_summary_file,
                             out_dir_list_full=cache_obj.file_list_full_file,
                             out_dir_list_proc=cache_obj.file_list_processed_file,
                             out_dir_visualization=cache_obj.out_dir_visualization)
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
            if verbose:
                display_progress(working_list_count, summary_obj.count_files,
                                total_size_gb, summary_obj.total_size_gb)
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
    if verbose:
        table = {"Initialization":
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
                    convert_duration_to_str(total_time / len(step_times))}
        print(tabulate(table.items(), tablefmt="pretty", stralign="left",
                       headers=["Timing", "Value"]))
        print("End of execution.")
    return 0

def main(args: argparse.Namespace) -> int:
    dest_dir, proj_name, separator, max_size_batch, \
        proc_speed, verbose = process_args(args)
    return exec(dest_dir, proj_name, separator,
                max_size_batch, proc_speed, verbose)

if __name__ == '__main__':
    sys.exit(main(parse_arguments()))
