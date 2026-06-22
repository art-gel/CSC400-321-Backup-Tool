from qiskit import QuantumCircuit
import numpy as np


def qft_circuit(n_qubits: int) -> QuantumCircuit:
    qc = QuantumCircuit(n_qubits)

    for j in range(n_qubits):
        qc.h(j)
        for k in range(j + 1, n_qubits):
            angle = np.pi / (2 ** (k - j))
            qc.cp(angle, k, j)

    # swap qubits (important for correct ordering)
    for i in range(n_qubits // 2):
        qc.swap(i, n_qubits - i - 1)

    return qc


def inverse_qft_circuit(n_qubits: int) -> QuantumCircuit:
    return qft_circuit(n_qubits).inverse()