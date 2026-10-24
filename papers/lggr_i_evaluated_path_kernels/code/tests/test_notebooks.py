"""Notebook discipline and headless execution for Paper 012 teaching series."""

from __future__ import annotations

import importlib.util
import io
import json
import os
import re
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.xdist_group(name="notebook_kernel")

PAPER_ROOT = Path(__file__).resolve().parents[2]
NB_DIR = PAPER_ROOT / "jupyter_notebooks"
PUBLIC_NOTEBOOKS = {
    "00_how_to_read_this_series.ipynb",
    "06_reviewer_reference_verification.ipynb",
}
SUPPLEMENTAL_NOTEBOOKS = {
    "01_the_five_trace_phone_test.ipynb",
    "02_the_evaluator_defect_trichotomy.ipynb",
    "03_boundary_slices_and_composition.ipynb",
    "04_why_green_evaluators_can_lie.ipynb",
    "05_cancellation_and_poe_vs_moe.ipynb",
    "07_llm_and_agentic_pipelines.ipynb",
}


def _notebooks() -> list[Path]:
    return sorted(NB_DIR.glob("*.ipynb"))


def _source(nb: dict) -> str:
    parts: list[str] = []
    for cell in nb.get("cells", []):
        src = cell.get("source", "")
        if isinstance(src, list):
            parts.append("".join(src))
        else:
            parts.append(str(src))
    return "\n".join(parts)


def test_public_notebooks_are_terse_clean_reader_lessons() -> None:
    forbidden = (
        "authorityeffect",
        "proof ledger",
        "red team",
        "green team",
        "quantum",
        "fully discharged",
        "minimal",
        "l020",
        "python 3.14",
    )
    for name in sorted(PUBLIC_NOTEBOOKS):
        nb = json.loads((NB_DIR / name).read_text(encoding="utf-8"))
        text = _source(nb)
        assert len(nb["cells"]) <= 9
        assert "../public_export/" in text
        assert "ipywidgets" in text and "HAS_WIDGETS" in text
        assert not re.search(r"\bRULE(?:[-_A-Z0-9]+)?\b", text)
        for phrase in forbidden:
            assert phrase not in text.casefold(), (name, phrase)
        assert "widgets" not in nb.get("metadata", {})
        assert nb["metadata"]["kernelspec"]["display_name"] == "Python 3"
        for cell in nb["cells"]:
            if cell["cell_type"] == "code":
                assert cell.get("execution_count") is None
                assert cell.get("outputs") == []


def test_public_notebook_claims_match_current_handles() -> None:
    enter = _source(json.loads((NB_DIR / "00_how_to_read_this_series.ipynb").read_text(encoding="utf-8")))
    falsify = _source(json.loads((NB_DIR / "06_reviewer_reference_verification.ipynb").read_text(encoding="utf-8")))
    assert r"\bigsqcup_{b\in\mathsf B}" in enter
    assert "+R_E(c,a)" in enter
    assert "C1c_g1_set_isomorphism" in enter
    assert "Missing Cartesian product trajectory" in falsify
    assert "four_term_contribution" in falsify
    assert "D3_fully_corrected_kernel_identity" in falsify
    assert "positive-denominator error" in falsify


def test_readme_and_quick_start_match_release_surface() -> None:
    readme = (PAPER_ROOT / "README.md").read_text(encoding="utf-8")
    quick = (PAPER_ROOT / "docs" / "quick_start.md").read_text(encoding="utf-8")
    for text in (readme, quick):
        assert "1.2.4" in text
        assert "2026-10-15" in text
        assert "pytest -n 8" in text
        assert "7-part" not in text
        assert "64 tests" not in text
        assert "99% combined" not in text
        assert "99% branch-aware coverage" not in text
    assert "00_how_to_read_this_series.ipynb" in readme
    assert "06_reviewer_reference_verification.ipynb" in readme
    assert "statement and branch coverage separately" in readme
    assert "each production module" in readme


def test_notebook_02_names_lake_lean_homes() -> None:
    path = NB_DIR / "02_the_evaluator_defect_trichotomy.ipynb"
    if not path.is_file():
        # The public archive intentionally omits supplemental lessons.  Its
        # tests must still pass and verify that the omission is the declared
        # two-notebook release surface, not a partial accidental deletion.
        assert {p.name for p in _notebooks()} == PUBLIC_NOTEBOOKS
        plan = (NB_DIR / "NOTEBOOK_PLAN.md").read_text(encoding="utf-8")
        assert path.name in plan and "supplemental" in plan.lower()
        return
    text = _source(json.loads(path.read_text(encoding="utf-8")))
    assert "same_lpr_gpr_and_delta_sum_different_egd" in text
    assert "local_dashboard_zero_identifies_all_green_and_lggr" in text
    assert "L020_13" not in text
    assert "L020_08" not in text
    assert "rate_matched_sample_counts_distinct_defect" not in text
    assert "local_dashboard_non_factorization" not in text


