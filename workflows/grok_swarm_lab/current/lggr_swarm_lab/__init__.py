"""A local SQLite experiment, with an explicitly pinned LGGR dependency."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "vendor"
sys.path.insert(0, str(VENDOR))
__version__ = "0.1.0"
