import datetime
from analytics.utils import convert_size_mb_to_str, convert_duration_to_str

class Summary:

    def __init__(self) -> None:
        self.max_duration = float('-inf')
        self.min_duration = float('inf')
        self.max_size = float('-inf')
        self.min_size = float('inf')
        self.oldest_date = None
        self.newest_date = None
        self.file_max_dur = ""
        self.file_max_size = ""
        self.file_min_dur = ""
        self.file_min_size = ""
        self.file_oldest_date = ""
        self.file_newest_date = ""
        self.count_files = 0
        self.total_time_taken = 0
        self.total_duration_mins = 0
        self.total_size_gb = 0
        self.average_size = 0
        self.average_duration = 0
        self.average_time_taken = 0
        self.encoding_dict = {}

    def step(self, file_name: str, encoding: str, size_mb: float,
             duration_mins: float, creation_date: datetime.datetime,
             time_taken_secs: float) -> None:
        if size_mb > self.max_size:
            self.max_size = size_mb
            self.file_max_size = file_name
        if size_mb < self.min_size:
            self.min_size = size_mb
            self.file_min_size = file_name
        if duration_mins > self.max_duration:
            self.max_duration = duration_mins
            self.file_max_dur = file_name
        if duration_mins < self.min_duration:
            self.min_duration = duration_mins
            self.file_min_dur = file_name
        if self.newest_date is None or creation_date > self.newest_date:
            self.newest_date = creation_date
            self.file_newest_date = file_name
        if self.oldest_date is None or creation_date < self.oldest_date:
            self.oldest_date = creation_date
            self.file_oldest_date = file_name
        self.total_duration_mins += duration_mins
        self.total_size_gb += (size_mb / 1024)
        self.total_time_taken += time_taken_secs
        self.count_files += 1
        if encoding in self.encoding_dict:
            self.encoding_dict[encoding] += 1
        else:
            self.encoding_dict[encoding] = 1

    def finalize(self) -> None:
        self.average_duration = self.total_duration_mins / self.count_files
        self.average_size = (self.total_size_gb * 1024) / self.count_files
        self.average_time_taken = self.total_time_taken / self.count_files

    def get_summary_lines(self) -> list[str]:
        return [
            "\n",
            f"total files: {self.count_files}",
            f"max size: {convert_size_mb_to_str(self.max_size)} -- {self.file_max_size}",
            f"min size: {convert_size_mb_to_str(self.min_size)} -- {self.file_min_size}",
            f"max duration: {convert_duration_to_str(self.max_duration * 60)} -- {self.file_max_dur}",
            f"min duration: {convert_duration_to_str(self.min_duration * 60)} -- {self.file_min_dur}",
            f"oldest date: {self.oldest_date} -- {self.file_oldest_date}",
            f"newest date: {self.newest_date} -- {self.file_newest_date}",
            f"time span of files: {self.newest_date - self.oldest_date}",
            f"avg duration: {convert_duration_to_str(self.average_duration * 60)}",
            f"avg size: {convert_size_mb_to_str(self.average_size)}",
            f"avg time taken: {self.average_time_taken}",
            f"avg processing speed: {self.total_size_gb / self.total_time_taken}",
            f"total time taken: {convert_duration_to_str(self.total_time_taken)}",
            "---------------\n"
        ]

    def generate_full_summary(self, raw_data_dict: list[dict]) -> list[str]:
        total_files = len(raw_data_dict)
        total_size_gb = 0
        total_duration_mins = 0
        max_duration = float('-inf')
        min_duration = float('inf')
        max_size = float('-inf')
        min_size = float('inf')
        oldest_date = None
        newest_date = None
        file_max_dur = ""
        file_max_size = ""
        file_min_dur = ""
        file_min_size = ""
        file_newest_date = ""
        file_oldest_date = ""
        total_time_taken = 0
        avg_size = 0
        avg_duration = 0
        avg_time_taken = 0
        encoding_dict = {}
        for elm in raw_data_dict:
            if elm['size (MB)'] > max_size:
                max_size = elm['size (MB)']
                file_max_size = elm['file']
            if elm['size (MB)'] < min_size:
                min_size = elm['size (MB)']
                file_min_size = elm['file']
            if elm['duration (mins)'] > max_duration:
                max_duration = elm['duration (mins)']
                file_max_dur = elm['file']
            if elm['duration (mins)'] < min_duration:
                min_duration = elm['duration (mins)']
                file_min_dur = elm['file']
            if newest_date is None or elm['creation date'] > newest_date:
                newest_date = elm['creation date'] 
                file_newest_date = elm['file']
            if oldest_date is None or elm['creation date']  < oldest_date:
                oldest_date = elm['creation date'] 
                file_oldest_date = elm['file']
            total_size_gb += (elm['size (MB)'] / 1024)
            total_duration_mins += elm['duration (mins)']
            total_time_taken += elm['processing time']
            if elm['encoding'] in encoding_dict:
                encoding_dict[elm['encoding']] += 1
            else:
                encoding_dict[elm['encoding']] = 1
        avg_size = (total_size_gb / total_files) * 1024
        avg_duration = total_duration_mins / total_files
        avg_time_taken = total_time_taken / total_files
        return [
            "\n",
            f"total files: {total_files}",
            f"max size: {convert_size_mb_to_str(max_size)} -- {file_max_size}",
            f"min size: {convert_size_mb_to_str(min_size)} -- {file_min_size}",
            f"max duration: {convert_duration_to_str(max_duration * 60)} -- {file_max_dur}",
            f"min duration: {convert_duration_to_str(min_duration * 60)} -- {file_min_dur}",
            f"oldest date: {oldest_date} -- {file_oldest_date}",
            f"newest date: {newest_date} -- {file_newest_date}",
            f"time span of files: {newest_date - oldest_date}",
            f"avg duration: {convert_duration_to_str(avg_duration * 60)}",
            f"avg size: {convert_size_mb_to_str(avg_size)}",
            f"avg processing time (s): {avg_time_taken}",
            f"avg processing speed (GB/s): {total_size_gb / total_time_taken}",
            f"total processing time: {convert_duration_to_str(total_time_taken)}",
            f"encoding(s): {encoding_dict}",
            "---------------\n"
        ]
