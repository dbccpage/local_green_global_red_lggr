"""Headless notebook launcher for Paper I.

Runs the public reader-entry and reviewer-falsification pair (00, 06) by
default, or every source notebook with ``--all``. Imports the shipped
``epk_core`` module through ``jupyter_notebooks/epk_nb.py``.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

CODE_DIR = Path(__file__).resolve().parent
PAPER_ROOT = CODE_DIR.parent
NB_DIR = PAPER_ROOT / "jupyter_notebooks"

ENTER = "00_how_to_read_this_series.ipynb"
FALSIFY = "06_reviewer_reference_verification.ipynb"


def package_preflight() -> None:
    missing = []
    if not (CODE_DIR / "epk_core.py").is_file():
        missing.append("code/epk_core.py")
    if not (CODE_DIR / "tests").is_dir():
        missing.append("code/tests/")
    if (PAPER_ROOT / "tests").is_dir():
        raise SystemExit("Package preflight failed: tests must live in code/tests/")
    if not (PAPER_ROOT / "docs" / "lean_claim_map.md").is_file():
        missing.append("docs/lean_claim_map.md")
    if not (NB_DIR / "epk_nb.py").is_file():
        missing.append("jupyter_notebooks/epk_nb.py")
    if missing:
        raise SystemExit("Package preflight failed: missing " + ", ".join(missing))


def execute_notebook(path: Path) -> None:
    import nbformat
    from nbclient import NotebookClient

    os.environ["EPK_HEADLESS"] = "1"
    os.environ.setdefault("MPLBACKEND", "Agg")
    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(
        nb,
        timeout=300,
        kernel_name="python3",
        resources={"metadata": {"path": str(NB_DIR)}},
    )
    client.execute()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Paper 012 notebook launcher")
    parser.add_argument("--all", action="store_true", help="run the full teaching series")
    args = parser.parse_args(argv)
    package_preflight()
    names = (
        sorted(p.name for p in NB_DIR.glob("*.ipynb"))
        if args.all
        else [ENTER, FALSIFY]
    )
    if not names:
        print(f"ERROR: no notebooks found to execute in {NB_DIR}")
        return 1
    for name in names:
        path = NB_DIR / name
        if not path.is_file():
            print("ERROR: missing", path)
            return 1
        print("Executing", name)
        execute_notebook(path)
        print("PASS", name)
    print("Package preflight and notebook run passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
