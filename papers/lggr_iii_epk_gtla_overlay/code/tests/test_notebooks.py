"""Contract and execution checks for the seven public notebooks and launcher."""

from __future__ import annotations

import asyncio
import base64
import json
import os
import sys
import tempfile
import warnings
from pathlib import Path
from types import SimpleNamespace

import nbformat
import pytest
from nbclient import NotebookClient

CODE_DIR = Path(__file__).resolve().parents[1]
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

import run_notebook

PAPER_ROOT = Path(__file__).resolve().parents[2]
NB_DIR = PAPER_ROOT / "jupyter_notebooks"
PUBLIC = (
    "00_start_here.ipynb",
    "01_two_passes_one_failure.ipynb",
    "02_why_zero_can_mislead.ipynb",
    "03_when_paths_compose.ipynb",
    "04_when_grouping_loses_information.ipynb",
    "05_one_record_six_roles.ipynb",
    "06_reviewer_verification.ipynb",
)


def _source(path: Path) -> str:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    return "\n".join(
        "".join(cell.get("source", ""))
        if isinstance(cell.get("source", ""), list)
        else str(cell.get("source", ""))
        for cell in notebook["cells"]
    )


def test_notebook_directory_contains_exact_public_sequence() -> None:
    assert tuple(path.name for path in sorted(NB_DIR.glob("*.ipynb"))) == PUBLIC
    assert tuple(path.name for path in run_notebook.notebook_paths()) == PUBLIC


@pytest.mark.parametrize("name", PUBLIC)
def test_each_notebook_is_valid_and_follows_hygiene(name: str) -> None:
    path = NB_DIR / name
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    source = _source(path)
    lowered = source.lower()

    if name != "00_start_here.ipynb":
        assert "exercise" in lowered

    assert "2026-10-15" in source and "1.5.2" in source

    # Standalone vs package-verification import boundaries
    if name in (
        "00_start_here.ipynb",
        "01_two_passes_one_failure.ipynb",
        "02_why_zero_can_mislead.ipynb",
    ):
        assert "epk_gtla_overlay_core" not in source

    for forbidden in (
        r"c:\\users",
        "c:/users/",
        "target/codex-worktrees",
        "coda_atlas/",
        "sys.path",
        "overlay_nb",
    ):
        assert forbidden not in lowered


