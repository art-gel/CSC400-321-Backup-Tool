from qiskit import QuantumCircuit

from qft_circuits import qft_circuit
from simulator import run_statevector, basis_state
from plots import plot_before_after


def run_demo(n_qubits=3, input_index=1):

    # -------------------------
    # Build input state
    # -------------------------
    prep = basis_state(n_qubits, input_index)
    before_state = run_statevector(prep)

    # -------------------------
    # Apply QFT
    # -------------------------
    qft = qft_circuit(n_qubits)
    full = prep.compose(qft)
    after_state = run_statevector(full)

    # -------------------------
    # Plot comparison
    # -------------------------
    plot_before_after(
        before_state,
        after_state,
        title=f"QFT Transformation (Input |{input_index:0{n_qubits}b}⟩)"
    )


if __name__ == "__main__":
    run_demo(n_qubits=3, input_index=2)