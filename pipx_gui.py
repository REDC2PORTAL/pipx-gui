import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import subprocess
import threading

def get_pipx_list():
    try:
        result = subprocess.run(['pipx', 'list'], capture_output=True, text=True)
        output = result.stdout.splitlines()

        apps = []
        current_app = None
        for line in output:
            if line.startswith('   package '):
                if current_app:
                    apps.append(current_app)
                package_info = line.split()
                package_name = package_info[1]
                package_version = package_info[2]
                current_app = {'name': package_name, 'description': f'Package: {package_name} {package_version}\nInstalled using: {" ".join(package_info[4:])}'}
            elif current_app and line.startswith('    - '):
                current_app['description'] += '\n' + line.strip()
        if current_app:
            apps.append(current_app)
        return apps
    except Exception as e:
        return [{'name': 'Error', 'description': str(e)}]

def show_description(event):
    selected_index = listbox.curselection()
    if not selected_index:
        return
    selected_app = apps[selected_index[0]]
    commands_listbox.delete(0, tk.END)
    for line in selected_app['description'].split('\n'):
        commands_listbox.insert(tk.END, line.strip())

def show_help(event=None):
    selected_index = commands_listbox.curselection()
    if not selected_index:
        return
    selected_command = commands_listbox.get(selected_index[0]).split()[1]
    help_output = get_app_help(selected_command)
    display_help_window(selected_command, help_output)

def get_app_help(app_name):
    try:
        result = subprocess.run([app_name, '-h'], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"Error fetching help for {app_name}: {e}"

def display_help_window(app_name, help_output):
    help_window = tk.Toplevel(root)
    help_window.title(f"{app_name} Help")
    help_text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, width=100, height=30, font=("Arial", 12), bg='#333333', fg='#ffffff')
    help_text.pack(fill=tk.BOTH, expand=True)
    help_text.insert(tk.END, help_output)
    help_text.config(state=tk.DISABLED)

def refresh_list():
    listbox.delete(0, tk.END)
    commands_listbox.delete(0, tk.END)
    global apps
    apps = get_pipx_list()
    for app in apps:
        listbox.insert(tk.END, app['name'])

def run_in_thread(func):
    threading.Thread(target=func).start()

root = tk.Tk()
root.title("My Pipx Applications")
root.geometry("800x600")
root.configure(bg='#2e2e2e')

style = ttk.Style()
style.theme_use('clam')
style.configure('TButton', background='#555555', foreground='#ffffff')
style.configure('TFrame', background='#2e2e2e')
style.configure('TLabel', background='#2e2e2e', foreground='#ffffff')

frame = ttk.Frame(root)
frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

listbox = tk.Listbox(frame, width=50, height=20, font=("Arial", 12), bg='#333333', fg='#ffffff', selectbackground='#555555', selectforeground='#ffffff')
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=listbox.yview)

right_frame = ttk.Frame(root)
right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

refresh_button = ttk.Button(right_frame, text="Refresh List", command=lambda: run_in_thread(refresh_list))
refresh_button.pack(pady=10)

commands_listbox = tk.Listbox(right_frame, width=60, height=20, font=("Arial", 12), bg='#333333', fg='#ffffff', selectbackground='#555555', selectforeground='#ffffff')
commands_listbox.pack(fill=tk.BOTH, expand=True)

help_button = ttk.Button(right_frame, text="Show Help", command=lambda: run_in_thread(lambda: show_help(None)))
help_button.pack(pady=10)

listbox.bind('<Double-Button-1>', show_description)
commands_listbox.bind('<Double-Button-1>', show_help)

apps = []
run_in_thread(refresh_list)

root.mainloop()
