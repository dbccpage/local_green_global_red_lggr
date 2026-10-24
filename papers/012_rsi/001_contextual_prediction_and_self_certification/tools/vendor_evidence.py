"""Check the pinned offline mathematical dependency bundle and its extracted cache."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_vendor(root: Path, *, cache_root: Path | None = None) -> dict:
    vendor = root / "lean4/vendor"
    data = json.loads((vendor / "manifest.json").read_text(encoding="utf-8"))
    archive = vendor / "dependencies.tar.gz"
    if data.get("schema_version") != 1 or data.get("toolchain") != "leanprover/lean4:v4.35.0":
        raise ValueError("INVALID_LEAN_VENDOR_MANIFEST")
    if archive.stat().st_size != data["archive_bytes"] or sha256(archive) != data["archive_sha256"]:
        raise ValueError("LEAN_VENDOR_ARCHIVE_CHANGED")
    if data["module_count"] != len(set(data["modules"])):
        raise ValueError("INVALID_LEAN_VENDOR_MODULE_COUNT")
    checked_directories: set[Path] = set()
    for relative, expected in data["files"].items():
        path = PurePosixPath(relative)
        if (path.is_absolute() or not path.parts or ".." in path.parts
                or "\\" in relative or ":" in relative or path.parts[0] not in {"lib", "source"}):
            raise ValueError("INVALID_LEAN_VENDOR_PATH")
        if cache_root is not None:
            target = cache_root.joinpath(*path.parts)
            for component in [target, *target.parents]:
                if component == cache_root.parent:
                    break
                if component != target and component in checked_directories:
                    break
                if component.is_symlink() or (component.exists() and
                        getattr(component.lstat(), "st_file_attributes", 0) & 0x400):
                    raise ValueError(f"LEAN_VENDOR_CACHE_REPARSE: {relative}")
                if component != target:
                    checked_directories.add(component)
            if not target.is_file() or target.is_symlink():
                raise ValueError(f"LEAN_VENDOR_CACHE_MISSING: {relative}")
            if target.stat().st_size != expected["bytes"] or sha256(target) != expected["sha256"]:
                raise ValueError(f"LEAN_VENDOR_CACHE_CHANGED: {relative}")
    if cache_root is not None:
        expected_marker = data["upstream"]["mathlib"]["rev"] + "\n"
        if (cache_root / "READY").read_text(encoding="utf-8") != expected_marker:
            raise ValueError("LEAN_VENDOR_CACHE_MARKER_CHANGED")
        actual = {p.relative_to(cache_root).as_posix() for p in cache_root.rglob("*") if p.is_file()}
        if actual != set(data["files"]) | {"READY"}:
            raise ValueError("LEAN_VENDOR_CACHE_FILE_SET_CHANGED")
    return data
