"""Regression gates for the public build and release metadata contract."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import verify_deposit


ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = ROOT / "scripts" / "build_paper_artifacts.py"


def load_build_module():
    spec = importlib.util.spec_from_file_location("lggr2_build", BUILD_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "relative",
    (
        "../outside.txt",
        "/absolute.txt",
        "C:/absolute.txt",
        "folder\\alias.txt",
        "./normalized.txt",
        "folder//normalized.txt",
        ".",
    ),
)
def test_manifest_paths_fail_closed(relative: str, tmp_path: Path) -> None:
    digest = "0" * 64
    manifest = tmp_path / "SHA256SUMS"
    manifest.write_text(f"{digest}  {relative}\n", encoding="utf-8")
    archive = load_module(
        ROOT / "scripts" / "build_deposit_zip.py",
        "lggr2_archive_paths",
    )
    with pytest.raises(SystemExit):
        verify_deposit.parse_manifest(manifest, tmp_path)
    with pytest.raises(ValueError, match="unsafe path"):
        archive.parse_manifest(manifest, tmp_path)


def test_manifest_paths_reject_casefold_duplicates(tmp_path: Path) -> None:
    digest = "0" * 64
    manifest = tmp_path / "SHA256SUMS"
    manifest.write_text(
        f"{digest}  docs/item.txt\n{digest}  DOCS/ITEM.TXT\n",
        encoding="utf-8",
    )
    archive = load_module(
        ROOT / "scripts" / "build_deposit_zip.py",
        "lggr2_archive_duplicates",
    )
    with pytest.raises(SystemExit):
        verify_deposit.parse_manifest(manifest, tmp_path)
    with pytest.raises(ValueError, match="more than once"):
        archive.parse_manifest(manifest, tmp_path)


def test_manifest_paths_reject_symlink_ancestors(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    target = real / "x.txt"
    target.write_text("content", encoding="utf-8")
    alias = tmp_path / "alias"
    try:
        alias.symlink_to(real, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Symlink creation not permitted in this environment")

    digest = "0" * 64
    manifest = tmp_path / "SHA256SUMS"
    manifest.write_text(f"{digest}  alias/x.txt\n", encoding="utf-8")
    archive = load_module(
        ROOT / "scripts" / "build_deposit_zip.py",
        "lggr2_archive_symlink_ancestors",
    )
    with pytest.raises(SystemExit):
        verify_deposit.parse_manifest(manifest, tmp_path)
    with pytest.raises(ValueError, match="unsafe path"):
        archive.parse_manifest(manifest, tmp_path)


def test_shared_preamble_and_pdflatex_contract():
    build = load_build_module()
    preamble = ROOT / "scripts" / "obstruction-preamble.tex"
    assert build.sha256_of(preamble) == build.CANONICAL_PREAMBLE_SHA256
    assert build.PDFLATEX_RUNS == 2
    pandoc = build.pandoc_command("pandoc", preamble)
    assert any(arg.startswith("--include-in-header=") for arg in pandoc)
    assert "--number-sections" not in pandoc
    latex = build.pdflatex_command("pdflatex", ROOT)
    assert latex[0] == "pdflatex"
    assert all("xelatex" not in arg.lower() and "lualatex" not in arg.lower() for arg in latex)


def test_current_build_contract_is_complete():
    assert verify_deposit.check_build_contract() == []
    assert (ROOT / "lean4" / "axiom_report.txt").is_file()


def test_zenodo_description_is_the_primary_block(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "descriptions.md").write_bytes(
        (ROOT / "docs" / "descriptions.md").read_bytes()
    )
    metadata = json.loads((ROOT / "zenodo_metadata.json").read_text(encoding="utf-8"))
    (tmp_path / "zenodo_metadata.json").write_text(
        json.dumps(metadata), encoding="utf-8"
    )
    assert verify_deposit.check_descriptions(tmp_path) == []
    metadata["description"] = "An independently written blurb."
    (tmp_path / "zenodo_metadata.json").write_text(
        json.dumps(metadata), encoding="utf-8"
    )
    assert verify_deposit.check_descriptions(tmp_path) == [
        "zenodo_metadata.json description does not equal the Primary description"
    ]


def test_sub_95_branch_coverage_fails_even_with_high_line_coverage():
    totals = {
        "num_statements": 100,
        "covered_lines": 99,
        "num_branches": 100,
        "covered_branches": 94,
    }
    assert verify_deposit.coverage_gate_problems(totals) == [
        "branch coverage 94.00% is below 95.00%"
    ]


def test_empty_coverage_totals_fail_as_zero_rate():
    totals = {
        "num_statements": 0,
        "covered_lines": 0,
        "num_branches": 0,
        "covered_branches": 0,
    }
    line_rate, branch_rate = verify_deposit.coverage_rates(totals)
    assert line_rate == 0.0
    assert branch_rate == 0.0
    problems = verify_deposit.coverage_gate_problems(totals)
    assert "coverage report contains zero statements" in problems
    assert "coverage report contains zero branches" in problems
    assert "line coverage 0.00% is below 95.00%" in problems
    assert "branch coverage 0.00% is below 95.00%" in problems


def test_manifest_paths_reject_directory_case_collisions(tmp_path: Path) -> None:
    digest = "0" * 64
    manifest = tmp_path / "SHA256SUMS"
    manifest.write_text(
        f"{digest}  docs/item.txt\n{digest}  DOCS/other.txt\n",
        encoding="utf-8",
    )
    archive = load_module(
        ROOT / "scripts" / "build_deposit_zip.py",
        "lggr2_archive_dir_collisions",
    )
    with pytest.raises(SystemExit):
        verify_deposit.parse_manifest(manifest, tmp_path)
    with pytest.raises(ValueError, match="directory component case collision"):
        archive.parse_manifest(manifest, tmp_path)


def test_manifest_paths_reject_file_dir_clashes(tmp_path: Path) -> None:
    digest = "0" * 64
    manifest = tmp_path / "SHA256SUMS"
    manifest.write_text(
        f"{digest}  item\n{digest}  item/child.txt\n",
        encoding="utf-8",
    )
    archive = load_module(
        ROOT / "scripts" / "build_deposit_zip.py",
        "lggr2_archive_file_dir_clash",
    )
    with pytest.raises(SystemExit):
        verify_deposit.parse_manifest(manifest, tmp_path)
    with pytest.raises(ValueError, match="collides with"):
        archive.parse_manifest(manifest, tmp_path)


def test_parse_axiom_reports_rejects_duplicate_declarations():
    census = (
        "'PaperAE005.orgDelta_range' does not depend on any axioms\n"
        "'PaperAE005.orgDelta_range' does not depend on any axioms\n"
    )
    reports, problems = verify_deposit._parse_axiom_reports(census)
    assert any("duplicate axiom report" in p for p in problems)


def test_axiom_report_has_no_platform_target_triples():
    report_text = (ROOT / "lean4" / "axiom_report.txt").read_text(encoding="utf-8")
    for triple in ("w64-windows-gnu", "unknown-linux-gnu", "apple-darwin"):
        assert triple not in report_text


def test_check_release_archive_passes_on_current_estate():
    entries = verify_deposit.parse_manifest()
    assert verify_deposit.check_release_archive(entries) == []


def test_check_release_archive_detects_upload_pdf_drift(tmp_path: Path):
    entries = {"lggr_ii_organizational_gluing.pdf": "0" * 64}
    canonical_pdf = tmp_path / f"{tmp_path.name}.pdf"
    upload_pdf = tmp_path / f"0_{tmp_path.name}.pdf"
    canonical_pdf.write_bytes(b"canonical")
    upload_pdf.write_bytes(b"different")
    archive_path = tmp_path / f"{tmp_path.name}_2026-10-15.zip"
    import zipfile
    with zipfile.ZipFile(archive_path, "w") as zf:
        zf.writestr(f"{tmp_path.name}/lggr_ii_organizational_gluing.pdf", b"canonical")
        zf.writestr(f"{tmp_path.name}/SHA256SUMS", b"sums")
    problems = verify_deposit.check_release_archive(entries, root_dir=tmp_path)
    assert any("differs from canonical PDF" in p for p in problems)


def test_check_release_archive_detects_obsolete_archive(tmp_path: Path):
    entries = {"lggr_ii_organizational_gluing.pdf": "0" * 64}
    canonical_pdf = tmp_path / f"{tmp_path.name}.pdf"
    canonical_pdf.write_bytes(b"canonical")
    obsolete_zip = tmp_path / f"1_{tmp_path.name}_2026-10-15.zip"
    obsolete_zip.write_bytes(b"fake")
    archive_path = tmp_path / f"{tmp_path.name}_2026-10-15.zip"
    import zipfile
    with zipfile.ZipFile(archive_path, "w") as zf:
        zf.writestr(f"{tmp_path.name}/lggr_ii_organizational_gluing.pdf", b"canonical")
        zf.writestr(f"{tmp_path.name}/SHA256SUMS", b"sums")
    problems = verify_deposit.check_release_archive(entries, root_dir=tmp_path)
    assert any("obsolete archive" in p for p in problems)


