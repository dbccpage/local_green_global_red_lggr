#!/usr/bin/env python3
"""Verify the pinned Paper VI public package and optionally replay Lean."""

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
SUMS = ROOT / "SHA256SUMS"
PAPER_STEM = "lggr_vi_nonlinear_aggregation_and_adjoint_probing"
RELEASE_DATE = "2026-10-15"
ARCHIVE_NAME = f"{PAPER_STEM}_{RELEASE_DATE}.zip"
AXIOM_REPORT = "lean4/AXIOM_REPORT.txt"
PRODUCTION_MODULES = ("lggr_vi_core.py", "generate_figures.py")
COVERAGE_THRESHOLD = 95.0
IGNORED_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".lake",
    ".venv",
    "venv",
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
    "legacy_omnibus",
}
IGNORED_FILE_NAMES = {"SHA256SUMS", ".coverage", "DEPOSIT_CHECKLIST.md"}
IGNORED_FILE_SUFFIXES = {".zip"}
PUBLIC_NOTEBOOKS = {
    "01_observation_blind_spots.ipynb",
    "02_adjoint_probes_and_falsifiers.ipynb",
}
REQUIRED_FILES = (
    ".gitignore",
    "LICENSE",
    "LICENSE-CODE",
    "MANIFEST.sha256",
    "README.md",
    "code/generate_figures.py",
    "code/lggr_vi_core.py",
    "code/tests/test_figures.py",
    "code/tests/test_lggr_vi_core.py",
    "code/tests/test_notebooks.py",
    "code/tests/test_release_surface.py",
    "docs/claim_code_map.yaml",
    "docs/descriptions.md",
    "docs/lean_claim_map.md",
    "docs/mutation_audit.md",
    "docs/quick_start.md",
    "figures/figure_1_kernel_and_adjoint.pdf",
    "figures/figure_1_kernel_and_adjoint.png",
    "figures/figure_2_sign_probe_error.pdf",
    "figures/figure_2_sign_probe_error.png",
    "jupyter_notebooks/01_observation_blind_spots.ipynb",
    "jupyter_notebooks/02_adjoint_probes_and_falsifiers.ipynb",
    "lean4/Core.lean",
    AXIOM_REPORT,
    "lean4/check_axioms.lean",
    "lean4/lake-manifest.json",
    "lean4/lakefile.lean",
    "lean4/lean-toolchain",
    "lggr_vi_nonlinear_aggregation_and_adjoint_probing.md",
    "lggr_vi_nonlinear_aggregation_and_adjoint_probing.pdf",
    "lggr_vi_nonlinear_aggregation_and_adjoint_probing.tex",
    "lggr_vi_nonlinear_aggregation_and_adjoint_probing_change_log.md",
    "lggr_vi_nonlinear_aggregation_and_adjoint_probing_claim_ledger.md",
    "pyproject.toml",
    "scripts/build_deposit_zip.py",
    "scripts/build_paper_artifacts.py",
    "scripts/capture_axiom_report.py",
    "scripts/obstruction-preamble.tex",
    "scripts/regen_sha256sums.py",
    "uv.lock",
    "verify_deposit.py",
    "zenodo_metadata.json",
)
AXIOM_WHITELIST = frozenset({"propext", "Classical.choice", "Quot.sound"})
EXPECTED_AXIOM_DECLARATIONS = (
    "LGGRVI.postprocessing_invariance",
    "LGGRVI.zero_preserving_accepts_hidden",
    "LGGRVI.gram_zero_iff_hidden",
    "LGGRVI.detectable_has_nonzero_gram",
    "LGGRVI.gram_kernel_iff",
    "LGGRVI.gram_detectable_iff",
    "LGGRVI.centered_directional_identity",
    "LGGRVI.sign_cube_recovers",
)
EXPECTED_AXIOM_REPORTS = len(EXPECTED_AXIOM_DECLARATIONS)
EXPECTED_SHARED_PREAMBLE_SHA256 = (
    "050ff13b2c82b6136fc4bbd9b2fc160fc0483ff7f96508277697b0316c584158"
)
CANONICAL_PREAMBLE_PARTS = (
    "coda_university",
    "_kits",
    "obstruction_paper_kit",
    "obstruction_preamble.tex",
)
BUILD_DIAGNOSTIC_MARKERS = (
    "Missing character:",
    "Unable to load picture or PDF file",
    "ignored error:",
    "Overfull \\hbox",
    "Overfull \\vbox",
    "Float too large for page",
    "Dimension too large",
)


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validated_manifest_path(relative: str, line_number: int, root: Path) -> Path:
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
    candidate = root.joinpath(*pure.parts)
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError:
        unsafe = True
    if candidate.is_symlink():
        unsafe = True
    if unsafe:
        raise ValueError(
            f"SHA256SUMS line {line_number} has unsafe path {relative!r}"
        )
    return candidate


