"""Figure Generator for Paper 012.

Generates publication-grade 4-panel diagnostic figure:
- Panel (a): LGGR Diagnostic Plane — Signed-Defect Level Sets
- Panel (b): Illustrative Activation-Density Model
- Panel (c): Evaluator Defect Trichotomy
- Panel (d): Illustrative Evaluator-Composition Scaling

Exports one four-panel figure to:
- public_export/figure_lggr_phase_boundary.png (.pdf), the primary name
- public_export/figure_1_lggr_diagnostics.png (.pdf), a byte-identical
  compatibility alias retained for older links

AuthorityEffect: None.
Anchoring: sealed-derivation-v1 (3100c4e).
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# Ensure headless execution
plt.switch_backend("Agg")

PUBLICATION_TIME = datetime(2026, 9, 15, 12, 0, 0, tzinfo=timezone.utc)
PDF_METADATA = {
    "Title": "Local Green, Global Red I — finite defect diagnostics",
    "Author": "Jeremy H. Carroll",
    "Subject": "Evaluated path kernels and finite evaluator-gluing defects",
    "Keywords": "evaluated path kernels, evaluator gluing defect, finite diagnostics",
    "Creator": "LGGR I deterministic figure producer",
    "Producer": "LGGR I deterministic figure producer",
    "CreationDate": PUBLICATION_TIME,
    "ModDate": PUBLICATION_TIME,
}
PNG_METADATA = {
    "Title": PDF_METADATA["Title"],
    "Author": PDF_METADATA["Author"],
    "Description": PDF_METADATA["Subject"],
    "Software": PDF_METADATA["Producer"],
    "Creation Time": "2026-09-15T12:00:00Z",
}


def generate_all_figures(output_dir: Path | str | None = None) -> Path:
    """Generates the publication 4-panel figure and exports to PNG and PDF."""
    if output_dir is None:
        paper_root = Path(__file__).resolve().parent.parent
        out_path = paper_root / "public_export"
    else:
        out_path = Path(output_dir)

    out_path.mkdir(parents=True, exist_ok=True)
    primary_fig_file = out_path / "figure_lggr_phase_boundary.png"
    compat_fig_file = out_path / "figure_1_lggr_diagnostics.png"

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
        "axes.edgecolor": "#333333",
        "axes.linewidth": 1.0,
        "grid.color": "#cccccc",
        "grid.linestyle": ":",
        "grid.linewidth": 0.8,
    })

    fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=300)
    fig.subplots_adjust(hspace=0.32, wspace=0.26)

    # -------------------------------------------------------------
    # Panel (a): LGGR Diagnostic Plane — Signed-Defect Level Sets
    # -------------------------------------------------------------
    ax_a = axes[0, 0]
    np.linspace(0.0, 1.0, 100)
    delta_couplings = [-0.6, -0.4, -0.2, 0.0, 0.2]
    colors_a = ["#d9534f", "#f0ad4e", "#5bc0de", "#5cb85c", "#0275d8"]

    for d_coup, col in zip(delta_couplings, colors_a):
        lpr_min = max(0.0, -d_coup)
        lpr_max = min(1.0, 1.0 - d_coup)
        lpr_segment = np.linspace(lpr_min, lpr_max, 100)
        gpr_curve = lpr_segment + d_coup
        label = f"$\\bar{{\\Delta}}_E = {d_coup:+.1f}$" if d_coup != 0 else "Zero Signed Mean ($\\bar{\\Delta}_E = 0$)"
        style = "--" if d_coup == 0 else "-"
        ax_a.plot(lpr_segment, gpr_curve, label=label, color=col, linestyle=style, linewidth=2.2)

    # Highlight Illustrative LGGR Zone (Local Green >= 0.7, Global Red <= 0.4)
    ax_a.axvspan(0.7, 1.0, 0.0, 0.4, color="#d9534f", alpha=0.18, label="Illustrative LGGR Zone")
    ax_a.plot([0.7, 1.0], [0.4, 0.4], color="#d9534f", linestyle=":", linewidth=1.5)
    ax_a.plot([0.7, 0.7], [0.0, 0.4], color="#d9534f", linestyle=":", linewidth=1.5)
    ax_a.text(0.85, 0.20, "Illustrative\nLGGR Zone", color="#841a18", fontsize=10,
              fontweight="bold", ha="center", va="center")

    ax_a.set_title("(a) LGGR Diagnostic Plane — Signed-Defect Level Sets", fontsize=12, fontweight="bold")
    ax_a.set_xlabel("Local Pass Rate (LPR)", fontsize=10)
    ax_a.set_ylabel("Global Pass Rate (GPR)", fontsize=10)
    ax_a.set_xlim(0.0, 1.0)
    ax_a.set_ylim(0.0, 1.0)
    ax_a.grid(True)
    ax_a.legend(loc="upper left", fontsize=8, framealpha=0.9)

    # -------------------------------------------------------------
    # Panel (b): Illustrative Activation-Density Model
    # -------------------------------------------------------------
    ax_b = axes[0, 1]
    alphas = np.linspace(0.0, 1.0, 200)
    c_base, gamma_c = 0.5, 0.5
    d_base, kappa, gamma_d = 0.0, 0.85, 1.6

    cap = c_base + (1.0 - c_base) * (alphas ** gamma_c)
    def_rate = np.clip(d_base + kappa * (alphas ** gamma_d), 0.0, 1.0)
    net_succ = cap * (1.0 - def_rate)

    best_idx = int(np.argmax(net_succ))
    alpha_star = alphas[best_idx]
    s_star = net_succ[best_idx]

    ax_b.plot(alphas, cap, color="#0275d8", linestyle="--", linewidth=2.0, label="Capability $C(\\alpha)$")
    ax_b.plot(alphas, def_rate, color="#d9534f", linestyle=":", linewidth=2.0, label="Defect Rate $D(\\alpha)$")
    ax_b.plot(alphas, net_succ, color="#5cb85c", linestyle="-", linewidth=2.5, label="Net Success $S(\\alpha)$")
    ax_b.axvline(alpha_star, color="#333333", linestyle="-.", linewidth=1.5, label=f"Interior Optimum $\\alpha^*={alpha_star:.2f}$")
    ax_b.scatter([alpha_star], [s_star], color="#2b542c", s=70, zorder=5)

    ax_b.text(alpha_star + 0.04, s_star - 0.08,
              f"$\\alpha^* = {alpha_star:.2f}$\n$S^* = {s_star:.2f}$",
              fontsize=9, fontweight="bold", color="#2b542c",
              bbox=dict(boxstyle="round,pad=0.3", facecolor="#e8f5e9", edgecolor="#5cb85c", alpha=0.8))

    ax_b.text(0.04, 0.92, "synthetic parameterization; model condition",
              transform=ax_b.transAxes, fontsize=8, fontstyle="italic", color="#555555",
              bbox=dict(boxstyle="round,pad=0.2", facecolor="#f8f9fa", edgecolor="#cccccc", alpha=0.8))

    ax_b.set_title("(b) Illustrative Activation-Density Model", fontsize=12, fontweight="bold")
    ax_b.set_xlabel("Tool/Expert Activation Density $\\alpha$", fontsize=10)
    ax_b.set_ylabel("Probability / Rate Index", fontsize=10)
    ax_b.set_xlim(0.0, 1.0)
    ax_b.set_ylim(0.0, 1.05)
    ax_b.grid(True)
    ax_b.legend(loc="lower left", fontsize=8, framealpha=0.9)

    # -------------------------------------------------------------
    # Panel (c): Evaluator Defect Trichotomy
    # -------------------------------------------------------------
    ax_c = axes[1, 0]
    regimes = ["Factorized", "Asymmetric LGGR", "Dynamic Rescue"]
    ngd_rates = [0.00, 0.40, 0.15]
    pgd_rates = [0.00, 0.00, 0.25]
    zdr_rates = [1.00, 0.60, 0.60]

    x = np.arange(len(regimes))
    width = 0.26

    rects1 = ax_c.bar(x - width, ngd_rates, width, label="NGD (Local Green, Global Red)", color="#d9534f", edgecolor="#841a18")
    rects2 = ax_c.bar(x, pgd_rates, width, label="PGD (Local Red, Global Green)", color="#0275d8", edgecolor="#014c8c")
    rects3 = ax_c.bar(x + width, zdr_rates, width, label="ZDR (Verdict Agreement)", color="#5cb85c", edgecolor="#398439")

    # Value annotations on bars
    for rects in (rects1, rects2, rects3):
        for rect in rects:
            height = rect.get_height()
            if height > 0.02:
                ax_c.annotate(f"{height:.2f}",
                              xy=(rect.get_x() + rect.get_width() / 2, height),
                              xytext=(0, 3), textcoords="offset points",
                              ha="center", va="bottom", fontsize=8)

    ax_c.set_title("(c) Evaluator Defect Trichotomy", fontsize=12, fontweight="bold")
    ax_c.set_xticks(x)
    ax_c.set_xticklabels(regimes, fontsize=9)
    ax_c.set_ylabel("Trace Fraction", fontsize=10)
    ax_c.set_ylim(0, 1.15)
    ax_c.grid(True, axis="y")
    ax_c.legend(loc="upper right", fontsize=8, framealpha=0.9)

    # -------------------------------------------------------------
    # Panel (d): Illustrative Evaluator-Composition Scaling
    # -------------------------------------------------------------
    ax_d = axes[1, 1]
    k_stages = np.arange(1, 11)
    p_step_success = 0.95
    p_step_defect = 0.04

    # Independent hard-gate conjunction: p^K (under independent validation stages)
    gate_pass = p_step_success ** k_stages
    # Complementary false refusal inflation under independent hard conjunction: 1 - p^K
    gate_refusal = 1.0 - (p_step_success ** k_stages)
    # Thresholded voting defect accumulation: separate synthetic scaling model curve
    voting_defect_model = 1.0 - (1.0 - p_step_defect) ** (k_stages * 0.6)

    ax_d.plot(k_stages, gate_pass, "o-", color="#d9534f", linewidth=2.2, label="Hard Conjunction $p^K$ (Independent)")
    ax_d.plot(k_stages, gate_refusal, "^--", color="#f0ad4e", linewidth=2.0, label="Conjunctive Refusal $1-p^K$ ($p=0.95$)")
    ax_d.plot(k_stages, voting_defect_model, "s-.", color="#0275d8", linewidth=2.0, label="Voting Defect Model (Synthetic Scaling)")
    ax_d.axhline(0.5, color="gray", linestyle=":", alpha=0.7)

    ax_d.set_title("(d) Illustrative Evaluator-Composition Scaling", fontsize=12, fontweight="bold")
    ax_d.set_xlabel("Number of Pipeline Stages $K$", fontsize=10)
    ax_d.set_ylabel("Probability", fontsize=10)
    ax_d.set_xlim(1, 10)
    ax_d.set_ylim(0, 1.05)
    ax_d.grid(True)
    ax_d.legend(loc="center right", fontsize=8, framealpha=0.9)

    # Render exactly once per format.  The historical second name is an
    # actual byte-for-byte alias, not a second figure or a second render whose
    # PDF metadata happens to differ.
    primary_pdf_file = primary_fig_file.with_suffix(".pdf")
    compat_pdf_file = compat_fig_file.with_suffix(".pdf")
    fig.savefig(
        primary_fig_file,
        bbox_inches="tight",
        dpi=300,
        metadata=PNG_METADATA,
    )
    fig.savefig(primary_pdf_file, bbox_inches="tight", metadata=PDF_METADATA)
    compat_fig_file.write_bytes(primary_fig_file.read_bytes())
    compat_pdf_file.write_bytes(primary_pdf_file.read_bytes())

    plt.close(fig)

    print(f"Generated publication figure: {primary_fig_file}")
    return primary_fig_file


def main(argv: list[str] | None = None) -> None:
    """Generate the four-file public figure surface."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="write the figures to this directory instead of public_export",
    )
    args = parser.parse_args(argv)
    generate_all_figures(args.output_dir)


if __name__ == "__main__":
    main()
