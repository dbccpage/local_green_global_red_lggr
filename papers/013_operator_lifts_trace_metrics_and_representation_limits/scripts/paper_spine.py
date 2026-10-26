#!/usr/bin/env python3
"""Canonical equation spine and source-bound document build (stdlib + Pandoc/XeLaTeX).

Syntax custody is not a proof. This module never assigns mathematical truth.
Copied unchanged into standalone paper packages; the application imports this source.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import uuid
import xml.etree.ElementTree as ET

READER = "markdown+tex_math_dollars+tex_math_single_backslash+raw_tex+pipe_tables"
TEXT_READER = "markdown+tex_math_dollars-tex_math_single_backslash+raw_tex+pipe_tables"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def normalized(latex: str) -> str:
    # Preserve signs, command names, grouping, order, and whitespace within text.
    # Only line endings and outer whitespace are ignored; no algebraic equivalence.
    return latex.replace("\r\n", "\n").strip()


def run(args: list[str], data: str | None = None, cwd: Path | None = None,
        env: dict | None = None) -> str:
    result = subprocess.run(args, input=data, text=True, encoding="utf-8",
                            capture_output=True, cwd=cwd, env=env, timeout=180)
    if result.returncode:
        raise ValueError(f"{args[0]} failed: {(result.stdout + result.stderr)[-5000:]}")
    return result.stdout


def parse(text: str, fmt: str = READER) -> dict:
    return json.loads(run(["pandoc", "--sandbox", "-f", fmt, "-t", "json"], text))


def nodes(value, path: str = ""):
    if isinstance(value, dict):
        if "t" in value:
            yield path, value
        for key, item in value.items():
            yield from nodes(item, path + "/" + key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from nodes(item, path + "/" + str(index))


def formulas(ast: dict) -> list[tuple[str, dict]]:
    return [(path, node) for path, node in nodes(ast) if node["t"] == "Math"]


def manuscript(root: Path) -> Path:
    candidates = [p for p in root.glob("*.md") if p.name.lower() not in
                  {"readme.md", "review_scope.md"} and not p.name.endswith(
                      ("_change_log.md", "_claim_ledger.md", "_math_spine.md"))]
    if len(candidates) != 1:
        raise ValueError(f"Expected one manuscript, found {[p.name for p in candidates]}")
    return candidates[0]


def header_body(text: str) -> tuple[list[str], str]:
    lines = text.splitlines()
    rows = []
    while lines and (match := re.fullmatch(r'<div align="center">(.+)</div>', lines[0])):
        rows.append(match[1]); lines.pop(0)
    body = "\n".join(lines).lstrip()
    if len(rows) not in (4, 5) or not rows[0].startswith("# ") or not body.startswith("## Abstract\n"):
        raise ValueError("Expected canonical centered header followed by Abstract")
    dt.date.fromisoformat(rows[-2])
    if not re.fullmatch(r"Version \d+\.\d+\.\d+", rows[-1]):
        raise ValueError("Invalid edition version")
    return rows, body


def spine_paths(md: Path) -> tuple[Path, Path]:
    # Keep companion filenames within the publication kit's Windows path budget.
    stem = md.stem.removesuffix("_monograph")
    return md.with_name(stem + "_math_spine.md"), md.with_name(stem + "_math_spine.json")


def read_spine(path: Path) -> dict[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    result = {}
    for match in re.finditer(r"(?ms)^## (E\d+) \{#([0-9a-f-]{36})\}\n(.*?)(?=^## |\Z)", text):
        key, identity, section = match.groups()
        uuid.UUID(identity)
        math = formulas(parse(section))
        if len(math) != 1 or key in result:
            raise ValueError(f"Each spine entry needs one formula and a unique key: {key}")
        result[key] = {"equation_id": identity, "latex": normalized(math[0][1]["c"][1])}
    if not result:
        raise ValueError("Empty or malformed math spine")
    return result


def initialize(root: Path) -> dict:
    md = manuscript(root); spine, registry = spine_paths(md)
    if spine.exists() or registry.exists():
        raise ValueError("Spine already exists; edit its equations explicitly, then use sync")
    rows, body = header_body(md.read_text(encoding="utf-8"))
    paper_id = str(uuid.uuid4())
    entries = {}; occurrences = []
    for path, node in formulas(parse(body)):
        latex = normalized(node["c"][1])
        if latex not in entries:
            key = f"E{len(entries)+1:04d}"
            entries[latex] = (key, str(uuid.uuid5(uuid.UUID(paper_id), key)))
        key, identity = entries[latex]
        occurrences.append({"ast_path": path, "equation_key": key, "math_type": node["c"][0]["t"]})
    intro = ("# Canonical math spine\n\n" + rows[0][2:] + "\n\n"
             "Each entry is an expression, not a standalone truth assertion. Domains, assumptions, "
             "and quantified statements belong to its linked manuscript context and claim ledger. "
             "The build requires every occurrence to agree with this spine before conversion. "
             "Equation IDs persist when an entry is edited; content hashes and edition bindings change.\n\n"
             "Formalization status: not inferred from LaTeX. Existing Lean results cover only the "
             "statements identified in the manuscript and claim ledger. No generated proof is asserted.\n\n")
    for latex, (key, identity) in entries.items():
        intro += f"## {key} {{#{identity}}}\n\n$$\n{latex}\n$$\n\n"
    spine.write_text(intro, encoding="utf-8", newline="\n")
    data = {"schema": "omega.math-spine.v1", "paper_id": paper_id,
            "manuscript": md.name, "occurrences": occurrences,
            "truth_status": "not_assessed_by_conversion"}
    registry.write_bytes(canonical(data) + b"\n")
    return check(root)


def check(root: Path) -> dict:
    md = manuscript(root); spine, registry = spine_paths(md)
    rows, body = header_body(md.read_text(encoding="utf-8"))
    ast = parse(body); math = formulas(ast)
    record = json.loads(registry.read_text(encoding="utf-8")); entries = read_spine(spine)
    if record["schema"] != "omega.math-spine.v1" or record["manuscript"] != md.name:
        raise ValueError("Spine schema or manuscript binding mismatch")
    uuid.UUID(record["paper_id"])
    ids = [entry["equation_id"] for entry in entries.values()]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate equation UUID")
    if len(math) != len(record["occurrences"]):
        raise ValueError("Formula occurrence count changed; reconcile the spine and use sync")
    checked = []
    for (path, node), occurrence in zip(math, record["occurrences"], strict=True):
        entry = entries[occurrence["equation_key"]]
        if normalized(node["c"][1]) != entry["latex"] or node["c"][0]["t"] != occurrence["math_type"]:
            raise ValueError(f"SPINE_DRIFT at {path}: {occurrence['equation_key']}")
        checked.append({**occurrence, "ast_path": path, **entry,
                        "expression_sha256": digest(entry["latex"].encode())})
    opaque = [path for path, node in nodes(ast) if node["t"] in {"RawBlock", "RawInline"}]
    if opaque:
        raise ValueError(f"Opaque raw content requires explicit review before a spine build: {opaque}")
    return {"paper_id": record["paper_id"], "header": rows, "ast": ast,
            "equations": entries, "occurrences": checked,
            "manuscript_sha256": digest(md.read_bytes()), "spine_sha256": digest(spine.read_bytes())}


def synchronize(root: Path) -> dict:
    """Rebind occurrences after explicit source/spine edits; never import new math silently."""
    md = manuscript(root); spine, registry = spine_paths(md)
    entries = read_spine(spine)
    reverse = {}
    for key, entry in entries.items():
        if entry["latex"] in reverse:
            raise ValueError("Ambiguous identical spine entries; retain one expression identity")
        reverse[entry["latex"]] = key
    _, body = header_body(md.read_text(encoding="utf-8"))
    occurrences = []
    for path, node in formulas(parse(body)):
        latex = normalized(node["c"][1])
        if latex not in reverse:
            raise ValueError(f"Unregistered equation at {path}; add an explicit spine entry first")
        occurrences.append({"ast_path": path, "equation_key": reverse[latex], "math_type": node["c"][0]["t"]})
    record = json.loads(registry.read_text(encoding="utf-8")); record["occurrences"] = occurrences
    registry.write_bytes(canonical(record) + b"\n")
    return check(root)


def compare_math(expected: dict, actual: dict) -> None:
    left = [(n["c"][0]["t"], normalized(n["c"][1])) for _, n in formulas(expected)]
    right = [(n["c"][0]["t"], normalized(n["c"][1])) for _, n in formulas(actual)]
    if left != right:
        bad = next((i for i, pair in enumerate(zip(left, right)) if pair[0] != pair[1]), min(len(left), len(right)))
        raise ValueError(f"FORMAT_MATH_DRIFT at occurrence {bad+1}; counts {len(left)} / {len(right)}")


def build(root: Path) -> dict:
    verified = check(root); md = manuscript(root); ast = verified["ast"]
    rows = verified["header"]
    title = run(["pandoc", "-f", "markdown", "-t", "latex"], rows[0][2:]).strip()
    header = "\\begin{center}\n{\\LARGE\\bfseries " + title + "\\par}\n"
    for row in rows[1:]:
        header += run(["pandoc", "-f", "markdown", "-t", "latex"], row).strip() + "\\par\n"
    header += "\\end{center}\n"
    rendered = copy.deepcopy(ast)
    # PDF named destinations identify occurrences without adding mathematical tokens.
    # A destination locates a rendering; it does not prove its symbolic equivalence.
    for index, ((_, node), occurrence) in enumerate(zip(formulas(rendered), verified["occurrences"], strict=True), 1):
        original = copy.deepcopy(node)
        marker = f"math-{occurrence['equation_key']}-{index:04d}"
        node.clear(); node.update({"t": "Span", "c": [[marker, [], []], [original]]})
    rendered["blocks"].insert(0, {"t": "RawBlock", "c": ["latex", header]})
    tex = run(["pandoc", "-f", "json", "-t", "latex", "-s", "--wrap=none",
               "--top-level-division=section", "-V", "geometry:margin=1in", "-V", "fontsize=10pt",
               "--include-in-header", str(root / "scripts/obstruction-preamble.tex")], json.dumps(rendered))
    tex = re.sub(r"\\phantomsection\\label\{(math-E[0-9]+-[0-9]+)\}",
                 lambda m: r"\hypertarget{" + m[1] + "}{}", tex)
    tex = f"% manuscript-sha256: {verified['manuscript_sha256']}\n% spine-sha256: {verified['spine_sha256']}\n" + tex
    compare_math(ast, parse(tex, "latex"))
    # UTF-8 text retains Markdown math delimiters and code fences. Removing
    # inline-code markers would turn literal examples such as `$x$` into math.
    plain = "\n".join([rows[0][2:], *rows[1:]]) + "\n\n" + run(
        ["pandoc", "-f", "json", "-t", "markdown+tex_math_dollars", "--wrap=none"], json.dumps(ast))
    plain_math = parse(plain, TEXT_READER)
    compare_math(ast, plain_math)
    env = dict(os.environ)
    epoch = int(dt.datetime.combine(dt.date.fromisoformat(rows[-2]), dt.time(), dt.timezone.utc).timestamp())
    env.update(SOURCE_DATE_EPOCH=str(epoch), FORCE_SOURCE_DATE="1")
    with tempfile.TemporaryDirectory(prefix="paper-spine-") as directory:
        temp = Path(directory); source = temp / md.with_suffix(".tex").name
        source.write_text(tex, encoding="utf-8", newline="\n")
        for _ in range(3):
            run(["xelatex", "-no-shell-escape", "-halt-on-error", "-interaction=nonstopmode", source.name], cwd=temp, env=env)
        log = source.with_suffix(".log").read_text(encoding="utf-8", errors="replace")
        failures = [line for line in log.splitlines() if "Missing character" in line or "Overfull \\hbox" in line]
        if failures:
            raise ValueError("RENDER_FAILURE: " + "\n".join(failures))
        pdf_data = source.with_suffix(".pdf").read_bytes()
        pdf_text = run(["pdftotext", "-layout", str(source.with_suffix(".pdf")), "-"])
    locations = []
    try:
        import fitz
    except ImportError:
        destination_status = "unresolved_missing_pymupdf"
    else:
        with fitz.open(stream=pdf_data, filetype="pdf") as document:
            destinations = document.resolve_names()
            for index, occurrence in enumerate(verified["occurrences"], 1):
                marker = f"math-{occurrence['equation_key']}-{index:04d}"
                destination = destinations.get(marker)
                if destination is None:
                    raise ValueError(f"Missing PDF equation destination: {marker}")
                locations.append({"equation_id": occurrence["equation_id"], "equation_key": occurrence["equation_key"],
                                  "occurrence": index, "marker": marker, "destination": destination,
                                  "expression_sha256": occurrence["expression_sha256"]})
        destination_status = "all_occurrences_located"
    # Promote only after all checks and compilation complete.
    md.with_suffix(".tex").write_text(tex, encoding="utf-8", newline="\n")
    md.with_suffix(".txt").write_text(plain, encoding="utf-8", newline="\n")
    md.with_suffix(".pdf").write_bytes(pdf_data)
    docs = root / "docs"; docs.mkdir(exist_ok=True)
    (docs / "rendered_text.txt").write_text(pdf_text, encoding="utf-8", newline="\n")
    (docs / "equation_locations.json").write_bytes(canonical({"pdf_sha256": digest(pdf_data),
        "status": destination_status, "locations": locations,
        "scope": "Destination points only; not glyph recognition or truth verification."})+b"\n")
    receipt = {"schema": "omega.render.v1", "paper_id": verified["paper_id"],
               "source_date_epoch": epoch, "manuscript_sha256": verified["manuscript_sha256"],
               "spine_sha256": verified["spine_sha256"],
               "registry_sha256": digest(spine_paths(md)[1].read_bytes()),
               "preamble_sha256": digest((root / "scripts/obstruction-preamble.tex").read_bytes()),
               "artifacts": {p.name: digest(p.read_bytes()) for p in
                             [md, md.with_suffix('.tex'), md.with_suffix('.txt'), md.with_suffix('.pdf')]},
               "formula_occurrences": len(verified["occurrences"]),
               "md_tex_math": "ordered_structural_match", "md_txt_math": "ordered_structural_match",
               "pdf": "fresh_compilation_bound_to_bytes", "pdf_symbolic_equivalence": "not_established",
               "mathematical_truth": "not_assessed", "missing_glyphs": 0, "overfull_hboxes": 0,
               "pandoc": run(["pandoc", "--version"]).splitlines()[0],
               "xelatex": run(["xelatex", "--version"]).splitlines()[0],
               "builder_sha256": digest(Path(__file__).read_bytes())}
    (docs / "render_receipt.json").write_bytes(canonical(receipt)+b"\n")
    return receipt


def verify_render(root: Path) -> dict:
    """Fail on any post-build source or artifact mutation; no automatic re-sealing."""
    md = manuscript(root); spine, registry = spine_paths(md)
    receipt = json.loads((root / "docs/render_receipt.json").read_text(encoding="utf-8"))
    for artifact in [md, md.with_suffix(".tex"), md.with_suffix(".txt"), md.with_suffix(".pdf")]:
        if digest(artifact.read_bytes()) != receipt["artifacts"][artifact.name]:
            raise ValueError(f"RENDER_BINDING_DRIFT: {artifact.name}")
    if digest(spine.read_bytes()) != receipt["spine_sha256"]:
        raise ValueError("RENDER_BINDING_DRIFT: canonical spine")
    for name, path in [("registry", registry), ("preamble", root / "scripts/obstruction-preamble.tex"),
                       ("builder", Path(__file__))]:
        if digest(path.read_bytes()) != receipt[name + "_sha256"]:
            raise ValueError(f"RENDER_BINDING_DRIFT: {name}")
    checked = check(root)
    if receipt["paper_id"] != checked["paper_id"]:
        raise ValueError("RENDER_BINDING_DRIFT: paper identity")
    compare_math(checked["ast"], parse(md.with_suffix(".tex").read_text(encoding="utf-8"), "latex"))
    compare_math(checked["ast"], parse(md.with_suffix(".txt").read_text(encoding="utf-8"), TEXT_READER))
    return {"paper_id": checked["paper_id"], "status": "PASS", "truth_status": "not_assessed"}


def inventory(root: Path) -> dict:
    verified = check(root); md = manuscript(root); paper_id = verified["paper_id"]
    edition_id = str(uuid.uuid5(uuid.UUID(paper_id), verified["manuscript_sha256"]))
    elements = []
    for path, node in nodes(verified["ast"]):
        content_hash = digest(canonical(node))
        elements.append({"occurrence_id": str(uuid.uuid5(uuid.UUID(edition_id), path)),
                         "kind": node["t"], "ast_path": path, "content_sha256": content_hash,
                         "content": node, "review_status": "unreviewed"})
    lines = []; offset = 0
    for number, line in enumerate(md.read_bytes().splitlines(keepends=True), 1):
        lines.append({"line": number, "start_byte": offset, "end_byte": offset+len(line),
                      "sha256": digest(line)}); offset += len(line)
    headings = []
    contextual = []
    for index, block in enumerate(verified["ast"]["blocks"]):
        if block["t"] == "Header":
            level = block["c"][0]
            title = " ".join(n["c"] for _, n in nodes(block) if n["t"] == "Str")
            headings = [h for h in headings if h["level"] < level] + [{"level": level, "title": title}]
        for occurrence in verified["occurrences"]:
            if occurrence["ast_path"].startswith(f"/blocks/{index}/"):
                contextual.append({**occurrence,
                                   "occurrence_id": str(uuid.uuid5(uuid.UUID(edition_id), occurrence["ast_path"])),
                                   "section_context": list(headings),
                                   "semantic_claim_binding": "requires_review"})
    result = {"schema": "omega.paper-inventory.v1", "paper_id": paper_id, "edition_id": edition_id,
              "manuscript_sha256": verified["manuscript_sha256"], "spine_sha256": verified["spine_sha256"],
              "elements": elements, "source_lines": lines, "equations": contextual,
              "scope": "All Pandoc AST nodes and source bytes; semantic claim completeness is unverified.",
              "correctness_percentage": None}
    return result


def ingest(source: Path, paper_id: str) -> dict:
    """Inventory untrusted external bytes without executing document content."""
    identity = uuid.UUID(paper_id)
    raw = source.read_bytes(); sha = digest(raw)
    suffix = source.suffix.lower()
    artifact_id = str(uuid.uuid5(identity, suffix + ":" + sha))
    elements = []; limitations = []
    if suffix == ".pdf":
        xml = run(["pdftotext", "-bbox-layout", str(source.resolve()), "-"])
        document = ET.fromstring(xml)
        pages = [node for node in document.iter() if node.tag.endswith("}page")]
        for number, page in enumerate(pages, 1):
            words = [{"text": word.text or "", "bbox": dict(word.attrib)}
                     for word in page.iter() if word.tag.endswith("}word")]
            elements.append({"kind": "pdf_page", "page": number, "geometry": dict(page.attrib),
                             "words": words, "content_sha256": digest(canonical(words))})
        limitations = ["PDF word extraction is not symbolic equation recognition or OCR.",
                       "Images, diagrams, reading order, and mathematical semantics require further review."]
    elif suffix in {".md", ".tex", ".txt"}:
        text = raw.decode("utf-8")
        ast = parse(text, "latex" if suffix == ".tex" else TEXT_READER if suffix == ".txt" else READER)
        elements = [{"kind": node["t"], "ast_path": path, "content": node,
                     "content_sha256": digest(canonical(node))} for path, node in nodes(ast)]
        limitations = ["AST coverage does not establish complete semantic claim extraction."]
        if suffix == ".txt":
            limitations.append("Plain text is interpreted using Markdown math delimiters; other notation remains prose.")
        if any(e["kind"] in {"RawInline", "RawBlock", "Image"} for e in elements):
            limitations.append("Raw markup and images are inventoried but their mathematical content is unresolved.")
    else:
        raise ValueError("Supported inputs: UTF-8 .md/.tex/.txt and .pdf")
    for index, element in enumerate(elements):
        element["occurrence_id"] = str(uuid.uuid5(uuid.UUID(artifact_id), str(index)))
        element["review_status"] = "unreviewed"
    return {"schema": "omega.paper-import.v1", "paper_id": str(identity), "artifact_id": artifact_id,
            "format": suffix[1:], "artifact_sha256": sha, "source_name": source.name,
            "source_size_bytes": len(raw), "elements": elements, "limitations": limitations,
            "correctness_percentage": None, "truth_status": "not_assessed"}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["init", "sync", "check", "build", "verify", "inventory", "ingest"])
    parser.add_argument("--paper-path", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--paper-id", help="Persistent UUID shared by all formats of an imported paper")
    args = parser.parse_args(argv)
    try:
        if args.command == "ingest":
            if args.source is None or args.paper_id is None:
                raise ValueError("ingest requires --source and --paper-id")
            result = ingest(args.source, args.paper_id)
        else:
            result = {"init": initialize, "sync": synchronize, "check": check,
                      "build": build, "verify": verify_render, "inventory": inventory}[args.command](args.paper_path.resolve())
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_bytes(canonical(result)+b"\n")
        print(json.dumps({"status": "PASS", "operation": args.command,
                          "paper_id": result.get("paper_id"), "truth_status": "not_assessed"}))
        return 0
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"status": "FAIL", "operation": args.command, "reason": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
