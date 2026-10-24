"""Tests for CLI demonstration runner."""
from __future__ import annotations

import sys
from pathlib import Path

from code_cli import main, run_paper_snippet_replay


def test_cli_replay():
    inc, J = run_paper_snippet_replay(6.0)
    assert abs(inc - 6.0) < 1e-9
    assert len(J) == 3
    assert all(abs(score) < 1e-9 for score in J)


def test_cli_main(capsys):
    exit_code = main()
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Numerical Witness & Replay Harness" in captured.out
    assert "PASS" in captured.out
    assert "All numerical witnesses and replay checks passed." in captured.out


def test_cli_main_failure_path(monkeypatch, capsys):
    # F6 Regression: Mock check_theorem_1_passivity to return False
    monkeypatch.setattr("code_cli.check_theorem_1_passivity", lambda sys, a: False)
    exit_code = main()
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "FAIL" in captured.out
    assert "FAIL: 1 numerical check(s) failed" in captured.out
    assert "All numerical witnesses and replay checks passed" not in captured.out


# Tests for verify_deposit.py
DEPOSIT_ROOT = Path(__file__).resolve().parent.parent
if str(DEPOSIT_ROOT) not in sys.path:
    sys.path.insert(0, str(DEPOSIT_ROOT))

import verify_deposit  # noqa: E402


def test_verify_deposit_sha256(tmp_path):
    test_file = tmp_path / "hello.txt"
    test_file.write_text("hello world\n", encoding="utf-8")
    h = verify_deposit.sha256_of(test_file)
    assert len(h) == 64


def test_verify_deposit_check_manifest_missing(tmp_path):
    missing_manifest = tmp_path / "NONEXISTENT"
    errors = verify_deposit.check_manifest(missing_manifest)
    assert len(errors) > 0


def test_verify_deposit_main_pass(monkeypatch):
    monkeypatch.setattr(verify_deposit, "check_manifest", lambda path: [])
    monkeypatch.setattr(verify_deposit, "check_tests", lambda targets: [])
    exit_code = verify_deposit.main([])
    assert exit_code == 0


def test_verify_deposit_main_fail(monkeypatch):
    monkeypatch.setattr(verify_deposit, "check_manifest", lambda path: ["manifest error"])
    exit_code = verify_deposit.main([])
    assert exit_code == 1


