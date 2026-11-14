"""Synthetic custody probes; these do not claim an actual published ZIP is corrupt."""

import io
import subprocess
import zipfile
from pathlib import Path

import deposit_paths
import pytest

import verify_deposit as verifier

refresh = verifier.runpy.run_path(str(Path(verifier.__file__).parent / "tools/rebuild_release.py"))[
    "refresh"
]


@pytest.fixture
def release(tmp_path, monkeypatch):
    package = tmp_path / "synthetic"
    package.mkdir()
    (package / "README.md").write_text("payload", encoding="utf-8")
    (package / "MANIFEST.sha256").write_text(
        verifier.sha256_of(package / "README.md") + "  README.md\n", encoding="utf-8"
    )
    refresh(package, ("README.md",))
    monkeypatch.setattr(verifier, "ROOT", package)
    monkeypatch.setattr(verifier, "REQUIRED_PATTERNS", ())
    return package


def test_rebuild_is_byte_identical_and_inventory_complete(release):
    before = verifier.capture_release_state()
    refresh(release)
    assert verifier.capture_release_state() == before


@pytest.mark.parametrize("control", ["SHA256SUMS", "MANIFEST.sha256", "archive"])
def test_nonregular_control_after_subprocess_is_fatal(release, monkeypatch, control):
    path = next(release.glob("*.zip")) if control == "archive" else release / control

    def replace_control(command, **kwargs):
        path.unlink()
        path.mkdir()
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(verifier.subprocess, "run", replace_control)
    with pytest.raises((ValueError, OSError)):
        verifier.run_preserving_release(["synthetic"])


@pytest.mark.parametrize("mutation", ["edit", "delete", "add", "reseal"])
def test_subprocess_payload_mutation_is_fatal(release, monkeypatch, mutation):
    def mutate(command, **kwargs):
        if mutation == "edit":
            (release / "README.md").write_text("changed", encoding="utf-8")
        elif mutation == "delete":
            (release / "README.md").unlink()
        else:
            (release / "extra.md").write_text("added", encoding="utf-8")
            if mutation == "reseal":
                refresh(release, ("extra.md",))
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(verifier.subprocess, "run", mutate)
    with pytest.raises((ValueError, OSError)):
        verifier.run_preserving_release(["synthetic"])


@pytest.mark.parametrize(
    "mutation", ["prefix", "suffix", "comment", "duplicate", "timestamp", "omitted_sums"]
)
def test_noncanonical_archive_is_rejected(release, mutation):
    archive = next(release.glob("*.zip"))
    data = archive.read_bytes()
    if mutation in {"prefix", "suffix"}:
        data = b"extra" + data if mutation == "prefix" else data + b"extra"
    else:
        output = io.BytesIO()
        with (
            zipfile.ZipFile(io.BytesIO(data)) as old,
            zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as new,
        ):
            for info in old.infolist():
                if mutation == "omitted_sums" and info.filename.endswith("/SHA256SUMS"):
                    continue
                content = old.read(info)
                if mutation == "timestamp":
                    info.date_time = (2000, 1, 1, 0, 0, 0)
                new.writestr(info, content)
            if mutation == "comment":
                new.comment = b"noncanonical"
            if mutation == "duplicate":
                with pytest.warns(UserWarning, match="Duplicate"):
                    new.writestr(old.infolist()[0], old.read(old.infolist()[0]))
        data = output.getvalue()
    archive.write_bytes(data)
    with pytest.raises(ValueError, match="Release integrity"):
        verifier.capture_release_state()


@pytest.mark.parametrize(
    "entries",
    [
        ["Dir/a", "dir/b"],
        ["Asset", "asset/child"],
        ["file", "file"],
    ],
)
def test_manifest_component_case_collisions_are_fatal(tmp_path, entries):
    manifest = tmp_path / "SHA256SUMS"
    manifest.write_text(
        "".join("0" * 64 + "  " + name + "\n" for name in entries), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="case-colliding"):
        deposit_paths.read_manifest(tmp_path, manifest)


def test_traversal_error_is_fatal(tmp_path, monkeypatch):
    def broken_walk(root, *, followlinks, onerror):
        onerror(PermissionError("synthetic unreadable directory"))
        return []

    monkeypatch.setattr(deposit_paths.os, "walk", broken_walk)
    with pytest.raises(PermissionError, match="unreadable"):
        deposit_paths.walk_files(tmp_path, set(), set(), set())


def test_missing_census_is_fatal(release):
    lean = release / "lean4"
    lean.mkdir()
    (lean / "lakefile.lean").write_text("import Lake", encoding="utf-8")
    assert verifier.check_lean() == ["Missing mandatory lean4/Census.lean"]


def test_missing_census_declarations_are_fatal(release, monkeypatch):
    lean = release / "lean4"
    lean.mkdir()
    (lean / "lakefile.lean").write_text("import Lake", encoding="utf-8")
    (lean / "Census.lean").write_text("-- synthetic", encoding="utf-8")
    monkeypatch.setattr(
        verifier,
        "run_preserving_release",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 0, stdout="", stderr=""),
    )
    assert any("inventory mismatch" in error for error in verifier.check_lean())


@pytest.mark.parametrize("control", ["SHA256SUMS", "MANIFEST.sha256", "archive"])
def test_reparse_control_after_subprocess_is_fatal(release, monkeypatch, control):
    from types import SimpleNamespace

    path = next(release.glob("*.zip")) if control == "archive" else release / control
    original = Path.lstat

    def mark_reparse(command, **kwargs):
        def metadata(self, *args, **kw):
            result = original(self, *args, **kw)
            if self == path:
                return SimpleNamespace(st_mode=result.st_mode, st_file_attributes=0x400)
            return result

        monkeypatch.setattr(Path, "lstat", metadata)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(verifier.subprocess, "run", mark_reparse)
    with pytest.raises((ValueError, OSError)):
        verifier.run_preserving_release(["synthetic"])
