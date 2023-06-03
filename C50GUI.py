import tkinter as tk
from tkinter import filedialog, messagebox as msgBox
import subprocess as sp
import threading
from webbrowser import open_new_tab as webTab
import os

"""
    * Potential Features
        > Open in file explorer button

"""

ARGS = [
    '-a', # Archive
    '-d', # Distro code
    '-x', # Exclude
    '-i', # Include
    '-n', # Number of Matches
    '-o', # Output directory
    '-v'  # Verbose 
] 

"""
    > structure (default: ON)
        Compares code structure by removing whitespace & comments;
        normalizing variable names, string literals, & numeric literals; 
        & then running the winnowing algorithm.
    > text (default: ON)
        Removes whitespace, then uses the winnowing algorithm to compare
        submissions.
    > exact (default: ON)
        Removes nothing, not even whitespace, then uses the winnowing 
        algorithm to compare submissions.
    > nocomments (default: OFF)
        Removes comments, but keeps whitespace, then uses the winnowing
        algorithm to compare submissions.
    > misspellings (default: OFF)
        Compares comments for identically misspelled English words.

"""
OPTIONS = ["structure", "text", "exact", "nocomments", "misspellings"]


def windows_to_wsl(path: str):
    ESC = '\\'
    return f"/mnt/{path[0].lower()}{(path.replace(ESC, '/').replace(':', ''))[1:]}/"


def browse_html():
    # Open a file dialog to select the HTML file
    file = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=(("HTML Files", "*.html"), ("All Files", "*.*")))
    # Save the selected file
    selected_html_file.set(file)

def open_html():
    # Open the selected HTML file in the default web browser
    if selected_html_file.get(): webTab(selected_html_file.get())
    else: msgBox.showerror("Error", "No file selected")


def browse_button(var: tk.StringVar) -> callable:
    def browse() -> None:
        # Open directory selection dialog and assign selected directory to variable
        filename: str = windows_to_wsl(filedialog.askdirectory())
        var.set(filename)
    return browse


def run_compare50() -> None:
    # Prepare compare50 command
    command = ["wsl", "compare50"]

    # Add each directory selection to command
    for text, var in zip(["*", "Archive", "Distro", "Exclude", "Include"], [submissions_dir, archive_dir, distro_dir, exclude_files, include_files]):
        if var.get():
            command.extend([text.lower(), var.get()])

    # Add each selected comparison method to command
    selected_methods = [method for method, var in option_vars.items() if var.get()]
    
    if selected_methods:
        command.extend(["-p"] + selected_methods)

    if "submissions" in command:
        command = command[:2] + ["*"] + command[3:]
    print(command)
    
    # Run compare50 command and print output to text box
    process = sp.Popen(command, stdout=sp.PIPE, stderr=sp.STDOUT)
    for line in iter(process.stdout.readline, b''):
        # Decode the output and replace control sequences
        line = line.decode(errors='replace').replace('\x1b[31m', '').replace('\x1b[0m', '')
        console.insert(tk.END, line)
        console.see(tk.END)
        # Update the GUI
        root.update_idletasks()


root = tk.Tk()

selected_html_file = tk.StringVar()

submissions_dir = tk.StringVar()
exclude_files   = tk.StringVar()
include_files   = tk.StringVar()
archive_dir     = tk.StringVar()
distro_dir      = tk.StringVar()

option_vars = {option : tk.IntVar() for option in OPTIONS}


# Create entry and button for each directory selection
for text, var in zip(["Submissions", "Archive", "Distro", "Exclude", "Include"], [submissions_dir, archive_dir, distro_dir, exclude_files, include_files]):
    label = tk.Label(root, text=text)
    entry = tk.Entry(root, textvariable=var)
    button = tk.Button(root, text="Browse", command=browse_button(var))

    label.pack()
    entry.pack()
    button.pack()
    
# Add button to select the HTML file
html_browse_button = tk.Button(root, text="Select HTML file", command=browse_html)
html_browse_button.pack()

# Add button to open the selected HTML file
html_open_button = tk.Button(root, text="Open selected HTML file", command=open_html)
html_open_button.pack()

# Create checkboxes for comparison methods
for method, var in option_vars.items():
    cb = tk.Checkbutton(root, text=method, variable=var)
    cb.pack()

run_button = tk.Button(root, text="Run Compare50", command=lambda: threading.Thread(target=run_compare50).start())
run_button.pack()

# Create console text box
console = tk.Text(root)
console.pack()

root.mainloop()
