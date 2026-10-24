@echo off
cd /d "%~dp0\.."
set EPK_HEADLESS=1
set MPLBACKEND=Agg
python code\run_notebook.py %*
