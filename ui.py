import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import time
import threading
import math
from tabulate import tabulate
import queue

def get_user_inputs(defaults_dict: dict = None) -> dict:

    def submit():
        nonlocal user_inputs
        project_name = entry_project_name.get()
        proc_speed = entry_proc_speed.get()
        exec_time = entry_exec_time.get()
        destination = entry_destination.get()
        quiet_mode = var_quiet.get()
        try:
            proc_speed = float(proc_speed)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid float number")
            return
        try:
            exec_time = int(exec_time)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer number")
            return
        user_inputs = {'project_name': project_name,
                    'proc_speed': proc_speed,
                    'exec_time': exec_time,
                    'destination': destination,
                    'quiet_mode': quiet_mode}
        root.destroy()

    def browse_directory():
        directory = filedialog.askdirectory()
        if directory:
            entry_destination.delete(0, tk.END)
            entry_destination.insert(0, directory)

    user_inputs = {}
    root = tk.Tk()
    root.title("Project Input Form")
    default_project_name = ""
    default_proc_speed = "0.1"
    default_exec_time = "60"
    default_destination = ""
    if defaults_dict:
        if 'proj_name' in defaults_dict:
            default_project_name = defaults_dict['proj_name']
        if 'proc_speed' in defaults_dict:
            default_proc_speed = defaults_dict['proc_speed']
        if 'exec_time' in defaults_dict:
            default_exec_time = defaults_dict['exec_time']
        if 'dest_dir' in defaults_dict:
            # if "None" != defaults_dict['dest_dir']:
                default_destination = defaults_dict['dest_dir']
    tk.Label(root, text="Project Name:").grid(row=0, column=0, padx=10, pady=5)
    entry_project_name = tk.Entry(root)
    entry_project_name.insert(0, default_project_name)
    entry_project_name.grid(row=0, column=1, padx=10, pady=5)
    tk.Label(root, text="Processing Speed:").grid(row=1, column=0, padx=10, pady=5)
    entry_proc_speed = tk.Entry(root)
    entry_proc_speed.insert(0, default_proc_speed)
    entry_proc_speed.grid(row=1, column=1, padx=10, pady=5)
    tk.Label(root, text="Execution Time:").grid(row=2, column=0, padx=10, pady=5)
    entry_exec_time = tk.Entry(root)
    entry_exec_time.insert(0, default_exec_time)
    entry_exec_time.grid(row=2, column=1, padx=10, pady=5)
    tk.Label(root, text="Destination:").grid(row=3, column=0, padx=10, pady=5)
    entry_destination = tk.Entry(root)
    entry_destination.insert(0, default_destination)
    entry_destination.grid(row=3, column=1, padx=10, pady=5)
    tk.Button(root, text="Browse", command=browse_directory).grid(row=3, column=2, padx=10, pady=5)
    var_quiet = tk.BooleanVar()
    chk_quiet = tk.Checkbutton(root, text='Quiet Mode', variable=var_quiet)
    chk_quiet.grid(row=4, columnspan=3, pady=5)
    tk.Button(root, text="Submit", command=submit).grid(row=5, columnspan=3, pady=10)
    root.mainloop()

    return user_inputs

def show_progress_window(initial_table: dict,
                         progress_queue: queue.Queue) -> None:
    root = tk.Tk()
    root.title("Processing Progress")
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress_bar.pack(pady=20)
    progress_label = tk.Label(root, text="0/0 files processed, 0.00/0.00 GB processed")
    progress_label.pack(pady=10)
    text_info = tk.Text(root, height=40, width=200)
    text_info.pack(pady=10)
    initial_info = tabulate(initial_table.items(), tablefmt="pretty",
                            stralign="left", headers=["Information", "Value"])
    text_info.insert(tk.END, initial_info + "\n")
    threading.Thread(target=update_progress_in_gui, args=(progress_queue,
                                                          progress_bar,
                                                          progress_label)).start()
    root.mainloop()
    
def update_progress_in_gui(progress_queue: queue.Queue,
                           progress_bar: ttk.Progressbar,
                           progress_label: tk.Label) -> None:
    while True:
        progress = progress_queue.get()
        if progress is None:
            break
        percent, prg_str = progress
        progress_bar['value'] = percent
        progress_label.config(text=f"{prg_str}")
