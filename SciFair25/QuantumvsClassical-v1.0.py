import time
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_algorithms import Grover, AmplificationProblem

# Simple fixed oracle for state |11> (for 2 qubits)
def fixed_oracle():
    qc = QuantumCircuit(2)
    qc.cz(0, 1)  # Phase flip on |11>
    return qc

def quantum_search_2qubits():
    sim = AerSimulator()
    oracle = fixed_oracle()
    problem = AmplificationProblem(oracle)
    iterations = 1  # Usually around sqrt(N), here N=4, so 1 iteration
    grover = Grover(iterations=iterations)

    qc = grover.construct_circuit(problem)
    compiled = transpile(qc, sim)

    start = time.perf_counter()
    result = sim.run(compiled).result()
    end = time.perf_counter()
    return end - start

def classical_search_4items(target=3):
    data = [0, 1, 2, 3]
    start = time.perf_counter()
    for item in data:
        if item == target:
            break
    end = time.perf_counter()
    return end - start

if __name__ == "__main__":
    q_time = quantum_search_2qubits()
    c_time = classical_search_4items()

    print(f"Quantum Search time: {q_time:.6f} seconds")
    print(f"Classical Search time: {c_time:.6f} seconds")