def parse_manifest(
    manifest_path: Path = SUMS, root: Path = ROOT
) -> dict[str, str]:
    if not manifest_path.is_file():
        raise ValueError("SHA256SUMS is missing")
    entries: dict[str, str] = {}
    for line_number, raw in enumerate(
        manifest_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or re.fullmatch(r"[0-9a-fA-F]{64}", parts[0]) is None:
            raise ValueError(f"SHA256SUMS line {line_number} is malformed: {raw!r}")
        relative = parts[1].strip().lstrip("*")
        _validated_manifest_path(relative, line_number, root)
        if relative.casefold() in {item.casefold() for item in entries}:
            raise ValueError(f"SHA256SUMS lists {relative} more than once")
        entries[relative] = parts[0].lower()
    return entries


def check_hashes(entries: dict[str, str], root_dir: Path = ROOT) -> list[str]:
    problems: list[str] = []
    for relative, expected in sorted(entries.items()):
        path = root_dir / relative
        if not path.is_file():
            problems.append(f"missing file listed in SHA256SUMS: {relative}")
        else:
            actual = sha256_of(path)
            if actual != expected:
                problems.append(
                    f"hash mismatch for {relative}: manifest {expected}, actual {actual}"
                )
    return problems


def sweep_unlisted(entries: dict[str, str], root_dir: Path = ROOT) -> list[str]:
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
        if path.name in IGNORED_FILE_NAMES or path.suffix in IGNORED_FILE_SUFFIXES:
            continue
        if relative not in entries:
            problems.append(f"file present but not listed in SHA256SUMS: {relative}")
    return problems


def check_required(entries: dict[str, str], root_dir: Path = ROOT) -> list[str]:
    problems: list[str] = []
    for required in REQUIRED_FILES:
        if required not in entries:
            problems.append(f"required file not pinned in SHA256SUMS: {required}")
        elif not (root_dir / required).is_file():
            problems.append(f"required file missing on disk: {required}")
    return problems


def find_canonical_preamble(root_dir: Path = ROOT) -> Path | None:
    """Find the live CODA kit when verifying from a source checkout."""

    for ancestor in (root_dir, *root_dir.parents):
        candidate = ancestor.joinpath(*CANONICAL_PREAMBLE_PARTS)
        if candidate.is_file():
            return candidate
    return None


def fenced_description(text: str, heading: str, language: str) -> str | None:
    pattern = (
        rf"^## {re.escape(heading)}\s*$.*?"
        rf"^```{re.escape(language)}\s*$\n(.*?)\n^```\s*$"
    )
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return match.group(1) if match is not None else None


def check_description_contract(root_dir: Path = ROOT) -> list[str]:
    problems: list[str] = []
    description_path = root_dir / "docs" / "descriptions.md"
    metadata_path = root_dir / "zenodo_metadata.json"
    if not description_path.is_file() or not metadata_path.is_file():
        return ["description contract inputs are missing"]
    text = description_path.read_text(encoding="utf-8")
    primary = fenced_description(text, "Primary Description", "html")
    secondary = fenced_description(text, "Secondary Description", "text")
    if primary is None:
        problems.append("docs/descriptions.md lacks the canonical Primary Description HTML block")
    if secondary is None:
        problems.append("docs/descriptions.md lacks the canonical Secondary Description text block")
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        problems.append(f"zenodo_metadata.json cannot be read: {error}")
    else:
        if primary is not None and metadata.get("description") != primary:
            problems.append(
                "zenodo_metadata.json.description does not match the canonical Primary Description"
            )
    return problems


def check_public_policy(
    entries: dict[str, str], root_dir: Path = ROOT
) -> list[str]:
    problems: list[str] = []
    notebooks = {
        PurePosixPath(relative).name
        for relative in entries
        if relative.startswith("jupyter_notebooks/") and relative.endswith(".ipynb")
    }
    if notebooks != PUBLIC_NOTEBOOKS:
        problems.append(
            f"public notebook set mismatch: expected {sorted(PUBLIC_NOTEBOOKS)}, "
            f"got {sorted(notebooks)}"
        )
    if any(relative.startswith("research/legacy_omnibus/") for relative in entries):
        problems.append("research/legacy_omnibus must not be pinned for public release")
    bundled = root_dir / "scripts" / "obstruction-preamble.tex"
    if not bundled.is_file():
        problems.append("bundled obstruction preamble is missing")
    elif sha256_of(bundled) != EXPECTED_SHARED_PREAMBLE_SHA256:
        problems.append("bundled obstruction preamble does not match the canonical hash")

    canonical = find_canonical_preamble(root_dir)
    if canonical is not None:
        if sha256_of(canonical) != EXPECTED_SHARED_PREAMBLE_SHA256:
            problems.append("live CODA obstruction preamble does not match the pinned hash")
        elif bundled.is_file() and canonical.read_bytes() != bundled.read_bytes():
            problems.append("bundled obstruction preamble differs from the live CODA kit")

    tex = root_dir / f"{PAPER_STEM}.tex"
    if bundled.is_file() and tex.is_file():
        bundled_text = bundled.read_text(encoding="utf-8").replace("\r\n", "\n")
        tex_text = tex.read_text(encoding="utf-8").replace("\r\n", "\n")
        if bundled_text.strip() not in tex_text:
            problems.append("generated TeX does not contain the bundled canonical preamble")
        if r"\setcounter{secnumdepth}{-\maxdimen}" not in tex_text:
            problems.append("generated TeX does not disable section numbering")

    producer = root_dir / "scripts" / "build_paper_artifacts.py"
    if producer.is_file():
        source = producer.read_text(encoding="utf-8").casefold()
        for forbidden in ("xelatex", "lualatex", "--number-sections"):
            if forbidden in source:
                problems.append(f"paper producer contains forbidden build option {forbidden}")

    problems.extend(check_description_contract(root_dir))
    return problems


def pytest_summary(output: str) -> str:
    """Return pytest's pass summary even when coverage prints after it."""

    lines = [line for line in output.splitlines() if line.strip()]
    for line in reversed(lines):
        if re.search(r"\b\d+ passed\b", line):
            return line
    return lines[-1] if lines else "(no pytest output)"


def coverage_percentages(
    report: dict[str, object], module_names: tuple[str, ...] = PRODUCTION_MODULES
) -> tuple[dict[str, tuple[float, float]], list[str]]:
    """Return independent line and branch percentages for every production module."""

    files = report.get("files")
    if not isinstance(files, dict):
        return {}, ["coverage JSON has no files mapping"]
    rates: dict[str, tuple[float, float]] = {}
    problems: list[str] = []
    for module_name in module_names:
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
        line_rate = 100.0 if statements == 0 else 100.0 * covered_lines / statements
        branch_rate = 100.0 if branches == 0 else 100.0 * covered_branches / branches
        rates[module_name] = (line_rate, branch_rate)
        if line_rate < COVERAGE_THRESHOLD:
            problems.append(
                f"{module_name} line coverage {line_rate:.2f}% is below "
                f"{COVERAGE_THRESHOLD:.2f}%"
            )
        if branch_rate < COVERAGE_THRESHOLD:
            problems.append(
                f"{module_name} branch coverage {branch_rate:.2f}% is below "
                f"{COVERAGE_THRESHOLD:.2f}%"
            )
    return rates, problems


def run_tests(
    root_dir: Path = ROOT,
) -> tuple[int, str, dict[str, tuple[float, float]], list[str]]:
    with tempfile.TemporaryDirectory(prefix="lggr-vi-pytest-") as raw_tmp:
        basetemp = Path(raw_tmp) / "pytest"
        coverage_json = Path(raw_tmp) / "coverage.json"
        environment = dict(os.environ)
        environment["COVERAGE_FILE"] = str(Path(raw_tmp) / ".coverage")
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
                str(basetemp),
                "--cov=lggr_vi_core",
                "--cov=generate_figures",
                "--cov-branch",
                "--cov-report=term",
                f"--cov-report=json:{coverage_json}",
                "--cov-fail-under=0",
            ],
            cwd=str(root_dir),
            capture_output=True,
            text=True,
            timeout=900,
            env=environment,
            check=False,
        )
        output = (process.stdout or "") + (process.stderr or "")
        summary = pytest_summary(output)
        if process.returncode != 0:
            print(output, file=sys.stderr)
            return process.returncode, summary, {}, ["pytest failed"]
        if not coverage_json.is_file():
            return 1, summary, {}, ["pytest did not emit coverage JSON"]
        try:
            coverage_report = json.loads(coverage_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            return 1, summary, {}, [f"coverage JSON is invalid: {error}"]
        rates, problems = coverage_percentages(coverage_report)
        return (1 if problems else 0), summary, rates, problems


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
            axiom_tail = line.partition("depends on axioms:")[2]
            while "]" not in axiom_tail and index + 1 < len(lines):
                index += 1
                continuation = lines[index].strip()
                chunks.append(continuation)
                axiom_tail += " " + continuation
            reports.append(" ".join(chunks))
        index += 1
    return reports


def _source_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256_of(path)
        for path in root.rglob("*")
        if path.is_file()
        and not any(
            part in {".lake", "__pycache__", ".pytest_cache"}
            for part in path.relative_to(root).parts
        )
        and path.name != "AXIOM_REPORT.txt"
    }


