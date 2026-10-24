#!/usr/bin/env python3
"""Generate publication metadata from manifest.json; check active release parity."""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def generated(root: Path) -> dict[str, str]:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    publication = manifest["publication"]
    metadata = {
        "title": manifest["title"],
        "upload_type": "publication",
        "publication_type": "preprint",
        "publication_date": manifest["date"],
        "version": manifest["version"],
        "access_right": "open",
        **publication,
    }
    encoded = json.dumps(metadata, ensure_ascii=False, indent=2) + "\n"
    paragraphs = re.findall(r"<p>(.*?)</p>", publication["description"], re.S)
    description = "# Publication description\n\n" + html.unescape("\n\n".join(paragraphs)) + "\n"
    return {".zenodo.json": encoded, "zenodo_metadata.json": encoded,
            "docs/descriptions.md": description}


def check(root: Path) -> list[str]:
    errors = []
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    for name, expected in generated(root).items():
        path = root / name
        if not path.is_file() or path.read_text(encoding="utf-8") != expected:
            errors.append(f"Generated publication metadata is stale: {name}")
    text = (root / (manifest["paper"] + ".md")).read_text(encoding="utf-8")
    title = re.search(r'^title: "(.+)"$', text, re.M)
    subtitle = re.search(r'^subtitle: "(.+)"$', text, re.M)
    if title is None or subtitle is None or f"{title[1]}: {subtitle[1]}" != manifest["title"]:
        errors.append("Manuscript title/subtitle differs from manifest")
    for field in ("date", "version"):
        if f'{field}: "{manifest[field]}"' not in text:
            errors.append(f"Manuscript {field} differs from manifest")
    readme = (root / "README.md").read_text(encoding="utf-8")
    for marker in (f'**Date:** {manifest["date"]}', f'**Version:** {manifest["version"]}', subtitle[1] if subtitle else ""):
        if not marker or marker not in readme:
            errors.append(f"README release identity is stale: {marker}")
    project = (root / "pyproject.toml").read_text(encoding="utf-8")
    if f'version = "{manifest["version"]}"' not in project or manifest["title"] not in project:
        errors.append("Python project version/title differs from manifest")
    if 'license = "Apache-2.0"' not in project:
        errors.append("Python code license must match LICENSE-CODE (Apache-2.0)")
    if "Apache License" not in (root / "LICENSE-CODE").read_text(encoding="utf-8"):
        errors.append("LICENSE-CODE does not contain the selected Apache license")
    if "Attribution 4.0 International" not in (root / "LICENSE").read_text(encoding="utf-8"):
        errors.append("LICENSE does not contain the selected CC BY 4.0 license")
    rights = manifest["publication"]["rights"]
    if manifest["publication"]["license"] != "cc-by-4.0" or [r["id"] for r in rights] != ["cc-by-4.0", "apache-2.0"]:
        errors.append("Publication license scopes differ from the shipped licenses")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        if not args.check:
            for name, content in generated(ROOT).items():
                (ROOT / name).write_text(content, encoding="utf-8", newline="\n")
        errors = check(ROOT)
    except (OSError, ValueError, KeyError) as error:
        errors = [str(error)]
    for error in errors:
        print(f"FAIL: {error}")
    if not errors:
        print("OK: canonical publication metadata, identity, and license scopes agree.")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
