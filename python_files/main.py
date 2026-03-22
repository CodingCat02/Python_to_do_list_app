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
cancel_btn = None 

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
    headers = 0
    
    for i in range(total):
        item = myList.get(i)
        
        if "---" in item:
            headers += 1
        elif "✔" in item:
            completed += 1
    
    actual_tasks = total - headers
    if actual_tasks < 0: actual_tasks = 0
    
    pending = actual_tasks - completed
    status_var.set(f" Tasks: {actual_tasks}  |  Pending: {pending}  |  Completed: {completed}")

def add_header():
    item_text = myEntry.get().strip()
    if item_text:
        header_text = f"--- {item_text.upper()} ---"
        myList.insert(tk.END, header_text)
        last_index = myList.size() - 1
        myList.itemconfig(last_index, fg="#000000")
        update_status()
        mark_modified()
    myEntry.delete(0, tk.END)

def add_item(event=None):
    item_text = myEntry.get().strip()
    if item_text:
        formatted_task = f"    {item_text}"
        myList.insert(tk.END, formatted_task)
        myList.itemconfig(tk.END, fg="#464646")
        update_status()
        mark_modified()
    myEntry.delete(0, tk.END)

def toggle_item_status():
    try:
        index = myList.curselection()[0]
        item_text = myList.get(index)
        if item_text.lstrip().startswith("---"):
            return 
        if "✔" in item_text:
            new_text = item_text.replace("✔ ", "")
            myList.delete(index)
            myList.insert(index, new_text)
            myList.itemconfig(index, fg="#464646")
        else:
            new_text = item_text.replace("    ", "    ✔ ")
            myList.delete(index)
            myList.insert(index, new_text)
            myList.itemconfig(index, fg="#dedede")
        myList.selection_clear(0, tk.END)
        update_status()
        mark_modified()
    except IndexError:
        pass

def exit_delete_mode():
    global delete_mode, cancel_btn
    main.unbind_all("<MouseWheel>")
    
    # Destroy everything except the original Listbox and its scrollbars
    for widget in myFrame.winfo_children():
        if widget not in [myList, y_scroll, x_scroll]:
            widget.destroy()
            
    if cancel_btn:
        cancel_btn.destroy()
        cancel_btn = None
        
    myList.grid()
    y_scroll.grid()
    x_scroll.grid()
    delete_mode = False
    delete.config(text="Delete Task", state=tk.NORMAL)
    myEntry.pack(pady=10, before=buttonFrame)
    
    # Restore all buttons
    add.grid()
    header.grid()
    move_up_btn.grid()
    move_down_btn.grid()
    
    update_status()

def toggle_delete_mode():
    global delete_mode, checkboxes, checkbox_frame, cancel_btn
    if not delete_mode:
        delete_mode = True
        delete.config(text="Confirm Delete", state=tk.DISABLED)
        
        # Hide standard UI
        myEntry.pack_forget()
        add.grid_remove()
        move_up_btn.grid_remove()
        move_down_btn.grid_remove()
        header.grid_remove()
        myList.grid_remove()
        y_scroll.grid_remove()
        x_scroll.grid_remove()
        
        # Create Cancel Button
        cancel_btn = tk.Button(buttonFrame, text="Cancel", command=exit_delete_mode, bg="#d3d3d3", fg="#000000")
        cancel_btn.grid(row=0, column=2, padx=10)
        
        # 1. Setup Canvas and Scrollbars
        delete_canvas = tk.Canvas(myFrame, bg="SystemButtonFace", highlightthickness=0)
        del_scroll_y = tk.Scrollbar(myFrame, orient="vertical", command=delete_canvas.yview)
        del_scroll_x = tk.Scrollbar(myFrame, orient="horizontal", command=delete_canvas.xview)
        
        checkbox_frame = tk.Frame(delete_canvas, bg="SystemButtonFace")
        
        delete_canvas.configure(yscrollcommand=del_scroll_y.set, xscrollcommand=del_scroll_x.set)
        
        # 2. Grid Layout for Delete Mode
        delete_canvas.grid(row=0, column=0, sticky="nsew")
        del_scroll_y.grid(row=0, column=1, sticky="ns")
        del_scroll_x.grid(row=1, column=0, sticky="ew")
        
        canvas_window = delete_canvas.create_window((0, 0), window=checkbox_frame, anchor="nw")
        
        def on_configure(event):
            # Update scroll region to encompass all content
            delete_canvas.configure(scrollregion=delete_canvas.bbox("all"))
            # If the frame is narrower than the canvas, stretch it to fill
            if checkbox_frame.winfo_reqwidth() < delete_canvas.winfo_width():
                delete_canvas.itemconfig(canvas_window, width=delete_canvas.winfo_width())

        checkbox_frame.bind("<Configure>", on_configure)
        
        def _on_mousewheel(event):
            delete_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main.bind_all("<MouseWheel>", _on_mousewheel)
        
        checkboxes = []
        
        # 3. SELECT ALL SECTION (Fixed at the top of the frame)
        def update_confirm_button(*args):
            any_checked = any(var.get() for _, var in checkboxes)
            delete.config(state=tk.NORMAL if any_checked else tk.DISABLED)
            
        select_all_var = tk.BooleanVar()
        
        def select_all_action():
            for _, var in checkboxes:
                var.set(select_all_var.get())
            update_confirm_button()

        # Pack Select All at the very top
        select_all_cb = tk.Checkbutton(checkbox_frame, text="Select All", variable=select_all_var, 
                                       font="Helvetica 10 bold", command=select_all_action, bg="SystemButtonFace")
        select_all_cb.pack(fill='x', padx=20, pady=(10, 0), anchor="w")
        
        # Add a visual separator line
        tk.Frame(checkbox_frame, height=2, bd=1, relief=tk.SUNKEN).pack(fill='x', pady=10, padx=20)
        
        # 4. TASK LOOP
        for item in myList.get(0, tk.END):
            var = tk.BooleanVar()
            var.trace_add("write", update_confirm_button)
            
            # anchor="w" and wraplength=0 ensures the text doesn't hide or wrap
            cb = tk.Checkbutton(checkbox_frame, text=item, variable=var, font=myFont, 
                                anchor="w", bg="SystemButtonFace", wraplength=0, justify=tk.LEFT)
            cb.pack(fill='x', padx=20, pady=2, anchor="w")
            checkboxes.append((cb, var))
            
    else:
        # Confirm Delete Logic
        deleted_anything = False
        for i in range(len(checkboxes) - 1, -1, -1):
            _, var = checkboxes[i]
            if var.get():
                myList.delete(i)
                deleted_anything = True
        if deleted_anything:
            mark_modified()
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
                task = line.rstrip("\n") 
                if task.strip():
                    myList.insert(tk.END, task)
                    clean_task = task.lstrip() 
                    if clean_task.startswith("---"):
                        myList.itemconfig(tk.END, fg="#000000")
                    elif clean_task.startswith("✔ "):
                        myList.itemconfig(tk.END, fg="#dedede")
                    else:
                        myList.itemconfig(tk.END, fg="#464646")
        is_modified = False
        update_title()
        update_status()

