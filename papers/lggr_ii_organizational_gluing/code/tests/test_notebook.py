"""Execute the public notebook in a fresh kernel."""

import asyncio
import sys
from pathlib import Path

import nbformat
import pytest
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / "jupyter_notebooks" / "lggr_ii_organizational_gluing.ipynb"


def test_notebook_executes_headlessly(monkeypatch):
    if sys.platform == "win32" and hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    monkeypatch.setenv("MPLBACKEND", "Agg")
    with NOTEBOOK.open(encoding="utf-8") as stream:
        notebook = nbformat.read(stream, as_version=4)
    nbformat.validate(notebook)

    source_code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    assert source_code_cells
    assert all(cell.execution_count is not None for cell in source_code_cells)
    assert all(cell.outputs for cell in source_code_cells)

    executed = NotebookClient(
        notebook,
        timeout=300,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
    ).execute()
    executed_code_cells = [cell for cell in executed.cells if cell.cell_type == "code"]
    assert executed_code_cells
    assert all(cell.execution_count is not None for cell in executed_code_cells)


@pytest.mark.parametrize("failure", [RuntimeError("kernel failed"), AssertionError("cell failed")])
def test_notebook_execution_failure_propagates(monkeypatch, failure):
    def fail_execution(self):
        raise failure

    monkeypatch.setattr(NotebookClient, "execute", fail_execution)
    with pytest.raises(type(failure), match=str(failure)):
        test_notebook_executes_headlessly(monkeypatch)

