"""Regression tests for real test routing, exact compiler pinning, and metadata drift."""
from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verifier = load("lggr_verifier", ROOT / "verify_deposit.py")


def test_named_flat_tests_execute_pass_failure_and_empty_collection(tmp_path, monkeypatch):
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    code = tmp_path / "code"
    code.mkdir()
    (code / "test_pass.py").write_text("def test_ok(): assert 2 + 2 == 4\n")
    (code / "test_fail.py").write_text("def test_bad(): assert False\n")
    (code / "test_empty.py").write_text("# no tests\n")
    assert verifier.check_tests(["code/test_pass.py"]) == []
    assert "Pytest failure" in verifier.check_tests(["code/test_fail.py"])[0]
    assert "Pytest failure" in verifier.check_tests(["code/test_empty.py"])[0]


def test_automatic_discovery_includes_flat_tests(tmp_path, monkeypatch):
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    (tmp_path / "code").mkdir()
    (tmp_path / "code/test_found.py").write_text("def test_found(): assert True\n")
    assert verifier.check_tests([]) == []


@pytest.mark.parametrize("target", ["../test_escape.py", "code/../test_escape.py", "code/test_missing.py", "code/helper.py", "/code/test_x.py", "code\\test_x.py"])
def test_invalid_test_targets_fail_closed(tmp_path, monkeypatch, target):
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    assert verifier.check_tests([target])


@pytest.fixture
def compiler(tmp_path, monkeypatch):
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    (tmp_path / "lean4").mkdir()
    (tmp_path / "lean4/lean-toolchain").write_text("leanprover/lean4:v99.2.3-rc1\n")
    monkeypatch.setattr(verifier, "_toolchain_roots", lambda: [], raising=False)
    binary = tmp_path / ("lean.exe" if os.name == "nt" else "lean")
    binary.touch()
    monkeypatch.setattr(verifier.shutil, "which", lambda name: str(binary))
    return binary


@pytest.mark.parametrize("reported,status,accepted", [
    ("Lean (version 99.2.3-rc1, x86_64, commit abc, Release)", 0, True),
    ("Lean (version 99.2.3, x86_64)", 0, False),
    ("Lean (version 99.2.3-rc10, x86_64)", 0, False),
    ("Lean (version 99.2.4, x86_64)", 0, False),
    ("Lean (version 99.2.3-rc1, x86_64)", 1, False),
    ("compiler version unavailable", 0, False),
])
def test_path_compiler_must_report_exact_pinned_release(compiler, monkeypatch, reported, status, accepted):
    calls = []
    def run(args, **kwargs):
        calls.append(args)
        return subprocess.CompletedProcess(args, status, reported, "")
    monkeypatch.setattr(verifier.subprocess, "run", run)
    assert verifier.toolchain_lean() == (compiler if accepted else None)
    assert calls == [[str(compiler), "--version"]]


def test_elan_launcher_does_not_install_an_absent_pin(compiler, monkeypatch):
    elan = compiler.with_name("elan.exe" if os.name == "nt" else "elan")
    elan.touch()
    calls = []
    def run(args, **kwargs):
        calls.append(args)
        assert kwargs["env"]["ELAN_TOOLCHAIN"] == "leanprover/lean4:v99.2.3-rc1"
        return subprocess.CompletedProcess(args, 1, "", "toolchain not installed")
    monkeypatch.setattr(verifier.subprocess, "run", run)
    assert verifier.toolchain_lean() is None
    assert calls == [[str(elan), "which", "lean"]]


def test_named_toolchain_directory_is_not_version_evidence(compiler, tmp_path, monkeypatch):
    home = tmp_path / ".elan"
    candidate = home / "toolchains/leanprover--lean4---v99.2.3-rc1/bin" / compiler.name
    candidate.parent.mkdir(parents=True)
    candidate.touch()
    monkeypatch.setenv("ELAN_HOME", str(home))
    monkeypatch.setattr(verifier, "_toolchain_roots", lambda: [home], raising=False)
    monkeypatch.setattr(verifier.subprocess, "run", lambda args, **kw: subprocess.CompletedProcess(args, 0, "Lean (version 99.2.4, x86_64)", ""))
    assert verifier.toolchain_lean() is None


def test_generated_metadata_rejects_version_and_license_drift(tmp_path):
    metadata = load("lggr_metadata", ROOT / "tools/sync_metadata.py")
    for name in ("manifest.json", ".zenodo.json", "zenodo_metadata.json", "README.md", "pyproject.toml", "LICENSE", "LICENSE-CODE", ROOT.name + ".md", "docs/descriptions.md"):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    assert metadata.check(tmp_path) == []
    project = tmp_path / "pyproject.toml"
    project.write_text(project.read_text().replace('license = "Apache-2.0"', 'license = "CC-BY-4.0"'))
    assert any("code license" in error for error in metadata.check(tmp_path))
    zenodo = tmp_path / ".zenodo.json"
    data = json.loads(zenodo.read_text(encoding="utf-8"))
    data["version"] = "0.1"
    zenodo.write_text(json.dumps(data), encoding="utf-8")
    assert any(".zenodo.json" in error for error in metadata.check(tmp_path))


def test_all_rational_reports_are_in_the_claim_inventory():
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    source = (ROOT / "lean4/minkowski_repair.lean").read_text(encoding="utf-8")
    reported = set(re.findall(r"^#print axioms (MinkowskiRepair\.\w+)$", source, re.M))
    assert len(reported) == 19
    assert set(manifest["declaration_groups"]["current_manuscript_rational_repair"]) == reported
    assert reported <= set(manifest["declarations"])
    assert manifest["declaration_count"] == len(set(manifest["declarations"]))
    assert len(manifest["lean_files"]) == 3


