"""Generate the publication figure for LGGR IV: Finite Presentations and Completion-Relative Obstruction.

Renders:
- public_export/figure_1_refinement_tower_and_completion.png (.pdf)

Uses headless Agg backend.
"""

from __future__ import annotations

from datetime import datetime, timezone
import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from lggr_iv_core import (
    compute_x_n,
    adic_distance_to_completion_solution,
)

RELEASE_INSTANT = datetime(2026, 9, 18, 12, tzinfo=timezone.utc)
PDF_METADATA = {
    "Title": "Local Green, Global Red IV: Finite-Stage Solvability and Completion-Relative Obstruction",
    "Author": "Jeremy H. Carroll",
    "Creator": "code/generate_figures.py",
    "CreationDate": RELEASE_INSTANT,
    "ModDate": RELEASE_INSTANT,
}


def ensure_export_dir() -> str:
    export_dir = os.path.join(os.path.dirname(__file__), "..", "public_export")
    os.makedirs(export_dir, exist_ok=True)
    return export_dir


def generate_figure_1(export_dir: str):
    """Generates Figure 1: Refinement tower, 2-adic convergence, and reflection descent."""
    fig, axs = plt.subplots(1, 3, figsize=(18, 5.5))
    fig.suptitle(
        "Local Green, Global Red IV: Finite-Stage Solvability and Completion-Relative Obstruction",
        fontsize=14,
        fontweight="bold",
    )

    # Panel A: Finite-Stage Residues and Compatibility
    ax_a = axs[0]
    ax_a.set_title("A. Finite-Stage Solvability: 3x + 1 = 0 (mod 2^n)", fontsize=11, fontweight="bold")
    stages = list(range(1, 9))
    x_vals = [compute_x_n(n) for n in stages]
    moduli = [2**n for n in stages]
    residues = [x % m for x, m in zip(x_vals, moduli)]

    y_pos = np.arange(len(stages))
    ax_a.barh(y_pos, residues, color="#2b5c8f", alpha=0.85, height=0.55, label="Residue $x_n \\bmod 2^n$")
    ax_a.set_yticks(y_pos)
    labels = [f"n={n} (mod {m})\n$x_{{{n}}}={x}$" for n, m, x in zip(stages, moduli, x_vals)]
    ax_a.set_yticklabels(labels, fontsize=8)
    ax_a.set_xlabel("Residue Value", fontsize=10)
    ax_a.grid(axis="x", linestyle="--", alpha=0.5)
    for idx, (res, mod) in enumerate(zip(residues, moduli)):
        ax_a.text(res + max(residues) * 0.02, idx, f"{res} / {mod}", va="center", fontsize=8, color="#1a365d")
    ax_a.set_xlim(0, max(residues) * 1.25)

    # Panel B: 2-adic Convergence to -1/3 in Z_2
    ax_b = axs[1]
    ax_b.set_title("B. 2-adic Distance |x_n - (-1/3)|_2 = 2^{-n}", fontsize=11, fontweight="bold")
    conv_stages = list(range(1, 16))
    distances = [float(adic_distance_to_completion_solution(n)) for n in conv_stages]
    ax_b.semilogy(conv_stages, distances, marker="o", color="#2e7d32", linewidth=2, label="2-adic distance in $\\mathbb{Z}_2$")
    ax_b.axhline(0, color="gray", linestyle=":")
    ax_b.set_xlabel("Stage $n$", fontsize=10)
    ax_b.set_ylabel("Metric Distance to $-1/3$", fontsize=10)
    ax_b.set_xticks(conv_stages[::2])
    ax_b.grid(True, linestyle="--", alpha=0.5)
    ax_b.annotate(
        "Completion Green:\n$x_\\infty = -1/3 \\in \\mathbb{Z}_2$",
        xy=(8, distances[7]),
        xytext=(9, 0.05),
        arrowprops=dict(facecolor="#2e7d32", shrink=0.08, width=1.5, headwidth=6),
        fontsize=9,
        fontweight="bold",
        color="#1b5e20",
    )

    # Panel C: Reflection Descent and Carrier Decoupling
    ax_c = axs[2]
    ax_c.set_title("C. Carrier Reflection: $\\eta: \\mathbb{Z} \\hookrightarrow \\mathbb{Z}_2$", fontsize=11, fontweight="bold")
    ax_c.axis("off")

    # Diagrammatic representation
    box_props_z = dict(boxstyle="round,pad=0.6", facecolor="#e3f2fd", edgecolor="#1565c0", linewidth=1.5)
    box_props_z2 = dict(boxstyle="round,pad=0.8", facecolor="#f1f8e9", edgecolor="#33691e", linewidth=1.5)
    box_props_sol = dict(boxstyle="round,pad=0.4", facecolor="#ffebee", edgecolor="#c62828", linewidth=1.5)

    ax_c.text(0.5, 0.85, "Original Carrier $\\mathbb{Z}$ (Integers)", ha="center", va="center", bbox=box_props_z, fontsize=10, fontweight="bold")
    ax_c.text(0.5, 0.72, "Global Red: $\\forall x \\in \\mathbb{Z},\\; \\exists n: 3x+1 \\not\\equiv 0$ (mod $2^n$)\nNo solution in $\\mathbb{Z}$ because $-1/3 \\notin \\mathbb{Z}$", ha="center", va="center", fontsize=8.5, color="#b71c1c")

    ax_c.annotate("", xy=(0.5, 0.48), xytext=(0.5, 0.63), arrowprops=dict(arrowstyle="->", lw=2, color="#1565c0"))
    ax_c.text(0.52, 0.55, "Canonical Reflection $\\eta$", ha="left", va="center", fontsize=9, fontstyle="italic", color="#0d47a1")

    ax_c.text(0.5, 0.35, "Completion $\\mathbb{Z}_2$ (2-adic Integers)", ha="center", va="center", bbox=box_props_z2, fontsize=10, fontweight="bold")
    ax_c.text(0.5, 0.20, "Unique Solution: $x_\\infty = -1/3 \\in \\mathbb{Z}_2$\nResidual: $-1/3 \\notin \\mathrm{im}(\\eta) \\Rightarrow [x_\\infty] \\neq 0 \\in \\mathbb{Z}_2 / \\mathbb{Z}$", ha="center", va="center", bbox=box_props_sol, fontsize=8.5, color="#263238")
    ax_c.text(0.5, 0.05, "Completion Green does NOT promote to Original Green", ha="center", va="center", fontsize=9, fontweight="bold", color="#c62828")

    plt.tight_layout()

    out_png = os.path.join(export_dir, "figure_1_refinement_tower_and_completion.png")
    out_pdf = os.path.join(export_dir, "figure_1_refinement_tower_and_completion.pdf")

    plt.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.savefig(out_pdf, bbox_inches="tight", metadata=PDF_METADATA)
    plt.close()
    print(f"Generated: {out_png}")
    print(f"Generated: {out_pdf}")


def main():
    export_dir = ensure_export_dir()
    generate_figure_1(export_dir)


if __name__ == "__main__":
    main()
