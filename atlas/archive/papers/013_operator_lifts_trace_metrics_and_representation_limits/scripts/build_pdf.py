#!/usr/bin/env python3
"""Build only after the canonical math spine and every source occurrence agree."""
from pathlib import Path
from paper_spine import build

if __name__ == "__main__":
    build(Path(__file__).resolve().parents[1])
