import tkinter as tk
from tkinter import font
from tkinter import filedialog

# Main window
main = tk.Tk()
main.title("To Do List")
main.geometry("500x500")
main.iconbitmap('icons/notepad.ico')

# Frame
myFrame = tk.Frame(main)
myFrame.pack(pady=10)

# Font
myFont = font.Font(family='Helvetica', size=25, weight='bold')

# List Box
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

# Scroll bar
myScroll = tk.Scrollbar(myFrame)
myScroll.pack(side=tk.RIGHT, fill=tk.BOTH)

myList.configure(yscrollcommand=myScroll.set)
myScroll.config(command=myList.yview)

# Entry box
myEntry = tk.Entry(main, font="Helvetica 24 bold", width=26)
myEntry.pack(pady=20)
# myEntry.insert(0, "sample")

# Button frame
buttonFrame = tk.Frame(main)
buttonFrame.pack(pady=20)

# Variables
checkboxes = []
delete_mode = False
checkbox_frame = None

# Functions
def add_item():
    # myList.insert(tk.END, myEntry.get())
    
    emptyText = myEntry.get().strip()
    if emptyText:
        myList.insert(tk.END, emptyText)
    myEntry.delete(0, tk.END)
    
def done_item():
    if not myList.curselection():
        return
    myList.itemconfig(myList.curselection(), fg="#dedede")
    myList.selection_clear(0, tk.END)

def undone_item():
    if not myList.curselection():
        return
    myList.itemconfig(myList.curselection(), fg="#464646")
    myList.selection_clear(0, tk.END)

def remove_complete_item():
    for i in range(myList.size() - 1, -1, -1):
        if myList.itemcget(i, 'fg') == '#dedede':
            myList.delete(i)

def toggle_delete_mode():
    global delete_mode, checkboxes, checkbox_frame

    if not delete_mode:  
        delete_mode = True
        delete.config(text="Confirm Delete")

        # Hide all the buttons listbox
        myEntry.pack_forget()        
        add.grid_remove()
        done.grid_remove()
        undone.grid_remove()
        
        myList.pack_forget()  
        checkbox_frame = tk.Frame(myFrame)
        checkbox_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        
        checkboxes = []
        for item in myList.get(0, tk.END):
            var = tk.BooleanVar()
            cb = tk.Checkbutton(checkbox_frame, text=item, variable=var, font=myFont, anchor="w")
            cb.pack(fill='x')
            checkboxes.append((cb, var))

    else:  # Confirm deletion
        for i in range(len(checkboxes) - 1, -1, -1): 
            cb, var = checkboxes[i]
            if var.get():
                myList.delete(i)

        # Clean up checkbox view
        for widget in checkbox_frame.winfo_children():
            widget.destroy()
        checkbox_frame.pack_forget()

        myList.pack(side=tk.LEFT, fill=tk.BOTH)
        delete.config(text="Delete Task")
        delete_mode = False
        
        myEntry.pack(pady=20, before=buttonFrame)   
        add.grid()
        done.grid()
        undone.grid()
        
# Menu functions
def save_list():
    file_name = filedialog.asksaveasfilename(
        defaultextension=".txt",
        title="Save File",
        filetypes=(
            ("Text Files", "*.txt"),
            ("All Files", "*.*")
        )
    )

    if file_name:  
        if not file_name.endswith(".txt"): 
            file_name = f"{file_name}.txt"

        with open(file_name, "w", encoding="utf-8") as f:
            for i in range(myList.size()):
                f.write(myList.get(i) + "\n")
                
    # NOTE - Delete completed tasks after saving
    count = 0    
    while count < myList.size():
        if myList.itemcget(count, 'fg') == '#dedede':
            myList.delete(myList.index(count))
        else:
            count += 1
             
def open_list():
    file_name = filedialog.askopenfilename(
        defaultextension=".txt",
        title="Open File", 
        filetypes=(
            ("Text Files", "*.txt"),
            ("All Files", "*.*")
        )
    )
    # Clear current list
    if file_name:
        myList.delete(0, tk.END)  
        with open(file_name, "r", encoding="utf-8") as f:
            for line in f:
                myList.insert(tk.END, line.strip())
        
def delete_list():
    myList.delete(0, tk.END)

my_Menu = tk.Menu(main)
main.config(menu=my_Menu)

# Menu items
file_menu = tk.Menu(my_Menu, tearoff=False)
my_Menu.add_cascade(label="File", menu=file_menu)

# Dropdown items
file_menu.add_command(label="Save List", command=save_list)
file_menu.add_command(label="Open List", command=open_list)
file_menu.add_command(label="Clear List", command=delete_list)

# Buttons
add = tk.Button(buttonFrame, text="Add Task", command=add_item)
delete = tk.Button(buttonFrame, text="Delete Task", command=toggle_delete_mode)
done = tk.Button(buttonFrame, text="Mark Complete", command=done_item)
undone = tk.Button(buttonFrame, text="Undo Mark", command=undone_item)
# removeComplete = tk.Button(buttonFrame, text="Delete Mark", command=remove_complete_item)

add.grid(row=0, column=1, padx=20)
delete.grid(row=0, column=0)
done.grid(row=0, column=2)
undone.grid(row=0, column=3, padx=20)
# removeComplete.grid(row=0, column=4, padx=20)

# Run app
main.mainloop()