def test_lean_claim_map_c1_c1b_d4_files() -> None:
    text = (PAPER_ROOT / "docs" / "lean_claim_map.md").read_text(encoding="utf-8")
    assert "| C1 | C1_kernel_composition_under_G1_G2_G3; C1b; C1c; C1d" in text
    assert "03b_product_of_sums.lean and 03c_g1_set_isomorphism.lean" in text
    assert "| D4 | D4_cancellation_not_pointwise_zero" in text
    lean = PAPER_ROOT / "lean4"
    assert "theorem kernel_composition_under_G1_G2_G3" in (lean / "03b_product_of_sums.lean").read_text(encoding="utf-8")
    assert "theorem kernel_pair_sum_reindexing_under_G1_G2_G3" in (lean / "03_kernel_composition.lean").read_text(encoding="utf-8")
    assert "theorem cancellation_net_zero" in (lean / "02_delta_partition.lean").read_text(encoding="utf-8")


def test_teaching_notebooks_exist() -> None:
    names = frozenset(p.name for p in _notebooks())
    assert PUBLIC_NOTEBOOKS <= names
    assert names in {
        frozenset(PUBLIC_NOTEBOOKS),
        frozenset(PUBLIC_NOTEBOOKS | SUPPLEMENTAL_NOTEBOOKS),
    }


def test_supplemental_notebook_claim_legends_and_exercises() -> None:
    paths = [
        NB_DIR / name
        for name in sorted(SUPPLEMENTAL_NOTEBOOKS)
        if (NB_DIR / name).is_file()
    ]
    if not paths:
        assert {path.name for path in _notebooks()} == PUBLIC_NOTEBOOKS
        return
    for path in paths:
        nb = json.loads(path.read_text(encoding="utf-8"))
        text = _source(nb)
        lower = text.lower()
        assert "pinned" in lower and "proved" in lower and "declared" in lower and "open" in lower
        assert "cannot" in lower
        assert "anchors" in lower
        assert "exercise" in lower


@pytest.mark.parametrize("path", _notebooks(), ids=lambda p: p.name)
def test_notebook_has_no_machine_local_import_path(path: Path) -> None:
    nb = json.loads(path.read_text(encoding="utf-8"))
    text = _source(nb)
    forbidden = (
        r"C:\Users",
        r"C:/Users",
        "c:/users/a343o",
        "c:\\users\\a343o",
    )
    low = text.lower()
    for needle in forbidden:
        assert needle.lower() not in low, f"{path.name} contains machine-local path {needle}"


def test_package_preflight_and_launchers_exist() -> None:
    from run_notebook import ENTER, FALSIFY, package_preflight

    package_preflight()
    assert (PAPER_ROOT / "public_export" / "run_notebook.sh").is_file()
    assert (PAPER_ROOT / "public_export" / "run_notebook.bat").is_file()
    assert (PAPER_ROOT / "public_export" / "run_notebook.ps1").is_file()
    assert (PAPER_ROOT / "code" / "run_notebook.py").is_file()
    assert (NB_DIR / ENTER).is_file()
    assert (NB_DIR / FALSIFY).is_file()
    assert not (PAPER_ROOT / "tests").is_dir()


def _load_launcher(name: str):
    path = PAPER_ROOT / "code" / "run_notebook.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_launcher_import_handles_non_reconfigurable_stdout(monkeypatch) -> None:
    stream = io.StringIO()
    assert not hasattr(stream, "reconfigure")
    monkeypatch.setattr(sys, "stdout", stream)
    module = _load_launcher("run_notebook_no_reconfigure")
    assert module.ENTER == "00_how_to_read_this_series.ipynb"


def test_launcher_import_handles_failed_stdout_reconfigure(monkeypatch) -> None:
    class RefusingStdout(io.StringIO):
        def reconfigure(self, **_kwargs):
            raise OSError("encoding is fixed by the host")

    monkeypatch.setattr(sys, "stdout", RefusingStdout())
    module = _load_launcher("run_notebook_refusing_reconfigure")
    assert module.FALSIFY == "06_reviewer_reference_verification.ipynb"


def _preflight_fixture(tmp_path: Path, monkeypatch):
    import run_notebook

    code_dir = tmp_path / "code"
    docs_dir = tmp_path / "docs"
    notebook_dir = tmp_path / "jupyter_notebooks"
    (code_dir / "tests").mkdir(parents=True)
    docs_dir.mkdir()
    notebook_dir.mkdir()
    (code_dir / "epk_core.py").write_text("# fixture\n", encoding="utf-8")
    (docs_dir / "lean_claim_map.md").write_text("# fixture\n", encoding="utf-8")
    (notebook_dir / "epk_nb.py").write_text("# fixture\n", encoding="utf-8")
    monkeypatch.setattr(run_notebook, "CODE_DIR", code_dir)
    monkeypatch.setattr(run_notebook, "PAPER_ROOT", tmp_path)
    monkeypatch.setattr(run_notebook, "NB_DIR", notebook_dir)
    return run_notebook, code_dir, docs_dir, notebook_dir


