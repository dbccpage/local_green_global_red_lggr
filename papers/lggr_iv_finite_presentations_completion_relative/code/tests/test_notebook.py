"""Execute the LGGR IV public notebook headlessly in a fresh kernel."""

from __future__ import annotations

import asyncio
from pathlib import Path
import sys

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / "jupyter_notebooks" / "001_finite_presentations.ipynb"


def test_notebook_executes_headlessly(monkeypatch):
    monkeypatch.setenv("MPLBACKEND", "Agg")
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    with NOTEBOOK.open(encoding="utf-8") as stream:
        notebook = nbformat.read(stream, as_version=4)
    nbformat.validate(notebook)

    source_code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]
    assert all(not cell.outputs for cell in source_code_cells)
    assert all(cell.execution_count is None for cell in source_code_cells)

    executed = NotebookClient(
        notebook,
        timeout=120,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
    ).execute()

    executed_code_cells = [cell for cell in executed.cells if cell.cell_type == "code"]
    assert executed_code_cells
    assert all(cell.execution_count is not None for cell in executed_code_cells)
