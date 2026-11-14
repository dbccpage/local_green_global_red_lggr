# Quick start

From the paper directory, use Python 3.11 or newer with
[uv](https://docs.astral.sh/uv/):

```text
uv run --isolated --frozen --extra dev python -m pytest -n 8 \
  --cov=lggr_vi_core --cov=generate_figures \
  --cov-branch --cov-report=term-missing --cov-fail-under=95
uv run --isolated --frozen --extra dev python code/generate_figures.py
```

Execute the two notebooks from a clean kernel with `nbclient` or Jupyter.

For the proof layer:

```text
uv run --isolated --frozen --extra dev python scripts/capture_axiom_report.py --check
```

The `lean4/` project has no external Lake dependency. The release verifier
performs a hash-checked short-path replay on Windows, compares a fresh census
with `lean4/AXIOM_REPORT.txt`, rebuilds the paper twice with pdfLaTeX, and builds
the dated archive twice:

```text
uv run --isolated --frozen --extra dev python verify_deposit.py --lean
```
