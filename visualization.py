import sys
import argparse
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
from analytics.utils import read_csv

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Visualize movie info')
    parser.add_argument('--proj', type=str, default="",
                        dest='proj_name',
                        help='Input project name')
    return parser.parse_args()

def group_data_by_month(data: list[dict]) -> dict:
    for entry in data:
        entry["creation date"] = datetime.strptime(entry["creation date"], '%Y-%m-%d %H:%M:%S.%f')
    grouped_by_month = defaultdict(list)
    for entry in data:
        key = entry["creation date"].strftime('%Y-%m')
        grouped_by_month[key].append(entry)
    sorted_months = sorted(grouped_by_month.keys())
    transformed_group = {}
    for idx, month in enumerate(sorted_months):
        new_key = idx + 1
        transformed_group[new_key] = grouped_by_month[month]
    return transformed_group

def sum_and_average_durations_by_month(grouped_data: dict) -> dict:
    sum_month_data = {}
    for month_label, entries in grouped_data.items():
        total_duration = sum(entry['duration (mins)'] for entry in entries)
        average_duration = total_duration / len(entries) if entries else 0
        sum_month_data[month_label] = {
            'total_duration': total_duration,
            'average_duration': average_duration
        }
    return sum_month_data

def sum_and_average_sizes_by_month(grouped_data: dict) -> dict:
    sum_month_data = {}
    for month_label, entries in grouped_data.items():
        total_size = sum(entry['size (MB)'] for entry in entries)
        average_size = total_size / len(entries) if entries else 0
        sum_month_data[month_label] = {}
        sum_month_data[month_label]['total_size'] = 0
        sum_month_data[month_label] = {
            'total_size': total_size,
            'average_size': average_size
        }
    return sum_month_data

def sum_and_average_resolutions_by_month(grouped_data: dict) -> dict:
    sum_month_data = {}
    for month_label, entries in grouped_data.items():
        total_resolution = sum(entry['resolution (h)'] for entry in entries)
        average_resolution = total_resolution / len(entries) if entries else 0
        sum_month_data[month_label] = {}
        sum_month_data[month_label]['total_size'] = 0
        sum_month_data[month_label] = {
            'total_resolution': total_resolution,
            'average_resolution': average_resolution
        }
    return sum_month_data

def main(args: argparse.Namespace) -> int:
    csv_file = 'cache/' + args.proj_name + '/out/files_raw.csv'
    data_dict = read_csv(csv_file)
    grouped_data = group_data_by_month(data_dict)
    sum_month_data_dur = sum_and_average_durations_by_month(grouped_data)
    sum_month_data_size = sum_and_average_sizes_by_month(grouped_data)
    sum_month_data_res = sum_and_average_resolutions_by_month(grouped_data)
    analyzed_months = {}
    for month_label, _ in grouped_data.items():
        analyzed_months[month_label] = {
            'duration': {
                'total': sum_month_data_dur[month_label]['total_duration'],
                'average': sum_month_data_dur[month_label]['average_duration']
            },
            'size': {
                'total': sum_month_data_size[month_label]['total_size'],
                'average': sum_month_data_size[month_label]['average_size']
            },
            'resolution': {
                'total': sum_month_data_res[month_label]['total_resolution'],
                'average': sum_month_data_res[month_label]['average_resolution']
            }
        }
    months = list(analyzed_months.keys())
    total_duration = [analyzed_months[month]['duration']['total'] for month in months]
    average_duration = [analyzed_months[month]['duration']['average'] for month in months]
    total_size = [analyzed_months[month]['size']['total'] for month in months]
    average_size = [analyzed_months[month]['size']['average'] for month in months]
    total_resolution = [analyzed_months[month]['resolution']['total'] for month in months]
    average_resolution = [analyzed_months[month]['resolution']['average'] for month in months]
    _, axes = plt.subplots(3, 2, figsize=(15, 15))
    axes[0, 0].plot(months, total_duration, marker='o', label='Total Duration')
    axes[0, 0].set_title('Total Duration per Month')
    axes[0, 0].set_xlabel('Month')
    axes[0, 0].set_ylabel('Total Duration (mins)')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    axes[0, 1].plot(months, average_duration, marker='o',label='Average Duration')
    axes[0, 1].set_title('Average Duration per Month')
    axes[0, 1].set_xlabel('Month')
    axes[0, 1].set_ylabel('Average Duration (mins)')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    axes[1, 0].plot(months, total_size, marker='o', label='Total Size')
    axes[1, 0].set_title('Total Size per Month')
    axes[1, 0].set_xlabel('Month')
    axes[1, 0].set_ylabel('Total Size (MBs)')
    axes[1, 0].legend()
    axes[1, 0].grid(True)
    axes[1, 1].plot(months, average_size, marker='o', label='Average Size')
    axes[1, 1].set_title('Average Size per Month')
    axes[1, 1].set_xlabel('Month')
    axes[1, 1].set_ylabel('Average Size (MBs)')
    axes[1, 1].legend()
    axes[1, 1].grid(True)
    axes[2, 0].plot(months, total_resolution, marker='o', label='Total Resolution')
    axes[2, 0].set_title('Total Resolution per Month')
    axes[2, 0].set_xlabel('Month')
    axes[2, 0].set_ylabel('Total Resolution')
    axes[2, 0].legend()
    axes[2, 0].grid(True)
    axes[2, 1].plot(months, average_resolution, marker='o', label='Average Resolution')
    axes[2, 1].set_title('Average Resolution per Month')
    axes[2, 1].set_xlabel('Month')
    axes[2, 1].set_ylabel('Average Resolution')
    axes[2, 1].legend()
    axes[2, 1].grid(True)
    plt.tight_layout()
    plt.savefig('cache/' + args.proj_name + '/out/monthly_data_analysis.jpg', format='jpg')

if __name__ == '__main__':
    sys.exit(main(parse_arguments()))