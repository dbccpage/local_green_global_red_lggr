"""Generate the two deterministic publication figures for LGGR III."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from epk_gtla_overlay_core import (
    EvaluatorVerdictTriple,
    audit_sample,
)

FIXED_INSTANT = datetime(2026, 10, 10, 12, 0, 0, tzinfo=timezone.utc)
PDF_METADATA = {
    "Title": "Local Green, Global Red III publication figure",
    "Author": "Jeremy H. Carroll",
    "Subject": "Finite evaluator defects; version 1.5.1; 2026-10-10",
    "Keywords": "finite evaluator defect, composition, quotient descent",
    "Creator": "LGGR III deterministic figure producer",
    "Producer": "LGGR III deterministic figure producer",
    "CreationDate": FIXED_INSTANT,
    "ModDate": FIXED_INSTANT,
}
PNG_METADATA = {
    "Author": "Jeremy H. Carroll",
    "Creation Time": "2026-10-10T12:00:00Z",
    "Description": "Local Green, Global Red III; version 1.5.1",
    "Software": "LGGR III deterministic figure producer",
}


def ensure_export_dir() -> Path:
    export = Path(__file__).resolve().parent.parent / "public_export"
    export.mkdir(parents=True, exist_ok=True)
    return export


def _save(fig: plt.Figure, export_dir: str | Path, stem: str) -> tuple[Path, Path]:
    destination = Path(export_dir)
    destination.mkdir(parents=True, exist_ok=True)
    png = destination / f"{stem}.png"
    pdf = destination / f"{stem}.pdf"
    fig.savefig(png, dpi=240, bbox_inches="tight", metadata=PNG_METADATA)
    fig.savefig(pdf, bbox_inches="tight", metadata=PDF_METADATA)
    plt.close(fig)
    print(f"Generated {png} and {pdf}")
    return png, pdf


def generate_figure_1(export_dir: str | Path) -> tuple[Path, Path]:
    """Show one defect record reused across six roles."""

    roles = (
        "finite\nobstruction",
        "foundations",
        "representation",
        "observer",
        "continuum\nshadow",
        "action and\nalignment",
    )
    colors = ("#286090", "#3a7ca5", "#4f91b8", "#65a3c8", "#7bb5d5", "#91c5df")

    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.set_xlim(-0.3, 6.3)
    ax.set_ylim(-0.25, 2.3)
    ax.axis("off")
    ax.set_title(
        "One finite comparison across six system roles", fontsize=17, weight="bold"
    )

    for index, (role, color) in enumerate(zip(roles, colors, strict=True)):
        box = FancyBboxPatch(
            (index, 0.8),
            0.8,
            0.72,
            boxstyle="round,pad=0.04",
            facecolor=color,
            edgecolor="#18364a",
            linewidth=1.2,
        )
        ax.add_patch(box)
        ax.text(
            index + 0.4,
            1.16,
            role,
            ha="center",
            va="center",
            color="white",
            fontsize=8.8
            if role in {"representation", "action and\nalignment"}
            else 10.5,
            weight="bold",
        )
        ax.annotate(
            "",
            xy=(index + 0.4, 0.73),
            xytext=(index + 0.4, 0.32),
            arrowprops={"arrowstyle": "->", "color": "#444444", "lw": 1.1},
        )

    ax.text(
        2.9,
        0.12,
        r"same record:  $(e_1,e_2,e_g,\Delta_E)$      with      $\Delta_E=e_g-e_1e_2$",
        ha="center",
        va="center",
        fontsize=14,
        bbox={
            "boxstyle": "round,pad=0.45",
            "facecolor": "#f4f7fa",
            "edgecolor": "#286090",
        },
    )
    ax.text(
        2.9,
        1.95,
        "The role changes the context; the defect formula does not.",
        ha="center",
        fontsize=12,
        color="#333333",
    )
    return _save(fig, export_dir, "figure_1_one_record_six_roles")


def generate_figure_2(export_dir: str | Path) -> tuple[Path, Path]:
    """Show the five-trace identity and a cancellation counterexample."""

    samples = (
        EvaluatorVerdictTriple(1, 1, 1),
        EvaluatorVerdictTriple(1, 1, 0),
        EvaluatorVerdictTriple(1, 1, 0),
        EvaluatorVerdictTriple(0, 1, 0),
        EvaluatorVerdictTriple(0, 0, 0),
    )
    audit = audit_sample(samples)
    x = list(range(1, 6))
    global_values = [sample.eg for sample in samples]
    local_values = [sample.local_product for sample in samples]
    defects = [sample.evaluator_defect for sample in samples]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.4))
    fig.suptitle(
        "Finite defects: pointwise values and their sum", fontsize=17, weight="bold"
    )

    width = 0.23
    left = axes[0]
    left.bar(
        [value - width for value in x],
        global_values,
        width,
        label=r"$e_g$",
        color="#4c956c",
    )
    left.bar(x, local_values, width, label=r"$e_1e_2$", color="#2f6690")
    left.bar(
        [value + width for value in x],
        defects,
        width,
        label=r"$\Delta_E$",
        color="#c44536",
    )
    left.axhline(0, color="#333333", linewidth=0.8)
    left.set_xticks(x, [str(value) for value in x])
    left.set_xlabel("trace")
    left.set_ylabel("value")
    left.set_title("Five-trace example")
    left.legend(frameon=False, ncols=3, loc="lower center")
    left.text(
        3,
        1.18,
        f"G={audit.global_sum}, L={audit.local_product_sum}, D={audit.defect_sum};  G-L=D",
        ha="center",
        weight="bold",
    )
    left.set_ylim(-1.35, 1.35)

    right = axes[1]
    pair = (1, -1)
    right.bar(("trace A", "trace B"), pair, color=("#e07a1f", "#c44536"), width=0.55)
    right.axhline(0, color="#333333", linewidth=0.8)
    right.set_ylim(-1.35, 1.35)
    right.set_ylabel(r"$\Delta_E$")
    right.set_title("Cancellation counterexample")
    right.text(0.5, 1.12, r"$1+(-1)=0$", ha="center", fontsize=14, weight="bold")
    right.text(
        0.5,
        -1.10,
        "A zero total does not make either\npointwise defect zero.",
        ha="center",
        fontsize=9.5,
    )

    fig.tight_layout()
    return _save(fig, export_dir, "figure_2_finite_defects_and_cancellation")


def main() -> None:
    export_dir = ensure_export_dir()
    generate_figure_1(export_dir)
    generate_figure_2(export_dir)


if __name__ == "__main__":  # pragma: no cover - exercised as the public command
    main()
