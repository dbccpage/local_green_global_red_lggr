#!/usr/bin/env python3
"""Verify the complete public deposit for Local Green, Global Red III.

The default checks both checksum manifests, the exact public-file selection,
the paper build, and branch-aware Python coverage. Add --lean to build the
short public Lean target and audit its axiom reports.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "SHA256SUMS"
PUBLIC_NOTEBOOKS = {
    "00_start_here.ipynb",
    "01_two_passes_one_failure.ipynb",
    "02_why_zero_can_mislead.ipynb",
    "03_when_paths_compose.ipynb",
    "04_when_grouping_loses_information.ipynb",
    "05_one_record_six_roles.ipynb",
    "06_reviewer_verification.ipynb",
}
PUBLIC_NOTEBOOK_PATHS = frozenset(
    {f"jupyter_notebooks/{name}" for name in PUBLIC_NOTEBOOKS}
)
PUBLIC_LEAN_FILES = {
    "AXIOM_REPORT.txt",
    "Core.lean",
    "check_axioms.lean",
    "lakefile.lean",
    "lake-manifest.json",
    "lean-toolchain",
}
PUBLIC_LEAN_PATHS = frozenset(
    {f"lean4/{name}" for name in PUBLIC_LEAN_FILES}
)
IGNORED_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    ".uv-cache",
    ".uv-python",
    "__pycache__",
    ".pytest_cache",
    ".lake",
    "b",
    "scratch",
    ".ipynb_checkpoints",
    ".mypy_cache",
    ".ruff_cache",
    "dev_rips",
    "rt",
    "dist",
    "build",
    "htmlcov",
    "_support",
    "research",
}
DATED_ARCHIVE_NAME = "lggr_iii_epk_gtla_overlay_2026-10-15.zip"
IGNORED_FILE_NAMES = {
    "SHA256SUMS",
    ".coverage",
    "DEPOSIT_CHECKLIST.md",
    "0_lggr_iii_epk_gtla_overlay.pdf",
    "1_lggr_iii_epk_gtla_overlay.zip",
    DATED_ARCHIVE_NAME,
}
REQUIRED_FILES = {
    "LICENSE",
    "LICENSE-CODE",
    "MANIFEST.sha256",
    "README.md",
    "code/epk_gtla_overlay_core.py",
    "code/generate_figures.py",
    "code/run_notebook.py",
    "code/tests/test_epk_gtla_overlay_core.py",
    "code/tests/test_figure_generator.py",
    "code/tests/test_invasive_injections.py",
    "code/tests/test_notebooks.py",
    "code/tests/test_release_contracts.py",
    "docs/claim_code_map.yaml",
    "docs/claim_ir.yaml",
    "docs/descriptions.md",
    "docs/keywords.md",
    "docs/lean_claim_map.md",
    "docs/mutation_audit.md",
    "docs/nonclaims.md",
    "docs/quick_start.md",
    "docs/references.md",
    "jupyter_notebooks/00_start_here.ipynb",
    "jupyter_notebooks/01_two_passes_one_failure.ipynb",
    "jupyter_notebooks/02_why_zero_can_mislead.ipynb",
    "jupyter_notebooks/03_when_paths_compose.ipynb",
    "jupyter_notebooks/04_when_grouping_loses_information.ipynb",
    "jupyter_notebooks/05_one_record_six_roles.ipynb",
    "jupyter_notebooks/06_reviewer_verification.ipynb",
    "lean4/Core.lean",
    "lean4/AXIOM_REPORT.txt",
    "lean4/check_axioms.lean",
    "lean4/lake-manifest.json",
    "lean4/lakefile.lean",
    "lean4/lean-toolchain",
    "lggr_iii_epk_gtla_overlay.md",
    "lggr_iii_epk_gtla_overlay.tex",
    "lggr_iii_epk_gtla_overlay.pdf",
    "lggr_iii_epk_gtla_overlay_change_log.md",
    "lggr_iii_epk_gtla_overlay_claim_ledger.md",
    "public_export/figure_1_one_record_six_roles.pdf",
    "public_export/figure_1_one_record_six_roles.png",
    "public_export/figure_2_finite_defects_and_cancellation.pdf",
    "public_export/figure_2_finite_defects_and_cancellation.png",
    "pyproject.toml",
    "scripts/build_deposit_zip.py",
    "scripts/build_lean_axiom_report.py",
    "scripts/build_paper_artifacts.py",
    "scripts/obstruction-preamble.tex",
    "scripts/regen_sha256sums.py",
    "uv.lock",
    "verify_deposit.py",
    "zenodo_metadata.json",
}
AXIOM_WHITELIST = frozenset({"propext", "Quot.sound", "Classical.choice"})
EXPECTED_AXIOM_REPORTS = 12
MINIMUM_TESTS = 60
CANONICAL_PREAMBLE_SHA256 = (
    "e2a8ac43c7abd8b971916d51e68f126798352d1bc0f2f05e3b2764c8176fb6dd"
)
AXIOM_REPORT_LINE = re.compile(
    r"^'LGGR3\.[^']+' (?:does not depend on any axioms|depends on axioms: .+)$"
)
PRODUCTION_MODULES = (
    "code/epk_gtla_overlay_core.py",
    "code/generate_figures.py",
    "code/run_notebook.py",
)
IDENTITY = {
    "Title": "Local Green, Global Red III",
    "Subtitle": "A finite evaluator overlay across six system roles",
    "Author": "Jeremy H. Carroll",
    "Date": "2026-10-15",
    "Version": "1.5.2",
    "License": "CC-BY-4.0",
}
HANDLE_FILES = (
    "lggr_iii_epk_gtla_overlay_claim_ledger.md",
    "docs/lean_claim_map.md",
    "docs/claim_code_map.yaml",
)


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validated_manifest_path(relative: str, number: int, root: Path) -> Path:
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
    current = root
    for part in pure.parts:
        current = current / part
        if current.is_symlink():
            unsafe = True
            break
    candidate = root.joinpath(*pure.parts)
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError:
        unsafe = True
    if unsafe:
        raise ValueError(
            f"manifest line {number} has unsafe path {relative!r}"
        )
    return candidate


def parse_manifest(
    path: Path = MANIFEST, root: Path = ROOT
) -> dict[str, str]:
    if not path.is_file():
        raise ValueError(f"manifest is missing: {path.name}")
    entries: dict[str, str] = {}
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        parts = raw.split(None, 1)
        if len(parts) != 2 or re.fullmatch(r"[0-9a-fA-F]{64}", parts[0]) is None:
            raise ValueError(f"malformed manifest line {number} in {path.name}: {raw!r}")
        relative = parts[1].strip().lstrip("*")
        _validated_manifest_path(relative, number, root)
        if relative.casefold() in {item.casefold() for item in entries}:
            raise ValueError(f"duplicate manifest path in {path.name}: {relative!r}")
        entries[relative] = parts[0].lower()
    return entries


def validate_public_path(relative: str) -> tuple[bool, str]:
    pure = PurePosixPath(relative)
    for part in pure.parts[:-1]:
        if part in IGNORED_DIR_NAMES or part.endswith(".egg-info"):
            return False, f"path contains excluded directory component {part!r}"
    if pure.parts and pure.parts[-1] in IGNORED_DIR_NAMES:
        return False, f"path names an excluded directory {pure.parts[-1]!r}"
    if (
        pure.name in IGNORED_FILE_NAMES
        or pure.name.startswith(".coverage")
        or pure.suffix in {".pyc", ".pyo", ".tmp"}
    ):
        return False, f"path names an excluded file {pure.name!r}"
    if pure.suffix == ".ipynb" or (pure.parts and pure.parts[0] == "jupyter_notebooks"):
        if relative not in PUBLIC_NOTEBOOK_PATHS:
            return False, f"unpermitted notebook path {relative!r}"
    if pure.parts and pure.parts[0] == "lean4":
        if relative not in PUBLIC_LEAN_PATHS:
            return False, f"unpermitted Lean path {relative!r}"
    return True, ""


def ignored(path: Path, root: Path) -> bool:
    relative = path.relative_to(root).as_posix()
    is_valid, _ = validate_public_path(relative)
    return not is_valid


def check_manifest_consistency(
    sums_entries: dict[str, str], manifest_entries: dict[str, str]
) -> list[str]:
    problems: list[str] = []
    if "MANIFEST.sha256" not in sums_entries:
        problems.append("SHA256SUMS is missing entry for MANIFEST.sha256")
    sums_without_manifest = {
        path: digest
        for path, digest in sums_entries.items()
        if path != "MANIFEST.sha256"
    }
    if sums_without_manifest != manifest_entries:
        missing_in_manifest = sorted(set(sums_without_manifest) - set(manifest_entries))
        extra_in_manifest = sorted(set(manifest_entries) - set(sums_without_manifest))
        mismatched_hashes = sorted(
            path
            for path in set(sums_without_manifest) & set(manifest_entries)
            if sums_without_manifest[path] != manifest_entries[path]
        )
        if missing_in_manifest:
            problems.append(
                f"MANIFEST.sha256 is missing entries present in SHA256SUMS: {missing_in_manifest}"
            )
        if extra_in_manifest:
            problems.append(
                f"MANIFEST.sha256 contains entries absent from SHA256SUMS: {extra_in_manifest}"
            )
        if mismatched_hashes:
            problems.append(
                f"MANIFEST.sha256 hash mismatch with SHA256SUMS on: {mismatched_hashes}"
            )
    return problems


def check_manifest(entries: dict[str, str], root: Path = ROOT) -> list[str]:
    problems: list[str] = []
    for relative, expected in sorted(entries.items()):
        path = root / relative
        if not path.is_file():
            problems.append(f"missing listed file: {relative}")
        elif path.is_symlink():
            problems.append(f"symbolic link is not allowed: {relative}")
        elif sha256_of(path) != expected:
            problems.append(f"hash mismatch: {relative}")
    for path in sorted(root.rglob("*")):
        if path.is_file() and not ignored(path, root):
            relative = path.relative_to(root).as_posix()
            if relative not in entries:
                problems.append(f"unlisted public file: {relative}")
    for relative in sorted(REQUIRED_FILES):
        if relative not in entries:
            problems.append(f"required file is not pinned: {relative}")
    return problems


def check_selection(entries: dict[str, str]) -> list[str]:
    notebooks = {
        path
        for path in entries
        if path.startswith("jupyter_notebooks/") or path.endswith(".ipynb")
    }
    lean_files = {
        path
        for path in entries
        if path.startswith("lean4/")
    }
    problems = []
    if notebooks != PUBLIC_NOTEBOOK_PATHS:
        problems.append(
            f"public notebook set is {sorted(notebooks)!r}, expected {sorted(PUBLIC_NOTEBOOK_PATHS)!r}"
        )
    if lean_files != PUBLIC_LEAN_PATHS:
        problems.append(
            f"public Lean set is {sorted(lean_files)!r}, expected {sorted(PUBLIC_LEAN_PATHS)!r}"
        )
    for path in sorted(entries):
        is_valid, reason = validate_public_path(path)
        if not is_valid:
            problems.append(f"manifest contains prohibited entry {path!r}: {reason}")
    return problems


def _flat(text: str) -> str:
    return " ".join(text.split())


def _metadata_text(value: object) -> str:
    if isinstance(value, dict):
        return " ".join(_metadata_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(_metadata_text(item) for item in value)
    return str(value)


def check_identity() -> list[str]:
    """Verify every identity field in Markdown, TeX, PDF text, and metadata."""

    problems: list[str] = []
    metadata = json.loads((ROOT / "zenodo_metadata.json").read_text(encoding="utf-8"))
    markdown = (ROOT / "lggr_iii_epk_gtla_overlay.md").read_text(encoding="utf-8")
    tex = (ROOT / "lggr_iii_epk_gtla_overlay.tex").read_text(encoding="utf-8")
    metadata_flat = _flat(_metadata_text(metadata))
    try:
        from pypdf import PdfReader

        reader = PdfReader(ROOT / "lggr_iii_epk_gtla_overlay.pdf")
        pdf_text = _flat("\n".join(page.extract_text() or "" for page in reader.pages))
        pdf_metadata = _flat(_metadata_text(dict(reader.metadata or {})))
    except (ImportError, OSError, ValueError) as error:
        return [f"PDF identity could not be read: {error}"]

    for field, value in IDENTITY.items():
        markdown_needle = f"**{field}:** {value}"
        if field in {"Title", "Subtitle"}:
            markdown_needle = value
        if markdown_needle not in markdown:
            problems.append(f"Markdown identity is missing {field}: {value}")
        if value not in tex:
            problems.append(f"TeX identity is missing {field}: {value}")
        if _flat(value) not in pdf_text:
            problems.append(f"PDF text identity is missing {field}: {value}")

    expected_title = f"{IDENTITY['Title']}: {IDENTITY['Subtitle']}"
    if metadata.get("title") != expected_title:
        problems.append("Zenodo title does not match the manuscript title and subtitle")
    if metadata.get("publication_date") != IDENTITY["Date"]:
        problems.append("Zenodo publication date does not match the identity block")
    if metadata.get("version") != IDENTITY["Version"]:
        problems.append("Zenodo version does not match the identity block")
    descriptions = (ROOT / "docs" / "descriptions.md").read_text(encoding="utf-8")
    primary = re.search(
        r"^## Primary description\s*\n\n```html\n(.*?)\n```$",
        descriptions,
        flags=re.MULTILINE | re.DOTALL,
    )
    secondary = re.search(
        r"^## Secondary description\s*\n\n```text\n(.*?)\n```$",
        descriptions,
        flags=re.MULTILINE | re.DOTALL,
    )
    if primary is None or secondary is None:
        problems.append("docs/descriptions.md lacks literal Primary/Secondary fences")
    elif metadata.get("description") != primary.group(1):
        problems.append("Zenodo description does not exactly match the Primary block")
    creators = metadata.get("creators", [])
    if not creators or creators[0].get("name") != "Carroll, Jeremy H.":
        problems.append("Zenodo creator does not match the identity block")

    for field, value in IDENTITY.items():
        if field in {"Title", "Subtitle", "Author"}:
            continue
        if f"{field}: {value}" not in pdf_metadata:
            problems.append(f"PDF metadata is missing {field}: {value}")
    if IDENTITY["Title"] not in pdf_metadata or IDENTITY["Author"] not in pdf_metadata:
        problems.append("PDF title/author metadata does not match the identity block")
    return problems


def lean_handles() -> tuple[str, ...]:
    handles: set[str] = set()
    for relative in HANDLE_FILES:
        text = (ROOT / relative).read_text(encoding="utf-8")
        handles.update(re.findall(r"\bLGGR3\.[A-Za-z_][A-Za-z0-9_]*\b", text))
    return tuple(sorted(handles))


def check_lean_handles_text() -> list[str]:
    core = (ROOT / "lean4" / "Core.lean").read_text(encoding="utf-8")
    declarations = set(
        re.findall(
            r"^(?:def|theorem|structure|inductive)\s+([A-Za-z_][A-Za-z0-9_]*)",
            core,
            flags=re.MULTILINE,
        )
    )
    return [
        f"public Lean handle is absent from Core.lean: {handle}"
        for handle in lean_handles()
        if handle.split(".", 1)[1] not in declarations
    ]


def check_claim_ir() -> list[str]:
    text = (ROOT / "docs" / "claim_ir.yaml").read_text(encoding="utf-8")
    ids = re.findall(
        r"^\s+- claim_id: (LGGR3-C\d{2})\s*$", text, flags=re.MULTILINE
    )
    expected = [f"LGGR3-C{number:02d}" for number in range(1, 16)]
    problems = []
    if ids != expected:
        problems.append(f"claim_ir ids are {ids!r}, expected {expected!r}")
    if "claim_count: 15" not in text:
        problems.append("claim_ir does not declare exactly 15 claims")
    classes = re.findall(
        r"^\s+mechanization_class: ([A-Z_]+)\s*$", text, flags=re.MULTILINE
    )
    expected_classes = (
        ["LEAN_FULL"] * 9
        + ["LEAN_PARTIAL"]
        + ["LEAN_FULL"] * 2
        + ["SCOPE_FENCE", "PYTHON_INSTANCE", "LITERATURE"]
    )
    if classes != expected_classes:
        problems.append(f"claim_ir mechanization classes are {classes!r}")
    return problems


def check_release_contract() -> list[str]:
    problems: list[str] = []
    preamble = ROOT / "scripts" / "obstruction-preamble.tex"
    if not preamble.is_file() or sha256_of(preamble) != CANONICAL_PREAMBLE_SHA256:
        problems.append("bundled preamble does not match the live canonical bytes")
    build_text = (ROOT / "scripts" / "build_paper_artifacts.py").read_text(
        encoding="utf-8"
    )
    lowered = build_text.lower()
    if (
        "max_pdflatex_passes" not in lowered
        or "rerun to get cross-references right" not in lowered
        or "converged" not in lowered
    ):
        problems.append(
            "paper build does not enforce auxiliary convergence and cross-reference checks"
        )
    for forbidden in ("xelatex", "lualatex", "--number-sections"):
        if forbidden in lowered:
            problems.append(f"paper build contains forbidden token: {forbidden}")
    if "audit_log(" not in build_text:
        problems.append("paper build lacks the layout-log guard")
    archive_text = (ROOT / "scripts" / "build_deposit_zip.py").read_text(
        encoding="utf-8"
    )
    if DATED_ARCHIVE_NAME not in archive_text:
        problems.append("archive builder does not enforce the dated release name")
    refs = (ROOT / "docs" / "references.md").read_text(encoding="utf-8")
    for forbidden in ("coda_atlas", "F004", "CODA GTLA", "omega_engine"):
        if forbidden.lower() in refs.lower():
            problems.append(f"public references contain internal dialect: {forbidden}")
    metadata = json.loads((ROOT / "zenodo_metadata.json").read_text(encoding="utf-8"))
    if any(str(keyword).strip().lower() == "coda" for keyword in metadata["keywords"]):
        problems.append("Zenodo keywords contain the internal CODA label")
    return problems


def check_axiom_inventory() -> list[str]:
    core = (ROOT / "lean4" / "Core.lean").read_text(encoding="utf-8")
    census = (ROOT / "lean4" / "check_axioms.lean").read_text(encoding="utf-8")
    theorems = set(re.findall(r"^theorem\s+([A-Za-z_][A-Za-z0-9_]*)", core, re.M))
    printed = set(re.findall(r"^#print axioms LGGR3\.([A-Za-z_][A-Za-z0-9_]*)", census, re.M))
    return [] if printed == theorems else [
        f"axiom census mismatch: missing={sorted(theorems - printed)!r}; "
        f"extra={sorted(printed - theorems)!r}"
    ]


def check_mutation_pairs() -> list[str]:
    text = (ROOT / "code" / "tests" / "test_invasive_injections.py").read_text(
        encoding="utf-8"
    )
    numbers = re.findall(r"^def test_mutation_(\d{2})_", text, flags=re.MULTILINE)
    expected = [f"{number:02d}" for number in range(1, 13)]
    return [] if numbers == expected else [f"paired mutation ids are {numbers!r}"]


def run_checked(
    command: list[str], cwd: Path, extra_env: dict[str, str] | None = None
) -> tuple[int, str]:
    environment = {
        **os.environ,
        "PYTHONDONTWRITEBYTECODE": "1",
        "MPLBACKEND": "Agg",
    }
    if extra_env:
        environment.update(extra_env)
    process = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env=environment,
    )
    return process.returncode, (process.stdout or "") + (process.stderr or "")


def run_tests() -> tuple[int, str, int, dict[str, tuple[float, float]]]:
    with tempfile.TemporaryDirectory(prefix="lggr3-pytest-") as temp:
        coverage_json = Path(temp) / "coverage.json"
        command = [
            sys.executable,
            "-m",
            "pytest",
            "-n",
            "4",
            "code/tests",
            "--basetemp",
            str(Path(temp) / "pytest"),
            "-p",
            "no:cacheprovider",
            "-p",
            "no:debugging",
            "-p",
            "no:asyncio",
            "--strict-config",
            "--strict-markers",
            "-W",
            "error",
            "-W",
            "ignore::coverage.exceptions.CoverageWarning",
            "-W",
            "ignore::DeprecationWarning",
            "--cov=epk_gtla_overlay_core",
            "--cov=generate_figures",
            "--cov=run_notebook",
            "--cov-branch",
            "--cov-report=term-missing",
            f"--cov-report=json:{coverage_json}",
            "--cov-fail-under=95",
            "-q",
        ]
        code, output = run_checked(
            command,
            ROOT,
            {
                "COVERAGE_FILE": str(Path(temp) / ".coverage"),
                "OPENBLAS_NUM_THREADS": "1",
                "OMP_NUM_THREADS": "1",
                "MKL_NUM_THREADS": "1",
            },
        )
        coverage_data = (
            json.loads(coverage_json.read_text(encoding="utf-8"))
            if coverage_json.is_file()
            else {"files": {}}
        )
    match = re.search(r"(\d+) passed(?:, [^\n]+)? in ", output)
    count = int(match.group(1)) if match else 0
    dirty_summary = re.search(r"\b(skipped|xfailed|xpassed|error|failed|warning)s?\b", output, re.I)
    module_coverage: dict[str, tuple[float, float]] = {}
    files = coverage_data.get("files", {})
    for required in PRODUCTION_MODULES:
        match_name = next(
            (
                name
                for name in files
                if name.replace("\\", "/").endswith(required)
            ),
            None,
        )
        if match_name is None:
            module_coverage[required] = (0.0, 0.0)
            continue
        summary = files[match_name]["summary"]
        statements = int(summary.get("num_statements", 0))
        covered_lines = int(summary.get("covered_lines", 0))
        line_percent = (
            100.0 if statements == 0 else 100.0 * covered_lines / statements
        )
        branches = int(summary.get("num_branches", 0))
        covered = int(summary.get("covered_branches", 0))
        branch_percent = 100.0 if branches == 0 else 100.0 * covered / branches
        module_coverage[required] = (line_percent, branch_percent)
    coverage_failed = not coverage_meets_threshold(module_coverage)
    if code != 0 or count < MINIMUM_TESTS or dirty_summary or coverage_failed:
        return 1, output, count, module_coverage
    return 0, output, count, module_coverage


def coverage_meets_threshold(
    module_coverage: dict[str, tuple[float, float]], minimum: float = 95.0
) -> bool:
    """Require statement and branch coverage independently for every module."""

    return bool(module_coverage) and all(
        line >= minimum and branch >= minimum
        for line, branch in module_coverage.values()
    )


def run_artifact_check() -> tuple[int, str]:
    return run_checked(
        [sys.executable, "scripts/build_paper_artifacts.py", "--check"],
        ROOT,
    )


def run_archive_check() -> tuple[int, str, str]:
    with tempfile.TemporaryDirectory(prefix="lggr3-archive-") as temp:
        first = Path(temp) / "first.zip"
        second = Path(temp) / "second.zip"
        outputs = []
        for destination in (first, second):
            code, output = run_checked(
                [
                    sys.executable,
                    "scripts/build_deposit_zip.py",
                    "--out",
                    str(destination),
                ],
                ROOT,
            )
            outputs.append(output)
            if code:
                return code, "".join(outputs), ""
        first_hash = sha256_of(first)
        second_hash = sha256_of(second)
        if first_hash != second_hash:
            return 1, "".join(outputs) + "\nerror: archive builds were not deterministic", ""

        # Extract and verify all archive members against MANIFEST.sha256
        extract_dir = Path(temp) / "extracted"
        extract_dir.mkdir()
        with zipfile.ZipFile(first, "r") as zf:
            zf.extractall(extract_dir)
        manifest_entries = parse_manifest(ROOT / "MANIFEST.sha256", ROOT)
        for rel_path, expected_hash in manifest_entries.items():
            extracted_file = extract_dir / ROOT.name / rel_path
            if not extracted_file.is_file():
                return 1, f"error: extracted archive missing member {rel_path}", ""
            actual_hash = sha256_of(extracted_file)
            if actual_hash != expected_hash:
                return 1, f"error: extracted member {rel_path} hash mismatch: {actual_hash} != {expected_hash}", ""

        # Verify upload-named artifacts are bound to canonical artifacts
        canonical_pdf = ROOT / "lggr_iii_epk_gtla_overlay.pdf"
        upload_pdf = ROOT / "0_lggr_iii_epk_gtla_overlay.pdf"
        if upload_pdf.is_file():
            if sha256_of(upload_pdf) != sha256_of(canonical_pdf):
                return 1, "error: 0_lggr_iii_epk_gtla_overlay.pdf differs from canonical PDF", ""

        dated_zip = ROOT / DATED_ARCHIVE_NAME
        sibling_dated_zip = ROOT.parent / DATED_ARCHIVE_NAME
        target_dated_zip = dated_zip if dated_zip.is_file() else (sibling_dated_zip if sibling_dated_zip.is_file() else None)
        if target_dated_zip is not None:
            if sha256_of(target_dated_zip) != first_hash:
                return 1, f"error: {target_dated_zip.name} does not match fresh archive build", ""

        upload_zip = ROOT / "1_lggr_iii_epk_gtla_overlay.zip"
        if upload_zip.is_file():
            if sha256_of(upload_zip) != first_hash:
                return 1, "error: 1_lggr_iii_epk_gtla_overlay.zip does not match fresh archive build", ""

        for obsolete_name in ("lggr_iii_epk_gtla_overlay_2026-09-18.zip",):
            if (ROOT / obsolete_name).is_file() or (ROOT.parent / obsolete_name).is_file():
                return 1, f"error: obsolete archive {obsolete_name} must be removed", ""


        return 0, "".join(outputs), first_hash



def run_lean() -> tuple[list[str], str]:
    problems: list[str] = []
    output = ""
    source = ROOT / "lean4"
    with tempfile.TemporaryDirectory(prefix="lggr3-lean-") as temp:
        lean = Path(temp) / "lean4"
        lean.mkdir()
        for name in sorted(PUBLIC_LEAN_FILES):
            shutil.copy2(source / name, lean / name)
        code, build_output = run_checked(["lake", "build"], lean)
        output += build_output
        if code != 0:
            return ["lake build failed"], output
        code, census_output = run_checked(
            ["lake", "env", "lean", "check_axioms.lean"], lean
        )
        output += census_output
        if code != 0:
            return ["axiom census failed"], output
        resolver = lean / "resolve_public_handles.lean"
        resolver.write_text(
            "import Core\n"
            + "\n".join(f"#check {handle}" for handle in lean_handles())
            + "\n",
            encoding="utf-8",
            newline="\n",
        )
        code, resolver_output = run_checked(
            ["lake", "env", "lean", resolver.name], lean
        )
        output += resolver_output
        if code != 0:
            return ["public Lean handle resolution failed"], output

    reports = [line for line in output.splitlines() if AXIOM_REPORT_LINE.fullmatch(line)]
    if len(reports) != EXPECTED_AXIOM_REPORTS:
        problems.append(
            f"expected {EXPECTED_AXIOM_REPORTS} axiom reports, found {len(reports)}"
        )
    for line in reports:
        if "does not depend on any axioms" in line:
            continue
        match = re.search(r"depends on axioms:\s*\[([^\]]*)\]", line)
        if match is None:
            problems.append(f"unparsed axiom report: {line}")
            continue
        for name in (part.strip() for part in match.group(1).split(",")):
            if name and name not in AXIOM_WHITELIST:
                problems.append(f"axiom outside whitelist: {name}")
    toolchain = (source / "lean-toolchain").read_text(encoding="utf-8").strip()
    expected_report = (
        "Local Green, Global Red III — theorem-level Lean axiom report\n"
        "Date: 2026-10-15\n"
        f"Toolchain: {toolchain}\n"
        "Default build target: LGGR3 (Core.lean)\n"
        "Census command: lake env lean check_axioms.lean\n"
        f"Theorem reports: {EXPECTED_AXIOM_REPORTS}\n\n"
        + "\n".join(reports)
        + "\n"
    )
    report_path = source / "AXIOM_REPORT.txt"
    if not report_path.is_file() or report_path.read_text(encoding="utf-8") != expected_report:
        problems.append("lean4/AXIOM_REPORT.txt does not match the current census")
    core = (source / "Core.lean").read_text(encoding="utf-8")
    for token in ("sorry", "admit"):
        if re.search(rf"\b{token}\b", core):
            problems.append(f"Lean source contains {token}")
    return problems, output


def main(argv: list[str]) -> int:
    try:
        entries = parse_manifest(MANIFEST, ROOT)
        manifest_entries = parse_manifest(ROOT / "MANIFEST.sha256", ROOT)
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    problems = (
        check_manifest(entries)
        + check_manifest_consistency(entries, manifest_entries)
        + check_selection(entries)
        + check_identity()
        + check_lean_handles_text()
        + check_claim_ir()
        + check_release_contract()
        + check_axiom_inventory()
        + check_mutation_pairs()
    )
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        return 1
    print(f"files: {len(entries)} hashes and exact public selection verified")

    print(f"claims: exactly 15 claim-IR rows; {len(lean_handles())} public Lean handles resolved textually")

    code, output, count, module_coverage = run_tests()
    if code:
        print(output, file=sys.stderr)
        for module, (lines, branches) in module_coverage.items():
            print(
                f"coverage {module}: lines {lines:.2f}%, branches {branches:.2f}%",
                file=sys.stderr,
            )
        print(f"FAIL: Python gate did not finish cleanly ({count} passes parsed)", file=sys.stderr)
        return 1
    print(f"python: {count} tests passed")
    for module, (lines, branches) in module_coverage.items():
        print(f"coverage: {module}: lines {lines:.2f}%, branches {branches:.2f}%")

    code, output = run_artifact_check()
    if code:
        print(output, file=sys.stderr)
        print("FAIL: Markdown, TeX, and PDF do not reproduce", file=sys.stderr)
        return 1
    print("artifacts: Markdown source reproduces the committed TeX and PDF")

    code, output, archive_hash = run_archive_check()
    if code:
        print(output, file=sys.stderr)
        print("FAIL: two public archive builds were not byte-identical", file=sys.stderr)
        return 1
    print(f"archive: two builds matched SHA-256 {archive_hash}")

    if "--lean" in argv:
        lean_problems, lean_output = run_lean()
        if lean_problems:
            print(lean_output, file=sys.stderr)
            for problem in lean_problems:
                print(f"FAIL: {problem}", file=sys.stderr)
            return 1
        print(
            f"lean: {EXPECTED_AXIOM_REPORTS} reports, all axiom-free or within "
            f"{sorted(AXIOM_WHITELIST)}"
        )

    print("verified: LGGR III public deposit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
