"""Negative controls for the complete release envelope and rendered source."""
import hashlib
import importlib.util
import json
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def frozen(tmp_path):
    target = tmp_path / ROOT.name
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(
        "scratch", "_support", ".lake", "__pycache__", ".pytest_cache", "*.egg-info"))
    identity = json.loads((target / "release_identity.json").read_text(encoding="utf-8"))
    archive = target / identity["archive"]
    if not archive.exists():
        # Extracted deposits contain the payload, never a recursive copy of the ZIP.
        builder = load("release_builder", target / "tools/rebuild_release.py")
        sums = target / "SHA256SUMS"
        entries = builder.read_manifest(sums, target)
        entries.append((sums.name, builder.sha256_file(sums)))
        builder.build_archive(target, archive, entries)
        archive.with_suffix(".zip.sha256").write_text(
            f"{builder.sha256_file(archive)}  {archive.name}\n", encoding="utf-8", newline="\n")
    return target


def test_release_bytes_match_their_manifests(frozen):
    builder = load("release_builder", ROOT / "tools/rebuild_release.py")
    assert builder.validate(frozen) == []


def test_resealed_archive_suffix_is_refused(frozen):
    builder = load("release_builder", ROOT / "tools/rebuild_release.py")
    identity = json.loads((frozen / "release_identity.json").read_text(encoding="utf-8"))
    archive = frozen / identity["archive"]
    archive.write_bytes(archive.read_bytes() + b"unreviewed suffix")
    archive.with_suffix(".zip.sha256").write_text(
        f"{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}\n", encoding="utf-8")
    assert "ZIP envelope differs from canonical deterministic build" in builder.validate(frozen)


def test_resealed_stale_render_is_refused(frozen):
    validator = load("release_metadata", ROOT / "tools/validate_release.py")
    identity = json.loads((frozen / "release_identity.json").read_text(encoding="utf-8"))
    source = frozen / identity["manuscript"]
    source.write_text(source.read_text(encoding="utf-8") + "\nAn additional mathematical claim.\n", encoding="utf-8")
    errors = validator.validate_metadata(frozen)
    assert any("Stale render binding" in error for error in errors)


def test_unmanifested_source_is_refused(frozen, monkeypatch):
    verifier = load("release_integrity", ROOT / "verify_deposit.py")
    monkeypatch.setattr(verifier, "ROOT", frozen)
    (frozen / "unreviewed.md").write_text("A source outside the manifest.", encoding="utf-8")
    assert "Unrecorded deposit file: unreviewed.md" in verifier.check_manifest(frozen / "SHA256SUMS")


def test_removed_census_query_is_refused(frozen):
    checker = load("release_census", ROOT / "tools/replay_lean_axiom_census.py")
    checker.ROOT = frozen
    path = frozen / "lean4/Census.lean"
    lines = path.read_text(encoding="utf-8").splitlines()
    first = next(i for i, line in enumerate(lines) if line.startswith("#print axioms "))
    del lines[first]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="exact source declaration set"):
        checker.replay(False)
