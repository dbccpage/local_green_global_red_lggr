"""Portable bootstrap for Paper 012 teaching notebooks.

Locates shipped ``code/epk_core.py`` by walking parents from CWD. Never uses a
machine-local hardcoded path.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any


def locate_code_dir() -> Path:
    start = Path.cwd().resolve()
    for base in (start, *start.parents):
        cand = (base / "code" / "epk_core.py").resolve()
        if cand.is_file() and (cand.parent.parent / "lggr_i_evaluated_path_kernels.md").is_file():
            return cand.parent
    raise FileNotFoundError(
        "Could not locate code/epk_core.py next to lggr_i_evaluated_path_kernels.md"
    )


def import_epk() -> Any:
    code_dir = locate_code_dir()
    expected_file = (code_dir / "epk_core.py").resolve()
    code_s = str(code_dir)
    if code_s not in sys.path:
        sys.path.insert(0, code_s)
    import epk_core as epk

    resolved_origin = Path(getattr(epk, "__file__", "")).resolve()
    if resolved_origin != expected_file:
        raise ImportError(
            f"Loaded epk_core origin mismatch: expected {expected_file}, "
            f"but module in sys.modules was loaded from {resolved_origin}"
        )

    return epk


def widgets_available() -> bool:
    import os

    if os.environ.get("EPK_HEADLESS", "").strip() in {"1", "true", "yes"}:
        return False
    try:
        import ipywidgets  # noqa: F401

        return True
    except Exception:
        return False
