#!/usr/bin/env python3
"""Refresh and verify a paper package's pinned deterministic release archive.

The existing MANIFEST.sha256 defines the release file set. This tool updates
hashes for that set, writes SHA256SUMS, and rebuilds the package's single ZIP.
An explicit ``--include`` extends that set with a package-relative file. A hash
match certifies byte identity only; it does not promote any claim.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import io
import json
import re
import stat
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

LINE = re.compile(r"^([0-9a-f]{64})  (.+)$")
ZIP_DATE = (*datetime.date.today().timetuple()[:3], 12, 0, 0)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_reparse(path: Path) -> bool:
    try:
        attributes = path.lstat()
    except FileNotFoundError:
        return False
    return path.is_symlink() or bool(
        getattr(attributes, "st_file_attributes", 0) & 0x400
    )


def _regular_control(path: Path) -> None:
    attributes = path.lstat()
    if not stat.S_ISREG(attributes.st_mode) or _is_reparse(path):
        raise ValueError(f"non-regular release control: {path.name}")


def safe_file(package: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or not pure.parts or any(part in {"", ".", ".."} for part in pure.parts):
        raise ValueError(f"unsafe manifest path: {relative}")
    path = package.joinpath(*pure.parts)
    try:
        path.resolve(strict=False).relative_to(package.resolve())
    except ValueError as error:
        raise ValueError(f"escaping manifest path: {relative}") from error
    cursor = package
    for part in pure.parts:
        cursor /= part
        if _is_reparse(cursor):
            raise ValueError(f"reparse point in manifest path: {relative}")
    if path.suffix.lower() == ".zip":
        raise ValueError(f"unsupported manifest path: {relative}")
    return path


def read_manifest(path: Path, package: Path) -> list[tuple[str, str]]:
    _regular_control(path)
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw or raw.startswith("#"):
            continue
        match = LINE.fullmatch(raw)
        if match is None:
            raise ValueError(f"malformed {path.name} line {lineno}")
        digest, relative = match.groups()
        folded = relative.casefold()
        if folded in seen:
            raise ValueError(f"duplicate {path.name} path: {relative}")
        seen.add(folded)
        safe_file(package, relative)
        entries.append((relative, digest))
    if not entries:
        raise ValueError(f"empty manifest: {path}")
    return entries


def render(entries: list[tuple[str, str]]) -> bytes:
    return ("\n".join(f"{digest}  {relative}" for relative, digest in entries) + "\n").encode()


def current_entries(
    package: Path, includes: tuple[str, ...] = ()
) -> list[tuple[str, str]]:
    paths: list[str] = []
    sys_path = package / "code" / "deposit_paths.py"
    if sys_path.is_file():
        import importlib.util
        spec = importlib.util.spec_from_file_location("deposit_paths", sys_path)
        if spec and spec.loader:
            dp = importlib.util.module_from_spec(spec)
            sys.modules["deposit_paths"] = dp
            spec.loader.exec_module(dp)
            excluded_dirs = {
                ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
                ".mypy_cache", ".ruff_cache", ".ipynb_checkpoints", ".lake",
                "dist", "build", "htmlcov", "dev_rips", "rt", "target", "b", "scratch",
                "_support", "evidence", "reconstruction_v1",
            }
            excluded_names = {"SHA256SUMS", "MANIFEST.sha256", ".coverage", ".env", "DEPOSIT_CHECKLIST.md", ".gitkeep", "density_lift.zip.sha256"}
            excluded_suffixes = {".zip", ".pyc", ".pyo", ".tmp", ".log", ".aux", ".toc", ".out"}
            paths = [p.relative_to(package).as_posix() for p in dp.walk_files(package, excluded_dirs, excluded_names, excluded_suffixes)]
    elif (package / "MANIFEST.sha256").is_file():
        paths = [relative for relative, _ in read_manifest(package / "MANIFEST.sha256", package)]

    folded = {relative.casefold(): relative for relative in paths}
    for relative in includes:
        safe_file(package, relative)
        prior = folded.get(relative.casefold())
        if prior is not None and prior != relative:
            raise ValueError(f"case-folded include collision: {relative} and {prior}")
        if prior is None:
            paths.append(relative)
            folded[relative.casefold()] = relative
    paths.sort()
    refreshed: list[tuple[str, str]] = []
    for relative in paths:
        path = safe_file(package, relative)
        if not path.is_file():
            raise ValueError(f"missing release file: {relative}")
        refreshed.append((relative, sha256_file(path)))
    return refreshed


def archive_path(package: Path) -> Path:
    archives = sorted(p for p in package.glob("*.zip") if not p.name.startswith("."))
    if len(archives) == 1 and not archives[0].is_symlink():
        return archives[0]
    if archives:
        raise ValueError(f"expected one regular release ZIP, found {[p.name for p in archives]}")
    return dated_archive_path(package)


def dated_archive_path(package: Path) -> Path:
    identity = json.loads((package / "release_identity.json").read_text(encoding="utf-8"))
    name = identity["archive"]
    if Path(name).name != name or not name.endswith(".zip"):
        raise ValueError("unsafe archive filename")
    return package / name


def zip_date_from_name(package: Path, archive: Path) -> tuple[int, int, int, int, int, int]:
    identity = json.loads((package / "release_identity.json").read_text(encoding="utf-8"))
    if archive.name != identity["archive"]:
        raise ValueError(f"noncanonical release ZIP name: {archive.name}")
    day = datetime.date.fromisoformat(identity["publication_date"])
    return (day.year, day.month, day.day, 12, 0, 0)


def refresh(package: Path, includes: tuple[str, ...] = ()) -> None:
    old_archives = sorted(p for p in package.glob("*.zip") if not p.name.startswith("."))
    if len(old_archives) > 1 or any(p.is_symlink() for p in old_archives):
        raise ValueError("expected at most one regular release ZIP before refresh")
    for old in old_archives:
        zip_date_from_name(package, old)
    manifest = package / "MANIFEST.sha256"
    sums = package / "SHA256SUMS"
    for control in (manifest, sums):
        if control.exists() or _is_reparse(control):
            _regular_control(control)
    entries = current_entries(package, includes)
    manifest.write_bytes(render(entries))
    sums_entries = entries + [(manifest.name, sha256_file(manifest))]
    sums_entries.sort(key=lambda item: item[0])
    sums.write_bytes(render(sums_entries))
    archive_entries = list(sums_entries)
    archive_entries.append((sums.name, sha256_file(sums)))
    archive_entries.sort(key=lambda item: item[0])
    target_archive = dated_archive_path(package)
    zip_date = zip_date_from_name(package, target_archive)
    build_archive(package, target_archive, archive_entries, zip_date)
    target_archive.with_suffix(".zip.sha256").write_text(f"{sha256_file(target_archive)}  {target_archive.name}\n", encoding="utf-8", newline="\n")
    for old in old_archives:
        if old != target_archive:
            old.unlink()


def build_archive(
    package: Path,
    archive_path_: Path,
    entries: list[tuple[str, str]],
    zip_date: tuple[int, int, int, int, int, int] | None = None,
) -> None:
    if zip_date is None:
        zip_date = zip_date_from_name(package, archive_path_)
    with tempfile.NamedTemporaryFile(
        prefix=f".{archive_path_.stem}-", suffix=".zip", dir=package, delete=False
    ) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(
            temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as archive:
            _write_archive_entries(archive, package, entries, zip_date)
        temporary.replace(archive_path_)
    finally:
        temporary.unlink(missing_ok=True)


def _write_archive_entries(
    archive: zipfile.ZipFile,
    package: Path,
    entries: list[tuple[str, str]],
    zip_date: tuple[int, int, int, int, int, int],
) -> None:
    for relative, expected in sorted(entries):
        path = safe_file(package, relative)
        data = path.read_bytes()
        if sha256_bytes(data) != expected:
            raise ValueError(f"hash changed while building archive: {relative}")
        info = zipfile.ZipInfo(f"{package.name}/{relative}", date_time=zip_date)
        info.create_system = 3
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, data, compresslevel=9)


def _canonical_archive_bytes(
    package: Path,
    entries: list[tuple[str, str]],
    zip_date: tuple[int, int, int, int, int, int],
) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(
        output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        _write_archive_entries(archive, package, entries, zip_date)
    return output.getvalue()


def validate(package: Path, selected_archive: Path | None = None) -> list[str]:
    errors: list[str] = []
    manifest = package / "MANIFEST.sha256"
    sums = package / "SHA256SUMS"
    try:
        manifest_entries = read_manifest(manifest, package)
        sums_entries = read_manifest(sums, package)
    except (OSError, UnicodeError, ValueError) as error:
        return [str(error)]

    expected_sums = {relative: digest for relative, digest in manifest_entries}
    expected_sums[manifest.name] = sha256_file(manifest)
    if dict(sums_entries) != dict(sorted(expected_sums.items())):
        errors.append("SHA256SUMS does not equal MANIFEST.sha256 plus its digest")
    for relative, digest in sums_entries:
        path = safe_file(package, relative)
        if not path.is_file():
            errors.append(f"missing release file: {relative}")
        elif sha256_file(path) != digest:
            errors.append(f"local hash mismatch: {relative}")

    try:
        archive_path_ = selected_archive if selected_archive is not None else archive_path(package)
        if not archive_path_.is_file():
            errors.append(f"missing release archive: {archive_path_}")
            return errors
        _regular_control(archive_path_)
        sidecar = archive_path_.with_suffix(".zip.sha256")
        _regular_control(sidecar)
        if sidecar.read_text(encoding="utf-8") != f"{sha256_file(archive_path_)}  {archive_path_.name}\n":
            raise ValueError("archive sidecar mismatch")
        expected_zip_date = zip_date_from_name(package, archive_path_)
        release_day = datetime.date(*expected_zip_date[:3]).isoformat()
        metadata_path = package / "zenodo_metadata.json"
        if metadata_path.is_file():
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            if metadata.get("publication_date") != release_day:
                errors.append("metadata publication_date differs from release ZIP date")
        cff_path = package / "CITATION.cff"
        if cff_path.is_file():
            match = re.search(r"(?m)^date-released:\s*(\d{4}-\d{2}-\d{2})\s*$", cff_path.read_text(encoding="utf-8"))
            if match is not None and match.group(1) != release_day:
                errors.append("CITATION.cff date-released differs from release ZIP date")
        with zipfile.ZipFile(archive_path_) as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            archive_entries = list(sums_entries)
            if any(info.filename.endswith("/SHA256SUMS") for info in infos):
                archive_entries.append(("SHA256SUMS", sha256_file(sums)))
                archive_entries.sort(key=lambda item: item[0])
            expected_names = [
                f"{package.name}/{relative}" for relative, _ in sorted(archive_entries)
            ]
            if names != expected_names:
                errors.append("ZIP membership or ordering differs from SHA256SUMS")
            if len({name.casefold() for name in names}) != len(names):
                errors.append("ZIP contains duplicate case-folded members")
            for info, (relative, digest) in zip(infos, sorted(archive_entries)):
                pure = PurePosixPath(info.filename)
                if pure.is_absolute() or ".." in pure.parts:
                    errors.append(f"unsafe ZIP member: {info.filename}")
                if info.date_time != expected_zip_date:
                    errors.append(f"noncanonical ZIP timestamp: {info.filename}")
                if sha256_bytes(archive.read(info)) != digest:
                    errors.append(f"ZIP member hash mismatch: {relative}")
        if archive_path_.read_bytes() != _canonical_archive_bytes(
            package, archive_entries, expected_zip_date
        ):
            errors.append("ZIP envelope differs from canonical deterministic build")
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        errors.append(str(error))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic release rebuild tool.")
    parser.add_argument("package_path", nargs="?", default=".", help="Paper directory path")
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        help="package-relative file to add deliberately to each release set",
    )
    args = parser.parse_args()
    package = Path(args.package_path).resolve()
    if not package.is_dir():
        print(f"FAIL: invalid directory: {package}")
        return 1

    try:
        if not args.check:
            refresh(package, tuple(args.include))
        errors = validate(package)
    except (OSError, UnicodeError, ValueError) as error:
        errors = [str(error)]

    if errors:
        for error in errors:
            print(f"FAIL {package.name}: {error}")
        return 1
    print(f"OK {package.name}: manifests and deterministic ZIP agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
