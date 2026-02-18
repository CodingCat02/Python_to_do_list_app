import os
import sys
import tkinter as tk
from tkinter import font, filedialog

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
main.geometry("500x500")
main.resizable(False, False)
main.configure(bg="SystemButtonFace")
main.maxsize(500, 500)
main.minsize(600, 600)  # Note: minsize > geometry; may cause issues
main.iconbitmap(resource_path("icons/notepad.ico"))

# ============================
# SECTION - Frames
# ============================
myFrame = tk.Frame(main)
myFrame.pack(pady=10)

buttonFrame = tk.Frame(main)
buttonFrame.pack(pady=20)

# ============================
# SECTION - Font
# ============================
myFont = font.Font(family='Helvetica', size=25, weight='bold')

# ============================
# SECTION - Listbox and Scrollbar
# ============================
myList = tk.Listbox(
    myFrame,
    font=myFont,
    width=25,
    height=5,
    bd=0,
    fg="#464646",
    bg="SystemButtonFace",
    highlightthickness=0,
    selectbackground="#a6a6a6",
    activestyle="none"
)
myList.pack(side=tk.LEFT, fill=tk.BOTH)

myScroll = tk.Scrollbar(myFrame)
myScroll.pack(side=tk.RIGHT, fill=tk.BOTH)

myList.configure(yscrollcommand=myScroll.set)
myScroll.config(command=myList.yview)

# ============================
# SECTION - Entry Box
# ============================
myEntry = tk.Entry(
    main, 
    font="Helvetica 24 bold", 
    width=26, 
    bd=3, 
    fg="#464646", 
    bg="SystemButtonFace", 
    highlightthickness=0
)
myEntry.pack(pady=20)

# ============================
# SECTION - Variables
# ============================
checkboxes = []
delete_mode = False
checkbox_frame = None

# ============================
# SECTION - Functions
# ============================
def add_item():
    """Add task from entry to listbox."""
    item_text = myEntry.get().strip()
    if item_text:
        myList.insert(tk.END, item_text)
    myEntry.delete(0, tk.END)

def done_item():
    """Mark selected task as complete."""
    if myList.curselection():
        myList.itemconfig(myList.curselection(), fg="#dedede")
        myList.selection_clear(0, tk.END)

def undone_item():
    """Undo completed status of selected task."""
    if myList.curselection():
        myList.itemconfig(myList.curselection(), fg="#464646")
        myList.selection_clear(0, tk.END)

def remove_complete_item():
    """Remove all completed tasks from listbox."""
    for i in range(myList.size() - 1, -1, -1):
        if myList.itemcget(i, 'fg') == '#dedede':
            myList.delete(i)

def toggle_delete_mode():
    """
    Toggle delete mode:
    - Show checkboxes for tasks
    - Confirm deletion
    """
    global delete_mode, checkboxes, checkbox_frame

    if not delete_mode:
        # Enter delete mode
        delete_mode = True
        delete.config(text="Confirm Delete")

        # Hide main widgets
        myEntry.pack_forget()
        add.grid_remove()
        done.grid_remove()
        undone.grid_remove()
        myList.pack_forget()

        # Show checkboxes
        checkbox_frame = tk.Frame(myFrame)
        checkbox_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        checkboxes = []

        for item in myList.get(0, tk.END):
            var = tk.BooleanVar()
            cb = tk.Checkbutton(checkbox_frame, text=item, variable=var, font=myFont, anchor="w")
            cb.pack(fill='x')
            checkboxes.append((cb, var))

    else:
        # Confirm deletion
        for i in range(len(checkboxes) - 1, -1, -1):
            cb, var = checkboxes[i]
            if var.get():
                myList.delete(i)

        # Clean up checkbox view
        for widget in checkbox_frame.winfo_children():
            widget.destroy()
        checkbox_frame.pack_forget()

        # Restore main view
        myList.pack(side=tk.LEFT, fill=tk.BOTH)
        delete.config(text="Delete Task")
        delete_mode = False
        myEntry.pack(pady=20, before=buttonFrame)
        add.grid()
        done.grid()
        undone.grid()

# ============================
# SECTION - Menu Functions
# ============================
def save_list():
    """Save tasks to a text file and remove completed tasks."""
    file_name = filedialog.asksaveasfilename(
        defaultextension=".txt",
        title="Save File",
        filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
    )

    if file_name:
        if not file_name.endswith(".txt"):
            file_name = f"{file_name}.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            for i in range(myList.size()):
                f.write(myList.get(i) + "\n")

        # Remove completed tasks
        count = 0
        while count < myList.size():
            if myList.itemcget(count, 'fg') == '#dedede':
                myList.delete(count)
            else:
                count += 1

def open_list():
    """Open tasks from a text file."""
    file_name = filedialog.askopenfilename(
        defaultextension=".txt",
        title="Open File",
        filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
    )
    if file_name:
        myList.delete(0, tk.END)
        with open(file_name, "r", encoding="utf-8") as f:
            for line in f:
                myList.insert(tk.END, line.strip())

def delete_list():
    """Clear all tasks."""
    myList.delete(0, tk.END)

# ============================
# SECTION - Menu
# ============================
my_Menu = tk.Menu(main)
main.config(menu=my_Menu)

file_menu = tk.Menu(my_Menu, tearoff=False)
my_Menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Save List", command=save_list)
file_menu.add_command(label="Open List", command=open_list)
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
done = tk.Button(
    buttonFrame, text="Mark Complete", command=done_item,
    bg="#99ff99", fg="#000000",
    activebackground="#66ff66", activeforeground="#000000"
)
undone = tk.Button(
    buttonFrame, text="Undo Mark", command=undone_item,
    bg="#ffcc99", fg="#000000",
    activebackground="#ffb366", activeforeground="#000000"
)

# Place buttons in grid
add.grid(row=0, column=1, padx=20)
delete.grid(row=0, column=0)
done.grid(row=0, column=2)
undone.grid(row=0, column=3, padx=20)

# ============================
# SECTION - Run Application
# ============================
main.mainloop()
