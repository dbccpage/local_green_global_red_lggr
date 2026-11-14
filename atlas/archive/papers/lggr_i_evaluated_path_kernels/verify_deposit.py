#!/usr/bin/env python3
"""Verify Paper I's pinned release surface, executable tests, and proof bundle.

A successful run establishes reproducibility of the finite package.  It does
not prove the empirical hypotheses or authorize deployment.
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
PAPER_STEM = "lggr_i_evaluated_path_kernels"
RELEASE_DATE = "2026-10-15"
ARCHIVE_NAME = f"{PAPER_STEM}_{RELEASE_DATE}.zip"
MANIFEST = ROOT / "SHA256SUMS"
AXIOM_REPORT = Path("lean4") / "axiom_report.txt"
LEAN_ROOT_MODULE = "lggr_i_evaluated_path_kernels.lean"
EXPECTED_AXIOM_REPORTS = 44
EXPECTED_SHARED_PREAMBLE_SHA256 = (
    "e2a8ac43c7abd8b971916d51e68f126798352d1bc0f2f05e3b2764c8176fb6dd"
)
CANONICAL_PREAMBLE_REL = (
    Path("coda_university")
    / "_kits"
    / "obstruction_paper_kit"
    / "obstruction_preamble.tex"
)
COVERAGE_THRESHOLD = 95.0
PRODUCTION_MODULES = (
    "epk_core.py",
    "generate_figures.py",
    "run_notebook.py",
    "carrier_kernel_census.py",
)
AXIOM_WHITELIST = frozenset({"propext", "Classical.choice", "Quot.sound"})

IGNORED_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".lake",
    ".venv",
    "venv",
    "b",
    "scratch",
    ".ipynb_checkpoints",
    ".mypy_cache",
    ".ruff_cache",
    ".git",
    "dev_rips",
    "rt",
    "dist",
    "build",
    "htmlcov",
}
IGNORED_FILE_NAMES = {
    "SHA256SUMS",
    ".coverage",
    "DEPOSIT_CHECKLIST.md",
    ARCHIVE_NAME,
    "0_lggr_i_evaluated_path_kernels.pdf",
    f"1_{ARCHIVE_NAME}",
}
PUBLIC_NOTEBOOKS = {
    "00_how_to_read_this_series.ipynb",
    "06_reviewer_reference_verification.ipynb",
}
BUILD_DIAGNOSTIC_MARKERS = (
    "Missing character:",
    "Unable to load picture or PDF file",
    "ignored error:",
    "Overfull \\hbox",
    "Overfull \\vbox",
    "Float too large for page",
    "Dimension too large",
)
REQUIRED_FILES = (
    "code/epk_core.py",
    "code/generate_figures.py",
    "code/run_notebook.py",
    "code/tests/test_epk_core.py",
    "code/tests/test_invasive_injections.py",
    "code/tests/test_notebooks.py",
    "code/tests/test_release_surface.py",
    "lggr_i_evaluated_path_kernels.md",
    "lggr_i_evaluated_path_kernels_claim_ledger.md",
    "lggr_i_evaluated_path_kernels.tex",
    "lggr_i_evaluated_path_kernels.pdf",
    "jupyter_notebooks/00_how_to_read_this_series.ipynb",
    "jupyter_notebooks/06_reviewer_reference_verification.ipynb",
    "docs/claim_ir.yaml",
    "docs/descriptions.md",
    "docs/lean_claim_map.md",
    "lean4/axiom_report.txt",
    "lean4/lakefile.lean",
    "lean4/lean-toolchain",
    "scripts/build_deposit_zip.py",
    "scripts/build_paper_artifacts.py",
    "scripts/capture_axiom_report.py",
    "scripts/obstruction-preamble.tex",
    "LICENSE",
    "LICENSE-CODE",
    "README.md",
    "zenodo_metadata.json",
)


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
    if candidate.is_symlink():
        unsafe = True
    if unsafe:
        raise SystemExit(
            f"FAIL: SHA256SUMS line {lineno} has unsafe path {relative!r}"
        )
    return candidate


def parse_manifest(
    manifest_path: Path = MANIFEST, root_dir: Path = ROOT
) -> dict[str, str]:
    if not manifest_path.is_file():
        raise SystemExit("FAIL: SHA256SUMS is missing")
    entries: dict[str, str] = {}
    for lineno, raw in enumerate(
        manifest_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or re.fullmatch(r"[0-9a-fA-F]{64}", parts[0]) is None:
            raise SystemExit(
                f"FAIL: SHA256SUMS line {lineno} is malformed: {raw!r}"
            )
        digest, relative = parts[0].lower(), parts[1].strip().lstrip("*")
        _validated_manifest_path(relative, lineno, root_dir)
        if relative.casefold() in {path.casefold() for path in entries}:
            raise SystemExit(f"FAIL: SHA256SUMS lists {relative} more than once")
        entries[relative] = digest
    return entries


def check_hashes(
    entries: dict[str, str], root_dir: Path = ROOT
) -> list[str]:
    problems: list[str] = []
    for relative, digest in sorted(entries.items()):
        path = root_dir / relative
        if not path.is_file():
            problems.append(f"missing file listed in SHA256SUMS: {relative}")
        elif sha256_of(path) != digest:
            problems.append(f"hash mismatch for {relative}")
    return problems


def sweep_unlisted(
    entries: dict[str, str], root_dir: Path = ROOT
) -> list[str]:
    problems: list[str] = []
    for path in sorted(root_dir.rglob("*")):
        if not path.is_file():
            continue
        parts = path.relative_to(root_dir).parts
        if any(part in IGNORED_DIR_NAMES for part in parts[:-1]):
            continue
        if any(part.endswith(".egg-info") for part in parts[:-1]):
            continue
        relative = "/".join(parts)
        if (
            parts[0] == "jupyter_notebooks"
            and path.suffix == ".ipynb"
            and path.name not in PUBLIC_NOTEBOOKS
        ):
            continue
        if relative in IGNORED_FILE_NAMES or path.name in IGNORED_FILE_NAMES:
            continue
        if relative not in entries:
            problems.append(f"file present but not listed in SHA256SUMS: {relative}")
    return problems


def check_required(
    entries: dict[str, str], root_dir: Path = ROOT
) -> list[str]:
    problems: list[str] = []
    for relative in REQUIRED_FILES:
        if relative not in entries:
            problems.append(f"required file not pinned in SHA256SUMS: {relative}")
        elif not (root_dir / relative).is_file():
            problems.append(f"required file missing on disk: {relative}")
    return problems


def find_canonical_preamble(root_dir: Path) -> Path | None:
    for ancestor in (root_dir, *root_dir.parents):
        candidate = ancestor / CANONICAL_PREAMBLE_REL
        if candidate.is_file():
            return candidate
    return None


def _fenced_block(text: str, heading: str, language: str) -> str | None:
    match = re.search(
        rf"^## {re.escape(heading)}\s+.*?^```{language}\s*$\n"
        rf"(.*?)^```\s*$",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group(1).strip() if match else None


def _extract_abstract(text: str) -> str:
    match = re.search(
        rf"(?ms)^## Abstract\s*\n(.*?)(?=^## |\Z)", text
    )
    return match.group(1).strip() if match else ""


def check_description_contract(root_dir: Path) -> list[str]:
    problems: list[str] = []
    desc_path = root_dir / "docs" / "descriptions.md"
    if not desc_path.is_file():
        return ["docs/descriptions.md is missing"]
    descriptions = desc_path.read_text(encoding="utf-8")
    if "<p>" in descriptions or "</p>" in descriptions:
        problems.append("docs/descriptions.md contains HTML tags")
    if re.search(r"(?:\$[^$\n]+\$|\$\$[\s\S]+?\$\$|\\\(|\\\)|\\\[|\\\])", descriptions):
        problems.append("docs/descriptions.md contains raw TeX math markup")
    abstract = _extract_abstract(descriptions)
    if not abstract:
        problems.append("docs/descriptions.md lacks an Abstract section")
    metadata = json.loads(
        (root_dir / "zenodo_metadata.json").read_text(encoding="utf-8")
    )
    if abstract and metadata.get("description") != abstract:
        problems.append(
            "zenodo_metadata.json.description does not exactly match Abstract"
        )
    return problems


def check_claim_ir(root_dir: Path) -> list[str]:
    problems: list[str] = []
    claim_ir_path = root_dir / "docs" / "claim_ir.yaml"
    try:
        data = json.loads(claim_ir_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"docs/claim_ir.yaml is not valid JSON-compatible YAML: {error}"]
    rows = data.get("claims") if isinstance(data, dict) else None
    if not isinstance(rows, list) or not rows:
        return ["docs/claim_ir.yaml has no claims list"]

    ids: list[str] = []
    lean_count = 0
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            problems.append(f"ClaimIR row {index} is not a mapping")
            continue
        claim_id = str(row.get("claim_id") or "").strip()
        mechanism = str(row.get("mechanization_class") or "").strip()
        if not claim_id:
            problems.append(f"ClaimIR row {index} lacks claim_id")
        if not mechanism:
            problems.append(f"ClaimIR row {index} lacks mechanization_class")
        if claim_id:
            ids.append(claim_id)
        if "LEAN" in mechanism.upper() and "TOY" not in mechanism.upper():
            lean_count += 1
    if len(ids) != len(set(ids)):
        problems.append("ClaimIR claim_id values are not unique")
    mapping = (root_dir / "docs" / "claim_code_map.yaml").read_text(
        encoding="utf-8"
    )
    mapped_ids = re.findall(r'^  - id: "([^"]+)"', mapping, flags=re.MULTILINE)
    if set(ids) != set(mapped_ids):
        problems.append("ClaimIR and claim_code_map claim ID sets differ")
    if lean_count == 0:
        problems.append("ClaimIR exposes no non-toy Lean mechanization rows")
    return problems


def check_release_contracts(
    entries: dict[str, str], root_dir: Path = ROOT
) -> list[str]:
    problems: list[str] = []
    notebooks = {
        PurePosixPath(relative).name
        for relative in entries
        if relative.startswith("jupyter_notebooks/")
        and relative.endswith(".ipynb")
    }
    if notebooks != PUBLIC_NOTEBOOKS:
        problems.append(
            f"public notebook set mismatch: expected {sorted(PUBLIC_NOTEBOOKS)}, "
            f"got {sorted(notebooks)}"
        )

    bundled = root_dir / "scripts" / "obstruction-preamble.tex"
    if not bundled.is_file():
        problems.append("bundled obstruction preamble is missing")
    elif sha256_of(bundled) != EXPECTED_SHARED_PREAMBLE_SHA256:
        problems.append("bundled obstruction preamble has the wrong canonical hash")
    canonical = find_canonical_preamble(root_dir)
    if canonical is not None:
        if sha256_of(canonical) != EXPECTED_SHARED_PREAMBLE_SHA256:
            problems.append("live canonical obstruction preamble has the wrong hash")
        elif bundled.is_file() and canonical.read_bytes() != bundled.read_bytes():
            problems.append("bundled preamble differs from the live canonical kit")

    tex = root_dir / f"{PAPER_STEM}.tex"
    if bundled.is_file() and tex.is_file():
        preamble_text = bundled.read_text(encoding="utf-8").strip()
        tex_text = tex.read_text(encoding="utf-8")
        if preamble_text not in tex_text:
            problems.append("generated TeX does not embed the canonical preamble")
        if "\\pdftrailerid{}" not in tex_text:
            problems.append("generated TeX lacks the deterministic trailer-ID guard")

    producer = root_dir / "scripts" / "build_paper_artifacts.py"
    if producer.is_file():
        source = producer.read_text(encoding="utf-8").casefold()
        if "pdflatexruns = 2" not in source.replace("_", ""):
            # The exact spelling below is the accepted source form.
            if "pdflatex_runs = 2" not in source:
                problems.append("paper builder does not bind exactly two pdfLaTeX passes")
        for forbidden in (
            'need("xelatex")',
            'need("lualatex")',
            '"--number-sections"',
            '"--pdf-engine"',
        ):
            if forbidden in source:
                problems.append(f"paper builder contains forbidden option {forbidden}")

    archive_builder = root_dir / "scripts" / "build_deposit_zip.py"
    if archive_builder.is_file():
        source = archive_builder.read_text(encoding="utf-8")
        if f'RELEASE_DATE = "{RELEASE_DATE}"' not in source:
            problems.append("archive builder does not bind the release date")
        if 'ARCHIVE_NAME = f"{ROOT.name}_{RELEASE_DATE}.zip"' not in source:
            problems.append("archive builder does not use the required dated name")

    problems.extend(check_description_contract(root_dir))
    problems.extend(check_claim_ir(root_dir))
    return problems


def pytest_summary(output: str) -> str:
    lines = [line for line in output.splitlines() if line.strip()]
    for line in reversed(lines):
        if re.search(r"\b\d+ passed\b", line):
            return line
    return lines[-1] if lines else "(no pytest output)"


def coverage_counts(
    report: dict[str, object],
) -> tuple[dict[str, tuple[int, int, int, int]], list[str]]:
    files = report.get("files")
    if not isinstance(files, dict):
        return {}, ["coverage JSON has no files mapping"]
    counts: dict[str, tuple[int, int, int, int]] = {}
    problems: list[str] = []
    for module_name in PRODUCTION_MODULES:
        matches = [
            value
            for key, value in files.items()
            if PurePosixPath(str(key).replace("\\", "/")).name == module_name
        ]
        if len(matches) != 1 or not isinstance(matches[0], dict):
            problems.append(
                f"coverage JSON has {len(matches)} entries for {module_name}; expected one"
            )
            continue
        summary = matches[0].get("summary")
        if not isinstance(summary, dict):
            problems.append(f"coverage JSON lacks a summary for {module_name}")
            continue
        statements = int(summary.get("num_statements", 0))
        covered_lines = int(summary.get("covered_lines", 0))
        branches = int(summary.get("num_branches", 0))
        covered_branches = int(summary.get("covered_branches", 0))
        counts[module_name] = (
            covered_lines,
            statements,
            covered_branches,
            branches,
        )
        line_rate = 100.0 if statements == 0 else 100.0 * covered_lines / statements
        branch_rate = 100.0 if branches == 0 else 100.0 * covered_branches / branches
        if line_rate < COVERAGE_THRESHOLD:
            problems.append(
                f"{module_name} line coverage {line_rate:.4f}% is below "
                f"{COVERAGE_THRESHOLD:.4f}%"
            )
        if branch_rate < COVERAGE_THRESHOLD:
            problems.append(
                f"{module_name} branch coverage {branch_rate:.4f}% is below "
                f"{COVERAGE_THRESHOLD:.4f}%"
            )

    if counts:
        covered_lines = sum(item[0] for item in counts.values())
        statements = sum(item[1] for item in counts.values())
        covered_branches = sum(item[2] for item in counts.values())
        branches = sum(item[3] for item in counts.values())
        line_rate = 100.0 * covered_lines / statements
        branch_rate = 100.0 * covered_branches / branches
        if line_rate < COVERAGE_THRESHOLD:
            problems.append(
                f"aggregate line coverage {covered_lines}/{statements} = "
                f"{line_rate:.4f}% is below {COVERAGE_THRESHOLD:.4f}%"
            )
        if branch_rate < COVERAGE_THRESHOLD:
            problems.append(
                f"aggregate branch coverage {covered_branches}/{branches} = "
                f"{branch_rate:.4f}% is below {COVERAGE_THRESHOLD:.4f}%"
            )
    return counts, problems


def run_tests(
    root_dir: Path = ROOT,
) -> tuple[int, str, dict[str, tuple[int, int, int, int]], list[str]]:
    with tempfile.TemporaryDirectory(prefix="lggr-i-pytest-") as raw_tmp:
        temporary = Path(raw_tmp)
        coverage_json = temporary / "coverage.json"
        environment = dict(os.environ)
        environment["COVERAGE_FILE"] = str(temporary / ".coverage")
        environment["COVERAGE_CORE"] = "pytrace"
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "-ra",
                "-n",
                "8",
                "--dist=loadgroup",
                "-o",
                "addopts=",
                "-p",
                "no:cacheprovider",
                "--no-header",
                "--basetemp",
                str(temporary / "pytest"),
                "--cov=epk_core",
                "--cov=generate_figures",
                "--cov=run_notebook",
                "--cov=carrier_kernel_census",
                "--cov-branch",
                "--cov-report=term",
                f"--cov-report=json:{coverage_json}",
                "--cov-fail-under=0",
            ],
            cwd=str(root_dir),
            capture_output=True,
            text=True,
            timeout=1200,
            env=environment,
            check=False,
        )
        output = (process.stdout or "") + (process.stderr or "")
        summary = pytest_summary(output)
        if process.returncode:
            print(output, file=sys.stderr)
            return process.returncode, summary, {}, ["pytest failed"]
        if not coverage_json.is_file():
            return 1, summary, {}, ["pytest did not emit coverage JSON"]
        try:
            report = json.loads(coverage_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            return 1, summary, {}, [f"coverage JSON is invalid: {error}"]
        counts, problems = coverage_counts(report)
        return (1 if problems else 0), summary, counts, problems


def _group_axiom_reports(transcript: str) -> list[str]:
    lines = transcript.splitlines()
    reports: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if "does not depend on any axioms" in line:
            reports.append(line.strip())
        elif "depends on axioms:" in line:
            chunks = [line.strip()]
            tail = line.partition("depends on axioms:")[2]
            while "]" not in tail and index + 1 < len(lines):
                index += 1
                continuation = lines[index].strip()
                chunks.append(continuation)
                tail += " " + continuation
            reports.append(" ".join(chunks))
        index += 1
    return reports


def _normalized(text: str) -> str:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    return "\n".join(line.rstrip() for line in lines).strip() + "\n"


def render_axiom_report(lean_version: str, reports: list[str]) -> str:
    body = "\n".join(reports)
    return (
        "Local Green, Global Red I — theorem-level Lean axiom report\n"
        f"Date: {RELEASE_DATE}\n"
        f"Toolchain: {lean_version.strip()}\n"
        "Build command: lake build\n"
        f"Census command: lake env lean {LEAN_ROOT_MODULE}\n"
        f"Axiom report count: {len(reports)}\n"
        f"Allowed dependencies: {', '.join(sorted(AXIOM_WHITELIST))}\n\n"
        f"{body}\n"
    )


def capture_axiom_report(
    root_dir: Path = ROOT,
) -> tuple[str, list[str], list[str]]:
    problems: list[str] = []
    lean_dir = root_dir / "lean4"
    for source in sorted(lean_dir.glob("*.lean")):
        if re.search(r"\b(?:sorry|admit)\b", source.read_text(encoding="utf-8")):
            problems.append(f"placeholder proof token in {source.name}")
    if problems:
        return "", [], problems

    ignored = shutil.ignore_patterns(
        ".lake", "b", "__pycache__", ".pytest_cache", AXIOM_REPORT.name
    )
    with tempfile.TemporaryDirectory(prefix="lggr-i-lean-") as raw_tmp:
        replay = Path(raw_tmp) / "lean4"
        shutil.copytree(lean_dir, replay, ignore=ignored)
        version = subprocess.run(
            ["lake", "env", "lean", "--version"],
            cwd=replay,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        if version.returncode:
            return "", [], ["Lean version probe failed"]
        build = subprocess.run(
            ["lake", "build"],
            cwd=replay,
            capture_output=True,
            text=True,
            timeout=1800,
            check=False,
        )
        if build.returncode:
            print(build.stdout + build.stderr, file=sys.stderr)
            return "", [], ["lake build failed in the short-path replay"]
        census = subprocess.run(
            ["lake", "env", "lean", LEAN_ROOT_MODULE],
            cwd=replay,
            capture_output=True,
            text=True,
            timeout=1800,
            check=False,
        )
        if census.returncode:
            print(census.stdout + census.stderr, file=sys.stderr)
            return "", [], ["theorem-level axiom census failed to elaborate"]
        reports = _group_axiom_reports(census.stdout + census.stderr)

    if len(reports) != EXPECTED_AXIOM_REPORTS:
        problems.append(
            f"expected {EXPECTED_AXIOM_REPORTS} axiom reports, got {len(reports)}"
        )
    for report in reports:
        if "does not depend on any axioms" in report:
            continue
        match = re.search(r"depends on axioms:\s*\[([^]]*)]", report)
        if match is None:
            problems.append(f"could not parse axiom report: {report}")
            continue
        for name in (item.strip() for item in match.group(1).split(",")):
            if name not in AXIOM_WHITELIST:
                problems.append(f"axiom outside whitelist: {name} in {report}")
    if problems:
        return "", reports, problems
    return render_axiom_report(_normalized(version.stdout + version.stderr), reports), reports, []


def run_lean(root_dir: Path = ROOT) -> tuple[list[str], int]:
    rendered, reports, problems = capture_axiom_report(root_dir)
    report_path = root_dir / AXIOM_REPORT
    if not report_path.is_file():
        problems.append(f"bundled axiom report is missing: {AXIOM_REPORT.as_posix()}")
    elif rendered and report_path.read_text(encoding="utf-8") != rendered:
        problems.append("bundled axiom report is stale or non-deterministic")
    if not problems:
        print(
            f"lean: build clean; bundled report matches {len(reports)} theorem "
            f"reports within {sorted(AXIOM_WHITELIST)}"
        )
    return problems, len(reports)


def check_artifact_reproducibility(root_dir: Path = ROOT) -> list[str]:
    problems: list[str] = []
    script = root_dir / "scripts" / "build_paper_artifacts.py"
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory(prefix="lggr-i-artifacts-") as raw_tmp:
        outputs: list[Path] = []
        for label in ("first", "second"):
            destination = Path(raw_tmp) / label
            process = subprocess.run(
                [sys.executable, str(script), "--output-dir", str(destination)],
                cwd=root_dir,
                capture_output=True,
                text=True,
                timeout=1800,
                env=environment,
                check=False,
            )
            if process.returncode:
                print(process.stdout + process.stderr, file=sys.stderr)
                return [f"artifact producer failed on the {label} run"]
            outputs.append(destination)

        for name in (f"{PAPER_STEM}.tex", f"{PAPER_STEM}.pdf"):
            first = outputs[0] / name
            second = outputs[1] / name
            committed = root_dir / name
            if first.read_bytes() != second.read_bytes():
                problems.append(f"two clean builds produced different {name} bytes")
            if first.read_bytes() != committed.read_bytes():
                problems.append(f"clean build does not reproduce committed {name}")

        log_name = f"{PAPER_STEM}-{RELEASE_DATE}-pdflatex.log"
        for destination in outputs:
            log_text = (destination / log_name).read_text(
                encoding="utf-8", errors="replace"
            )
            engine_banner = next(
                (
                    line
                    for line in log_text.splitlines()
                    if line.startswith("This is ")
                ),
                "",
            )
            if not engine_banner.startswith("This is pdfTeX"):
                problems.append(
                    "build log engine banner is not pdfTeX/pdfLaTeX: "
                    f"{engine_banner or '(missing)'}"
                )
            for marker in BUILD_DIAGNOSTIC_MARKERS:
                if marker in log_text:
                    problems.append(f"build log contains release diagnostic: {marker}")
    if not problems:
        print(
            "artifacts: two canonical-preamble pdfLaTeX builds reproduced "
            "committed TeX/PDF; layout logs are clean"
        )
    return problems


def check_archive_reproducibility(
    entries: dict[str, str], root_dir: Path = ROOT
) -> list[str]:
    problems: list[str] = []
    script = root_dir / "scripts" / "build_deposit_zip.py"
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory(prefix="lggr-i-archive-") as raw_tmp:
        archives = [Path(raw_tmp) / "first.zip", Path(raw_tmp) / "second.zip"]
        for archive in archives:
            process = subprocess.run(
                [sys.executable, str(script), "--out", str(archive)],
                cwd=root_dir,
                capture_output=True,
                text=True,
                timeout=300,
                env=environment,
                check=False,
            )
            if process.returncode:
                print(process.stdout + process.stderr, file=sys.stderr)
                return ["archive producer failed"]
        if archives[0].read_bytes() != archives[1].read_bytes():
            problems.append("two archive builds produced different bytes")

        committed = root_dir / ARCHIVE_NAME
        if committed.is_file() and committed.read_bytes() != archives[0].read_bytes():
            problems.append("clean archive build does not reproduce committed archive")

        prefix = root_dir.name
        expected = {f"{prefix}/{relative}" for relative in entries}
        expected.add(f"{prefix}/SHA256SUMS")
        with zipfile.ZipFile(archives[0]) as handle:
            names = handle.namelist()
            if len(names) != len(set(names)):
                problems.append("archive has duplicate members")
            if set(names) != expected:
                problems.append("archive member set differs from the pinned public set")
            for info in handle.infolist():
                if info.date_time != (2026, 10, 15, 12, 0, 0):
                    problems.append(f"archive timestamp drift for {info.filename}")
                    break
    if not problems:
        print(
            f"archive: two builds matched; {len(entries) + 1} members under "
            f"{root_dir.name}/ with fixed timestamps"
        )
    return problems


def main(argv: list[str]) -> int:
    entries = parse_manifest()
    problems = (
        check_hashes(entries)
        + sweep_unlisted(entries)
        + check_required(entries)
        + check_release_contracts(entries)
    )
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        print(f"verification FAILED: {len(problems)} package problem(s)")
        return 1
    print(f"files: all {len(entries)} pinned members verified")

    collected = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-q",
            "-o",
            "addopts=",
            "-p",
            "no:cacheprovider",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    match = re.search(r"(\d+) tests collected", collected.stdout + collected.stderr)
    if match is None:
        print("verification FAILED: could not collect tests", file=sys.stderr)
        return 1
    expected_tests = int(match.group(1))

    return_code, summary, counts, coverage_problems = run_tests()
    if return_code or coverage_problems:
        for problem in coverage_problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        print(f"verification FAILED: test or coverage gate failed -- {summary}")
        return 1
    if any(token in summary for token in ("skipped", "xfailed", "xpassed", "error")):
        print(f"verification FAILED: suite was not clean -- {summary}", file=sys.stderr)
        return 1
    if f"{expected_tests} passed" not in summary:
        print(
            f"verification FAILED: expected {expected_tests} passing tests -- {summary}",
            file=sys.stderr,
        )
        return 1
    print(f"tests: {summary}")
    for module_name, values in sorted(counts.items()):
        covered_lines, statements, covered_branches, branches = values
        print(
            f"coverage: {module_name}: statements {covered_lines}/{statements} "
            f"({100.0 * covered_lines / statements:.4f}%), branches "
            f"{covered_branches}/{branches} "
            f"({100.0 * covered_branches / branches:.4f}%)"
        )
    total_lines = sum(values[0] for values in counts.values())
    total_statements = sum(values[1] for values in counts.values())
    total_covered_branches = sum(values[2] for values in counts.values())
    total_branches = sum(values[3] for values in counts.values())
    print(
        f"coverage total: statements {total_lines}/{total_statements} "
        f"({100.0 * total_lines / total_statements:.4f}%), branches "
        f"{total_covered_branches}/{total_branches} "
        f"({100.0 * total_covered_branches / total_branches:.4f}%)"
    )

    axiom_count = 0
    if "--lean" in argv:
        lean_problems, axiom_count = run_lean()
        problems.extend(lean_problems)
        problems.extend(check_artifact_reproducibility())
        problems.extend(check_archive_reproducibility(entries))
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        print(f"verification FAILED: {len(problems)} replay problem(s)")
        return 1

    detail = f", {axiom_count} axiom reports" if "--lean" in argv else ""
    print(
        f"verified: {len(entries)} files pinned, {expected_tests} tests passed"
        f"{detail}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
