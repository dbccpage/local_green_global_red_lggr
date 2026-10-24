"""Build a deterministic, byte-manifested source/evidence archive."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)

def included(path):
    rel = path.relative_to(ROOT)
    return (path.is_file() and "__pycache__" not in rel.parts and rel.parts[0] != "dist"
            and path.suffix not in (".pyc", ".olean", ".ilean")
            and not rel.as_posix().startswith("evidence/upstream/tmp/")
            and rel.as_posix() != "MANIFEST.sha256")

files = sorted(p for p in ROOT.rglob("*") if included(p))
manifest = "".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}\n" for p in files)
(ROOT / "MANIFEST.sha256").write_text(manifest, encoding="utf-8", newline="\n")
files.append(ROOT / "MANIFEST.sha256")
archive = DIST / "lggr-swarm-lab-2026-10-24.zip"
with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for path in sorted(files):
        name = "grok_swarm_lab/" + path.relative_to(ROOT).as_posix()
        info = zipfile.ZipInfo(name, (2026, 10, 24, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        z.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
sha = hashlib.sha256(archive.read_bytes()).hexdigest()
(DIST / (archive.name + ".sha256")).write_text(f"{sha}  {archive.name}\n", encoding="utf-8")
print(json.dumps({"archive":str(archive),"sha256":sha,"members":len(files),"archive_bytes":archive.stat().st_size,
                  "uncompressed_bytes":sum(p.stat().st_size for p in files)}))
