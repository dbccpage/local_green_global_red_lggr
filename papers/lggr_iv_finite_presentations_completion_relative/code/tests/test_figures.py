"""Test generation of publication figures."""

from pathlib import Path
import generate_figures


def test_generate_figures(tmp_path: Path):
    """Verify that generate_figure_1 produces non-empty PNG and PDF."""
    export_dir = generate_figures.ensure_export_dir()
    assert Path(export_dir).is_dir()
    generate_figures.generate_figure_1(str(tmp_path))
    png = tmp_path / "figure_1_refinement_tower_and_completion.png"
    pdf = tmp_path / "figure_1_refinement_tower_and_completion.pdf"
    assert png.is_file() and png.stat().st_size > 0
    assert pdf.is_file() and pdf.stat().st_size > 0


def test_main_figure_generation(monkeypatch, tmp_path: Path):
    """Verify main() entrypoint in generate_figures."""
    monkeypatch.setattr(generate_figures, "ensure_export_dir", lambda: str(tmp_path))
    generate_figures.main()
    assert (tmp_path / "figure_1_refinement_tower_and_completion.png").is_file()