@pytest.mark.parametrize(
    ("relative", "message"),
    [
        ("code/epk_core.py", "code/epk_core.py"),
        ("code/tests", "code/tests/"),
        ("docs/lean_claim_map.md", "docs/lean_claim_map.md"),
        ("jupyter_notebooks/epk_nb.py", "jupyter_notebooks/epk_nb.py"),
    ],
)
def test_package_preflight_identifies_each_missing_surface(
    tmp_path, monkeypatch, relative, message
) -> None:
    run_notebook, _code, _docs, _notebooks = _preflight_fixture(
        tmp_path, monkeypatch
    )
    missing = tmp_path / relative
    if missing.is_dir():
        missing.rmdir()
    else:
        missing.unlink()
    with pytest.raises(SystemExit, match=re.escape(message)):
        run_notebook.package_preflight()


def test_package_preflight_rejects_legacy_root_tests(tmp_path, monkeypatch) -> None:
    run_notebook, _code, _docs, _notebooks = _preflight_fixture(
        tmp_path, monkeypatch
    )
    (tmp_path / "tests").mkdir()
    with pytest.raises(SystemExit, match="tests must live in code/tests"):
        run_notebook.package_preflight()


def test_launcher_all_mode_runs_every_source_notebook(
    tmp_path, monkeypatch
) -> None:
    import run_notebook

    notebook_dir = tmp_path / "jupyter_notebooks"
    notebook_dir.mkdir()
    for name in ("b.ipynb", "a.ipynb"):
        (notebook_dir / name).write_text("{}\n", encoding="utf-8")
    seen: list[str] = []
    monkeypatch.setattr(run_notebook, "NB_DIR", notebook_dir)
    monkeypatch.setattr(run_notebook, "package_preflight", lambda: None)
    monkeypatch.setattr(
        run_notebook, "execute_notebook", lambda path: seen.append(path.name)
    )
    assert run_notebook.main(["--all"]) == 0
    assert seen == ["a.ipynb", "b.ipynb"]


def test_launcher_all_mode_fails_closed_on_empty_directory(
    tmp_path, monkeypatch, capsys
) -> None:
    import run_notebook

    notebook_dir = tmp_path / "jupyter_notebooks"
    notebook_dir.mkdir()
    monkeypatch.setattr(run_notebook, "NB_DIR", notebook_dir)
    monkeypatch.setattr(run_notebook, "package_preflight", lambda: None)
    assert run_notebook.main(["--all"]) == 1
    assert "ERROR: no notebooks found to execute" in capsys.readouterr().out


def test_import_epk_verifies_resolved_origin(tmp_path) -> None:
    sys.path.insert(0, str(NB_DIR))
    import epk_nb

    # Authentic import works
    epk = epk_nb.import_epk()
    assert epk is not None

    # Tampered origin in sys.modules raises ImportError. The key stays a literal
    # so the contract import-boundary gate can read it; restore the real module.
    fake_module = type(sys)("epk_core")
    fake_module.__file__ = str(tmp_path / "fake_epk_core.py")
    authentic = sys.modules["epk_core"]
    sys.modules["epk_core"] = fake_module
    try:
        with pytest.raises(ImportError, match="origin mismatch"):
            epk_nb.import_epk()
    finally:
        sys.modules["epk_core"] = authentic


def test_launcher_fails_closed_when_public_notebook_is_missing(
    tmp_path, monkeypatch, capsys
) -> None:
    import run_notebook

    notebook_dir = tmp_path / "jupyter_notebooks"
    notebook_dir.mkdir()
    monkeypatch.setattr(run_notebook, "NB_DIR", notebook_dir)
    monkeypatch.setattr(run_notebook, "package_preflight", lambda: None)
    monkeypatch.setattr(
        run_notebook,
        "execute_notebook",
        lambda _path: pytest.fail("a missing notebook must not execute"),
    )
    assert run_notebook.main([]) == 1
    assert "ERROR: missing" in capsys.readouterr().out


@pytest.mark.xdist_group(name="notebook_kernel")
def test_run_notebook_main_enter_falsify() -> None:
    from run_notebook import main

    os.environ["EPK_HEADLESS"] = "1"
    os.environ.setdefault("MPLBACKEND", "Agg")
    assert main([]) == 0


@pytest.mark.parametrize("path", _notebooks(), ids=lambda p: p.name)
@pytest.mark.xdist_group(name="notebook_kernel")
def test_notebook_executes_headless(path: Path) -> None:
    nbformat = pytest.importorskip("nbformat")
    nbclient = pytest.importorskip("nbclient")
    os.environ["EPK_HEADLESS"] = "1"
    os.environ.setdefault("MPLBACKEND", "Agg")
    nb = nbformat.read(path, as_version=4)
    client = nbclient.NotebookClient(
        nb,
        timeout=300,
        kernel_name="python3",
        resources={"metadata": {"path": str(NB_DIR)}},
    )
    client.execute()
