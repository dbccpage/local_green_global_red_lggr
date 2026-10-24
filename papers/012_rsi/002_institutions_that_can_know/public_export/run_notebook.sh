#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python tools/replay_notebook.py
