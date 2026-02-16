import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_algorithms import Grover, AmplificationProblem
import time

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

def run_grover_search(target):
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
        if target.lower() in str(row['Name']).lower() or target in str(row['Phone Number']):
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
        qc.x(n)
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

def search():
    target = entry_query.get().strip()
    if not target:
        messagebox.showwarning("Warning", "Please enter a name or phone number")
        return

    time_used, found, row = run_grover_search(target)
    if found and row is not None:
        messagebox.showinfo("Found", f"Name: {row['Name']}\nPhone: {row['Phone Number']}\nSearch time: {time_used:.4f}s")
    else:
        messagebox.showinfo("Not Found", "No matching contact found")

root = tk.Tk()
root.title("Contact Finder")

btn_load = tk.Button(root, text="Load CSV", command=load_csv)
btn_load.pack()

entry_query = tk.Entry(root)
entry_query.pack()

btn_search = tk.Button(root, text="Search", command=search)
btn_search.pack()

root.mainloop()