def render_axiom_report(lean_dir: Path, reports: list[str]) -> str:
    """Render only deterministic source bindings and theorem-level results."""

    toolchain = (lean_dir / "lean-toolchain").read_text(encoding="utf-8").strip()
    lines = [
        "LGGR VI theorem-level axiom report",
        "Format: lggr-vi-axioms-v1",
        f"Toolchain: {toolchain}",
        f"Core.lean SHA-256: {sha256_of(lean_dir / 'Core.lean')}",
        f"check_axioms.lean SHA-256: {sha256_of(lean_dir / 'check_axioms.lean')}",
        "Build command: lake build",
        "Census command: lake env lean check_axioms.lean",
        "",
        "Reports:",
        *reports,
        "",
    ]
    return "\n".join(lines)


def capture_axiom_report(
    root_dir: Path = ROOT,
) -> tuple[str, list[str], list[str]]:
    """Build exact sources in a short path and return the normalized census."""

    problems: list[str] = []
    lean_dir = root_dir / "lean4"
    if shutil.which("lake") is None:
        return "", [], ["lake is not available on PATH"]

    for source in sorted(lean_dir.glob("*.lean")):
        match = re.search(r"\b(sorry|admit)\b", source.read_text(encoding="utf-8"))
        if match:
            problems.append(f"{source.name} contains {match.group(1)}")
    if problems:
        return "", [], problems

    ignored = shutil.ignore_patterns(
        ".lake", "__pycache__", ".pytest_cache", "AXIOM_REPORT.txt"
    )
    with tempfile.TemporaryDirectory(prefix="lggr-vi-lean-") as raw_tmp:
        replay = Path(raw_tmp) / "lean4"
        shutil.copytree(lean_dir, replay, ignore=ignored)
        if _source_hashes(lean_dir) != _source_hashes(replay):
            return "", [], ["short-path Lean replay does not match packaged inputs"]

        build = subprocess.run(
            ["lake", "build"],
            cwd=str(replay),
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        if build.returncode != 0:
            print(build.stdout + build.stderr, file=sys.stderr)
            return "", [], ["lake build failed in the exact short-path replay"]

        census = subprocess.run(
            ["lake", "env", "lean", "check_axioms.lean"],
            cwd=str(replay),
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        if census.returncode != 0:
            print(census.stdout + census.stderr, file=sys.stderr)
            return "", [], ["axiom census failed to elaborate"]
        reports = _group_axiom_reports(census.stdout + census.stderr)
        if len(reports) != EXPECTED_AXIOM_REPORTS:
            problems.append(
                f"expected {EXPECTED_AXIOM_REPORTS} axiom reports, got {len(reports)}"
            )
        for index, report in enumerate(reports):
            if index < len(EXPECTED_AXIOM_DECLARATIONS):
                expected_prefix = f"'{EXPECTED_AXIOM_DECLARATIONS[index]}' "
                if not report.startswith(expected_prefix):
                    problems.append(
                        "axiom report order/name mismatch: expected "
                        f"{EXPECTED_AXIOM_DECLARATIONS[index]}, got {report}"
                    )
            if "does not depend on any axioms" in report:
                continue
            match = re.search(r"depends on axioms:\s*\[([^]]*)]", report)
            if match is None:
                problems.append(f"could not parse axiom report: {report}")
                continue
            for name in (item.strip() for item in match.group(1).split(",")):
                if name not in AXIOM_WHITELIST:
                    problems.append(f"axiom outside whitelist: {name} in {report}")

    rendered = render_axiom_report(lean_dir, reports) if not problems else ""
    return rendered, reports, problems


def run_lean(root_dir: Path = ROOT) -> list[str]:
    report, reports, problems = capture_axiom_report(root_dir)
    report_path = root_dir / AXIOM_REPORT
    if not report_path.is_file():
        problems.append(f"bundled axiom report is missing: {AXIOM_REPORT}")
    elif report and report_path.read_text(encoding="utf-8") != report:
        problems.append("bundled axiom report is stale or non-deterministic")
    if not problems:
        print(
            f"lean: build clean, bundled report matches {len(reports)} theorems; "
            "all dependencies within "
            f"{sorted(AXIOM_WHITELIST)}"
        )
    return problems


def check_artifact_reproducibility(root_dir: Path = ROOT) -> list[str]:
    """Build TeX/PDF twice and compare both runs with committed artifacts."""

    problems: list[str] = []
    script = root_dir / "scripts" / "build_paper_artifacts.py"
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory(prefix="lggr-vi-artifacts-") as raw_tmp:
        outputs: list[Path] = []
        for label in ("first", "second"):
            destination = Path(raw_tmp) / label
            process = subprocess.run(
                [sys.executable, str(script), "--output-dir", str(destination)],
                cwd=str(root_dir),
                capture_output=True,
                text=True,
                timeout=1800,
                env=environment,
                check=False,
            )
            if process.returncode != 0:
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
            if "This is pdfTeX" not in log_text:
                problems.append("build log does not identify pdfTeX/pdfLaTeX")
            if "This is XeTeX" in log_text or "This is LuaTeX" in log_text:
                problems.append("build log identifies a forbidden TeX engine")
            for marker in BUILD_DIAGNOSTIC_MARKERS:
                if marker in log_text:
                    problems.append(f"build log contains release diagnostic: {marker}")

        if not problems:
            print(
                "artifacts: two pdfLaTeX builds reproduced committed TeX/PDF; "
                "logs have no clipping or overfull markers"
            )
    return problems


def check_archive_reproducibility(
    entries: dict[str, str], root_dir: Path = ROOT
) -> list[str]:
    """Build the dated archive twice and validate its exact member set."""

    problems: list[str] = []
    script = root_dir / "scripts" / "build_deposit_zip.py"
    source = script.read_text(encoding="utf-8")
    if f'RELEASE_DATE = "{RELEASE_DATE}"' not in source:
        problems.append("archive producer does not bind the release date")
    if 'ARCHIVE_NAME = f"{ROOT.name}_{RELEASE_DATE}.zip"' not in source:
        problems.append("archive producer does not use the dated per-paper name")

    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory(prefix="lggr-vi-archive-") as raw_tmp:
        archives = [Path(raw_tmp) / "first.zip", Path(raw_tmp) / "second.zip"]
        for archive in archives:
            process = subprocess.run(
                [sys.executable, str(script), "--out", str(archive)],
                cwd=str(root_dir),
                capture_output=True,
                text=True,
                timeout=300,
                env=environment,
                check=False,
            )
            if process.returncode != 0:
                print(process.stdout + process.stderr, file=sys.stderr)
                return problems + ["archive producer failed"]
        if archives[0].read_bytes() != archives[1].read_bytes():
            problems.append("two archive builds produced different bytes")

        prefix = root_dir.name
        expected = {f"{prefix}/{relative}" for relative in entries}
        expected.add(f"{prefix}/SHA256SUMS")
        with zipfile.ZipFile(archives[0]) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                problems.append("archive contains duplicate member names")
            if set(names) != expected:
                problems.append("archive member set differs from SHA256SUMS")
            if any(info.date_time != (2026, 10, 15, 0, 0, 0) for info in infos):
                problems.append("archive members do not use the fixed release timestamp")

        if not problems:
            print(
                f"archive: two {ARCHIVE_NAME} builds matched SHA-256 "
                f"{sha256_of(archives[0])}"
            )
    return problems


def main(argv: list[str]) -> int:
    try:
        entries = parse_manifest()
    except ValueError as error:
        print(f"verification FAILED: {error}", file=sys.stderr)
        return 1

    problems = (
        check_hashes(entries)
        + sweep_unlisted(entries)
        + check_required(entries)
        + check_public_policy(entries, ROOT)
    )
    for problem in problems:
        print(f"FAIL: {problem}", file=sys.stderr)
    if problems:
        print(f"verification FAILED: {len(problems)} manifest problem(s)")
        return 1
    print(f"SHA256SUMS: all {len(entries)} files verified")

    collection_environment = dict(os.environ)
    collection_environment["PYTHONDONTWRITEBYTECODE"] = "1"
    collected = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-p",
            "no:cacheprovider",
            "-o",
            "addopts=",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=180,
        env=collection_environment,
        check=False,
    )
    transcript = collected.stdout + collected.stderr
    match = re.search(r"collected\s+(\d+)\s+items", transcript)
    if match is None:
        match = re.search(r"(\d+)\s+tests collected", transcript)
    if collected.returncode != 0 or match is None:
        print(transcript, file=sys.stderr)
        print("verification FAILED: could not collect tests", file=sys.stderr)
        return 1
    expected = int(match.group(1))

    return_code, summary, coverage_rates, coverage_problems = run_tests()
    if return_code != 0:
        for problem in coverage_problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        print(
            f"verification FAILED: test suite did not pass -- {summary}",
            file=sys.stderr,
        )
        return 1
    if any(word in summary for word in ("skipped", "xfailed", "xpassed", "error")):
        print(f"verification FAILED: suite was not clean -- {summary}", file=sys.stderr)
        return 1
    if f"{expected} passed" not in summary:
        print(
            f"verification FAILED: expected {expected} passing tests, got -- {summary}",
            file=sys.stderr,
        )
        return 1
    print(f"tests: {summary}")
    for module_name, (line_rate, branch_rate) in sorted(coverage_rates.items()):
        print(
            f"coverage: {module_name}: lines {line_rate:.2f}%, "
            f"branches {branch_rate:.2f}%"
        )

    artifact_problems = check_artifact_reproducibility()
    archive_problems = check_archive_reproducibility(entries)
    for problem in artifact_problems + archive_problems:
        print(f"FAIL: {problem}", file=sys.stderr)
    if artifact_problems or archive_problems:
        print("verification FAILED: deterministic build checks did not pass")
        return 1

    if "--lean" in argv:
        lean_problems = run_lean()
        for problem in lean_problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        if lean_problems:
            print("verification FAILED: Lean checks did not pass")
            return 1

    print(f"verified: {len(entries)} files pinned, {expected} tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
