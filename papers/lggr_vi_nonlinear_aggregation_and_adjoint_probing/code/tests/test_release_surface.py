"""Release-surface checks for Paper VI."""

from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path
from types import ModuleType

import pytest


PAPER_ROOT = Path(__file__).resolve().parents[2]
PAPER_STEM = "lggr_vi_nonlinear_aggregation_and_adjoint_probing"


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
    verify = _load(PAPER_ROOT / "verify_deposit.py", "paper_vi_verify_paths")
    archive = _load(
        PAPER_ROOT / "scripts" / "build_deposit_zip.py",
        "paper_vi_archive_paths",
    )
    with pytest.raises(ValueError, match="unsafe path"):
        verify.parse_manifest(manifest, tmp_path)
    with pytest.raises(ValueError, match="unsafe path"):
        archive.parse_sums(manifest, tmp_path)


def test_manifest_paths_reject_casefold_duplicates(tmp_path: Path) -> None:
    digest = "0" * 64
    manifest = tmp_path / "SHA256SUMS"
    manifest.write_text(
        f"{digest}  docs/item.txt\n{digest}  DOCS/ITEM.TXT\n",
        encoding="utf-8",
    )
    verify = _load(PAPER_ROOT / "verify_deposit.py", "paper_vi_verify_duplicates")
    archive = _load(
        PAPER_ROOT / "scripts" / "build_deposit_zip.py",
        "paper_vi_archive_duplicates",
    )
    with pytest.raises(ValueError, match="more than once"):
        verify.parse_manifest(manifest, tmp_path)
    with pytest.raises(ValueError, match="more than once"):
        archive.parse_sums(manifest, tmp_path)


def test_public_notebook_set_is_exact_and_output_free() -> None:
    regen = _load(PAPER_ROOT / "scripts" / "regen_sha256sums.py", "paper_vi_regen")
    verify = _load(PAPER_ROOT / "verify_deposit.py", "paper_vi_verify")
    expected = {
        "01_observation_blind_spots.ipynb",
        "02_adjoint_probes_and_falsifiers.ipynb",
    }
    assert regen.PUBLIC_NOTEBOOKS == expected
    assert verify.PUBLIC_NOTEBOOKS == expected
    included = {
        path.name for path in regen.iter_files(PAPER_ROOT) if path.suffix == ".ipynb"
    }
    assert included == expected
    for name in expected:
        notebook = json.loads(
            (PAPER_ROOT / "jupyter_notebooks" / name).read_text(encoding="utf-8")
        )
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                assert cell.get("outputs", []) == []
                assert cell.get("execution_count") is None


def test_verifier_finds_pytest_summary_before_coverage_footer() -> None:
    verify = _load(PAPER_ROOT / "verify_deposit.py", "paper_vi_summary")
    output = """........................................... [100%]
43 passed, 1 warning in 12.34s
Required test coverage of 95% reached. Total coverage: 100.00%
"""
    assert verify.pytest_summary(output) == "43 passed, 1 warning in 12.34s"


def test_legacy_omnibus_is_excluded_from_public_file_set() -> None:
    regen = _load(PAPER_ROOT / "scripts" / "regen_sha256sums.py", "paper_vi_files")
    relative = {
        path.relative_to(PAPER_ROOT).as_posix() for path in regen.iter_files(PAPER_ROOT)
    }
    assert not any(path.startswith("research/legacy_omnibus/") for path in relative)
    legacy = PAPER_ROOT / "research" / "legacy_omnibus"
    if legacy.exists():
        assert any(legacy.rglob("*"))


