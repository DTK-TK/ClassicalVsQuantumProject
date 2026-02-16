import time
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
import matplotlib.pyplot as plt
import numpy as np

def classical_search(data, target):
    for item in data:
        if item == target:
            return True
    return False

def grover_search(n_qubits, target_state):
    backend = Aer.get_backend('qasm_simulator')
    qc = QuantumCircuit(n_qubits, n_qubits)
    
    # Initialize all qubits in superposition
    qc.h(range(n_qubits))
    
    # Oracle: phase flip for target_state
    for i, bit in enumerate(format(target_state, f'0{n_qubits}b')):
        if bit == '0':
            qc.x(i)
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    qc.h(n_qubits - 1)
    for i, bit in enumerate(format(target_state, f'0{n_qubits}b')):
        if bit == '0':
            qc.x(i)
    
    # Diffuser
    qc.h(range(n_qubits))
    qc.x(range(n_qubits))
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    qc.h(n_qubits - 1)
    qc.x(range(n_qubits))
    qc.h(range(n_qubits))
    
    qc.measure(range(n_qubits), range(n_qubits))
    
    shots = 1024
    compiled_circuit = transpile(qc, backend)
    job = backend.run(compiled_circuit, shots=shots)
    result = job.result().get_counts()
    
    return max(result, key=result.get)

db_sizes = [4, 8, 16, 32]
classical_times = []
quantum_times = []

for size in db_sizes:
    target = size // 2
    
    # Prepare data for classical search
    data = list(range(size))
    
    # Classical timing (average over 5 runs)
    c_times = []
    for _ in range(5):
        start = time.time()
        classical_search(data, target)
        c_times.append(time.time() - start)
    classical_times.append(np.mean(c_times))
    
    # Quantum timing (simulate Grover's algorithm average over 5 runs)
    q_times = []
    for _ in range(5):
        start = time.time()
        grover_search(int(np.log2(size)), target)
        q_times.append(time.time() - start)
    quantum_times.append(np.mean(q_times))

plt.plot(db_sizes, classical_times, 'o-', label='Classical Search')
plt.plot(db_sizes, quantum_times, 's-', label='Grover Quantum Search')
plt.xlabel('Database Size')
plt.ylabel('Average Time (seconds)')
plt.title('Classical vs Grover Search Timing Comparison')
plt.legend()
plt.show()
