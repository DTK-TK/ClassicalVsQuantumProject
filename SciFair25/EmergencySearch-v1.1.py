import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd

data = pd.DataFrame()

def load_csv():
    global data
    path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if path:
        try:
            data = pd.read_csv(path)
            messagebox.showinfo("Loaded", "CSV loaded yayy")
        except Exception as e:
            messagebox.showerror("Error", "Failed to load CSV")

def search():
    query = entry_query.get().strip()
    if data.empty:
        messagebox.showwarning("Warning", "No data loaded yet")
        return
    for i, row in data.iterrows():
        if 'Name' in data.columns and str(row['Name']).lower() == query.lower():
            messagebox.showinfo("Found", f"Name: {row['Name']}\nPhone: {row.get('Phone Number', 'N/A')}")
            return
        if 'Phone Number' in data.columns and str(row['Phone Number']) == query:
            messagebox.showinfo("Found", f"Name: {row.get('Name', 'N/A')}\nPhone: {row['Phone Number']}")
            return
    messagebox.showinfo("Not Found", "No matching entry found")

root = tk.Tk()
root.title("Contact Finder")


btn_load = tk.Button(root, text="Load CSV", command=load_csv)
btn_load.pack()

entry_query = tk.Entry(root)
entry_query.pack()

btn_search = tk.Button(root, text="Search", command=search)
btn_search.pack()

root.mainloop()
