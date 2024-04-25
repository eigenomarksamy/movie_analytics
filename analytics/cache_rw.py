import os
from analytics.utils import (write_file, update_csv, extract_info_from_file,
                             read_csv)

class CacheRW:

    def __init__(self, proj_name: str) -> None:
        self.project_exists = False
        self.proj_cache_dir = 'cache/' + proj_name + '/'
        if os.path.exists(self.proj_cache_dir):
            self.project_exists = True
        self.report_dir = self.proj_cache_dir + 'out/'
        self.csv_clean_file = self.report_dir + 'files.csv'
        self.csv_raw_file = self.report_dir + 'files_raw.csv'
        self.summary_file = self.report_dir + 'summary.txt'
        self.full_summary_file = self.report_dir + 'full_summary.txt'
        self.file_lists_dir = self.proj_cache_dir + 'working_file_lists/'
        self.file_list_full_file = self.file_lists_dir + 'full_file_list.txt'
        self.file_list_processed_file = self.file_lists_dir + 'processed_file_list.txt'
        self.destination_file = self.proj_cache_dir + 'destination.txt'
        self.make_dirs()

    def make_dirs(self):
        os.makedirs(self.proj_cache_dir, exist_ok=True)
        os.makedirs(self.report_dir, exist_ok=True)
        os.makedirs(self.file_lists_dir, exist_ok=True)

    def write_full_files_list(self, list_files: list[os.PathLike]) -> None:
        write_file(self.file_list_full_file, list_files)

    def write_processed_files_list(self, list_files: list[os.PathLike]) -> None:
        write_file(self.file_list_processed_file, list_files, 'a')

    def write_summary_file(self, summary_lines: list[str]) -> None:
        try:
            write_file(self.summary_file, summary_lines, 'a')
        except Exception as e:
            raise RuntimeError(f"Exception happened in writing: {e}")

    def write_full_summary_file(self, summary_lines: list[str]) -> None:
        try:
            write_file(self.full_summary_file, summary_lines)
        except Exception as e:
            raise RuntimeError(f"Exception happened in writing: {e}")

    def write_csv_clean_file(self, data_dict: list[dict]) -> None:
        try:
            update_csv(data_dict, self.csv_clean_file)
        except Exception as e:
            raise RuntimeError(f"Exception happened in writing: {e}")

    def write_csv_raw_file(self, data_dict: list[dict]) -> None:
        try:
            update_csv(data_dict, self.csv_raw_file)
        except Exception as e:
            raise RuntimeError(f"Exception happened in writing: {e}")

    def read_full_files_list(self) -> list[os.PathLike]:
        try:
            return extract_info_from_file(self.file_list_full_file)
        except Exception as e:
            raise RuntimeError(f"Exception happened in reading: {e}")

    def read_processed_list(self) -> list[os.PathLike]:
        try:
            return extract_info_from_file(self.file_list_processed_file)
        except Exception as e:
            raise RuntimeError(f"Exception happened in reading: {e}")

    def read_summary(self) -> list[str]:
        try:
            return extract_info_from_file(self.summary_file)
        except Exception as e:
            raise RuntimeError(f"Exception happened in reading: {e}")

    def read_destination(self) -> os.PathLike:
        try:
            return extract_info_from_file(self.destination_file)
        except Exception as e:
            raise RuntimeError(f"Exception happened in reading: {e}")

    def read_raw_csv_file(self) -> list[dict]:
        return read_csv(self.csv_raw_file)