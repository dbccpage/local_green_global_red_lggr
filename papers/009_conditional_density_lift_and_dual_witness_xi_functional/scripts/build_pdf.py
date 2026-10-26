"""Render the canonical Markdown and bind the resulting TeX/PDF to its bytes."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], **kwargs) -> str:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=180, check=True, **kwargs)
    return result.stdout


def build() -> None:
    source = (ROOT / "density_lift.md").read_text(encoding="utf-8")
    rows = re.findall(r'^<div align="center">(.+)</div>$', source, re.M)
    if len(rows) != 4 or not rows[0].startswith("# "):
        raise ValueError("Expected the four-line centered manuscript header")
    header = "\\begin{center}\n{\\LARGE\\bfseries " + rows[0][2:] + "\\par}\n"
    header += "\n".join(row + "\\par" for row in rows[1:]) + "\n\\end{center}\n\n"
    body = source[source.index("## Abstract"):]
    tex = run(["pandoc", "--from", "markdown+tex_math_dollars+tex_math_single_backslash+raw_tex+pipe_tables",
               "--to", "latex", "--standalone", "--top-level-division=section",
               "--lua-filter", "scripts/paper_code_wrap.lua", "--variable", "geometry:margin=1in",
               "--variable", "mainfont:Times New Roman", "--variable", "monofont:Consolas",
               "--variable", "mathfont:Latin Modern Math"], input=header + body)
    digest = hashlib.sha256((ROOT / "density_lift.md").read_bytes()).hexdigest()
    tex = f"% manuscript-sha256: {digest}\n" + tex
    # Long exact coefficients and matrix identities need a little more display room.
    tex = tex.replace("\\begin{document}", "\\allowdisplaybreaks\n\\begin{document}")
    (ROOT / "density_lift.tex").write_text(tex, encoding="utf-8", newline="\n")
    for _ in range(3):
        run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "-no-shell-escape", "density_lift.tex"])
    log = (ROOT / "density_lift.log").read_text(encoding="utf-8", errors="replace")
    missing = log.count("Missing character:")
    overfull = [float(x) for x in re.findall(r"Overfull \\hbox \(([0-9.]+)pt too wide\)", log)]
    if missing or any(x > 10 for x in overfull):
        raise ValueError(f"Render refused: {missing} missing glyphs; overfull widths {overfull}")
    pages = re.search(r"Output written on .*?\((\d+) pages?", log)
    if pages is None:
        raise ValueError("PDF page count missing from build log")
    binding = {
        "source": "density_lift.md", "tex": "density_lift.tex", "pdf": "density_lift.pdf",
        "sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                   for name in ("density_lift.md", "density_lift.tex", "density_lift.pdf", "scripts/build_pdf.py", "scripts/paper_code_wrap.lua")},
        "pages": int(pages.group(1)), "missing_glyphs": missing,
        "overfull_hbox_gt_10pt": sum(x > 10 for x in overfull),
        "pandoc": run(["pandoc", "--version"]).splitlines()[0],
        "xelatex": run(["xelatex", "--version"]).splitlines()[0],
        "passes": 3, "formal_replay": "NOT_PERFORMED",
    }
    (ROOT / "render_binding.json").write_text(json.dumps(binding, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(binding, indent=2))


if __name__ == "__main__":
    build()
