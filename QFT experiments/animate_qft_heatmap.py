import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from qft_circuits import qft_circuit
from simulator import basis_state, run_statevector


def compute_qft_matrix(n_qubits):
    size = 2 ** n_qubits
    matrix = np.zeros((size, size))

    qft = qft_circuit(n_qubits)

    for i in range(size):
        prep = basis_state(n_qubits, i)
        full_circuit = prep.compose(qft)

        state = run_statevector(full_circuit)
        probs = np.abs(state) ** 2
        matrix[i] = probs

    return matrix


def animate_heatmap(matrix):
    fig, ax = plt.subplots(figsize=(6, 5))

    def update(frame):
        ax.clear()
        data = matrix[: frame + 1, :]
        sns_plot = ax.imshow(data, cmap="viridis", aspect="auto")
        ax.set_title("QFT Transformation (Growing Input Set)")
        ax.set_xlabel("Output State")
        ax.set_ylabel("Input State")

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=len(matrix),
        interval=800,
        repeat=False
    )

    plt.show()


if __name__ == "__main__":
    n_qubits = 3  # change to 2 or 3
    matrix = compute_qft_matrix(n_qubits)

    animate_heatmap(matrix)