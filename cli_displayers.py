import math
from tabulate import tabulate
from analytics.utils import convert_duration_to_str

def display_table(**kwargs) -> None:
    table = kwargs.get('table')
    tablefmt = kwargs.get('tablefmt', "pretty")
    stralign = kwargs.get('stralign', "left")
    headers = kwargs.get('headers')
    print(tabulate(table.items(), tablefmt=tablefmt,
                   stralign=stralign, headers=headers))

def display_progress(total_count: int,
                     processed_count: int,
                     progress_text: str) -> None:
    progress_bar = ['-'] * 100
    for i in range(int(processed_count * 100 / total_count)):
        progress_bar[i] = '+'
    print(f"{''.join(progress_bar)}\t\t"
          f"{progress_text}")
