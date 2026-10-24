$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
$env:EPK_HEADLESS = "1"
$env:MPLBACKEND = "Agg"
python code/run_notebook.py @args
