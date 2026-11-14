"""Release-surface checks for Paper I."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from types import ModuleType

import pytest

PAPER_ROOT = Path(__file__).resolve().parents[2]


def _claim_blocks(mapping: str) -> dict[str, str]:
    """Extract the small, regular claim records without adding a YAML runtime."""
    matches = list(
        re.finditer(
            r'^  - id: "([^"]+)"\n(.*?)(?=^  - id: "|\Z)',
            mapping,
            flags=re.MULTILINE | re.DOTALL,
        )
    )
    return {match.group(1): match.group(2) for match in matches}


def _load(path: Path, name: str) -> ModuleType:
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
    verify = _load(PAPER_ROOT / "verify_deposit.py", "paper_i_verify_paths")
    archive = _load(
        PAPER_ROOT / "scripts" / "build_deposit_zip.py",
        "paper_i_archive_paths",
    )
    with pytest.raises(SystemExit, match="unsafe path"):
        verify.parse_manifest(manifest, tmp_path)
    with pytest.raises(ValueError, match="unsafe path"):
        archive.parse_manifest(manifest, tmp_path)


def test_manifest_paths_reject_casefold_duplicates(tmp_path: Path) -> None:
    digest = "0" * 64
    manifest = tmp_path / "SHA256SUMS"
    manifest.write_text(
        f"{digest}  docs/item.txt\n{digest}  DOCS/ITEM.TXT\n",
        encoding="utf-8",
    )
    verify = _load(PAPER_ROOT / "verify_deposit.py", "paper_i_verify_duplicates")
    archive = _load(
        PAPER_ROOT / "scripts" / "build_deposit_zip.py",
        "paper_i_archive_duplicates",
    )
    with pytest.raises(SystemExit, match="more than once"):
        verify.parse_manifest(manifest, tmp_path)
    with pytest.raises(ValueError, match="more than once"):
        archive.parse_manifest(manifest, tmp_path)


def test_public_notebook_set_is_exact() -> None:
    regen = _load(
        PAPER_ROOT / "scripts" / "regen_sha256sums.py",
        "paper_i_regen",
    )
    verify = _load(PAPER_ROOT / "verify_deposit.py", "paper_i_verify")
    expected = {
        "00_how_to_read_this_series.ipynb",
        "06_reviewer_reference_verification.ipynb",
    }
    assert regen.PUBLIC_NOTEBOOKS == expected
    assert verify.PUBLIC_NOTEBOOKS == expected
    included = {
        path.name
        for path in regen.iter_files(PAPER_ROOT)
        if path.suffix == ".ipynb"
    }
    assert included == expected


def test_release_date_version_and_licences_are_aligned() -> None:
    metadata = json.loads(
        (PAPER_ROOT / "zenodo_metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["publication_date"] == "2026-10-15"
    assert metadata["version"] == "1.2.4"
    assert metadata["license"] == "cc-by-4.0"
    for rel in (
        "README.md",
        "lggr_i_evaluated_path_kernels.md",
        "lggr_i_evaluated_path_kernels_claim_ledger.md",
        "docs/descriptions.md",
    ):
        text = (PAPER_ROOT / rel).read_text(encoding="utf-8")
        assert "2026-10-15" in text
        assert "1.2.4" in text
    assert (PAPER_ROOT / "LICENSE").is_file()
    assert (PAPER_ROOT / "LICENSE-CODE").is_file()


def test_primary_secondary_descriptions_and_zenodo_parity() -> None:
    verify = _load(PAPER_ROOT / "verify_deposit.py", "paper_i_verify_descriptions")
    descriptions = (PAPER_ROOT / "docs" / "descriptions.md").read_text(
        encoding="utf-8"
    )
    assert "<p>" not in descriptions
    assert "$" not in descriptions
    abstract = verify._extract_abstract(descriptions)
    assert abstract
    metadata = json.loads(
        (PAPER_ROOT / "zenodo_metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["description"] == abstract
    assert "finite synthetic fixtures" in abstract
    assert verify.check_description_contract(PAPER_ROOT) == []


def test_claim_ir_uses_host_schema_and_matches_claim_map() -> None:
    verify = _load(PAPER_ROOT / "verify_deposit.py", "paper_i_verify_claim_ir")
    data = json.loads(
        (PAPER_ROOT / "docs" / "claim_ir.yaml").read_text(encoding="utf-8")
    )
    rows = data["claims"]
    assert rows
    assert all(row.get("claim_id") for row in rows)
    assert all(row.get("mechanization_class") for row in rows)
    assert any(
        "LEAN" in row["mechanization_class"]
        and "TOY" not in row["mechanization_class"]
        for row in rows
    )
    assert verify.check_claim_ir(PAPER_ROOT) == []


def test_canonical_pdflatex_and_dated_archive_contracts() -> None:
    builder = _load(
        PAPER_ROOT / "scripts" / "build_paper_artifacts.py",
        "paper_i_artifact_builder",
    )
    archive = _load(
        PAPER_ROOT / "scripts" / "build_deposit_zip.py",
        "paper_i_archive_builder",
    )
    preamble = PAPER_ROOT / "scripts" / "obstruction-preamble.tex"
    expected_hash = (
        "e2a8ac43c7abd8b971916d51e68f126798352d1bc0f2f05e3b2764c8176fb6dd"
    )
    assert hashlib.sha256(preamble.read_bytes()).hexdigest() == expected_hash
    assert builder.CANONICAL_PREAMBLE_SHA256 == expected_hash
    assert builder.PDFLATEX_RUNS == 2
    assert builder.validated_preamble().read_bytes() == preamble.read_bytes()
    source = (PAPER_ROOT / "scripts" / "build_paper_artifacts.py").read_text(
        encoding="utf-8"
    )
    assert '"--number-sections"' not in source
    assert '"--pdf-engine"' not in source
    assert 'need("xelatex")' not in source.casefold()
    assert 'need("lualatex")' not in source.casefold()
    assert archive.ARCHIVE_NAME == (
        "lggr_i_evaluated_path_kernels_2026-10-15.zip"
    )


def test_claim_map_names_existing_lean_declarations() -> None:
    mapping = (PAPER_ROOT / "docs" / "claim_code_map.yaml").read_text(
        encoding="utf-8"
    )
    lean = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((PAPER_ROOT / "lean4").glob("*.lean"))
    )
    for raw in re.findall(r'lean4_decl:\s*"([^"]+)"', mapping):
        if raw.startswith("none"):
            continue
        for qualified in raw.split(","):
            head = qualified.split("(", 1)[0].strip()
            token = head.rsplit(".", 1)[-1]
            assert re.search(rf"\b{re.escape(token)}\b", lean), qualified


def test_claim_map_ids_and_critical_semantic_handles_are_exact() -> None:
    mapping = (PAPER_ROOT / "docs" / "claim_code_map.yaml").read_text(
        encoding="utf-8"
    )
    ids = re.findall(r'^  - id: "([^"]+)"', mapping, flags=re.MULTILINE)
    blocks = _claim_blocks(mapping)

    assert len(ids) == len(set(ids))
    assert {"P1", "P2", "P3", "P4", "P5", "P6"} <= blocks.keys()
    assert {"G1", "G2", "G3", "G4", "G5", "G6"}.isdisjoint(blocks.keys())
    assert "RUST-TESTED" not in mapping
    assert "test_four_term_contribution_expansion" in blocks["D3"]
    assert "E2_count_gap_eq_delta_sum" in blocks["E2"]
    assert "test_e2_count_gap_equals_signed_defect_sum" in blocks["E2"]
    assert "E6_egd_zero_iff_all_zdr" in blocks["E6"]
    assert "test_e6_egd_zero_iff_all_zdr" in blocks["E6"]
    assert "test_hybrid_composition_under_g1_g2_g3_g4" in blocks["P5"]
    assert {"H2a", "H2b", "H2c", "I7a", "I7b"} <= blocks.keys()
    assert "neither factors" not in blocks["I7a"] + blocks["I7b"]


def test_claim_map_python_test_handles_exist() -> None:
    mapping = (PAPER_ROOT / "docs" / "claim_code_map.yaml").read_text(
        encoding="utf-8"
    )
    for nodeid in re.findall(r'python_test:\s*"([^"]+)"', mapping):
        if nodeid.startswith(("none", "absent")):
            continue
        parts = nodeid.split("::")
        path = PAPER_ROOT / parts[0]
        assert path.is_file(), nodeid
        if len(parts) == 1:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))}
        for handle in parts[1:]:
            assert handle in names, nodeid


def test_public_math_conditions_match_executable_boundaries() -> None:
    manuscript = (PAPER_ROOT / "lggr_i_evaluated_path_kernels.md").read_text(
        encoding="utf-8"
    )
    ledger = (PAPER_ROOT / "lggr_i_evaluated_path_kernels_claim_ledger.md").read_text(
        encoding="utf-8"
    )

    assert r"\bigsqcup_{b\in\mathsf B}" in manuscript
    assert "every compatible segment pair" in manuscript
    assert "No compatible pair is omitted or duplicated" in manuscript
    assert "+R_E(c,a)" in manuscript
    assert r"+\Delta_E\Delta_w" in manuscript
    assert r"D_{\mathrm{PoE}}>0" in manuscript
    assert re.search(r"common-support\s+condition", manuscript)
    assert "empty-global/nonempty-segments countermodel" in ledger


def test_public_prose_has_no_stale_receipt_or_internal_review_language() -> None:
    rels = (
        "README.md",
        "lggr_i_evaluated_path_kernels.md",
        "lggr_i_evaluated_path_kernels_claim_ledger.md",
        "docs/descriptions.md",
        "docs/nonclaims.md",
        "docs/quick_start.md",
    )
    forbidden = (
        "64 tests",
        "99% combined",
        "AuthorityEffect:",
        "proof ledger",
        "red team",
        "green team",
        "GTOC",
        "GTLA",
    )
    public_texts = [
        (rel, (PAPER_ROOT / rel).read_text(encoding="utf-8"))
        for rel in rels
    ]
    for rel, text in public_texts:
        for phrase in forbidden:
            assert phrase.casefold() not in text.casefold(), (rel, phrase)
    for path in sorted((PAPER_ROOT / "jupyter_notebooks").glob("*.ipynb")):
        text = path.read_text(encoding="utf-8")
        assert "authorityeffect:" not in text.casefold(), path.name
