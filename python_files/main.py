import os
import sys
import tkinter as tk
from tkinter import font, filedialog
from datetime import datetime

# ============================
# SECTION - Resource Path
# ============================
def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and PyInstaller.
    """
    try:
        # PyInstaller stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Development mode
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ============================
# SECTION - Main Window
# ============================
main = tk.Tk()
main.title("To Do List")
main.resizable(False, False)
main.configure(bg="SystemButtonFace")
main.geometry("600x600")
main.minsize(600, 600)
main.maxsize(600, 600) 
main.iconbitmap(resource_path("icons/notepad.ico"))

# ============================
# SECTION - Center Window
# ============================
# 1. Temporarily hide the window so it doesn't "jump" from the corner
main.withdraw()

# 2. Force Tkinter to calculate window size
main.update_idletasks()

window_width = 600
window_height = 600

# 3. Get the actual screen dimension
screen_width = main.winfo_screenwidth()
screen_height = main.winfo_screenheight()

# 4. Calculate the center coordinates
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)

# 5. Apply the geometry
main.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

# 6. Show the window again now that it's centered
main.deiconify()

# ============================
# SECTION - Frames
# ============================
myFrame = tk.Frame(main, width=550, height=350) 
myFrame.pack_propagate(False) 
myFrame.pack(pady=10)

buttonFrame = tk.Frame(main)
buttonFrame.pack(pady=20)

# ============================
# SECTION - Font
# ============================
myFont = font.Font(family='Helvetica', size=11, weight='bold')

# ============================
# SECTION - Listbox with X & Y Scrollbars (CORRECT)
# ============================
myFrame.grid_rowconfigure(0, weight=1)
myFrame.grid_columnconfigure(0, weight=1)

myList = tk.Listbox(
    myFrame,
    font=myFont,
    width=55,     
    height=20,
    bd=0,
    fg="#464646",
    bg="SystemButtonFace",
    highlightthickness=0,
    selectbackground="#a6a6a6",
    activestyle="none"
)
# Place Listbox in the top-left cell
myList.grid(row=0, column=0, sticky="nsew")
myList.bind('<Double-1>', lambda event: toggle_item_status())

# Create Scrollbars
y_scroll = tk.Scrollbar(myFrame, orient=tk.VERTICAL, command=myList.yview)
x_scroll = tk.Scrollbar(myFrame, orient=tk.HORIZONTAL, command=myList.xview)

# Link Listbox to Scrollbars
myList.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

# Place Scrollbars in the grid (Always visible)
y_scroll.grid(row=0, column=1, sticky="ns")  # Right side
x_scroll.grid(row=1, column=0, sticky="ew")  # Bottom side

# ============================
# SECTION - Entry Box
# ============================
bottom_container = tk.Frame(main)
bottom_container.pack(pady=5)

myEntry = tk.Entry(
    bottom_container, 
    font="Helvetica 12 bold", 
    width=35, 
    bd=3, 
    fg="#464646", 
    bg="SystemButtonFace", 
    highlightthickness=0
)
myEntry.pack(pady=10)

buttonFrame = tk.Frame(bottom_container)
buttonFrame.pack(pady=5) 

# ============================
# SECTION - Variables
# ============================
checkboxes = []
delete_mode = False
checkbox_frame = None
current_file_path = None  # Tracks the currently opened/saved file
is_modified = False       # Tracks if changes were made since last save

# ============================
# SECTION - Status Bar
# ============================
status_var = tk.StringVar()
status_bar = tk.Label(
    main, 
    textvariable=status_var, 
    bd=1, 
    relief=tk.SUNKEN, 
    anchor=tk.W, 
    font="Helvetica 9 italic",
    pady=2,
)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

def update_status():
    total = myList.size()
    completed = 0
    for i in range(total):
        if myList.get(i).startswith("✔ "):
            completed += 1
    
    pending = total - completed
    status_var.set(f" Total Tasks: {total}  |  Pending: {pending}  |  Completed: {completed}")

# ============================
# SECTION - CRUD Functions
# ============================
def add_item():
    """Add task from entry to listbox."""
    item_text = myEntry.get().strip()
    if item_text:
        myList.insert(tk.END, item_text)
        update_status()
        mark_modified()
    myEntry.delete(0, tk.END)

def toggle_item_status():
    """Toggles the checkmark and color when an item is double-clicked."""
    try:
        index = myList.curselection()[0]
        item_text = myList.get(index)
        
        if item_text.startswith("✔ "):
            # REMOVE MARK: Remove the first two characters "✔ "
            new_text = item_text[2:] 
            myList.delete(index)
            myList.insert(index, new_text)
            myList.itemconfig(index, fg="#464646") # Restore original color
        else:
            # ADD MARK: Add the checkmark
            new_text = f"✔ {item_text}"
            myList.delete(index)
            myList.insert(index, new_text)
            myList.itemconfig(index, fg="#dedede") # Set completed color
            
        myList.selection_clear(0, tk.END)
        update_status()
        mark_modified() # Ensure the * appears in the title
    except IndexError:
        pass
        
def remove_complete_item():
    """Remove all completed tasks from listbox."""
    for i in range(myList.size() - 1, -1, -1):
        if myList.itemcget(i, 'fg') == '#dedede':
            myList.delete(i)
            update_status()
    
def toggle_delete_mode():
    global delete_mode, checkboxes, checkbox_frame, cancel_btn

    if not delete_mode:
        delete_mode = True
        delete.config(text="Confirm Delete", state=tk.DISABLED)
        
        # Hide standard UI
        myEntry.pack_forget()
        add.grid_remove()
        myList.grid_remove()
        y_scroll.grid_remove()
        x_scroll.grid_remove()
        
        # 1. Add the Cancel Button
        cancel_btn = tk.Button(
            buttonFrame, text="Cancel", command=exit_delete_mode,
            bg="#d3d3d3", fg="#000000"
        )
        cancel_btn.grid(row=0, column=2, padx=10)

        # 2. Setup Canvas
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

        # 3. Re-insert Select All Logic
        select_all_var = tk.BooleanVar()
        def select_all_action():
            for _, var in checkboxes:
                var.set(select_all_var.get())
            update_confirm_button()

        tk.Checkbutton(checkbox_frame, text="Select All", variable=select_all_var, 
                       font="Helvetica 10 bold", command=select_all_action).pack(fill='x', padx=20)
        tk.Frame(checkbox_frame, height=2, bd=1, relief=tk.SUNKEN).pack(fill='x', pady=5, padx=20)

        # 4. Populate tasks
        for item in myList.get(0, tk.END):
            var = tk.BooleanVar()
            var.trace_add("write", update_confirm_button)
            cb = tk.Checkbutton(checkbox_frame, text=item, variable=var, font=myFont, anchor="w")
            cb.pack(fill='x', padx=20)
            checkboxes.append((cb, var))
            
    else:
        # Finalize Deletion
        for i in range(len(checkboxes) - 1, -1, -1):
            _, var = checkboxes[i]
            if var.get():
                myList.delete(i)
        exit_delete_mode()

def exit_delete_mode():
    """Helper to restore the main screen."""
    global delete_mode, cancel_btn
    
    # Clean up canvas widgets
    for widget in myFrame.winfo_children():
        if widget not in [myList, y_scroll, x_scroll]:
            widget.destroy()
    
    # Remove Cancel button
    if 'cancel_btn' in globals():
        try:
            cancel_btn.destroy()
        except:
            pass

    # Restore Main View
    myList.grid()
    y_scroll.grid()
    x_scroll.grid()
    delete_mode = False
    delete.config(text="Delete Task", state=tk.NORMAL)
    myEntry.pack(pady=10, before=buttonFrame)
    add.grid()
    update_status()

# ============================
# SECTION - Menu Functions
# ============================
def save_list():
    """Save to the existing file path. If none exists, trigger Save As."""
    global current_file_path, is_modified
    
    if current_file_path:
        try:
            with open(current_file_path, "w", encoding="utf-8") as f:
                for i in range(myList.size()):
                    f.write(myList.get(i) + "\n")
            is_modified = False
            update_title()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"Could not save file: {e}")
    else:
        save_as_list()

def save_as_list():
    """Force the user to choose a new file location."""
    global current_file_path, is_modified
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    default_filename = f"task-list-{current_date}"

    file_path = filedialog.asksaveasfilename(
        initialfile=default_filename,
        defaultextension=".txt",
        title="Save File As",
        filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
    )

    if file_path:
        current_file_path = file_path
        save_list() # Reuse the logic above

def open_list():
    global current_file_path, is_modified
    file_path = filedialog.askopenfilename(
        defaultextension=".txt",
        filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
    )
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
    """Clear all tasks."""
    myList.delete(0, tk.END)
    update_status()
    
def mark_modified():
    global is_modified
    is_modified = True
    update_title()

def update_title():
    title = "To Do List"
    if current_file_path:
        # Show just the filename, not the full path
        file_name = os.path.basename(current_file_path)
        title += f" - {file_name}"
    if is_modified:
        title += " *"
    main.title(title)
# ============================
# SECTION - Menu
# ============================
my_Menu = tk.Menu(main)
main.config(menu=my_Menu)

file_menu = tk.Menu(my_Menu, tearoff=False)
my_Menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open List", command=open_list)
file_menu.add_command(label="Save", command=save_list) # Quick save / overwrite
file_menu.add_command(label="Save As...", command=save_as_list) # New file
file_menu.add_separator()
file_menu.add_command(label="Clear List", command=delete_list)

# ============================
# SECTION - Buttons
# ============================
add = tk.Button(
    buttonFrame, text="Add Task", command=add_item,
    bg="#cce6ff", fg="#000000",
    activebackground="#99ccff", activeforeground="#000000"
)
delete = tk.Button(
    buttonFrame, text="Delete Task", command=toggle_delete_mode,
    bg="#ff9999", fg="#000000",
    activebackground="#ff6666", activeforeground="#000000"
)
# done = tk.Button(
#     buttonFrame, text="Mark Complete", command=done_item,
#     bg="#99ff99", fg="#000000",
#     activebackground="#66ff66", activeforeground="#000000"
# )
# undone = tk.Button(
#     buttonFrame, text="Undo Mark", command=undone_item,
#     bg="#ffcc99", fg="#000000",
#     activebackground="#ffb366", activeforeground="#000000"
# )

# Place buttons in grid
add.grid(row=0, column=1, padx=20)
delete.grid(row=0, column=0)
# done.grid(row=0, column=2)
# undone.grid(row=0, column=2)
# ============================
# SECTION - Input Validation & Tracers
# ============================
def check_entry(*args):
    """Enables/Disables Add button based on text content."""
    if myEntry.get().strip():
        add.config(state=tk.NORMAL)
    else:
        add.config(state=tk.DISABLED)

# Link the entry box to the validation function
entry_var = tk.StringVar()
myEntry.config(textvariable=entry_var)
entry_var.trace_add("write", check_entry)

# Set initial state
add.config(state=tk.DISABLED)
update_status()
# ============================
# SECTION - Run Application
# ============================
main.mainloop()