def test_release_date_version_and_licences_are_aligned() -> None:
    metadata = json.loads(
        (PAPER_ROOT / "zenodo_metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["publication_date"] == "2026-10-15"
    assert metadata["version"] == "0.1.1"
    assert metadata["license"] == "cc-by-4.0"
    assert metadata["publication_type"] == "preprint"
    assert metadata["access_right"] == "open"
    for relative in (
        "README.md",
        f"{PAPER_STEM}.md",
        f"{PAPER_STEM}_claim_ledger.md",
        f"{PAPER_STEM}_change_log.md",
    ):
        text = (PAPER_ROOT / relative).read_text(encoding="utf-8")
        assert "2026-10-15" in text
        assert "0.1.1" in text
    assert "Attribution 4.0 International" in (PAPER_ROOT / "LICENSE").read_text(
        encoding="utf-8"
    )
    assert "Apache License" in (PAPER_ROOT / "LICENSE-CODE").read_text(encoding="utf-8")


def test_descriptions_are_the_only_canonical_zenodo_source() -> None:
    metadata = json.loads(
        (PAPER_ROOT / "zenodo_metadata.json").read_text(encoding="utf-8")
    )
    descriptions = (PAPER_ROOT / "docs" / "descriptions.md").read_text(encoding="utf-8")
    primary = re.search(
        r"^## Primary Description\s*$.*?^```html\s*$\n(.*?)\n^```\s*$",
        descriptions,
        re.MULTILINE | re.DOTALL,
    )
    secondary = re.search(
        r"^## Secondary Description\s*$.*?^```text\s*$\n(.*?)\n^```\s*$",
        descriptions,
        re.MULTILINE | re.DOTALL,
    )
    assert primary is not None
    assert secondary is not None
    assert metadata["description"] == primary.group(1)
    assert secondary.group(1).startswith("Abstract.")
    for path in PAPER_ROOT.rglob("*"):
        if not path.is_file() or path in {
            PAPER_ROOT / "docs" / "descriptions.md",
            PAPER_ROOT / "zenodo_metadata.json",
        }:
            continue
        if any(part in {"legacy_omnibus", "dist", ".lake"} for part in path.parts):
            continue
        if path.suffix.lower() not in {".md", ".json", ".py", ".toml", ".cff"}:
            continue
        assert primary.group(1) not in path.read_text(
            encoding="utf-8", errors="replace"
        ), path


def test_claim_map_names_existing_lean_declarations() -> None:
    mapping = (PAPER_ROOT / "docs" / "claim_code_map.yaml").read_text(encoding="utf-8")
    lean_map = (PAPER_ROOT / "docs" / "lean_claim_map.md").read_text(encoding="utf-8")
    lean = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((PAPER_ROOT / "lean4").glob("*.lean"))
    )
    declarations = set(re.findall(r"LGGRVI\.[A-Za-z0-9_]+", mapping + lean_map))
    assert declarations == {
        "LGGRVI.postprocessing_invariance",
        "LGGRVI.zero_preserving_accepts_hidden",
        "LGGRVI.gram_zero_iff_hidden",
        "LGGRVI.detectable_has_nonzero_gram",
        "LGGRVI.gram_kernel_iff",
        "LGGRVI.gram_detectable_iff",
        "LGGRVI.centered_directional_identity",
        "LGGRVI.sign_cube_recovers",
    }
    for declaration in declarations:
        token = declaration.rsplit(".", 1)[-1]
        assert re.search(rf"\b{re.escape(token)}\b", lean), declaration


def test_public_prose_has_no_internal_workflow_dialect_or_stale_tags() -> None:
    relative_paths = [
        Path("README.md"),
        Path(f"{PAPER_STEM}.md"),
        Path("docs/descriptions.md"),
        Path("docs/quick_start.md"),
        Path("docs/research_program_25_steps.md"),
    ] + [
        path.relative_to(PAPER_ROOT)
        for path in sorted((PAPER_ROOT / "jupyter_notebooks").glob("*.ipynb"))
    ]
    forbidden = (
        "AuthorityEffect",
        "Authority Effect",
        "authority_effect",
        "GlobalGreen",
        "ProducerReceipt",
        "IndependentEvaluationReceipt",
        "role receipt",
    )
    for relative in relative_paths:
        text = (PAPER_ROOT / relative).read_text(encoding="utf-8")
        for phrase in forbidden:
            assert phrase.casefold() not in text.casefold(), (relative, phrase)
    manuscript = (PAPER_ROOT / f"{PAPER_STEM}.md").read_text(encoding="utf-8")
    assert re.search(r"\[(VERIFY|OPEN|TODO)]", manuscript) is None


def test_build_recipe_uses_the_release_epoch_and_all_figures() -> None:
    build = _load(PAPER_ROOT / "scripts" / "build_paper_artifacts.py", "paper_vi_build")
    assert build.SOURCE_EPOCH == 1760529600
    assert build.PAPER_MD.name == f"{PAPER_STEM}.md"
    assert set(build.FIGURES) == {
        "figure_1_kernel_and_adjoint.png",
        "figure_2_sign_probe_error.png",
    }
    assert build.SHARED_PREAMBLE_SHA256 == (
        "050ff13b2c82b6136fc4bbd9b2fc160fc0483ff7f96508277697b0316c584158"
    )
    live = build.shared_preamble()
    if live is not None:
        assert live.as_posix().endswith(
            "coda_atlas/_kits/obstruction_paper_kit/obstruction_preamble.tex"
        ) or live.as_posix().endswith(
            "coda_university/_kits/obstruction_paper_kit/obstruction_preamble.tex"
        )
        assert build.sha256_of(live) == build.SHARED_PREAMBLE_SHA256
        assert live.read_bytes() == build.BUNDLED_PREAMBLE.read_bytes()
    assert build.sha256_of(build.BUNDLED_PREAMBLE) == build.SHARED_PREAMBLE_SHA256
    source = (PAPER_ROOT / "scripts" / "build_paper_artifacts.py").read_text(
        encoding="utf-8"
    )
    assert 'need("pdflatex")' in source
    assert "xelatex" not in source.casefold()
    assert "lualatex" not in source.casefold()
    assert "--number-sections" not in source
    assert "for pass_number in (1, 2)" in source
    tex = (PAPER_ROOT / f"{PAPER_STEM}.tex").read_text(encoding="utf-8")
    assert r"\setcounter{secnumdepth}{-\maxdimen}" in tex
    assert build.BUNDLED_PREAMBLE.read_text(encoding="utf-8").strip() in tex


def test_archive_name_is_paper_specific_and_dated() -> None:
    archive = _load(PAPER_ROOT / "scripts" / "build_deposit_zip.py", "paper_vi_archive")
    assert archive.RELEASE_DATE == "2026-10-15"
    assert archive.ARCHIVE_NAME == f"{PAPER_ROOT.name}_2026-10-15.zip"
    assert archive.ZIP_DATE == (2026, 10, 15, 0, 0, 0)


def test_bundled_axiom_report_is_bound_to_exact_sources() -> None:
    verify = _load(PAPER_ROOT / "verify_deposit.py", "paper_vi_axiom_binding")
    report = (PAPER_ROOT / "lean4" / "AXIOM_REPORT.txt").read_text(encoding="utf-8")
    assert (
        f"Core.lean SHA-256: {verify.sha256_of(PAPER_ROOT / 'lean4' / 'Core.lean')}"
        in report
    )
    assert (
        "check_axioms.lean SHA-256: "
        f"{verify.sha256_of(PAPER_ROOT / 'lean4' / 'check_axioms.lean')}"
    ) in report
    for declaration in verify.EXPECTED_AXIOM_DECLARATIONS:
        matched = [
            line
            for line in report.splitlines()
            if line.startswith(f"'{declaration}' ")
        ]
        assert len(matched) == 1
        if "does not depend on any axioms" in matched[0]:
            continue
        found = re.search(r"depends on axioms:\s*\[([^]]*)]", matched[0])
        assert found is not None
        names = {item.strip() for item in found.group(1).split(",") if item.strip()}
        assert names <= verify.AXIOM_WHITELIST


def test_coverage_gate_measures_lines_and_branches_per_module() -> None:
    verify = _load(PAPER_ROOT / "verify_deposit.py", "paper_vi_coverage_gate")
    report = {
        "files": {
            "code/lggr_vi_core.py": {
                "summary": {
                    "num_statements": 100,
                    "covered_lines": 100,
                    "num_branches": 20,
                    "covered_branches": 18,
                }
            },
            "code/generate_figures.py": {
                "summary": {
                    "num_statements": 40,
                    "covered_lines": 40,
                    "num_branches": 4,
                    "covered_branches": 4,
                }
            },
        }
    }
    rates, problems = verify.coverage_percentages(report)
    assert rates["lggr_vi_core.py"] == (100.0, 90.0)
    assert rates["generate_figures.py"] == (100.0, 100.0)
    assert problems == ["lggr_vi_core.py branch coverage 90.00% is below 95.00%"]
