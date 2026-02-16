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
    relation = entry_relation.get().strip().lower()
    if data.empty:
        messagebox.showwarning("Warning", "No data loaded yet")
        return

    matches = []
    for i, row in data.iterrows():
        if (str(row.get('Name', '')).lower() == query.lower() or str(row.get('Phone Number', '')) == query):
            if relation:
                if str(row.get('Relationship', '')).lower() == relation:
                    matches.append(row)
            else:
                matches.append(row)

    if matches:
        result_text = ""
        for m in matches:
            result_text += f"{m['Relationship']} of {m['Name']} - {m['Phone Number']}\n"
        messagebox.showinfo("Results", result_text)
    else:
        messagebox.showinfo("Not Found", "No matching contacts found")

root = tk.Tk()
root.title("Contact Finder")

btn_load = tk.Button(root, text="Load CSV", command=load_csv)
btn_load.pack()

entry_query = tk.Entry(root)
entry_query.pack()

entry_relation = tk.Entry(root)
entry_relation.pack()

btn_search = tk.Button(root, text="Search", command=search)
btn_search.pack()

root.mainloop()
