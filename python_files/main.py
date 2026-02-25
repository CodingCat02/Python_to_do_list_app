import os
import sys
import tkinter as tk
from tkinter import font, filedialog, messagebox
from datetime import datetime

# ============================
# SECTION - Resource Path
# ============================
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ============================
# SECTION - Global Variables
# ============================
checkboxes = []
delete_mode = False
checkbox_frame = None
current_file_path = None
is_modified = False

# ============================
# SECTION - Functions
# ============================
def update_title():
    title = "To Do List"
    if current_file_path:
        file_name = os.path.basename(current_file_path)
        title += f" - {file_name}"
    if is_modified:
        title += " *"
    main.title(title)

def mark_modified():
    global is_modified
    is_modified = True
    update_title()

def update_status():
    total = myList.size()
    completed = 0
    for i in range(total):
        if myList.get(i).startswith("✔ "):
            completed += 1
    pending = total - completed
    status_var.set(f" Total Tasks: {total}  |  Pending: {pending}  |  Completed: {completed}")

def add_item(event=None):
    item_text = myEntry.get().strip()
    if item_text:
        myList.insert(tk.END, item_text)
        update_status()
        mark_modified()
    myEntry.delete(0, tk.END)

def toggle_item_status():
    try:
        index = myList.curselection()[0]
        item_text = myList.get(index)
        if item_text.startswith("✔ "):
            new_text = item_text[2:] 
            myList.delete(index)
            myList.insert(index, new_text)
            myList.itemconfig(index, fg="#464646")
        else:
            new_text = f"✔ {item_text}"
            myList.delete(index)
            myList.insert(index, new_text)
            myList.itemconfig(index, fg="#dedede")
        myList.selection_clear(0, tk.END)
        update_status()
        mark_modified()
    except IndexError:
        pass

def remove_complete_item():
    for i in range(myList.size() - 1, -1, -1):
        if myList.itemcget(i, 'fg') == '#dedede':
            myList.delete(i)
            update_status()

def exit_delete_mode():
    global delete_mode
    for widget in myFrame.winfo_children():
        if widget not in [myList, y_scroll, x_scroll]:
            widget.destroy()
    myList.grid()
    y_scroll.grid()
    x_scroll.grid()
    delete_mode = False
    delete.config(text="Delete Task", state=tk.NORMAL)
    myEntry.pack(pady=10, before=buttonFrame)
    add.grid()
    update_status()

def toggle_delete_mode():
    global delete_mode, checkboxes, checkbox_frame, cancel_btn
    if not delete_mode:
        delete_mode = True
        delete.config(text="Confirm Delete", state=tk.DISABLED)
        myEntry.pack_forget()
        add.grid_remove()
        myList.grid_remove()
        y_scroll.grid_remove()
        x_scroll.grid_remove()
        cancel_btn = tk.Button(buttonFrame, text="Cancel", command=exit_delete_mode, bg="#d3d3d3", fg="#000000")
        cancel_btn.grid(row=0, column=2, padx=10)
        delete_canvas = tk.Canvas(myFrame, bg="SystemButtonFace", highlightthickness=0)
        delete_scrollbar = tk.Scrollbar(myFrame, orient="vertical", command=delete_canvas.yview)
        checkbox_frame = tk.Frame(delete_canvas, bg="SystemButtonFace")
        delete_canvas.configure(yscrollcommand=delete_scrollbar.set)
        delete_canvas.grid(row=0, column=0, sticky="nsew")
        delete_scrollbar.grid(row=0, column=1, sticky="ns")
        canvas_window = delete_canvas.create_window((0, 0), window=checkbox_frame, anchor="nw")
        def on_configure(event):
            delete_canvas.configure(scrollregion=delete_canvas.bbox("all"))
            delete_canvas.itemconfig(canvas_window, width=event.width)
        checkbox_frame.bind("<Configure>", on_configure)
        checkboxes = []
        def update_confirm_button(*args):
            any_checked = any(var.get() for _, var in checkboxes)
            delete.config(state=tk.NORMAL if any_checked else tk.DISABLED)
        select_all_var = tk.BooleanVar()
        def select_all_action():
            for _, var in checkboxes:
                var.set(select_all_var.get())
            update_confirm_button()
        tk.Checkbutton(checkbox_frame, text="Select All", variable=select_all_var, font="Helvetica 10 bold", command=select_all_action).pack(fill='x', padx=20)
        tk.Frame(checkbox_frame, height=2, bd=1, relief=tk.SUNKEN).pack(fill='x', pady=5, padx=20)
        for item in myList.get(0, tk.END):
            var = tk.BooleanVar()
            var.trace_add("write", update_confirm_button)
            cb = tk.Checkbutton(checkbox_frame, text=item, variable=var, font=myFont, anchor="w")
            cb.pack(fill='x', padx=20)
            checkboxes.append((cb, var))
    else:
        for i in range(len(checkboxes) - 1, -1, -1):
            _, var = checkboxes[i]
            if var.get():
                myList.delete(i)
        exit_delete_mode()

