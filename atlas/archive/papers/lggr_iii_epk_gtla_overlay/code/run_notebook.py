"""Execute the seven public Paper III notebooks headlessly."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import tempfile
import warnings
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
PAPER_ROOT = CODE_DIR.parent
NB_DIR = PAPER_ROOT / "jupyter_notebooks"
NOTEBOOKS = (
    "00_start_here.ipynb",
    "01_two_passes_one_failure.ipynb",
    "02_why_zero_can_mislead.ipynb",
    "03_when_paths_compose.ipynb",
    "04_when_grouping_loses_information.ipynb",
    "05_one_record_six_roles.ipynb",
    "06_reviewer_verification.ipynb",
)


def notebook_paths(directory: Path | None = None) -> tuple[Path, ...]:
    """Return the exact public sequence, refusing missing or extra notebooks."""

    directory = NB_DIR if directory is None else directory
    found = {path.name for path in directory.glob("*.ipynb")}
    expected = set(NOTEBOOKS)
    if found != expected:
        missing = sorted(expected - found)
        extra = sorted(found - expected)
        raise FileNotFoundError(
            f"public notebook set mismatch; missing={missing!r}; extra={extra!r}"
        )
    return tuple(directory / name for name in NOTEBOOKS)


def configure_event_loop() -> None:
    """Use the selector policy required by Jupyter kernels on Windows."""

    # Python 3.14 deprecates the policy API, but pyzmq still requires the
    # selector loop on Windows.  Suppress only that compatibility deprecation;
    # Python 3.16 removes policies, by which point pyzmq uses the default loop.
    if sys.platform == "win32" and sys.version_info < (3, 16):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            policy_cls = getattr(asyncio, "WindowsSelectorEventLoopPolicy", None)
            if policy_cls is not None:
                asyncio.set_event_loop_policy(policy_cls())


def _restore_environment(name: str, previous: str | None) -> None:
    if previous is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = previous


def execute_notebook(path: Path) -> None:
    """Execute one notebook without modifying the archived notebook bytes."""

    import nbformat
    from nbclient import NotebookClient

    configure_event_loop()
    prior = {
        name: os.environ.get(name)
        for name in ("LGGR3_HEADLESS", "MPLBACKEND", "IPYTHONDIR", "PYTHONPATH")
    }
    os.environ["LGGR3_HEADLESS"] = "1"
    os.environ["MPLBACKEND"] = "Agg"
    code_path = str(CODE_DIR)
    old_pythonpath = os.environ.get("PYTHONPATH")
    os.environ["PYTHONPATH"] = (
        f"{code_path}{os.pathsep}{old_pythonpath}" if old_pythonpath else code_path
    )
    with tempfile.TemporaryDirectory(prefix="lggr3-ipython-") as profile:
        os.environ["IPYTHONDIR"] = profile
        try:
            notebook = nbformat.read(path, as_version=4)
            NotebookClient(
                notebook,
                timeout=300,
                kernel_name="python3",
                resources={"metadata": {"path": str(path.parent)}},
            ).execute()
        finally:
            for name, previous in prior.items():
                _restore_environment(name, previous)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    try:
        paths = notebook_paths()
    except FileNotFoundError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    for path in paths:
        print(f"Executing {path.name}")
        execute_notebook(path)
        print(f"PASS {path.name}")
    print(f"All {len(paths)} public notebooks executed successfully")
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised as the public command
    raise SystemExit(main())
