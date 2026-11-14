"""Execution and byte-determinism checks for the figure producer."""

from __future__ import annotations

import hashlib
from pathlib import Path

import matplotlib.pyplot as plt
from pypdf import PdfReader

import generate_figures


EXPECTED = {
    "figure_1_one_record_six_roles.png",
    "figure_1_one_record_six_roles.pdf",
    "figure_2_finite_defects_and_cancellation.png",
    "figure_2_finite_defects_and_cancellation.pdf",
}


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _render(directory: Path) -> None:
    generate_figures.generate_figure_1(directory)
    generate_figures.generate_figure_2(directory)


def test_figure_generator_writes_all_formats_and_fixed_pdf_metadata(
    tmp_path: Path,
) -> None:
    _render(tmp_path)
    assert {path.name for path in tmp_path.iterdir()} == EXPECTED
    assert all((tmp_path / name).stat().st_size > 1_000 for name in EXPECTED)
    assert not plt.get_fignums()
    for name in EXPECTED:
        if name.endswith(".pdf"):
            metadata = PdfReader(tmp_path / name).metadata
            assert metadata is not None
            assert metadata.author == "Jeremy H. Carroll"
            assert metadata.creation_date is not None
            assert metadata.creation_date.isoformat() == "2026-10-10T12:00:00+00:00"
            assert metadata.modification_date is not None
            assert metadata.modification_date.isoformat() == "2026-10-10T12:00:00+00:00"


def test_pdf_generation_is_byte_deterministic_across_two_runs(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    _render(first)
    _render(second)
    for name in sorted(EXPECTED):
        assert _hash(first / name) == _hash(second / name), name


def test_export_directory_is_package_local() -> None:
    export_dir = generate_figures.ensure_export_dir().resolve()
    assert export_dir.name == "public_export"
    assert export_dir.parent == Path(generate_figures.__file__).resolve().parent.parent


def test_figure_one_uses_exact_sixth_role_label() -> None:
    source = Path(generate_figures.__file__).read_text(encoding="utf-8")
    assert '"action and\\nalignment"' in source
    assert '        "action",' not in source


def test_main_uses_the_single_export_directory(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(generate_figures, "ensure_export_dir", lambda: tmp_path)
    generate_figures.main()
    assert {path.name for path in tmp_path.iterdir()} == EXPECTED