def save_list(event=None):
    global current_file_path, is_modified
    if current_file_path:
        try:
            with open(current_file_path, "w", encoding="utf-8") as f:
                for i in range(myList.size()):
                    f.write(myList.get(i) + "\n")
            is_modified = False
            update_title()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")
    else:
        save_as_list()

def save_as_list():
    global current_file_path
    current_date = datetime.now().strftime("%Y-%m-%d")
    default_filename = f"task-list-{current_date}"
    file_path = filedialog.asksaveasfilename(initialfile=default_filename, defaultextension=".txt", title="Save File As", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
    if file_path:
        current_file_path = file_path
        save_list()

def open_list():
    global current_file_path, is_modified
    file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
    if file_path:
        myList.delete(0, tk.END)
        current_file_path = file_path
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                task = line.strip()
                if task:
                    myList.insert(tk.END, task)
                    if task.startswith("✔ "):
                        myList.itemconfig(tk.END, fg="#dedede")
        is_modified = False
        update_title()
        update_status()

def delete_list():
    myList.delete(0, tk.END)
    update_status()

def on_closing():
    global is_modified
    if is_modified:
        if messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Do you really want to quit?"):
            main.destroy()
    else:
        main.destroy()

def check_entry(*args):
    if myEntry.get().strip():
        add.config(state=tk.NORMAL)
    else:
        add.config(state=tk.DISABLED)

# ============================
# SECTION - Main Window Setup
# ============================
main = tk.Tk()
main.withdraw()
main.title("To Do List")
main.resizable(False, False)
main.configure(bg="SystemButtonFace")

# Center Calculation
main.update_idletasks()
window_width, window_height = 600, 600
screen_width = main.winfo_screenwidth()
screen_height = main.winfo_screenheight()
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)
main.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
main.protocol("WM_DELETE_WINDOW", on_closing)

try:
    main.iconbitmap(resource_path("icons/notepad.ico"))
except:
    pass

main.deiconify()

# ============================
# SECTION - UI Elements
# ============================
myFont = font.Font(family='Helvetica', size=11, weight='bold')

myFrame = tk.Frame(main, width=550, height=350) 
myFrame.pack_propagate(False) 
myFrame.pack(pady=10)

myFrame.grid_rowconfigure(0, weight=1)
myFrame.grid_columnconfigure(0, weight=1)

myList = tk.Listbox(myFrame, font=myFont, width=55, height=20, bd=0, fg="#464646", bg="SystemButtonFace", highlightthickness=0, selectbackground="#a6a6a6", activestyle="none")
myList.grid(row=0, column=0, sticky="nsew")

y_scroll = tk.Scrollbar(myFrame, orient=tk.VERTICAL, command=myList.yview)
x_scroll = tk.Scrollbar(myFrame, orient=tk.HORIZONTAL, command=myList.xview)
myList.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
y_scroll.grid(row=0, column=1, sticky="ns")
x_scroll.grid(row=1, column=0, sticky="ew")

bottom_container = tk.Frame(main)
bottom_container.pack(pady=5)

myEntry = tk.Entry(bottom_container, font="Helvetica 12 bold", width=35, bd=3, fg="#464646", bg="SystemButtonFace", highlightthickness=0)
myEntry.pack(pady=10)

buttonFrame = tk.Frame(bottom_container)
buttonFrame.pack(pady=5) 

add = tk.Button(buttonFrame, text="Add Task", command=add_item, bg="#cce6ff", fg="#000000")
delete = tk.Button(buttonFrame, text="Delete Task", command=toggle_delete_mode, bg="#ff9999", fg="#000000")
add.grid(row=0, column=1, padx=20)
delete.grid(row=0, column=0)

status_var = tk.StringVar()
status_bar = tk.Label(main, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, font="Helvetica 9 italic", pady=2)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# ============================
# SECTION - Menu & Bindings
# ============================
my_Menu = tk.Menu(main)
main.config(menu=my_Menu)
file_menu = tk.Menu(my_Menu, tearoff=False)
my_Menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open List", command=open_list)
file_menu.add_command(label="Save", command=save_list, accelerator="Ctrl+S")
file_menu.add_command(label="Save As...", command=save_as_list)
file_menu.add_separator() 

main.bind('<Control-s>', save_list)
main.bind('<Control-S>', save_list)
main.bind('<Return>', add_item)
myList.bind('<Double-1>', lambda event: toggle_item_status())

entry_var = tk.StringVar()
myEntry.config(textvariable=entry_var)
entry_var.trace_add("write", check_entry)

add.config(state=tk.DISABLED)
update_status()

main.mainloop()