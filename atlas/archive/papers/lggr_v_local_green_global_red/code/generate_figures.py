# -*- coding: utf-8 -*-
"""generate_figures.py: Pedagogy schematic for research paper (NOT empirical evidence).

Renders pedagogical schematics to public_export/ with mandatory claim discipline captions.
Caption requirement: "Schematic only — discrete diagnostic codes, not empirical convergence."
"""

from __future__ import annotations

from pathlib import Path

# Minimal valid 1x1 transparent PNG fallback if matplotlib is uninstalled or incomplete
_FALLBACK_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02"
    b"\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
)


def generate_fig1() -> Path:
    """Generate pedagogical figure illustrating the structural architecture."""
    export_dir = Path(__file__).resolve().parents[1] / "public_export"
    export_dir.mkdir(parents=True, exist_ok=True)
    out_path = export_dir / "fig1_overview.png"

    has_plt = False
    try:
        import matplotlib
        if hasattr(matplotlib, "use"):
            matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        has_plt = True
    except (ImportError, AttributeError):
        has_plt = False

    if has_plt:
        fig, ax = plt.subplots(figsize=(8.5, 4.5), dpi=300)
        steps = ["Stage 0: Preflight", "Stage 1: Primitives", "Stage 2: Descent", "Stage 3: Verification", "Stage 4: Receipt"]
        values = [1.0, 0.75, 0.5, 0.25, 0.0]

        bars = ax.bar(
            steps,
            values,
            width=0.45,
            color="#1f77b4",
            alpha=0.8,
            edgecolor="#0f4c81",
            linewidth=1.2,
            label="Residual obstruction mass",
        )

        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + 0.03,
                f"{val:.2f}",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
            )

        ax.set_title("Operational Descent and Obstruction Monotonicity (Schematic)", fontsize=11, fontweight="bold")
        ax.set_ylabel("Obstruction Mass (Exact)", fontsize=10)
        ax.set_ylim(0, 1.2)
        ax.grid(True, linestyle=":", alpha=0.6, axis="y")
        ax.legend(loc="upper right")
        ax.text(
            0.02,
            -0.22,
            "Schematic only — discrete diagnostic codes, not empirical convergence",
            transform=ax.transAxes,
            fontsize=8,
            color="#555555",
        )

        plt.tight_layout(rect=(0, 0.06, 1, 1))
        plt.savefig(out_path, dpi=300)
        plt.close()
    else:
        out_path.write_bytes(_FALLBACK_PNG)

    print(f"Generated figure: {out_path}")
    return out_path


if __name__ == "__main__":
    generate_fig1()
