#!/usr/bin/env python3
"""Build the DOCX from the checked manuscript and compare its math AST."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import paper_spine


def math_tokens(source):
    """Limited typesetting normalization for this edition, not algebraic rewriting."""
    source = re.sub(r'\\(mathcal|bar)\s+([A-Za-z])', r'\\\1{\2}', source)
    for name in ("CanAnswer", "Auth", "Var", "joint", "eff"):
        source = source.replace(r"\operatorname{" + name + "}", name)
        source = source.replace(r"\mathrm{" + name + "}", name)
    source = source.replace("{CanAnswer}", "CanAnswer")
    aliases = {"to": r"\rightarrow", "ne": r"\neq", "lbrack": "[",
               "rbrack": "]", "square": "▫"}
    source = re.sub(r'\\([A-Za-z]+)', lambda m: aliases.get(m[1], m[0]), source)
    source = re.sub(r'\\(?:bigl|bigr|left|right|qquad|quad)(?![A-Za-z])', '', source)
    source = re.sub(r'\s+', '', source)
    return re.sub(r'([_^])([A-Za-z0-9])', r'\1{\2}', source)


def compare_docx_math(expected, actual):
    left = [n['c'] for _, n in paper_spine.formulas(expected)]
    right = [n['c'] for _, n in paper_spine.formulas(actual)]
    if len(left) != len(right):
        raise ValueError("DOCX formula occurrence count changed")
    differences = []
    for i, (a, b) in enumerate(zip(left, right), 1):
        if a[0] != b[0] or math_tokens(a[1]) != math_tokens(b[1]):
            raise ValueError(f"DOCX math mismatch at {i}: {a!r} / {b!r}")
        if paper_spine.normalized(a[1]) != paper_spine.normalized(b[1]):
            differences.append({'occurrence': i, 'source_tex': a[1], 'docx_roundtrip_tex': b[1]})
    return {'occurrences': len(left), 'typesetting_differences': differences,
            'normalizations': 'Whitespace; single-token script braces; arrow/inequality/bracket aliases; delimiter sizing; math spacing; square end-proof glyph; font wrappers for five explicitly named identifiers. No arithmetic, operand-order, or grouping rewrite.',
            'scope': 'Token agreement under listed typesetting normalizations; not symbolic proof or visual glyph equivalence.'}


def build():
    checked = paper_spine.check(ROOT)
    md = paper_spine.manuscript(ROOT)
    rows, body = paper_spine.header_body(md.read_text(encoding="utf-8"))
    source = "\n\n".join([rows[0], *rows[1:], body])
    with tempfile.TemporaryDirectory(prefix="institutions-docx-") as directory:
        target = Path(directory) / "paper.docx"
        result = subprocess.run(["pandoc", "--sandbox", "-f", paper_spine.READER,
                                 "-t", "docx", "-o", str(target)], input=source,
                                text=True, encoding="utf-8", capture_output=True, timeout=120)
        if result.returncode:
            raise ValueError(result.stderr)
        result = subprocess.run(["pandoc", "--sandbox", "-f", "docx", "-t", "json", str(target)],
                                text=True, encoding="utf-8", capture_output=True, timeout=120)
        if result.returncode:
            raise ValueError(result.stderr)
        comparison = compare_docx_math(checked["ast"], json.loads(result.stdout))
        data = target.read_bytes()
    output = md.with_suffix(".docx")
    output.write_bytes(data)
    receipt = {"schema": "institutions.docx.v1", "manuscript_sha256": checked["manuscript_sha256"],
               "artifact": output.name, "sha256": hashlib.sha256(data).hexdigest(),
               "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "ordered_math_roundtrip": "PASS_under_listed_typesetting_normalizations", **comparison}
    (ROOT / "docs/docx_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("PASS: DOCX built; all math occurrences agree under documented typesetting normalizations")


if __name__ == "__main__":
    build()
