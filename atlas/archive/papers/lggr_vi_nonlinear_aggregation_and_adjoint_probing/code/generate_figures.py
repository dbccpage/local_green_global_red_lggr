"""Generate the two publication figures for LGGR VI."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from lggr_vi_core import (
    ObservationSystem,
    full_rademacher_directions,
    rademacher_adjoint_estimate,
)


# Noon UTC keeps the calendar date on 2026-09-21 in both UTC and North
# American time zones while making the generated PDF metadata deterministic.
RELEASE_TIME = datetime(2026, 9, 21, 12, tzinfo=timezone.utc)


def _save(figure: plt.Figure, stem: Path) -> tuple[Path, Path]:
    png = stem.with_suffix(".png")
    pdf = stem.with_suffix(".pdf")
    figure.savefig(png, dpi=180, bbox_inches="tight", metadata={"Software": "LGGR VI"})
    figure.savefig(
        pdf,
        bbox_inches="tight",
        metadata={
            "Creator": "LGGR VI",
            "CreationDate": RELEASE_TIME,
            "ModDate": RELEASE_TIME,
        },
    )
    plt.close(figure)
    return png, pdf


def generate_geometry_figure(output_directory: Path) -> tuple[Path, Path]:
    system = ObservationSystem([[1.0, 0.0]])
    hidden = np.array([0.0, 1.25])
    visible = np.array([1.0, 0.25])
    figure, axis = plt.subplots(figsize=(6.2, 4.2))
    axis.axvline(0.0, color="#377eb8", linewidth=5, alpha=0.35, label=r"$\ker Q$")
    axis.arrow(
        0.0, 0.0, *hidden, color="#4daf4a", width=0.015, length_includes_head=True
    )
    axis.arrow(
        0.0, 0.0, *visible, color="#e41a1c", width=0.015, length_includes_head=True
    )
    axis.arrow(
        0.0,
        0.0,
        *system.adjoint_signal(visible),
        color="#984ea3",
        width=0.012,
        length_includes_head=True,
    )
    axis.text(0.05, 1.3, "hidden state", color="#2b7b32")
    axis.text(1.02, 0.27, "visible state", color="#b31316")
    axis.text(1.02, -0.12, r"$Q^TQx$", color="#6a3280")
    axis.set(
        xlim=(-0.45, 1.55),
        ylim=(-0.45, 1.7),
        xlabel="visible coordinate",
        ylabel="hidden coordinate",
    )
    axis.set_aspect("equal")
    axis.grid(alpha=0.2)
    axis.legend(loc="upper right")
    return _save(figure, output_directory / "figure_1_kernel_and_adjoint")


def generate_probe_figure(output_directory: Path) -> tuple[Path, Path]:
    system = ObservationSystem([[2.0, -1.0], [0.0, 0.5]])
    state = np.array([0.8, -0.4])
    directions = full_rademacher_directions(2)
    truth = system.adjoint_signal(state)
    errors = []
    for count in range(1, len(directions) + 1):
        estimate = rademacher_adjoint_estimate(system, state, directions[:count])
        errors.append(float(np.linalg.norm(estimate - truth)))
    figure, axis = plt.subplots(figsize=(6.2, 4.2))
    axis.plot(range(1, len(errors) + 1), errors, marker="o", color="#ff7f00")
    axis.set(
        xlabel="number of sign probes",
        ylabel=r"$\|\widehat{Q^TQx}-Q^TQx\|_2$",
        xticks=range(1, len(errors) + 1),
    )
    axis.set_title("All four sign probes recover the adjoint signal")
    axis.grid(alpha=0.25)
    return _save(figure, output_directory / "figure_2_sign_probe_error")


def generate_all(output_directory: str | Path) -> tuple[Path, ...]:
    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)
    return (*generate_geometry_figure(output_path), *generate_probe_figure(output_path))


if __name__ == "__main__":  # pragma: no cover
    generate_all(Path(__file__).resolve().parents[1] / "figures")
