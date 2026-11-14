"""Cross-surface release contracts for claims, identity, and provenance."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import epk_gtla_overlay_core as core
import pytest
import verify_deposit

PAPER_ROOT = Path(__file__).resolve().parents[2]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "relative",
    (
        "../outside.txt",
        "/absolute.txt",
        "C:/absolute.txt",
        "folder\\alias.txt",
        "./normalized.txt",
        "folder//normalized.txt",
        ".",
    ),
)
def test_manifest_paths_fail_closed(relative: str, tmp_path: Path) -> None:
    digest = "0" * 64
    manifest = tmp_path / "SHA256SUMS"
    manifest.write_text(f"{digest}  {relative}\n", encoding="utf-8")
    archive = _load(
        PAPER_ROOT / "scripts" / "build_deposit_zip.py",
        "lggr3_archive_paths",
    )
    with pytest.raises(ValueError, match="unsafe path"):
        verify_deposit.parse_manifest(manifest, tmp_path)
    with pytest.raises(ValueError, match="unsafe path"):
        archive.parse_manifest(manifest, tmp_path)


def test_manifest_paths_reject_casefold_duplicates(tmp_path: Path) -> None:
    digest = "0" * 64
    manifest = tmp_path / "SHA256SUMS"
    manifest.write_text(
        f"{digest}  docs/item.txt\n{digest}  DOCS/ITEM.TXT\n",
        encoding="utf-8",
    )
    archive = _load(
        PAPER_ROOT / "scripts" / "build_deposit_zip.py",
        "lggr3_archive_duplicates",
    )
    with pytest.raises(ValueError, match="duplicate"):
        verify_deposit.parse_manifest(manifest, tmp_path)
    with pytest.raises(ValueError, match="more than once"):
        archive.parse_manifest(manifest, tmp_path)


def test_claim_ir_has_exactly_fifteen_ordered_claims() -> None:
    assert verify_deposit.check_claim_ir() == []


def test_claim_ir_drives_all_live_review_stages() -> None:
    text = (PAPER_ROOT / "docs" / "claim_ir.yaml").read_text(encoding="utf-8")
    assert text.count("claim_id: LGGR3-C") == 15
    assert "mechanization_class: LEAN_FULL" in text
    assert "mechanization_class: LEAN_PARTIAL" in text
    assert "mechanization_class: SCOPE_FENCE" in text
    assert "mechanization_class: PYTHON_INSTANCE" in text
    assert "mechanization_class: LITERATURE" in text


def test_all_documented_lean_handles_exist_in_public_core() -> None:
    handles = verify_deposit.lean_handles()
    assert len(handles) == 12
    assert verify_deposit.check_lean_handles_text() == []


def test_all_mapped_python_symbols_resolve() -> None:
    text = (PAPER_ROOT / "docs" / "claim_code_map.yaml").read_text(encoding="utf-8")
    specifications = re.findall(r"^\s+python: (.+)$", text, flags=re.MULTILINE)
    for specification in specifications:
        for handle in (part.strip() for part in specification.split(";")):
            value = core
            for component in handle.split("."):
                value = getattr(value, component)
            assert value is not None


def test_identity_block_matches_markdown_tex_pdf_and_metadata() -> None:
    assert verify_deposit.check_identity() == []


def test_public_build_and_provenance_contracts() -> None:
    assert verify_deposit.check_release_contract() == []
    assert verify_deposit.check_axiom_inventory() == []


def test_branch_floor_is_independent_of_line_floor() -> None:
    assert verify_deposit.coverage_meets_threshold({"module.py": (100.0, 95.0)})
    assert not verify_deposit.coverage_meets_threshold({"module.py": (100.0, 94.99)})


def test_checklist_and_metadata_agree_on_exact_frozen_tag_scope() -> None:
    checklist_path = PAPER_ROOT / "DEPOSIT_CHECKLIST.md"
    metadata = json.loads(
        (PAPER_ROOT / "zenodo_metadata.json").read_text(encoding="utf-8")
    )
    checklist = (
        checklist_path.read_text(encoding="utf-8")
        if checklist_path.is_file()
        else "operator checklist intentionally excluded from compact archive"
    )
    combined = checklist + json.dumps(metadata, sort_keys=True)
    assert "sealed-derivation-v1" in combined
    assert "3100c4e" in combined
    assert metadata["related_identifiers"][0]["identifier"].endswith(
        "/tree/sealed-derivation-v1"
    )
    assert "mechanical" in metadata["notes"]
    assert "not evidence" in metadata["notes"]


def test_legacy_omnibus_bytes_match_relocation_manifest() -> None:
    legacy = PAPER_ROOT / "research" / "legacy_omnibus"
    manifest = legacy / "SHA256SUMS"
    if not manifest.is_file():
        assert not legacy.exists()
        assert "excluded from release evidence" in (PAPER_ROOT / "README.md").read_text(
            encoding="utf-8"
        )
        return
    entries = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split(None, 1)
        entries[relative.strip()] = digest
    assert len(entries) == 27
    for relative, expected in entries.items():
        assert _sha256(legacy / relative) == expected


def test_current_surface_does_not_import_legacy_omnibus() -> None:
    active = (
        (PAPER_ROOT / "code" / "epk_gtla_overlay_core.py").read_text(encoding="utf-8")
        + (PAPER_ROOT / "lean4" / "Core.lean").read_text(encoding="utf-8")
        + (PAPER_ROOT / "lean4" / "lakefile.lean").read_text(encoding="utf-8")
    )
    assert "CleanLocusGates" not in active
    assert "legacy_omnibus" not in active


def test_checksum_manifests_match_only_the_public_tree() -> None:
    process = subprocess.run(
        [sys.executable, "scripts/regen_sha256sums.py", "--check"],
        cwd=PAPER_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert process.returncode == 0, process.stdout + process.stderr
    entries = verify_deposit.parse_manifest()
    assert verify_deposit.check_manifest(entries) == []
    assert verify_deposit.check_selection(entries) == []


def test_exact_twelve_paired_mutations_are_registered() -> None:
    assert verify_deposit.check_mutation_pairs() == []


def test_manifest_paths_reject_intermediate_symlinks(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    payload = data_dir / "payload.txt"
    payload.write_text("hello", encoding="utf-8")
    alias = tmp_path / "alias"
    try:
        alias.symlink_to(data_dir, target_is_directory=True)
    except OSError:
        pytest.skip("symlinks not permitted without privilege in this environment")

    digest = "0" * 64
    manifest = tmp_path / "SHA256SUMS"
    manifest.write_text(f"{digest}  alias/payload.txt\n", encoding="utf-8")
    archive = _load(
        PAPER_ROOT / "scripts" / "build_deposit_zip.py",
        "lggr3_archive_symlinks",
    )
    with pytest.raises(ValueError, match="unsafe path"):
        verify_deposit.parse_manifest(manifest, tmp_path)
    with pytest.raises(ValueError, match="unsafe path"):
        archive.parse_manifest(manifest, tmp_path)


def test_selection_gate_rejects_excluded_entries() -> None:
    base_entries = {path: "0" * 64 for path in verify_deposit.REQUIRED_FILES}
    for prohibited in (
        ".coverage",
        "DEPOSIT_CHECKLIST.md",
        "scratch/private.txt",
        "lean4/b/Core.lean",
        "jupyter_notebooks/duplicate/01_two_passes_one_failure.ipynb",
    ):
        entries = dict(base_entries)
        entries[prohibited] = "0" * 64
        problems = verify_deposit.check_selection(entries)
        assert problems, f"selection gate unexpectedly accepted {prohibited}"


def test_manifest_consistency_detects_mismatch() -> None:
    sums_entries = {"README.md": "a" * 64, "MANIFEST.sha256": "b" * 64}
    manifest_entries = {"README.md": "a" * 64}
    assert (
        verify_deposit.check_manifest_consistency(sums_entries, manifest_entries) == []
    )

    # Missing MANIFEST.sha256 in sums
    bad_sums = {"README.md": "a" * 64}
    assert verify_deposit.check_manifest_consistency(bad_sums, manifest_entries) != []

    # Content mismatch between sums and manifest
    mismatched_manifest = {"README.md": "c" * 64}
    assert (
        verify_deposit.check_manifest_consistency(sums_entries, mismatched_manifest)
        != []
    )

    # Extra file in manifest
    extra_manifest = {"README.md": "a" * 64, "scratch/foo.txt": "d" * 64}
    assert verify_deposit.check_manifest_consistency(sums_entries, extra_manifest) != []
