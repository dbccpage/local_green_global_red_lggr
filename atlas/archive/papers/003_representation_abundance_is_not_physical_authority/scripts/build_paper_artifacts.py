#!/usr/bin/env python3
"""Compatibility entry point: all publication builds now pass through the math spine."""
from pathlib import Path
import argparse
from paper_spine import build

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tex-only", action="store_true", help="Deprecated: a complete checked build is always performed")
    parser.parse_args()
    build(Path(__file__).resolve().parents[1])
