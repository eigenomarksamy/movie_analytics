import os
import sys
import argparse
from typing import Tuple
from analytics.summary import Summary
from analytics.cache_rw import CacheRW
from analytics.directory_manager import DirectoryMgr
from analytics.mp4_handler import get_video_info
from analytics.utils import (get_total_size_gb, convert_duration_to_str,
                             convert_size_to_str, convert_resolution_to_str,
                             convert_size_mb_to_str)

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Create movie info')
    parser.add_argument('--dest', type=str,
                        help='Input directory path',
                        dest='input_directory')
    parser.add_argument('--proj', type=str, default="",
                        help='Input project name',
                        dest='proj_name')
    parser.add_argument('--proc-speed', type=float, default=0.1,
                        help='Processing speed (GB/s)',
                        dest='proc_speed')
    parser.add_argument('--exec-time', type=float, default=60,
                        help='Allowed time to execute (s)',
                        dest='max_exec_time')
    return parser.parse_args()

def process_args(args: argparse.Namespace) -> Tuple[os.PathLike, str,
                                                    str, float, float]:
    dest_dir = args.input_directory
    proj_name = args.proj_name
    separator = '\\' if sys.platform == 'win32' else '/'
    if proj_name == "":
        proj_name = dest_dir.replace(separator, '_')
    if dest_dir[-1] != separator:
        dest_dir += separator
    max_size_batch = args.proc_speed * args.max_exec_time
    return dest_dir, proj_name, separator, max_size_batch, args.proc_speed

def display_progress(total_count: int,
                     processed_count: int,
                     total_size: float,
                     processed_size: float) -> None:
    print(f"Progress: {processed_count}/{total_count} -- "
          f"{(processed_size*100)/total_size:.2f}%")

def display_initial_info(exp_proc_time: float, list_count: int, tot_size: float,
                         proc_speed: float, rem_list_count: int,
                         total_list_count: int, total_list_size: float,
                         rem_list_size: float, proc_list_size: float) -> None:
    print("Execution initiated:\n"
          f"\tNumber of total files: {total_list_count}\n"
          f"\tNumber of processed files: {total_list_count - rem_list_count}\n"
          f"\tNumber of remaining files: {rem_list_count}\n"
          f"\tNumber of batch files: {list_count}\n"
          f"\tExpected time: {convert_duration_to_str(exp_proc_time)}\n"
          f"\tTotal size of batch: {convert_size_mb_to_str(tot_size * 1024)}\n"
          f"\tAssumed processing speed: {proc_speed} GB/s")
    print("Overall progress:\n"
          f"\tTotal list size: {total_list_size:.2f} GB\n"
          f"\tRemaining list size: {rem_list_size:.2f} GB\n"
          f"\tProcessed list size: {proc_list_size:.2f} GB\n"
          f"\tProcessed: {proc_list_size*100/total_list_size:.2f}%")

def main(args: argparse.Namespace) -> int:
    dest_dir, proj_name, separator, max_size_batch, proc_speed = process_args(args)
    cache_obj = CacheRW(proj_name)
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
        return 0
    working_list = dir_mgr_obj.get_working_batch_list_files(remaining_list, max_size_batch)
    actual_processed = []
    total_size_gb = get_total_size_gb(working_list)
    working_list_count = len(working_list)
    expected_total_processing_time = total_size_gb / proc_speed
    csv_dict = []
    csv_raw = []
    display_initial_info(expected_total_processing_time, working_list_count,
                         total_size_gb, proc_speed, len(remaining_list),
                         len(total_list), total_list_size, remaining_list_size,
                         processed_list_size)
    for file in working_list:
        mp4_file = get_video_info(f'{file}')
        summary_obj.step(file.split(separator)[-1], mp4_file._encoding,
                        mp4_file._size / (1024 ** 2),
                        mp4_file._duration / 60,
                        mp4_file._creation_time,
                        mp4_file._time_taken)
        display_progress(working_list_count, summary_obj.count_files,
                        total_size_gb,
                        summary_obj.total_size_gb)
        csv_dict.append({
            "file": file.split(separator)[-1],
            "encoding": mp4_file._encoding,
            "size": convert_size_to_str(mp4_file._size),
            "duration": convert_duration_to_str(mp4_file._duration),
            "creation date": mp4_file._creation_time,
            "resolution": convert_resolution_to_str(mp4_file._resolution.width,
                                                    mp4_file._resolution.height),
            "processing time": mp4_file._time_taken
        })
        csv_raw.append({
            "file": file.split(separator)[-1],
            "encoding": mp4_file._encoding,
            "size (MB)": mp4_file._size / (1024 ** 2),
            "duration (mins)": mp4_file._duration / 60,
            "creation date": mp4_file._creation_time,
            "resolution (h)": mp4_file._resolution.height,
            "processing time": mp4_file._time_taken
        })
        actual_processed.append(file)
    summary_obj.finalize()
    summary = summary_obj.get_summary_lines()
    cache_obj.write_processed_files_list(actual_processed)
    cache_obj.write_summary_file(summary)
    cache_obj.write_csv_clean_file(csv_dict)
    cache_obj.write_csv_raw_file(csv_raw)
    return 0

if __name__ == '__main__':
    sys.exit(main(parse_arguments()))
