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
        doi = identity.get("doi")
        if identity.get("status") == "prepared_revision":
            if doi is not None or meta.get("doi") is not None:
                raise ValueError("Prepared revision must not claim an assigned DOI")
        elif identity.get("status") == "published_record_verified":
            if not isinstance(doi, str) or not re.fullmatch(r"10\.5281/zenodo\.\d+", doi) or meta.get("doi") != doi:
                raise ValueError("Published DOI identity mismatch")
            record = json.loads((root / "docs/publication_record.json").read_text(encoding="utf-8"))
            if (record.get("record_doi") != doi or record.get("concept_doi") != identity.get("concept_doi") or
                    record.get("status") != "published" or record.get("datacite_state") != "findable" or
                    record.get("publication_date") != meta["publication_date"] or
                    record.get("doi_url") != "https://doi.org/" + doi):
                raise ValueError("Published record binding mismatch")
            if (identity.get("local_artifact_state") != "doi_metadata_refresh_not_uploaded" or
                    record.get("local_refresh_uploaded") is not False):
                raise ValueError("Local DOI refresh must remain distinct from deposited bytes")
            citation = (root / "CITATION.cff").read_text(encoding="utf-8")
            for key, value in (("doi", doi), ("version", meta["version"]), ("date-released", meta["publication_date"])):
                if not re.search(r"(?m)^" + re.escape(key + ": " + value) + r"$", citation):
                    raise ValueError("Citation metadata mismatch: " + key)
            if "https://doi.org/" + doi not in text:
                raise ValueError("Manuscript omits the version DOI")
        else:
            raise ValueError("Unsupported publication state")
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
