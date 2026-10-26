"""Make code/operations importable so `import swarm` resolves to code/operations/swarm."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
_OPS = str(ROOT / "code" / "operations")
if _OPS not in sys.path:
    sys.path.insert(0, _OPS)

import swarm  # noqa: E402,F401
