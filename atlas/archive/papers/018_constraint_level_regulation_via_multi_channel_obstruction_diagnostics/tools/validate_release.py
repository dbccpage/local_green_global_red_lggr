"""Validate reader-facing identity, render bindings and publication boundaries."""
import hashlib
import json
import re
from pathlib import Path


def validate_metadata(root: Path) -> list[str]:
    try:
        identity = json.loads((root / "release_identity.json").read_text(encoding="utf-8"))
        meta = json.loads((root / "zenodo_metadata.json").read_text(encoding="utf-8"))
        for key in ("title", "version", "publication_date", "creators", "upload_type", "publication_type"):
            if identity[key] != meta[key]:
                raise ValueError(f"Release identity mismatch: {key}")
        text = (root / identity["manuscript"]).read_text(encoding="utf-8")
        rows = re.findall(r'^<div align="center">(.+)</div>$', text, re.M)
        expected = ["# " + meta["title"], "Jeremy H. Carroll", meta["publication_date"], "Version " + meta["version"]]
        if rows != expected or not text.split("\n\n", 1)[1].startswith("## Abstract"):
            raise ValueError("Noncanonical header or metadata/source mismatch")
        for item in meta.get("related_identifiers", []):
            if not all(item.get(key) for key in ("identifier", "relation", "resource_type", "scheme")):
                raise ValueError("Incomplete related identifier")
        if identity.get("doi") is not None or meta.get("doi") is not None:
            raise ValueError("Prepared revision must not claim an assigned DOI")
        if not identity.get("concept_doi") or not any(
            item["relation"] == "isVersionOf" and item["identifier"] == identity["concept_doi"]
            for item in meta.get("related_identifiers", [])
        ):
            raise ValueError("Missing verified concept DOI lineage")
        readers = [root / identity["manuscript"], root / "README.md", *sorted((root / "docs").glob("*.md"))]
        forbidden = re.compile(r"AuthorityEffect|sovereign|FOC-\d|\bEPK\b|\bLGGR\b|QHeld|Q-gated|PaperAF000|ENC-\d|firewall|local-green|global-red|terminalizer|jurisdiction", re.I)
        for path in readers:
            content = path.read_text(encoding="utf-8")
            if forbidden.search(content):
                raise ValueError(f"Internal terminology in public text: {path.name}")
        for name in ("descriptions", "references", "keywords", "quick_start"):
            if (root / "docs" / (name + ".md")).stat().st_size < 100:
                raise ValueError(f"Stub documentation: {name}")
        description = (root / "docs/descriptions.md").read_text(encoding="utf-8")
        if "$" in description or re.search(r"<[a-zA-Z]|\\[a-zA-Z]", description):
            raise ValueError("Description must use plain Unicode text")
        binding = json.loads((root / "render_binding.json").read_text(encoding="utf-8"))
        stem = Path(identity["manuscript"]).stem
        bound = {stem + ext for ext in (".md", ".tex", ".pdf")} | {"scripts/build_pdf.py", "scripts/paper_code_wrap.lua"}
        if set(binding["sha256"]) != bound:
            raise ValueError("Incomplete render binding")
        for name, expected_digest in binding["sha256"].items():
            if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected_digest:
                raise ValueError(f"Stale render binding: {name}")
        if binding["missing_glyphs"] or binding["overfull_hbox_gt_10pt"] or binding["pages"] < 1:
            raise ValueError("Unclean publication PDF")
        source_digest = hashlib.sha256((root / identity["manuscript"]).read_bytes()).hexdigest()
        if not (root / (stem + ".tex")).read_text(encoding="utf-8").startswith(f"% manuscript-sha256: {source_digest}\n"):
            raise ValueError("TeX does not bind the current source")
    except (OSError, ValueError, KeyError, TypeError) as error:
        return [str(error)]
    return []
