"""Replay the prepared half of every lesson and every recipe demo, and print a scorecard.

AuthorityEffect: None. From the repository root: python learn/check.py
"""
from __future__ import annotations

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from learn.support import LESSONS, RECIPES, load_lesson, load_recipe  # noqa: E402


def main() -> int:
    failed = False
    for lesson_id, stem in LESSONS:
        module = load_lesson(stem)
        row = module.prepared()
        print(f"{lesson_id}  {row['schema']}  {row['status']}")
        if row["lesson_id"] != lesson_id or row["status"] != module.EXPECTED_STATUS:
            failed = True
        if row.get("authority_effect") != "None":
            failed = True
    for name in RECIPES:
        module = load_recipe(name)
        row = module.demo()
        print(f"{name}  {row['schema']}  {row['status']}")
        if row["recipe_id"] != name or row["status"] != module.EXPECTED_STATUS:
            failed = True
        if row.get("authority_effect") != "None":
            failed = True
    if failed:
        print("scorecard mismatch")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
