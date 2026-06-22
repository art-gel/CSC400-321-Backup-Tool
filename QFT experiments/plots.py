import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure results directory exists
os.makedirs("qft_visualization/results", exist_ok=True)

def plot_probabilities(statevector, title=""):
    probs = np.abs(statevector) ** 2
    x = np.arange(len(probs))

    plt.figure(figsize=(6, 4))
    plt.bar(x, probs)
    plt.title(title)
    plt.xlabel("Basis State")
    plt.ylabel("Probability")
    plt.ylim(0, 1)

    filename = f"{RESULTS_DIR}/probabilities_{title.replace(' ', '_')}.png"
    plt.savefig(filename, dpi=300, bbox_inches="tight")

    plt.show()
    plt.close()


def plot_heatmap(matrix, title="QFT Transformation Heatmap"):
    plt.figure(figsize=(8, 6))
    sns.heatmap(matrix, cmap="viridis", annot=False)

    plt.title(title)
    plt.xlabel("Output State")
    plt.ylabel("Input State")

    # Save figure to file
    output_path = "qft_visualization/results/heatmap.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")

    plt.show()
    plt.close()

def plot_before_after(before_state, after_state, title="Before vs After QFT"):
    before_probs = np.abs(before_state) ** 2
    after_probs = np.abs(after_state) ** 2

    x = np.arange(len(before_probs))

    plt.figure(figsize=(10, 4))

    # Before QFT
    plt.subplot(1, 2, 1)
    plt.bar(x, before_probs, color="blue")
    plt.title("Before QFT")
    plt.xlabel("Basis State")
    plt.ylabel("Probability")
    plt.ylim(0, 1)

    # After QFT
    plt.subplot(1, 2, 2)
    plt.bar(x, after_probs, color="orange")
    plt.title("After QFT")
    plt.xlabel("Basis State")
    plt.ylim(0, 1)

    plt.suptitle(title)
    plt.tight_layout()

    # Save figure to file
    output_path = "qft_visualization/results/heatmap.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")

    plt.show()