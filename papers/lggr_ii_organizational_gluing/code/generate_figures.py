"""
Generate the two publication figures for LGGR II.

Renders:
- public_export/figure_1_organizational_cut_architecture.png (.pdf)
- public_export/figure_2_case_studies_defect_matrix.png (.pdf)

The module always uses the headless Agg backend.
"""

from __future__ import annotations

from datetime import datetime, timezone
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


RELEASE_INSTANT = datetime(2026, 9, 15, 12, tzinfo=timezone.utc)
PDF_METADATA = {
    "Title": "Local Green, Global Red II: Organizational Evaluator Gluing",
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
    """Generates Figure 1: 4-panel organizational cut architecture."""
    fig, axs = plt.subplots(2, 2, figsize=(15, 11))
    fig.suptitle("Local Green, Global Red II: Organizational Evaluator Gluing", fontsize=16, fontweight="bold")

    # Panel A: Truth Table of Evaluator Gluing Defect Δ_E = E_G - E_1 * E_2
    ax_a = axs[0, 0]
    ax_a.set_title("A. Evaluator Gluing Defect Trichotomy Δ_E", fontsize=12, fontweight="bold")
    truth_data = [
        ("0", "0", "0", "0", "0", "Agreement at Joint Failure"),
        ("0", "1", "0", "0", "0", "Agreement (Partial Fail)"),
        ("1", "0", "0", "0", "0", "Agreement (Partial Fail)"),
        ("1", "1", "1", "0", "-1", "Disagreement: Local Green, Global Red (LGGR)"),
        ("0", "0", "0", "1", "+1", "Disagreement: Global-Only Pass"),
        ("0", "1", "0", "1", "+1", "Disagreement: Global-Only Pass"),
        ("1", "0", "0", "1", "+1", "Disagreement: Global-Only Pass"),
        ("1", "1", "1", "1", "0", "Agreement at Joint Pass"),
    ]
    col_labels = ["E1", "E2", "∏ Ei", "EG", "Δ_E", "Regime"]
    col_widths = [0.09, 0.09, 0.11, 0.09, 0.10, 0.52]
    cell_colors = []
    for row in truth_data:
        delta = row[4]
        if delta == "-1":
            cell_colors.append(["#ffcccc"] * len(row))
        elif delta == "+1":
            cell_colors.append(["#fff2cc"] * len(row))
        else:
            cell_colors.append(["#e2f0d9"] * len(row))

    table = ax_a.table(
        cellText=truth_data,
        colLabels=col_labels,
        colWidths=col_widths,
        cellColours=cell_colors,
        loc="center",
        cellLoc="center",
    )
    table.scale(1, 1.4)
    table.auto_set_font_size(False)
    table.set_fontsize(9.5)
    ax_a.axis("off")

    # Panel B: Range Violation (Lemma 4.2.1) vs Shapley Values
    ax_b = axs[0, 1]
    ax_b.set_title("B. Direct sums can leave the Boolean defect range", fontsize=12, fontweight="bold")
    x = np.arange(1, 4)
    individual_defects = [-1, -1, -1]
    cumulative = np.cumsum(individual_defects)

    for val, lbl in [(-1, "-1"), (0, "0"), (1, "+1")]:
        ax_b.axhspan(val - 0.15, val + 0.15, color="#e2f0d9", alpha=0.6)
    ax_b.plot([], [], color="#e2f0d9", linewidth=8, alpha=0.6, label="Allowed Evaluator Defect Values {-1, 0, +1}")
    ax_b.plot(x, cumulative, marker="s", color="crimson", linewidth=2.5, markersize=10, label="Direct Scalar Sum (-1, -2, -3)")
    for xi, yi in zip(x, cumulative):
        ax_b.annotate(f"{yi}", (xi, yi), textcoords="offset points", xytext=(8, 8), fontweight="bold", fontsize=10)
    ax_b.axhline(-1, color="red", linestyle="--", alpha=0.7)
    ax_b.axhline(1, color="green", linestyle="--", alpha=0.7)
    ax_b.set_xticks([1, 2, 3])
    ax_b.set_xticklabels(["Δ_rep (-1)", "+ Δ_auth (-1)", "+ Δ_time (-1)"])
    ax_b.set_ylabel("Accumulated Defect Value")
    ax_b.set_ylim(-3.5, 1.5)
    ax_b.annotate("Range Violation: -3 ∉ {-1, 0, 1}", xy=(3, -3), xytext=(2.0, -2.5),
                 arrowprops=dict(arrowstyle="->", color="black", lw=1.5), fontweight="bold")
    ax_b.legend(loc="upper right", fontsize=9)
    ax_b.grid(True, alpha=0.3)

    # Panel C: three abstract assignments with the same defect.
    ax_c = axs[1, 0]
    ax_c.set_title("C. Three local-green / global-red assignments", fontsize=12, fontweight="bold", pad=16)
    cases = ["Boundary A", "Boundary B", "Boundary C"]
    lpr = [1.0, 1.0, 1.0]  # Local pass model inputs
    gpr = [0.0, 0.0, 0.0]  # Global pass model inputs
    width = 0.35
    ind = np.arange(len(cases))

    ax_c.bar(ind - width/2, lpr, width, label="Local Pass Verdict (E1·E2 = 1)", color="forestgreen")
    ax_c.bar(ind + width/2, gpr, width, label="Global Pass Verdict (EG = 0)", color="firebrick")
    ax_c.set_ylabel("Declared Verdict (Model Input)", fontweight="bold")
    ax_c.set_xticks(ind)
    ax_c.set_xticklabels(cases, fontweight="bold")
    ax_c.set_ylim(0, 1.25)
    ax_c.text(0.5, 1.01, "Boolean inputs, not measured rates",
              transform=ax_c.transAxes, ha="center", fontsize=8.5, fontstyle="italic", color="#444444")
    ax_c.legend(loc="upper right", fontsize=9)
    for i in ind:
        ax_c.text(i, 0.5, "Δ_E = -1\n(LGGR)", ha="center", va="center", color="black", fontweight="bold",
                 bbox=dict(boxstyle="round,pad=0.3", fc="#ffcccc", ec="red"))
    ax_c.grid(axis="y", alpha=0.3)

    # Panel D: Conjunction & Boundary Governance Architecture
    ax_d = axs[1, 1]
    ax_d.set_title("D. Boundary Governance & Verification Architecture", fontsize=12, fontweight="bold")
    ax_d.axis("off")
    formula_text = (
        "Boolean boundary model:\n\n"
        "  Evaluator Defect: Δ_E = E_G - ∏ E_i ∈ {-1, 0, +1}\n"
        "  Factorization:    E_G = ∏ E_i  (Δ_E = 0)\n\n"
        "Declared governance checks:\n\n"
        "  • G_rep  (Representational sufficiency)\n"
        "  • G_auth (authority + accountability)\n"
        "  • G_time (Temporal coherence)\n\n"
        "Weak-sufficiency counterexample (Proposition 2):\n\n"
        "  G_rep ∧ G_auth ∧ G_time DOES NOT FORCE E_G = ∏ E_i\n"
        "  (Counterexample: R recovers E_G, yet Δ_E = -1)\n\n"
        "Checked-closure eligibility (definition):\n\n"
        "  Requires BOTH evaluator agreement (Δ_E = 0)\n"
        "  AND verified governance prerequisites.\n"
        "  GovernanceReady ==> G_auth  [conjunction elimination]\n\n"
        "Detector note:\n\n"
        "  • RED (Δ_E = -1): Sound detection of non-factorization\n"
        "  • GREEN (Δ_E = 0): Unsound certificate without adequacy\n"
    )
    ax_d.text(0.04, 0.5, formula_text, fontsize=9.5, family="monospace", va="center",
              bbox=dict(boxstyle="round,pad=0.8", fc="#f8f9fa", ec="#dee2e6", lw=2))

    plt.tight_layout()
    png_path = os.path.join(export_dir, "figure_1_organizational_cut_architecture.png")
    pdf_path = os.path.join(export_dir, "figure_1_organizational_cut_architecture.pdf")
    plt.savefig(png_path, dpi=300)
    plt.savefig(pdf_path, metadata=PDF_METADATA)
    plt.close(fig)
    print(f"Saved Figure 1 to {png_path} and {pdf_path}")


def generate_figure_2(export_dir: str):
    """Generate Figure 2: a generic boundary-condition matrix."""
    fig, ax = plt.subplots(figsize=(14, 3.8))
    ax.set_title("Figure 2: Boundary-condition matrix\n"
                 "(declared Boolean assignments)", fontsize=13, fontweight="bold")

    headers = [
        "Scenario",
        "Incoming Side",
        "Outgoing Side",
        "E1 Validator",
        "E2 Validator",
        "EG Evaluator",
        "Ownership state",
        "Δ_E",
    ]
    matrix_data = [
        [
            "A: handoff",
            "Validated input",
            "Integrated output",
            "Unit check 1 (1)",
            "Unit check 2 (1)",
            "End-to-end check (0)",
            "authority only",
            "-1",
        ],
        [
            "B: scale-up",
            "Pilot output",
            "Production output",
            "Unit check 1 (1)",
            "Unit check 2 (1)",
            "End-to-end check (0)",
            "accountability only",
            "-1",
        ],
        [
            "C: composed test",
            "Subsystem outputs",
            "System outcome",
            "Unit check 1 (1)",
            "Unit check 2 (1)",
            "End-to-end check (0)",
            "no declared owner",
            "-1",
        ],
    ]
    col_widths = [0.16, 0.13, 0.13, 0.12, 0.12, 0.14, 0.15, 0.05]

    colors = [["#ffcccc"] * len(headers) for _ in matrix_data]
    tbl = ax.table(
        cellText=matrix_data,
        colLabels=headers,
        colWidths=col_widths,
        cellColours=colors,
        loc="center",
        cellLoc="center",
    )
    tbl.scale(1, 1.8)
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    ax.axis("off")

    plt.tight_layout()
    png_path = os.path.join(export_dir, "figure_2_case_studies_defect_matrix.png")
    pdf_path = os.path.join(export_dir, "figure_2_case_studies_defect_matrix.pdf")
    plt.savefig(png_path, dpi=300)
    plt.savefig(pdf_path, metadata=PDF_METADATA)
    plt.close(fig)
    print(f"Saved Figure 2 to {png_path} and {pdf_path}")


if __name__ == "__main__":
    out_dir = ensure_export_dir()
    generate_figure_1(out_dir)
    generate_figure_2(out_dir)
