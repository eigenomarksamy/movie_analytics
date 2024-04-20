import os
import csv

from typing import Union

def get_total_size_gb(files_list: list[os.PathLike]) -> float:
    size = 0
    for file in files_list:
        size += (os.path.getsize(file) / 1024 ** 3)
    return size

def get_files_dict_sizes_gb(files_list: list[os.PathLike]) -> dict:
    ret_dict = {}
    for file in files_list:
        ret_dict[file] = os.path.getsize(file) / (1024 ** 3)
    return ret_dict

def sort_files_by_size(files_dict: dict) -> dict:
    sorted_items = sorted(files_dict.items(), key=lambda x:x[1])
    sorted_dict = {k: v for k, v in sorted_items}
    return sorted_dict

def extract_info_from_file(file_path: os.PathLike,
                           default_val: str=None) -> Union[str, list[str]]:
    if not os.path.exists(file_path):
        if not default_val:
            return default_val
        raise RuntimeError("Error extracting info from file. "
                           f"File {file_path} does not exist. "
                           "No default value was provided.")
    with open(file_path, 'r') as file:
        lines = file.readlines()
        if len(lines) == 1:
            return lines[0].strip()
        else:
            return [line.strip() for line in lines]

def write_file(file: os.PathLike, lines: list[str], mode: str = 'w') -> None:
    with open(file, mode, encoding='utf-8') as out_file:
        for i in range(len(lines)):
            line = lines[i] + '\n'
            out_file.write(line)

def update_csv(data_dict: list[dict], csv_file: os.PathLike,
               mode: str = 'a') -> None:
    write_header = True
    if os.path.exists(csv_file):
        write_header = False
    header = list(data_dict[0].keys()) if data_dict else []
    with open(csv_file, mode, newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=header)
        if write_header:
            writer.writeheader()
        for dic in data_dict:
            writer.writerow(dic)

def read_csv(csv_file: os.PathLike) -> list[dict]:
    data = []
    with open(csv_file, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            converted_row = {key: float(value) if value.replace('.', '', 1).isdigit() else value for key, value in row.items()}
            data.append(dict(converted_row))
    return data

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
