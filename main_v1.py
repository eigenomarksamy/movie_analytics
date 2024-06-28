import os
import sys
import argparse

from tabulate import tabulate

from analytics.utils import get_total_size_gb
from analytics.mp4_handler import get_video_info

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Create movie info')
    parser.add_argument('--dest', type=str,
                        help='Input directory path',
                        dest='input_directory')
    return parser.parse_args()

def convert_duration_to_str(duration: float) -> str:
    duration_hours = duration // 3600
    duration_mins = (duration % 3600) // 60
    duration_secs = duration % 60
    hours_str = str(int(duration_hours)).zfill(2)
    mins_str = str(int(duration_mins)).zfill(2)
    secs_str = str(int(duration_secs)).zfill(2)
    if duration_hours > 0:
        duration_str = f"{hours_str}:{mins_str}:{secs_str}"
    else:
        duration_str = f"{mins_str}:{secs_str}"
    return duration_str

def convert_size_to_str(size_bytes: float) -> str:
    size_kb = size_bytes / 1024.0
    size_mb = size_kb / 1024.0
    size_gb = size_mb / 1024.0
    return f"{size_gb:.2f} GB" if size_gb > 1 else f"{size_mb:.2f} MB"

def convert_size_mb_to_str(size_mb: float) -> str:
    size_gb = size_mb / 1024.0
    return f"{size_gb:.2f} GB" if size_gb > 1 else f"{size_mb:.2f} MB"

def convert_resolution_to_str(width: int, height: int) -> str:
    return f"{width}x{height}"

def main(args: argparse.Namespace) -> int:
    try:
        table = []
        headers = ["File Name", "Encoding", "Size", "Duration", "Resolution", "Time Taken"]
        directory = args.input_directory
        if not os.path.exists(directory):
            print("Destination directory does not exist.")
            return 1
        if directory[-1] != '/':
            directory += '/'
        processed = 0
        processing_speed = 0.15
        files = os.listdir(directory)
        files = [directory + file for file in files]
        total_size_gb = get_total_size_gb(files)
        expected_processing_time = total_size_gb / processing_speed
        totals = {'files': len(files), 'size_gb': total_size_gb,
                  'processing_time': 0, 'duration': 0}
        print(f"Files count: {len(files)}")
        print(f"Expected processing time: {convert_duration_to_str(expected_processing_time)}")
        print(f"Total size (GB): {total_size_gb:.2f}")
        max_duration = float('-inf')
        min_duration = float('inf')
        max_size = float('-inf')
        min_size = float('inf')
        file_max_dur = ""
        file_max_size = ""
        file_min_dur = ""
        file_min_size = ""
        for file in files:
            file_name = file.split('/')[-1]
            mp4_file, encoding = get_video_info(f'{file}')
            if mp4_file._duration > max_duration:
                max_duration = mp4_file._duration
                file_max_dur = file_name
            if mp4_file._duration < min_duration:
                min_duration = mp4_file._duration
                file_min_dur = file_name
            if mp4_file._size > max_size:
                max_size = mp4_file._size
                file_max_size = file_name
            if mp4_file._size < min_size:
                min_size = mp4_file._size
                file_min_size = file_name
            table.append([file_name, encoding, convert_size_to_str(mp4_file._size),
                          convert_duration_to_str(mp4_file._duration),
                          convert_resolution_to_str(mp4_file._resolution.width,
                                                    mp4_file._resolution.height),
                          mp4_file._time_taken])
            totals['processing_time'] += mp4_file._time_taken
            totals['duration'] += mp4_file._duration
            processed += 1
            print(f"Progress: {processed}/{len(files)} -- "
                  f"{(totals['processing_time']*100)/expected_processing_time:.2f}%")
        print(tabulate(table, headers=headers, tablefmt="grid"))
        print(f"Total time taken to process: {convert_duration_to_str(totals['processing_time'])}")
        print(f"Total size processed (GB): {totals['size_gb']}")
        print(f"Average processing speed (GB/s): {totals['size_gb']/totals['processing_time']}")
        print(f"Average duration: {convert_duration_to_str(totals['duration']/totals['files'])}")
        print(f"Average size (MB): {(totals['size_gb']/totals['files'])*1024:.2f}")
        print(f"Minimum size: {convert_size_to_str(min_size)} - {file_min_size}")
        print(f"Maximum size: {convert_size_to_str(max_size)} - {file_max_size}")
        print(f"Minimum duration: {convert_duration_to_str(min_duration)} - {file_min_dur}")
        print(f"Maximum duration: {convert_duration_to_str(max_duration)} - {file_max_dur}")
        return 0
    except Exception as e:
        print(f"Error occurred: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main(parse_arguments()))