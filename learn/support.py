"""Shared loader for the learn/ course.

AuthorityEffect: None.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
LEARN = Path(__file__).resolve().parent
LESSON_DIR = LEARN / "lessons"
TRACE_DIR = LEARN / "traces"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lggr.common import json_value  # noqa: E402

LESSONS: tuple[tuple[str, str], ...] = (
    ("00", "00_name_the_question"),
    ("01", "01_same_summary_different_job"),
    ("02", "02_local_green_is_not_global"),
    ("03", "03_prefix_is_not_endpoint"),
    ("04", "04_the_review_cycle"),
    ("05", "05_moving_the_ledger"),
    ("06", "06_a_boundary_that_holds"),
    ("07", "07_recursion_on_a_fixed_report"),
    ("08", "08_three_ways_a_loop_stops"),
    ("09", "09_the_pass_comes_from_outside"),
)
STEM_BY_ID = {lesson_id: stem for lesson_id, stem in LESSONS}


def load_json(name: str) -> Any:
    path = TRACE_DIR / name
    return json.loads(path.read_text(encoding="utf-8"))


def load_repo_json(relative: str) -> Any:
    path = ROOT / relative
    return json.loads(path.read_text(encoding="utf-8"))


def finish(row: dict[str, Any]) -> dict[str, Any]:
    """Return a JSON-ready scorecard row. Fractions become exact strings."""
    body = json_value(row)
    if body.get("authority_effect") != "None":
        raise RuntimeError("A learn receipt must carry authority_effect 'None'")
    return body


def load_lesson(stem: str):
    path = LESSON_DIR / f"{stem}.py"
    spec = importlib.util.spec_from_file_location(f"learn_lesson_{stem}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load lesson {stem}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dumps(receipt: Any) -> str:
    return json.dumps(json_value(receipt), indent=2, sort_keys=True)
