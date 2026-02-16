import numpy as np
import time
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import ZGate
from qiskit_algorithms import Grover, AmplificationProblem

def oracle_thing(n_qubits: int, target: int) -> QuantumCircuit:
    oracle = QuantumCircuit(n_qubits)
    binary = format(target, f"0{n_qubits}b")

    for i, bit in enumerate(reversed(binary)):
        if bit == '0':
            oracle.x(i)

    oracle.h(n_qubits - 1)
    oracle.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    oracle.h(n_qubits - 1)

    for i, bit in enumerate(reversed(binary)):
        if bit == '0':
            oracle.x(i)

    return oracle


def quantumSearch(n_qubits: int, target: int) -> float:
    simulator = AerSimulator()
    oracle = oracle_thing(n_qubits, target)

    problem = AmplificationProblem(oracle, is_good_state=lambda bits: bits == format(target, f'0{n_qubits}b'))

    iterations = int(np.pi / 4 * np.sqrt(2 ** n_qubits))
    grover = Grover(iterations=iterations)
    qc = grover.construct_circuit(problem)

    qc.measure_all()

    compiled = transpile(qc, simulator)
    t0 = time.perf_counter()
    result = simulator.run(compiled).result()
    tf = time.perf_counter()
    return tf - t0


def normalSearch(db_size: int, index: int) -> float:
    items = list(range(db_size))
    np.random.shuffle(items)  

    t0 = time.perf_counter()
    for i in range(len(items)):
        if items[i] == index:
            break
    tf = time.perf_counter()
    return tf - t0


def runTests(dbSizes, times=5):
    qts, cts = [], []

    for db in dbSizes:
        nq = int(np.ceil(np.log2(db)))
        pick = np.random.randint(0, 2 ** nq)

        qavg = [quantumSearch(nq, pick) for _ in range(times)]
        cavg = [normalSearch(2 ** nq, pick) for _ in range(times)]

        qts.append(np.mean(qavg))
        cts.append(np.mean(cavg))

    return qts, cts


def showTable(sizes, qt, ct):
    print("Results (averages from 5 runs):")
    print("DB Size       | Quantum Time      | Classical Time")
    print("----------------------------------------------------")
    for i in range(len(sizes)):
        print(f"{sizes[i]:<13} {qt[i]:<18.6f} {ct[i]:<18.6f}")


def plotit():
    dbs = [2 ** i for i in range(3, 18)]  
    qt, ct = runTests(dbs)

    showTable(dbs, qt, ct)

    fig, ax = plt.subplots(1, 3, figsize=(18, 5))

    ax[0].plot(dbs, qt, label="Quantum", marker='^', color='b')
    ax[0].set_xscale("log")
    ax[0].set_yscale("log")
    ax[0].set_title("Quantum Search")
    ax[0].set_xlabel("DB Size")
    ax[0].set_ylabel("Time")
    ax[0].legend()
    ax[0].grid()

    ax[1].plot(dbs, ct, label="Classical", marker='o', color='r')
    ax[1].set_xscale("log")
    ax[1].set_yscale("log")
    ax[1].set_title("Classical Search")
    ax[1].set_xlabel("DB Size")
    ax[1].set_ylabel("Time")
    ax[1].legend()
    ax[1].grid()

    qdiff = [qt[i + 1] / qt[i] for i in range(len(qt) - 1)]
    cdiff = [ct[i + 1] / ct[i] for i in range(len(ct) - 1)]

    ax[2].plot(dbs[:-1], qdiff, label="Quantum Growth", marker='^', color='blue')
    ax[2].plot(dbs[:-1], cdiff, label="Classical Growth", marker='o', color='red')
    ax[2].set_xscale("log")
    ax[2].set_title("Growth Comparison")
    ax[2].set_xlabel("DB Size")
    ax[2].set_ylabel("Ratio")
    ax[2].legend()
    ax[2].grid()

    plt.tight_layout()
    plt.show()

plotit()
