import os
import gc
import time
import datetime
from moviepy.editor import VideoFileClip

class MP4File:

    class Resolution:
        def __init__(self, width: int=0, height: int=0) -> None:
            self.width = width
            self.height = height

        def set_resolution(self, width: int=0, height: int=0,
                           res_list: list[int]=[]) -> None:
            if width != 0 and height != 0:
                self.width = width
                self.height = height
            elif len(res_list) == 2:
                self.width = res_list[0]
                self.height = res_list[1]
            else:
                raise RuntimeError("Error storing resolution:"
                                   f" -width: {width}"
                                   f" -height: {height}"
                                   f" -res-list: {res_list}")

    def __init__(self, file_path: os.PathLike, encoding: str) -> None:
        self._file_path = file_path
        self._encoding = encoding
        self._size = 0
        self._resolution = self.Resolution()
        self._duration = 0
        self._time_taken = 0
        self._creation_time = 0

    def compute_video_info(self) -> None:
        start_time = time.time()
        try:
            with open(self._file_path, 'r', encoding=self._encoding) as f:
                _ = f.read()
            video = VideoFileClip(self._file_path)
            self._duration = video.duration
            try:
                self._resolution.set_resolution(res_list=video.size)
            except RuntimeError as rte:
                raise RuntimeError(f"Error in setting resolution: {rte}")
            self._size = os.path.getsize(self._file_path)
            self._creation_time = datetime.datetime.fromtimestamp(os.stat(self._file_path).st_ctime)
            self._time_taken = time.time() - start_time
        except FileNotFoundError:
            raise RuntimeError("Error getting video info: File not found")
        except UnicodeDecodeError:
            raise RuntimeError("Error getting video info: Encoding error")

def get_encoding(file_path: os.PathLike,
                 encodings: list[str]=['utf-8', 'latin-1']) -> str:
    if not os.path.exists(file_path):
        raise RuntimeError("File is not found.")
    for encoding in encodings:
        try:
            with open(file_path, encoding=encoding) as file:
                file.read()
            return encoding
        except UnicodeDecodeError:
            continue
    raise RuntimeError("Can't obtain encoding")

def get_video_info(file_path: os.PathLike) -> dict:
    try:
        encoding = get_encoding(file_path)
    except RuntimeError as e:
        raise RuntimeError(f"Finding encoding error: {e}")
    mp4_file = MP4File(file_path, encoding)
    try:
        mp4_file.compute_video_info()
        ret_dict = {
            'encoding': mp4_file._encoding,
            'size': mp4_file._size,
            'duration': mp4_file._duration,
            'creation_time': mp4_file._creation_time,
            'time_taken': mp4_file._time_taken,
            'resolution_width': mp4_file._resolution.width,
            'resolution_height': mp4_file._resolution.height
        }
    except Exception as e:
        raise RuntimeError(f"Error occurred in getting video info: {e}")
    finally:
        del mp4_file
        gc.collect()
    return ret_dict
