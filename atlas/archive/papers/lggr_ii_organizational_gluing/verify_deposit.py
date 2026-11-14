#!/usr/bin/env python3
"""One-command verifier for the Local Green, Global Red II (Organizational Gluing) deposit.

Deterministic, and it fails in both directions. Four checks, all required:

1. Every file listed in SHA256SUMS exists and hashes to its recorded value.
2. Sweep: no file is present in the deposit tree that SHA256SUMS does not
   list (SHA256SUMS itself and build/cache noise excepted). Both directions,
   so neither an altered file nor a smuggled extra file passes.
3. The files a reader needs in order to re-run anything are present and
   pinned -- not merely present on disk.
4. The full Python suite passes with no failures, errors, or skips, while the
   branch-aware production coverage remains at least 95 percent.

Optionally (`--lean`) it also runs `lake build` and elaborates the axiom
census, requiring a clean build and no axiom outside the recorded whitelist.
Lean is off by default because it needs a toolchain a reader may not have;
everything else uses the package's ``dev`` dependency set.

Exit status is 0 only if every check passes. The final line is a summary.

A hash match certifies that the bytes on disk are the bytes that were
hashed. It is not evidence for any mathematical claim in the paper.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "SHA256SUMS"

# Build output, caches and scratch are not deposit members. `b` is the Lake
# buildDir set in lean4/lakefile.lean; its files embed absolute local paths.
IGNORED_DIR_NAMES = {
    "__pycache__", ".pytest_cache", ".lake", "b", "scratch",
    ".ipynb_checkpoints", ".mypy_cache", ".ruff_cache", ".git",
    # Repository review records are not part of the public deposit payload.
    "_support",
    "dev_rips",
    "rt",
}
RELEASE_DATE = "2026-10-15"
ARCHIVE_NAME = f"{ROOT.name}_{RELEASE_DATE}.zip"
IGNORED_FILE_NAMES = {
    "SHA256SUMS",
    ".coverage",
    "DEPOSIT_CHECKLIST.md",
    ARCHIVE_NAME,
    "0_lggr_ii_organizational_gluing.pdf",
    f"1_{ARCHIVE_NAME}",
}

REQUIRED_FILES = (
    "code/organizational_gluing_core.py",
    "code/generate_figures.py",
    "code/tests/test_organizational_gluing_core.py",
    "code/tests/test_invasive_injections.py",
    "code/tests/test_notebook.py",
    "code/tests/test_release_contract.py",
    "jupyter_notebooks/lggr_ii_organizational_gluing.ipynb",
    "lggr_ii_organizational_gluing.md",
    "lggr_ii_organizational_gluing.tex",
    "lggr_ii_organizational_gluing.pdf",
    "lggr_ii_organizational_gluing_claim_ledger.md",
    "lggr_ii_organizational_gluing_change_log.md",
    "public_export/figure_1_organizational_cut_architecture.png",
    "public_export/figure_1_organizational_cut_architecture.pdf",
    "public_export/figure_2_case_studies_defect_matrix.png",
    "public_export/figure_2_case_studies_defect_matrix.pdf",
    "docs/claim_code_map.yaml",
    "docs/lean_claim_map.md",
    "docs/descriptions.md",
    "docs/keywords.md",
    "docs/mutation_audit.md",
    "docs/nonclaims.md",
    "docs/quick_start.md",
    "docs/references.md",
    "lean4/01_certified_closure.lean",
    "lean4/02_boundary_sufficiency.lean",
    "lean4/03_non_additivity.lean",
    "lean4/04_carrier_boundary_obstruction.lean",
    "lean4/05_detector_adequacy.lean",
    "lean4/core.lean",
    "lean4/lggr_ii_organizational_gluing.lean",
    "lean4/primitive_difference.lean",
    "lean4/lakefile.lean",
    "lean4/lake-manifest.json",
    "lean4/lean-toolchain",
    "lean4/check_axioms.lean",
    "lean4/axiom_report.txt",
    "LICENSE",
    "LICENSE-CODE",
    "MANIFEST.sha256",
    "pyproject.toml",
    "uv.lock",
    "README.md",
    "scripts/build_deposit_zip.py",
    "scripts/build_paper_artifacts.py",
    "scripts/obstruction-preamble.tex",
    "scripts/regen_sha256sums.py",
    "verify_deposit.py",
    "zenodo_metadata.json",
)

AXIOM_WHITELIST = frozenset({"Quot.sound", "Classical.choice"})
CANONICAL_PREAMBLE_SHA256 = (
    "e2a8ac43c7abd8b971916d51e68f126798352d1bc0f2f05e3b2764c8176fb6dd"
)
LEAN_TARGET = "LGGR2"
EXPECTED_AXIOM_REPORTS = 18

LEAN_MAP_ROWS = (
    ("M1", "PaperAE005.orgDelta_range", "lean4/03_non_additivity.lean", "MECHANIZED"),
    ("M2", "PaperAE005.orgDelta_is_negative_one_iff", "lean4/03_non_additivity.lean", "MECHANIZED"),
    ("M3", "PaperAE005.weak_boundary_sufficiency_does_not_force_factorization", "lean4/02_boundary_sufficiency.lean", "MECHANIZED"),
    ("M4", "PaperAE005.product_sufficiency_iff_evaluator_factorization", "lean4/02_boundary_sufficiency.lean", "MECHANIZED"),
    ("M5", "PaperAE005.three_binary_defects_sum_can_leave_binary_range", "lean4/03_non_additivity.lean", "MECHANIZED"),
    ("M6", "PaperAE005.zero_defect_does_not_imply_all_pass", "lean4/05_detector_adequacy.lean", "MECHANIZED"),
    ("M7", "PaperAE005.aligned_validator_forces_zero_defect", "lean4/05_detector_adequacy.lean", "MECHANIZED"),
    ("M7", "PaperAE005.aligned_validator_proxy_collapsing_detector", "lean4/05_detector_adequacy.lean", "MECHANIZED-SUPPORT"),
    ("M8", "PaperAE005.boundary_carrier_mixing_blocks_quotient_factorization", "lean4/04_carrier_boundary_obstruction.lean", "MECHANIZED"),
    ("M9", "PaperAE005.boundary_carrier_mixing_forces_lggr", "lean4/04_carrier_boundary_obstruction.lean", "MECHANIZED"),
    ("D1", "PaperAE005.governancePrerequisitesSatisfied", "lean4/01_certified_closure.lean", "MECHANIZED-DEFINITION"),
    ("D1", "PaperAE005.governance_prerequisites_require_auth", "lean4/01_certified_closure.lean", "MECHANIZED"),
)

LEDGER_MECHANIZATION = {
    "M1": "LEAN", "M2": "LEAN", "M3": "LEAN", "M4": "LEAN",
    "M5": "LEAN", "M6": "LEAN", "M7": "LEAN", "M8": "LEAN",
    "M9": "LEAN", "D1": "LEAN", "D2": "PYTHON", "D3": "PYTHON",
    "I1": "PROSE", "I2": "PYTHON", "R1": "PYTHON", "R2": "PYTHON",
}

PUBLIC_TEXT_FILES = (
    "README.md",
    "lggr_ii_organizational_gluing.md",
    "lggr_ii_organizational_gluing.tex",
    "lggr_ii_organizational_gluing_claim_ledger.md",
    "lggr_ii_organizational_gluing_change_log.md",
    "docs/descriptions.md",
    "docs/keywords.md",
    "docs/lean_claim_map.md",
    "docs/mutation_audit.md",
    "docs/nonclaims.md",
    "docs/quick_start.md",
    "docs/references.md",
    "jupyter_notebooks/lggr_ii_organizational_gluing.ipynb",
    "zenodo_metadata.json",
)

FORBIDDEN_PUBLIC_PATTERNS = (
    re.compile(r"Authority\s*Effect", re.IGNORECASE),
    re.compile(r"authority_effect", re.IGNORECASE),
    re.compile(r"GlobalGreen", re.IGNORECASE),
    re.compile(r"\brole[- ]receipt", re.IGNORECASE),
    re.compile(r"\bpipeline custody\b", re.IGNORECASE),
    re.compile(r"\bi3_review_receipt\b", re.IGNORECASE),
    re.compile(r"\bagent_proposal\b", re.IGNORECASE),
    re.compile(r"\breceipts?\b", re.IGNORECASE),
)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _validated_manifest_path(relative: str, lineno: int, root_dir: Path) -> Path:
    pure = PurePosixPath(relative)
    unsafe = (
        not relative
        or not pure.parts
        or pure.is_absolute()
        or pure.as_posix() != relative
        or ".." in pure.parts
        or "\\" in relative
        or ":" in pure.parts[0]
    )
    candidate = root_dir.joinpath(*pure.parts)
    try:
        candidate.resolve().relative_to(root_dir.resolve())
    except ValueError:
        unsafe = True
    current = root_dir
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            unsafe = True
            break
    if unsafe:
        print(
            f"FAIL: SHA256SUMS line {lineno} has unsafe path {relative!r}",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return candidate


def parse_manifest(
    manifest_path: Path = MANIFEST, root_dir: Path = ROOT
) -> dict[str, str]:
    """Parse SHA256SUMS lines of the form '<sha256>  <relative/path>'."""
    if not manifest_path.is_file():
        print("FAIL: SHA256SUMS is missing", file=sys.stderr)
        raise SystemExit(1)
    entries: dict[str, str] = {}
    seen_files_casefold: set[str] = set()
    seen_dirs: dict[str, str] = {}
    for lineno, raw in enumerate(
        manifest_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or re.fullmatch(r"[0-9a-fA-F]{64}", parts[0]) is None:
            print(f"FAIL: SHA256SUMS line {lineno} is malformed: {raw!r}", file=sys.stderr)
            raise SystemExit(1)
        digest, rel = parts[0].lower(), parts[1].strip().lstrip("*")
        _validated_manifest_path(rel, lineno, root_dir)
        key = rel.casefold()
        if key in seen_files_casefold:
            print(f"FAIL: SHA256SUMS lists {rel} more than once", file=sys.stderr)
            raise SystemExit(1)
        if key in seen_dirs:
            print(
                f"FAIL: SHA256SUMS path {rel!r} collides with directory {seen_dirs[key]!r}",
                file=sys.stderr,
            )
            raise SystemExit(1)
        pure = PurePosixPath(rel)
        for i in range(1, len(pure.parts)):
            dir_parts = pure.parts[:i]
            dir_str = "/".join(dir_parts)
            dir_cf = dir_str.casefold()
            if dir_cf in seen_files_casefold:
                print(
                    f"FAIL: SHA256SUMS directory component {dir_str!r} collides with file path",
                    file=sys.stderr,
                )
                raise SystemExit(1)
            if dir_cf in seen_dirs:
                if seen_dirs[dir_cf] != dir_str:
                    print(
                        f"FAIL: SHA256SUMS directory component case collision: {dir_str!r} vs {seen_dirs[dir_cf]!r}",
                        file=sys.stderr,
                    )
                    raise SystemExit(1)
            else:
                seen_dirs[dir_cf] = dir_str
        seen_files_casefold.add(key)
        entries[rel] = digest
    return entries


def check_hashes(entries: dict[str, str], root_dir: Path = ROOT) -> list[str]:
    problems: list[str] = []
    for rel, digest in sorted(entries.items()):
        path = root_dir / rel
        if not path.is_file():
            problems.append(f"missing file listed in SHA256SUMS: {rel}")
            continue
        actual = sha256_of(path)
        if actual != digest:
            problems.append(f"hash mismatch for {rel}: manifest {digest}, actual {actual}")
    return problems


def sweep_unlisted(entries: dict[str, str], root_dir: Path = ROOT) -> list[str]:
    problems: list[str] = []
    for path in sorted(root_dir.rglob("*")):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(root_dir).parts
        if any(
            part in IGNORED_DIR_NAMES or part.endswith(".egg-info")
            for part in rel_parts[:-1]
        ):
            continue
        rel = "/".join(rel_parts)
        if (
            rel in IGNORED_FILE_NAMES
            or path.name in IGNORED_FILE_NAMES
            or path.name.startswith(".coverage")
        ):
            continue
        if rel not in entries:
            problems.append(f"file present but not listed in SHA256SUMS: {rel}")
    return problems


def check_required(entries: dict[str, str], root_dir: Path = ROOT) -> list[str]:
    problems: list[str] = []
    for required in REQUIRED_FILES:
        if required not in entries:
            problems.append(f"required file not pinned in SHA256SUMS: {required}")
        elif not (root_dir / required).is_file():
            problems.append(f"required file missing on disk: {required}")
    return problems


def _normalized_lean_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def lean_statement_hash(path: Path, declaration: str) -> str:
    """Hash the exact normalized declaration statement, excluding its body."""
    text = _normalized_lean_text(path)
    local_name = declaration.rsplit(".", 1)[-1]
    start_match = re.search(
        rf"(?m)^(?:theorem|def|abbrev)\s+{re.escape(local_name)}\b", text
    )
    if start_match is None:
        raise ValueError(f"declaration not found: {declaration} in {path.name}")
    end = text.find(":=", start_match.start())
    if end < 0:
        raise ValueError(f"declaration body delimiter not found: {declaration}")
    statement = text[start_match.start():end].rstrip().encode("utf-8")
    return hashlib.sha256(statement).hexdigest()


def lean_import_hash(path: Path) -> str:
    """Hash normalized top-level import lines in source order."""
    text = _normalized_lean_text(path)
    imports = [line for line in text.split("\n") if line.startswith("import ")]
    block = (("\n".join(imports) + "\n") if imports else "").encode("utf-8")
    return hashlib.sha256(block).hexdigest()


def check_lean_claim_map(root_dir: Path = ROOT) -> list[str]:
    """Check claim/declaration coverage and the pinned statement/import hashes."""
    path = root_dir / "docs" / "lean_claim_map.md"
    if not path.is_file():
        return ["docs/lean_claim_map.md is missing"]
    text = path.read_text(encoding="utf-8")
    required_markers = (
        "**Default build target:** `LGGR2`",
        "**Lean version:** `4.33.1`",
        "**Build result:** 11 jobs completed successfully",
        "**Axiom result:** 18 reports; 17 axiom-free; one uses only `Quot.sound`",
    )
    problems = [
        f"lean claim map missing current-check marker: {marker}"
        for marker in required_markers if marker not in text
    ]

    rows: list[tuple[str, str, str, str, str, str]] = []
    for line in text.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 6:
            problems.append(f"malformed lean claim-map row: {line}")
            continue
        rows.append(tuple(cell.strip("`") for cell in cells))  # type: ignore[arg-type]

    expected = set(LEAN_MAP_ROWS)
    actual = {(claim, decl, source, status) for claim, decl, source, status, _, _ in rows}
    for missing in sorted(expected - actual):
        problems.append(f"lean claim map missing row: {missing}")
    for extra in sorted(actual - expected):
        problems.append(f"lean claim map has unexpected row: {extra}")
    if len(rows) != len(actual):
        problems.append("lean claim map contains duplicate declaration rows")

    for claim, declaration, source, status, statement_digest, import_digest in rows:
        if (claim, declaration, source, status) not in expected:
            continue
        source_path = root_dir / source
        if not source_path.is_file():
            problems.append(f"lean claim source missing: {source}")
            continue
        try:
            expected_statement = lean_statement_hash(source_path, declaration)
            expected_import = lean_import_hash(source_path)
        except ValueError as exc:
            problems.append(str(exc))
            continue
        if statement_digest != expected_statement:
            problems.append(
                f"statement hash mismatch for {declaration}: "
                f"map {statement_digest}, actual {expected_statement}"
            )
        if import_digest != expected_import:
            problems.append(
                f"import hash mismatch for {source}: "
                f"map {import_digest}, actual {expected_import}"
            )
    return problems


def check_ledger_mechanization(root_dir: Path = ROOT) -> list[str]:
    """Require a complete host-readable Mechanization column in the ledger."""
    path = root_dir / "lggr_ii_organizational_gluing_claim_ledger.md"
    text = path.read_text(encoding="utf-8")
    header: list[str] | None = None
    actual: dict[str, str] = {}
    problems: list[str] = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        lowered = [cell.lower() for cell in cells]
        if header is None and "id" in lowered and "mechanization" in lowered:
            header = lowered
            continue
        if header is None or all(set(cell) <= set("-: ") for cell in cells):
            continue
        row = dict(zip(header, cells))
        claim_id = row.get("id", "").strip().strip("`")
        if claim_id in actual:
            problems.append(f"duplicate claim-ledger row: {claim_id}")
        elif claim_id:
            actual[claim_id] = row.get("mechanization", "").strip()
    if header is None:
        return ["claim ledger lacks a structured Mechanization column"]
    for missing in sorted(set(LEDGER_MECHANIZATION) - set(actual)):
        problems.append(f"claim ledger missing mechanization row: {missing}")
    for extra in sorted(set(actual) - set(LEDGER_MECHANIZATION)):
        problems.append(f"unexpected claim-ledger row: {extra}")
    for claim_id, expected in LEDGER_MECHANIZATION.items():
        if actual.get(claim_id) != expected:
            problems.append(
                f"claim-ledger mechanization mismatch for {claim_id}: "
                f"expected {expected}, got {actual.get(claim_id)!r}"
            )
    return problems


def _description_block(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)", text
    )
    return " ".join(match.group(1).split()) if match else ""


def check_descriptions(root_dir: Path = ROOT) -> list[str]:
    """Keep the two public descriptions explicit and Zenodo on the primary text."""
    text = (root_dir / "docs" / "descriptions.md").read_text(encoding="utf-8")
    primary = _description_block(text, "Primary description")
    secondary = _description_block(text, "Secondary description")
    problems: list[str] = []
    if not primary:
        problems.append("docs/descriptions.md lacks a Primary description block")
    if not secondary:
        problems.append("docs/descriptions.md lacks a Secondary description block")
    metadata = json.loads((root_dir / "zenodo_metadata.json").read_text(encoding="utf-8"))
    zenodo_description = " ".join(str(metadata.get("description", "")).split())
    if primary and zenodo_description != primary:
        problems.append("zenodo_metadata.json description does not equal the Primary description")
    return problems


def check_build_contract(root_dir: Path = ROOT) -> list[str]:
    """Pin the shared-kit, pdfLaTeX, two-pass artifact-build contract."""
    problems: list[str] = []
    preamble = root_dir / "scripts" / "obstruction-preamble.tex"
    if not preamble.is_file():
        problems.append("packaged obstruction preamble is missing")
    elif sha256_of(preamble) != CANONICAL_PREAMBLE_SHA256:
        problems.append("packaged obstruction preamble differs from the canonical kit")
    script = (root_dir / "scripts" / "build_paper_artifacts.py").read_text(
        encoding="utf-8"
    )
    forbidden = ("xelatex", "lualatex", "--number-sections")
    for token in forbidden:
        if token in script.lower():
            problems.append(f"artifact builder contains forbidden option or engine: {token}")
    required = (
        'PDFLATEX_RUNS = 2',
        'SOURCE_DATE_EPOCH = "1789473600"',
        CANONICAL_PREAMBLE_SHA256,
        '"lake", "build", LEAN_TARGET',
        'AXIOM_REPORT.write_text',
    )
    for marker in required:
        if marker not in script:
            problems.append(f"artifact builder lacks required marker: {marker}")
    archive_script = (root_dir / "scripts" / "build_deposit_zip.py").read_text(
        encoding="utf-8"
    )
    for marker in (
        'ZIP_DATE = (2026, 10, 15, 0, 0, 0)',
        'RELEASE_DATE = "2026-10-15"',
        'f"{ROOT.name}_{RELEASE_DATE}.zip"',
    ):
        if marker not in archive_script:
            problems.append(f"archive builder lacks required marker: {marker}")
    tex = root_dir / "lggr_ii_organizational_gluing.tex"
    if tex.is_file():
        tex_text = tex.read_text(encoding="utf-8")
        if "% obstruction_preamble.tex — shared house style" not in tex_text:
            problems.append("generated TeX does not embed the canonical obstruction preamble")
        if "\\pdftrailerid{}" not in tex_text:
            problems.append("generated TeX does not suppress the nondeterministic trailer ID")
    return problems


def coverage_rates(totals: dict[str, object]) -> tuple[float, float]:
    statements = int(totals.get("num_statements", 0))
    covered_lines = int(totals.get("covered_lines", 0))
    branches = int(totals.get("num_branches", 0))
    covered_branches = int(totals.get("covered_branches", 0))
    line_rate = 0.0 if statements == 0 else 100.0 * covered_lines / statements
    branch_rate = 0.0 if branches == 0 else 100.0 * covered_branches / branches
    return line_rate, branch_rate


def coverage_gate_problems(
    totals: dict[str, object], threshold: float = 95.0
) -> list[str]:
    """Enforce line/statement and branch coverage as separate production gates."""
    statements = int(totals.get("num_statements", 0))
    branches = int(totals.get("num_branches", 0))
    problems = []
    if statements == 0:
        problems.append("coverage report contains zero statements")
    if branches == 0:
        problems.append("coverage report contains zero branches")
    line_rate, branch_rate = coverage_rates(totals)
    if line_rate < threshold:
        problems.append(f"line coverage {line_rate:.2f}% is below {threshold:.2f}%")
    if branch_rate < threshold:
        problems.append(f"branch coverage {branch_rate:.2f}% is below {threshold:.2f}%")
    return problems


def check_public_language(root_dir: Path = ROOT) -> list[str]:
    """Keep reader-facing package surfaces free of internal process dialect."""
    problems: list[str] = []
    for rel in PUBLIC_TEXT_FILES:
        path = root_dir / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PUBLIC_PATTERNS:
            match = pattern.search(text)
            if match:
                line = text.count("\n", 0, match.start()) + 1
                problems.append(
                    f"forbidden public-language token {match.group(0)!r} in {rel}:{line}"
                )
    return problems


def run_tests(root_dir: Path = ROOT) -> tuple[int, str, float, float]:
    """Run tests and return status, summary, line rate, and branch rate."""
    with tempfile.TemporaryDirectory(prefix="lggr2-pytest-") as raw:
        coverage_json = Path(raw) / "coverage.json"
        basetemp = Path(raw) / "pytest"
        basetemp.mkdir(parents=True, exist_ok=True)
        proc = subprocess.run(
            [
                sys.executable, "-m", "pytest", "-q", "-n", "4",
                "--basetemp", str(basetemp),
                "-p", "no:cacheprovider", "-p", "no:asyncio", "--no-header",
                "--cov=organizational_gluing_core", "--cov=generate_figures",
                "--cov-branch", "--cov-report=term-missing",
                f"--cov-report=json:{coverage_json}",
            ],
            cwd=str(root_dir), capture_output=True, text=True,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        tail = [ln for ln in out.splitlines() if ln.strip()]
        passed_lines = [ln for ln in tail if re.search(r"\d+ passed", ln)]
        summary = passed_lines[-1] if passed_lines else (tail[-1] if tail else "(no pytest output)")
        if proc.returncode != 0 or not coverage_json.is_file():
            print(out, file=sys.stderr)
            return proc.returncode or 1, summary, 0.0, 0.0
        totals = json.loads(coverage_json.read_text(encoding="utf-8"))["totals"]
        line_rate, branch_rate = coverage_rates(totals)
        gate_problems = coverage_gate_problems(totals)
        if gate_problems:
            print("\n".join(f"FAIL: {problem}" for problem in gate_problems), file=sys.stderr)
            return 1, summary, line_rate, branch_rate
    return 0, summary, line_rate, branch_rate


def _normalized_output(text: str) -> str:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    return "\n".join(line.rstrip() for line in lines).strip() + "\n"


EXPECTED_AXIOM_DECLARATIONS = (
    "PaperAE005.certified_closure_requires_auth",
    "PaperAE005.boundary_owner_not_sufficient",
    "PaperAE005.weak_boundary_sufficiency_does_not_force_factorization",
    "PaperAE005.product_sufficiency_iff_evaluator_factorization",
    "PaperAE005.three_binary_defects_sum_can_leave_binary_range",
    "PaperAE005.organizational_lggr_instance",
    "PaperAE005.orgDelta_range",
    "PaperAE005.orgDelta_is_negative_one_iff",
    "PaperAE005.boundary_carrier_mixing_forces_lggr",
    "PaperAE005.boundary_carrier_mixing_blocks_quotient_factorization",
    "PaperAE005.aligned_validator_collapsing_detector",
    "PaperAE005.aligned_validator_proxy_collapsing_detector",
    "PaperAE005.red_verdict_sound_detection",
    "PaperAE005.green_verdict_unsound_as_certificate",
    "PaperAE005.governance_prerequisites_require_auth",
    "PaperAE005.governancePrerequisitesSatisfied",
    "PaperAE005.zero_defect_does_not_imply_all_pass",
    "PaperAE005.aligned_validator_forces_zero_defect",
)


def _normalize_lean_version(lean_version: str) -> str:
    return re.sub(
        r",\s*[a-zA-Z0-9_]+-(?:w64-windows-gnu|unknown-linux-gnu|apple-darwin)[^,]*,",
        ",",
        lean_version.strip(),
    )


def _render_axiom_report(lean_version: str, census: str) -> str:
    return (
        "Paper II Lean axiom report\n"
        "Date: 2026-10-15\n"
        f"Toolchain: {_normalize_lean_version(lean_version)}\n"
        f"Build target: {LEAN_TARGET}\n"
        "Build result: success\n"
        "Census command: lake env lean check_axioms.lean\n\n"
        f"{_normalized_output(census)}"
    )


def _parse_axiom_reports(text: str) -> tuple[dict[str, list[str]], list[str]]:
    reports: dict[str, list[str]] = {}
    problems: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or not line.startswith("'"):
            continue
        m_decl = re.search(r"^'([^']+)'", line)
        if not m_decl:
            problems.append(f"could not parse declaration from axiom report: {line}")
            continue
        decl = m_decl.group(1)
        if decl in reports:
            problems.append(f"duplicate axiom report for declaration: {decl}")
            continue
        if "does not depend on any axioms" in line:
            reports[decl] = []
            continue
        _, _, tail = line.partition("depends on axioms: ")
        names = [n.strip(" []") for n in re.split(r"[,\s]+", tail) if n.strip(" []")]
        reports[decl] = names
    return reports, problems


def _axiom_reports(lean_dir: Path) -> tuple[list[str], str, str | None]:
    """Collect `#print axioms` reports."""
    census = lean_dir / "check_axioms.lean"
    if census.is_file():
        proc = subprocess.run(["lake", "env", "lean", "check_axioms.lean"],
                              cwd=str(lean_dir), capture_output=True, text=True)
        if proc.returncode != 0:
            detail = proc.stdout + proc.stderr
            return [], "", "axiom census failed to elaborate: " + detail.strip()
        census = (proc.stdout or "") + (proc.stderr or "")
        return [ln for ln in census.splitlines() if ln.strip().startswith("'")], census, None
    build = subprocess.run(["lake", "build"], cwd=str(lean_dir),
                           capture_output=True, text=True)
    reports = [ln for ln in build.stdout.splitlines() if ln.strip().startswith("'")]
    if not reports:
        for f in lean_dir.glob("*.lean"):
            f.touch()
        build = subprocess.run(["lake", "build"], cwd=str(lean_dir),
                               capture_output=True, text=True)
        reports = [ln for ln in build.stdout.splitlines() if ln.strip().startswith("'")]
    census = (build.stdout or "") + (build.stderr or "")
    return reports, census, None


def run_lean(root_dir: Path = ROOT) -> list[str]:
    """Build a short-path copy, then run the axiom census.

    The package path is long enough to exceed legacy Windows path limits in
    Lean's object-file writer. Copying source files to the system temporary
    directory makes the same source replayable without mutating the deposit.
    """
    problems: list[str] = []
    source = root_dir / "lean4"
    for path in source.glob("*.lean"):
        if re.search(r"\b(?:sorry|admit)\b", path.read_text(encoding="utf-8")):
            problems.append(f"placeholder proof token in {path.name}")
    if problems:
        return problems
    with tempfile.TemporaryDirectory(prefix="lggr2-lean-") as raw:
        lean_dir = Path(raw)
        for path in source.iterdir():
            if path.is_file():
                shutil.copy2(path, lean_dir / path.name)
        version = subprocess.run(
            ["lake", "env", "lean", "--version"], cwd=str(lean_dir),
            capture_output=True, text=True,
        )
        if version.returncode != 0:
            problems.append("Lean version check failed")
            return problems
        lean_version = _normalized_output(
            (version.stdout or "") + (version.stderr or "")
        ).strip()
        build = subprocess.run(["lake", "build", LEAN_TARGET], cwd=str(lean_dir),
                               capture_output=True, text=True)
        if build.returncode != 0:
            problems.append("lake build failed")
            print(build.stdout + build.stderr, file=sys.stderr)
            return problems
        reports, census, err = _axiom_reports(lean_dir)
        if err:
            problems.append(err)
            return problems
    report_path = source / "axiom_report.txt"
    if not report_path.is_file():
        problems.append("captured axiom report is missing")
        return problems
    stored_report = report_path.read_text(encoding="utf-8")
    for triple in ("w64-windows-gnu", "unknown-linux-gnu", "apple-darwin"):
        if triple in stored_report:
            problems.append(f"platform target triple {triple!r} found in stored axiom report")

    # Verify toolchain identity independently from platform target triple
    m_stored_toolchain = re.search(r"(?m)^Toolchain:\s*(.+)$", stored_report)
    expected_toolchain = f"Toolchain: {_normalize_lean_version(lean_version)}"
    if not m_stored_toolchain:
        problems.append("stored axiom report lacks a Toolchain line")
    elif m_stored_toolchain.group(0).strip() != expected_toolchain:
        problems.append(
            f"stored toolchain {m_stored_toolchain.group(0).strip()!r} does not match "
            f"current normalized toolchain {expected_toolchain!r}"
        )

    # Compare declaration and axiom content separately
    census_decls, census_errs = _parse_axiom_reports(census)
    stored_decls, stored_errs = _parse_axiom_reports(stored_report)
    problems.extend(census_errs)
    problems.extend(stored_errs)

    if len(census_decls) != EXPECTED_AXIOM_REPORTS:
        problems.append(
            f"axiom census produced {len(census_decls)} distinct reports, expected {EXPECTED_AXIOM_REPORTS}"
        )
    missing = set(EXPECTED_AXIOM_DECLARATIONS) - set(census_decls)
    if missing:
        problems.append(f"axiom census missing expected declarations: {sorted(missing)}")
    extra = set(census_decls) - set(EXPECTED_AXIOM_DECLARATIONS)
    if extra:
        problems.append(f"axiom census has unexpected declarations: {sorted(extra)}")

    for decl, axioms in census_decls.items():
        for ax in axioms:
            if ax not in AXIOM_WHITELIST:
                problems.append(f"axiom outside whitelist: {ax} in {decl}")

    if census_decls != stored_decls:
        problems.append("census declaration/axiom content differs from stored axiom report")

    if not problems:
        print(f"lean: build clean, {len(census_decls)} axiom reports, all within "
              f"{sorted(AXIOM_WHITELIST)}")
    return problems


def check_release_archive(entries: dict[str, str], root_dir: Path = ROOT) -> list[str]:
    """Verify source-to-release agreement against the release candidate archive."""
    archive_name = f"{root_dir.name}_{RELEASE_DATE}.zip"
    archive_path = root_dir / archive_name
    if not archive_path.is_file():
        return [f"release archive is missing: {archive_name}"]
    problems: list[str] = []

    canonical_pdf = root_dir / f"{root_dir.name}.pdf"
    upload_pdf = root_dir / f"0_{root_dir.name}.pdf"
    if upload_pdf.is_file() and canonical_pdf.is_file():
        if sha256_of(upload_pdf) != sha256_of(canonical_pdf):
            problems.append(f"upload PDF {upload_pdf.name} differs from canonical PDF {canonical_pdf.name}")

    obsolete_zip = root_dir / f"1_{archive_name}"
    if obsolete_zip.is_file():
        problems.append(f"obsolete archive {obsolete_zip.name} must be removed")

    try:
        import zipfile
        with zipfile.ZipFile(archive_path, "r") as zf:
            names = zf.namelist()
            if len(names) != len(set(names)):
                problems.append("release archive contains duplicate member names")
            prefix = root_dir.name
            expected_members = {f"{prefix}/{rel}" for rel in entries}
            expected_members.add(f"{prefix}/SHA256SUMS")
            if set(names) != expected_members:
                missing = sorted(expected_members - set(names))
                extra = sorted(set(names) - expected_members)
                if missing:
                    problems.append(f"release archive missing members: {missing[:5]}")
                if extra:
                    problems.append(f"release archive contains unexpected members: {extra[:5]}")
            for info in zf.infolist():
                if info.date_time != (2026, 10, 15, 0, 0, 0):
                    problems.append(
                        f"release archive timestamp drift in {info.filename}: {info.date_time}"
                    )
                    break
            for member in names:
                rel = member.partition("/")[2]
                disk_path = root_dir / rel
                if not disk_path.is_file():
                    problems.append(f"release archive member missing on disk: {rel}")
                    continue
                if zf.read(member) != disk_path.read_bytes():
                    problems.append(f"release archive member differs from disk source: {rel}")
    except Exception as exc:
        problems.append(f"could not verify release archive: {exc}")
    return problems


def main(argv: list[str]) -> int:
    entries = parse_manifest()
    problems = (
        check_hashes(entries)
        + sweep_unlisted(entries)
        + check_required(entries)
        + check_release_archive(entries)
        + check_descriptions()
        + check_build_contract()
        + check_public_language()
    )
    for p in problems:
        print(f"FAIL: {p}", file=sys.stderr)
    if problems:
        print(f"verification FAILED: {len(problems)} manifest problem(s)")
        return 1
    print(f"SHA256SUMS: all {len(entries)} files verified")

    collected = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    match = re.search(r"(\d+) tests collected", collected.stdout + collected.stderr)
    if match is None:
        print("verification FAILED: could not collect tests", file=sys.stderr)
        return 1
    expected = int(match.group(1))

    rc, summary, line_rate, branch_rate = run_tests()
    if rc != 0:
        print(f"verification FAILED: test suite did not pass -- {summary}", file=sys.stderr)
        return 1
    if "xfail" in summary or "error" in summary:
        print(f"verification FAILED: suite was not clean -- {summary}", file=sys.stderr)
        return 1
    if f"{expected} passed" not in summary:
        print(f"verification FAILED: expected {expected} passing tests, got "
              f"-- {summary}", file=sys.stderr)
        return 1
    print(f"tests: {summary}")
    print(f"coverage: lines {line_rate:.2f}%, branches {branch_rate:.2f}%")

    if "--lean" in argv:
        lean_problems = run_lean()
        for p in lean_problems:
            print(f"FAIL: {p}", file=sys.stderr)
        if lean_problems:
            print("verification FAILED: Lean checks did not pass")
            return 1

    print(f"verified: {len(entries)} files pinned, {expected} tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