@pytest.mark.parametrize("name", PUBLIC)
def test_each_notebook_executes_headlessly_and_restores_environment(
    name: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LGGR3_HEADLESS", "prior-headless")
    monkeypatch.setenv("MPLBACKEND", "prior-backend")
    monkeypatch.setenv("IPYTHONDIR", "prior-ipython")
    run_notebook.execute_notebook(NB_DIR / name)
    assert os.environ["LGGR3_HEADLESS"] == "prior-headless"
    assert os.environ["MPLBACKEND"] == "prior-backend"
    assert os.environ["IPYTHONDIR"] == "prior-ipython"


def test_execute_notebook_restores_absent_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in ("LGGR3_HEADLESS", "MPLBACKEND", "IPYTHONDIR"):
        monkeypatch.delenv(name, raising=False)
    run_notebook.execute_notebook(NB_DIR / PUBLIC[0])
    for name in ("LGGR3_HEADLESS", "MPLBACKEND", "IPYTHONDIR"):
        assert name not in os.environ


def test_visual_notebooks_emit_embedded_png_output() -> None:
    """Validate that display_figure embeds real PNG bytes under the Agg backend."""
    test_target = NB_DIR / "01_two_passes_one_failure.ipynb"
    notebook = nbformat.read(test_target, as_version=4)
    run_notebook.configure_event_loop()

    prior_headless = os.environ.get("LGGR3_HEADLESS")
    prior_backend = os.environ.get("MPLBACKEND")
    os.environ["LGGR3_HEADLESS"] = "1"
    os.environ["MPLBACKEND"] = "Agg"

    try:
        with tempfile.TemporaryDirectory(prefix="lggr3-test-nb-") as profile:
            os.environ["IPYTHONDIR"] = profile
            client = NotebookClient(
                notebook,
                timeout=120,
                kernel_name="python3",
                resources={"metadata": {"path": str(NB_DIR)}},
            )
            client.execute()

        png_found = False
        for cell in notebook.cells:
            for out in cell.get("outputs", []):
                data = out.get("data", {})
                if "image/png" in data:
                    raw = base64.b64decode(data["image/png"])
                    assert raw.startswith(b"\x89PNG\r\n\x1a\n")
                    png_found = True
        assert png_found, "01_two_passes_one_failure did not emit embedded PNG data"
    finally:
        if prior_headless is None:
            os.environ.pop("LGGR3_HEADLESS", None)
        else:
            os.environ["LGGR3_HEADLESS"] = prior_headless
        if prior_backend is None:
            os.environ.pop("MPLBACKEND", None)
        else:
            os.environ["MPLBACKEND"] = prior_backend


def test_notebook_set_mismatch_reports_missing_and_extra(tmp_path: Path) -> None:
    (tmp_path / "00_start_here.ipynb").write_text("{}", encoding="utf-8")
    (tmp_path / "extra.ipynb").write_text("{}", encoding="utf-8")
    with pytest.raises(
        FileNotFoundError, match="missing=.*01_two_passes_one_failure.*extra=.*extra"
    ):
        run_notebook.notebook_paths(tmp_path)


def test_event_loop_configuration_has_platform_guard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[object] = []
    sentinel = object()
    fake_asyncio = SimpleNamespace(
        set_event_loop_policy=calls.append,
        WindowsSelectorEventLoopPolicy=lambda: sentinel,
    )
    monkeypatch.setattr(run_notebook, "asyncio", fake_asyncio)
    monkeypatch.setattr(run_notebook.sys, "version_info", (3, 15))
    monkeypatch.setattr(run_notebook.sys, "platform", "not-windows")
    run_notebook.configure_event_loop()
    assert calls == []

    monkeypatch.setattr(run_notebook.sys, "platform", "win32")
    run_notebook.configure_event_loop()
    assert calls == [sentinel]

    monkeypatch.setattr(run_notebook.sys, "version_info", (3, 16))
    run_notebook.configure_event_loop()
    assert calls == [sentinel]


def test_main_executes_exact_sequence(monkeypatch: pytest.MonkeyPatch) -> None:
    paths = tuple(NB_DIR / name for name in PUBLIC)
    seen = []
    monkeypatch.setattr(run_notebook, "notebook_paths", lambda: paths)
    monkeypatch.setattr(
        run_notebook, "execute_notebook", lambda path: seen.append(path.name)
    )
    assert run_notebook.main([]) == 0
    assert seen == list(PUBLIC)


def test_main_reports_notebook_set_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail():
        raise FileNotFoundError("broken sequence")

    monkeypatch.setattr(run_notebook, "notebook_paths", fail)
    assert run_notebook.main([]) == 2


def test_single_documented_launcher_is_python() -> None:
    surfaces = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (PAPER_ROOT / "README.md", PAPER_ROOT / "docs" / "quick_start.md")
    )
    assert "python code/run_notebook.py" in surfaces
    assert "run_notebook.sh" not in surfaces
    assert "run_notebook.ps1" not in surfaces
    assert "run_notebook.bat" not in surfaces
    assert not tuple((PAPER_ROOT / "public_export").glob("run_notebook.*"))


def test_python_version_supported_by_notebook_metadata() -> None:
    for name in PUBLIC:
        notebook = json.loads((NB_DIR / name).read_text(encoding="utf-8"))
        assert notebook["metadata"]["kernelspec"]["name"] == "python3"
        assert (
            int(notebook["metadata"]["language_info"]["version"].split(".")[0])
            <= sys.version_info.major
        )


def test_configure_event_loop_non_win32(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "platform", "linux")
    run_notebook.configure_event_loop()


def test_configure_event_loop_when_policy_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "platform", "win32")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        monkeypatch.setattr(
            asyncio, "WindowsSelectorEventLoopPolicy", None, raising=False
        )
        run_notebook.configure_event_loop()

