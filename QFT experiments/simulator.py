from qiskit_aer import AerSimulator
from qiskit import QuantumCircuit
import numpy as np

def basis_state(n_qubits, index):
    qc = QuantumCircuit(n_qubits)
    binary = format(index, f"0{n_qubits}b")

    for i, bit in enumerate(reversed(binary)):
        if bit == "1":
            qc.x(i)
    return qc


def run_statevector(qc: QuantumCircuit):
    sim = AerSimulator(method="statevector")
    qc = qc.copy()
    qc.save_statevector()
    result = sim.run(qc).result()
    return result.get_statevector()

def run_statevector(qc):
    sim = AerSimulator(method="statevector")
    qc = qc.copy()
    qc.save_statevector()
    result = sim.run(qc).result()
    return result.get_statevector()