def delete_list():
    if myList.size() > 0:
        if messagebox.askyesno("Clear List", "Are you sure you want to delete all tasks?"):
            myList.delete(0, tk.END)
            mark_modified()
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
        header.config(state=tk.NORMAL)
    else:
        add.config(state=tk.DISABLED)
        header.config(state=tk.DISABLED)

def move_up():
    try:
        index = myList.curselection()[0]
        if index > 0:
            text = myList.get(index)
            color = myList.itemcget(index, 'fg')
            myList.delete(index)
            myList.insert(index - 1, text)
            myList.itemconfig(index - 1, fg=color)
            myList.selection_set(index - 1)
            mark_modified()
    except IndexError:
        pass

def move_down():
    try:
        index = myList.curselection()[0]
        if index < myList.size() - 1:
            text = myList.get(index)
            color = myList.itemcget(index, 'fg')
            myList.delete(index)
            myList.insert(index + 1, text)
            myList.itemconfig(index + 1, fg=color)
            myList.selection_set(index + 1)
            mark_modified()
    except IndexError:
        pass

# ============================
# SECTION - Main Window Setup
# ============================
main = tk.Tk()
main.withdraw()
main.title("To Do List")
main.resizable(False, False)
main.configure(bg="SystemButtonFace")
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

delete = tk.Button(buttonFrame, text="Delete Task", command=toggle_delete_mode, bg="#ff9999", fg="#000000")
header = tk.Button(buttonFrame, text="Add As Header", command=add_header, bg="#e0e0e0", fg="#000000")
add = tk.Button(buttonFrame, text="Add Task", command=add_item, bg="#cce6ff", fg="#000000")
move_up_btn = tk.Button(buttonFrame, text="▲", command=move_up, bg="#f0f0f0", width=2)
move_down_btn = tk.Button(buttonFrame, text="▼", command=move_down, bg="#f0f0f0", width=2)

delete.grid(row=0, column=0, padx=2)
header.grid(row=0, column=1, padx=2)
add.grid(row=0, column=2, padx=2)
move_up_btn.grid(row=0, column=3, padx=2)
move_down_btn.grid(row=0, column=4, padx=2)

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
file_menu.add_command(label="Clear List", command=delete_list)

main.bind('<Control-s>', save_list)
main.bind('<Control-S>', save_list)
main.bind('<Return>', add_item)
myList.bind('<Double-1>', lambda event: toggle_item_status())

entry_var = tk.StringVar()
myEntry.config(textvariable=entry_var)
entry_var.trace_add("write", check_entry)

add.config(state=tk.DISABLED)
header.config(state=tk.DISABLED)
update_status()

main.mainloop()