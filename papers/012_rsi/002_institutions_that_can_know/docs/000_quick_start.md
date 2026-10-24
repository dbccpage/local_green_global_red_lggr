# Quick start

From the extracted package root, run `python tools/run_checks.py` and `python verify_deposit.py --test`. These need Python 3.10+ and no third-party module. For fresh Lean, notebook, contract and document checks use the dependency profiles and commands in [README](../README.md). A requested missing dependency fails explicitly.

The notebook illustrates lost order under a sum, a two-bit recovery code, a globally obstructed constraint cycle and common action with separate reasons. It does not execute a council or authorize an action.
