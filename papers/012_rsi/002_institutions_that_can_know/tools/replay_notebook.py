#!/usr/bin/env python3
"""Execute the notebook in memory; never rewrite the deposited source."""
from pathlib import Path
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "jupyter_notebooks/000_institutions_that_can_know_walkthrough.ipynb"
original = path.read_bytes()
notebook = nbformat.reads(original.decode("utf-8"), as_version=4)
NotebookClient(notebook, timeout=120, kernel_name="python3",
               resources={"metadata": {"path": str(ROOT)}}).execute()
if path.read_bytes() != original:
    raise ValueError("Deposited notebook changed during replay")
print("PASS: all four notebook code cells executed; deposited notebook unchanged")
