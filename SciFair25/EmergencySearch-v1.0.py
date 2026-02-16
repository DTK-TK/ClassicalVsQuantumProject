import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

data = pd.DataFrame()

def load_csv():
    global data
    path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if path:
        data = pd.read_csv(path)
        messagebox.showinfo("Loaded", "CSV loaded yayy")

def search():
    name = entry_name.get().strip()
    if data.empty:
        messagebox.showwarning("Warning", "No data loaded yet")
        return
    for i, row in data.iterrows():
        if row['Name'].lower() == name.lower():
            messagebox.showinfo("Found", f"Name: {row['Name']}\nPhone: {row['Phone Number']}")
            return
    messagebox.showinfo("Not Found", "Name not found")

root = tk.Tk()
root.title("Contact Finder")

btn_load = tk.Button(root, text="Load CSV", command=load_csv)
btn_load.pack()

entry_name = tk.Entry(root)
entry_name.pack()

btn_search = tk.Button(root, text="Search", command=search)
btn_search.pack()

root.mainloop()
