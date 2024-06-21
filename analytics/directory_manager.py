import os
from analytics.cache_rw import CacheRW
from analytics.utils import get_files_dict_sizes_gb, sort_files_by_size

class DirectoryMgr:

    def __init__(self, directory: os.PathLike,
                 cache: CacheRW) -> None:
        if not os.path.exists(directory):
            raise RuntimeError("DirectoryMgr: Directory does not exist.")
        self.directory = directory
        self.cache_obj = cache

    def get_list_of_files(self,
                          include_full_path: bool=True) -> list[os.PathLike]:
        file_names = os.listdir(self.directory)
        self.all_files = [self.directory + file for file in file_names]
        self.cache_obj.write_full_files_list(self.all_files)
        if include_full_path:
            return self.all_files
        return file_names

    def get_total_size_gb_of_files(self) -> float:
        total_size = 0
        for file in self.all_files:
            total_size +=  (os.path.getsize(file) / (1024 ** 3))
        return total_size

    def get_remaining_list_files(self) -> list[os.PathLike]:
        # self.processed_list = self.cache_obj.read_processed_list()
        proc_list = []
        proc_dict_list = self.cache_obj.read_raw_csv_file()
        for proc in proc_dict_list:
            proc_list.append(self.directory + proc['file'])
        self.processed_list = proc_list
        self.remaining_files = []
        if self.processed_list:
            for file in self.all_files:
                if file not in self.processed_list:
                    self.remaining_files.append(file)
        else:
            self.remaining_files = self.all_files
        return self.remaining_files

    def get_total_size_gb_of_remaining_files(self) -> float:
        total_size = 0
        for file in self.remaining_files:
            total_size +=  (os.path.getsize(file) / (1024 ** 3))
        return total_size

    def get_total_size_gb_of_processed_files(self) -> float:
        total_size = 0
        for file in self.processed_list:
            total_size +=  (os.path.getsize(file) / (1024 ** 3))
        return total_size

    def get_working_batch_list_files(self, remaining_list: list[os.PathLike],
                                    size_threshold_gb: float) -> list[os.PathLike]:
        if len(remaining_list) <= 1:
            return remaining_list
        working_files = []
        total_size = 0
        files_dict = sort_files_by_size(get_files_dict_sizes_gb(remaining_list))
        sorted_names = list(files_dict.keys())
        left_index = 0
        right_index = len(sorted_names) - 1
        while left_index <= right_index:
            left_file_name = sorted_names[left_index]
            left_file_size = files_dict[left_file_name]
            right_file_name = sorted_names[right_index]
            right_file_size = files_dict[right_file_name]
            if min(left_file_size, right_file_size) > size_threshold_gb - total_size:
                break
            if left_index == right_index:
                if left_file_size + total_size <= size_threshold_gb:
                    working_files.append(left_file_name)
                    total_size += left_file_size
                break
            if left_file_size + total_size <= size_threshold_gb:
                working_files.append(left_file_name)
                total_size += left_file_size
                left_index += 1
            if right_file_size + total_size <= size_threshold_gb:
                working_files.append(right_file_name)
                total_size += right_file_size
                right_index -= 1
        return working_files
