import numpy as np
import time
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_algorithms import Grover, AmplificationProblem


# Oracle to mark the correct state
def custom_oracle(num_qubits, target_index):
    oracle = QuantumCircuit(num_qubits)
    binary_target = format(target_index, f'0{num_qubits}b')

    for i, bit in enumerate(reversed(binary_target)):
        if bit == '0':
            oracle.x(i)

    oracle.h(num_qubits - 1)
    oracle.mcx(list(range(num_qubits - 1)), num_qubits - 1)
    oracle.h(num_qubits - 1)

    for i, bit in enumerate(reversed(binary_target)):
        if bit == '0':
            oracle.x(i)

    return oracle


# Grover's algorithm execution
def grover_search(num_qubits, target_index):
    backend = AerSimulator()
    oracle = custom_oracle(num_qubits, target_index)
    problem = AmplificationProblem(oracle)
    num_iterations = int(np.pi / 4 * np.sqrt(2 ** num_qubits))
    grover = Grover(iterations=num_iterations)

    qc = grover.construct_circuit(problem)
    transpiled_qc = transpile(qc, backend)

    start_time = time.perf_counter()
    backend.run(transpiled_qc).result()
    elapsed_time = time.perf_counter() - start_time
    return elapsed_time

# Classical search 
def classical_search(database_size, target_index):
    database = list(range(database_size))

    start_time = time.perf_counter()
    for idx, item in enumerate(database):
        if idx == target_index:
            break
    elapsed_time = time.perf_counter() - start_time
    return elapsed_time

# Comparison function
def compare_search_algorithms(database_sizes, num_trials=5):
    quantum_times = []
    classical_times = []

    for n in database_sizes:
        num_qubits = int(np.log2(n)) + 1
        target_index = np.random.randint(0, n)

        q_time_avg = np.mean([grover_search(num_qubits, target_index) for _ in range(num_trials)])
        c_time_avg = np.mean([classical_search(n, target_index) for _ in range(num_trials)])

        quantum_times.append(q_time_avg)
        classical_times.append(c_time_avg)

    return quantum_times, classical_times

# Display raw data in a table
def print_raw_data_table(database_sizes, quantum_times, classical_times):
    print("\nRaw Timing Data (Averages from 5 trials):")
    print("{:<15} {:<20} {:<20}".format("Database Size", "Quantum Time (s)", "Classical Time (s)"))
    print("-" * 55)
    for size, q_time, c_time in zip(database_sizes, quantum_times, classical_times):
        print("{:<15} {:<20.6f} {:<20.6f}".format(size, q_time, c_time))

# Plotting the results
def plot_search_performance():
    database_sizes = [2 ** i for i in range(3, 18)]  # 2^3 = 8 up to 2^17 = 131072
    quantum_times, classical_times = compare_search_algorithms(database_sizes)

    print_raw_data_table(database_sizes, quantum_times, classical_times)

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))  # Now 3 plots side by side

    # Quantum search performance
    axes[0].plot(database_sizes, quantum_times, label="Grover’s Algorithm", marker='^', color='b')
    axes[0].set_xscale("log")
    axes[0].set_yscale("log")
    axes[0].set_xlabel("Database Size")
    axes[0].set_ylabel("Execution Time (s)")
    axes[0].set_title("Quantum Search Performance")
    axes[0].legend()
    axes[0].grid()

    # Classical search performance
    axes[1].plot(database_sizes, classical_times, label="Classical Linear Search", marker='o', color='r')
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_xlabel("Database Size")
    axes[1].set_ylabel("Execution Time (s)")
    axes[1].set_title("Classical Search Performance")
    axes[1].legend()
    axes[1].grid()

    # Time Growth Rate plot
    quantum_growth = [quantum_times[i+1] / quantum_times[i] for i in range(len(quantum_times) - 1)]
    classical_growth = [classical_times[i+1] / classical_times[i] for i in range(len(classical_times) - 1)]

    axes[2].plot(database_sizes[:-1], quantum_growth, label="Quantum Growth Rate", marker='^', color='blue')
    axes[2].plot(database_sizes[:-1], classical_growth, label="Classical Growth Rate", marker='o', color='red')
    axes[2].set_xscale("log")
    axes[2].set_xlabel("Database Size")
    axes[2].set_ylabel("Growth Rate (Next/Current)")
    axes[2].set_title("Time Growth Rate Comparison")
    axes[2].legend()
    axes[2].grid()

    plt.tight_layout()
    plt.show()

# Run everything
plot_search_performance()
