import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_algorithms import Grover, AmplificationProblem
import time

data = pd.DataFrame()

def load_csv(path):
    global data
    try:
        data = pd.read_csv(path)
        messagebox.showinfo("Loaded", "File loaded yay")
    except:
        messagebox.showerror("Oops", "Couldn't read the file")


def run_grover(thing_to_find):
    global data
    if data.empty:
        return None, False, None
    
    
    original_len = len(data)
    next_pow = 2 ** int(np.ceil(np.log2(original_len)))
    if next_pow > original_len:
        padding = pd.DataFrame([[""] * len(data.columns)] * (next_pow - original_len), columns=data.columns)
        padded = pd.concat([data, padding], ignore_index=True)
    else:
        padded = data.copy()

    
    idx = None
    for i in range(len(padded)):
        row = padded.iloc[i]
        if thing_to_find.lower() in str(row['Name']).lower() or thing_to_find in str(row['Phone Number']):
            idx = i
            break
    if idx is None:
        return None, False, None

    qubits = int(np.ceil(np.log2(len(padded))))

    def make_oracle(n, idx):
        qc = QuantumCircuit(n + 1)
        b = format(idx, f'0{n}b')
        for j in range(n):
            if b[::-1][j] == '0':
                qc.x(j)
        qc.x(n) # ancilla qubit
        qc.h(n)
        qc.mcx(list(range(n)), n)
        qc.h(n)
        qc.x(n)
        for j in range(n):
            if b[::-1][j] == '0':
                qc.x(j)
        return qc

    oracle = make_oracle(qubits, idx)
    backend = AerSimulator()

    def good_state(bits):
        return bits == format(idx, f'0{qubits}b')

    prob = AmplificationProblem(oracle, is_good_state=good_state)
    grover = Grover(iterations=1)

    circuit = grover.construct_circuit(prob)
    circuit.measure_all()
    job = backend.run(transpile(circuit, backend), shots=1024)

    start = time.perf_counter()
    result = job.result()
    duration = time.perf_counter() - start

    counts = result.get_counts()
    best = max(counts, key=counts.get)
    found = int(best, 2)

    if found == idx and found < original_len:
        return duration, True, data.iloc[found]
    else:
        return duration, False, None

def do_search():
    name = name_entry.get().strip()
    relation = relation_entry.get().strip()

    if not name:
        messagebox.showwarning("Wait", "Please enter a name or number")
        return

    time_used, ok, row = run_grover(name)
    if not ok or row is None:
        messagebox.showinfo("Nope", "Didn't find anything for " + name)
        return

    matches = data[data['Name'].str.lower() == row['Name'].lower()]
    if relation:
        matches = matches[matches['Relationship'].str.lower() == relation.lower()]
        if matches.empty:
            messagebox.showinfo("None", "No such relationship found")
            return

    lines = []
    for i, r in matches.iterrows():
        lines.append(f"{r['Relationship']} of {r['Name']} - {r['Phone Number']} | {r['Related Person Name']} - {r['Related Person Number']}")

    messagebox.showinfo("Results", "\n".join(lines))

def show_all_contacts():
    win = tk.Toplevel(root)
    win.title("All Contacts")
    txt = tk.Text(win, wrap='word')
    txt.pack(expand=True, fill='both')

    if data.empty:
        txt.insert(tk.END, "No contacts loaded yet.")
    else:
        for i, r in data.iterrows():
            txt.insert(tk.END, f"{r['Relationship']} of {r['Name']} - {r['Phone Number']} | {r['Related Person Name']} - {r['Related Person Number']}\n")

def import_csv_data():
    path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if path:
        load_csv(path)

# ---- UI setup weeeeeeeee im so good at graphic designing haha ----
root = tk.Tk()
root.title("Emergency Contact Finder")
root.geometry("600x560")

label_title = tk.Label(root, text="Emergency Contact Finder", font=("Arial", 18, "bold"))
label_title.pack(pady=12)

label_name = tk.Label(root, text="Person Name or Phone Number:")
label_name.pack()
name_entry = tk.Entry(root, width=45)
name_entry.pack(pady=5)

label_relation = tk.Label(root, text="Relationship (optional):")
label_relation.pack()
relation_entry = tk.Entry(root, width=45)
relation_entry.pack(pady=5)

btn_search = tk.Button(root, text="Search Relationship(s)", command=do_search, width=30, bg="#4CAF50", fg="white")
btn_search.pack(pady=10)

btn_show_all = tk.Button(root, text="Show All Contacts", command=show_all_contacts, width=30)
btn_show_all.pack(pady=5)

btn_import_data = tk.Button(root, text="Import CSV Data", command=import_csv_data, width=30)
btn_import_data.pack(pady=5)

btn_exit = tk.Button(root, text="Exit", command=root.quit, width=30, bg="#f44336", fg="white")
btn_exit.pack(pady=20)

root.mainloop()
