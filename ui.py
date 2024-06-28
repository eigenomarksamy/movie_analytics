import tkinter as tk
from tkinter import filedialog, messagebox

def get_user_inputs() -> dict:

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

## window: progress
def display_progress():
    def display_initial_info():
        pass
    def display_progress_bar():
        pass
    def display_processed_size():
        pass
    def display_estimated_time_left():
        pass
    def display_count_files():
        pass
    def display_current_file():
        pass
    pass

## window: on exit
def display_summary():
    def display_run_summary():
        pass
    def display_total_summary():
        pass
    def display_timetable():
        pass
    def display_out_locations():
        pass
    pass
