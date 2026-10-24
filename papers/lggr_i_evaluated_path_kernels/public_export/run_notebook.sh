#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export EPK_HEADLESS=1
export MPLBACKEND=Agg
python code/run_notebook.py "$@"