def test_release_rebuild_is_independent_of_rebuild_day(tmp_path, monkeypatch):
    import datetime
    release = load("lggr_release_builder", ROOT / "tools/rebuild_release.py")
    package = tmp_path / "paper"
    package.mkdir()
    (package / "manifest.json").write_text('{"date": "2026-10-10"}')
    (package / "zenodo_metadata.json").write_text('{"publication_date": "2026-10-10"}')
    paths = ["manifest.json", "zenodo_metadata.json"]
    entries = [(name, release.sha256_file(package / name)) for name in paths]
    (package / "MANIFEST.sha256").write_bytes(release.render(entries))
    class LaterDate(datetime.date):
        @classmethod
        def today(cls):
            return cls(2027, 2, 3)
    monkeypatch.setattr(release.datetime, "date", LaterDate)
    release.refresh(package)
    assert release.validate(package) == []
    archive = package / "paper_2026-10-10.zip"
    first = archive.read_bytes()
    release.refresh(package)
    assert archive.read_bytes() == first
    with release.zipfile.ZipFile(archive, "a") as modified:
        modified.writestr("paper/unrecorded.txt", "mutation")
    assert release.validate(package)


def test_retained_directory_read_errors_are_fatal(tmp_path, monkeypatch):
    import deposit_paths
    def inaccessible(root, *, followlinks, onerror):
        onerror(PermissionError("unreadable retained directory"))
    monkeypatch.setattr(deposit_paths.os, "walk", inaccessible)
    with pytest.raises(PermissionError, match="unreadable"):
        deposit_paths.walk_files(tmp_path, set(), set(), set())


def test_nested_build_name_does_not_hide_payload(tmp_path):
    import deposit_paths
    for rel in ("build/cache.py", "code/build/payload.py"):
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("payload")
    files = deposit_paths.walk_files(tmp_path, {"build"}, set(), set())
    assert [p.relative_to(tmp_path).as_posix() for p in files] == ["code/build/payload.py"]


def test_verifier_rechecks_payload_after_mutable_replay(tmp_path, monkeypatch, capsys):
    release = load("lggr_mutation_release", ROOT / "tools/rebuild_release.py")
    package = tmp_path / ROOT.name
    shutil.copytree(ROOT, package, ignore=shutil.ignore_patterns("*.zip", ".lake", "__pycache__", ".pytest_cache"))
    release.refresh(package)
    monkeypatch.setattr(verifier, "ROOT", package)
    monkeypatch.setattr(verifier, "MANIFEST", package / "SHA256SUMS")
    def mutate():
        with (package / "README.md").open("a", encoding="utf-8") as handle:
            handle.write("\npost-check mutation\n")
        return []
    monkeypatch.setattr(verifier, "check_exact_replay", mutate)
    monkeypatch.setattr(verifier, "check_minkowski", lambda: [])
    assert verifier.main([]) == 1
    assert "Post-replay integrity: Hash mismatch: README.md" in capsys.readouterr().out


@pytest.mark.parametrize("axiom", ["sorryAx", "Unapproved.assumption"])
def test_matching_census_cannot_admit_unapproved_axioms(tmp_path, monkeypatch, axiom):
    """A tampered report matching replay must still fail the independent allowlist."""
    import sys
    from types import SimpleNamespace

    lean = tmp_path / "lean4"
    lean.mkdir()
    (lean / "lake-manifest.json").write_text('{"packages": []}', encoding="utf-8")
    binary = tmp_path / ("lean.exe" if os.name == "nt" else "lean")
    binary.touch()
    binary.with_name("lake.exe" if os.name == "nt" else "lake").touch()
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    monkeypatch.setattr(verifier, "toolchain_lean", lambda: binary)
    monkeypatch.setattr(
        verifier.subprocess,
        "run",
        lambda args, **kwargs: subprocess.CompletedProcess(args, 0, "census", ""),
    )
    declarations = [SimpleNamespace(name="Fixture.theorem", axioms=frozenset({axiom}))]
    census = SimpleNamespace(
        check_census=lambda root: None,
        _declarations=lambda text, source: declarations,
        parse_report=lambda root: declarations,
    )
    _missing_module = object()
    _previous_module = sys.modules.get("replay_lean_axiom_census", _missing_module)
    try:
        sys.modules["replay_lean_axiom_census"] = census
        errors = verifier.check_lean()
        assert any(axiom in error and "Unauthorized" in error for error in errors)
    finally:
        if _previous_module is _missing_module:
            sys.modules.pop("replay_lean_axiom_census", None)
        else:
            sys.modules["replay_lean_axiom_census"] = _previous_module


def test_release_refresh_preserves_prior_dated_archive(tmp_path):
    release = load("historical_release", ROOT / "tools/rebuild_release.py")
    package = tmp_path / ROOT.name
    shutil.copytree(ROOT, package, ignore=shutil.ignore_patterns("*.zip", ".lake", "__pycache__", ".pytest_cache"))
    old = package / f"{ROOT.name}_2026-10-05.zip"
    old.write_bytes(b"historical bytes must remain exact")
    release.refresh(package)
    assert old.read_bytes() == b"historical bytes must remain exact"
    assert release.archive_path(package).name.endswith("2026-10-15.zip")
    assert release.validate(package) == []
