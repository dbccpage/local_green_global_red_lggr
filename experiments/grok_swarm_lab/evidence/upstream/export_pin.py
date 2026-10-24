"""Export byte-exact Python dependency blobs; requires the containing Git checkout."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

PIN = "6910e0730c44bc37a65c44d3f7a5c9f2d7bf6a85"
LAB = Path(__file__).resolve().parents[2]
ROOT = LAB.parents[1]


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def main() -> None:
    entries = git("ls-tree", "-r", "--name-only", PIN, "lggr").decode().splitlines()
    entries = [p for p in entries if p.endswith(".py")] + ["LICENSE"]
    files = []
    for path in entries:
        blob = git("show", f"{PIN}:{path}")
        out = LAB / "vendor" / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(blob)
        git_blob = hashlib.sha1(f"blob {len(blob)}\0".encode() + blob).hexdigest()
        expected_blob = git("rev-parse", f"{PIN}:{path}").decode().strip()
        if git_blob != expected_blob:
            raise RuntimeError(f"Git blob mismatch: {path}")
        files.append({"upstream_path": path, "bundled_path": f"vendor/{path}",
                      "size_bytes": len(blob), "git_blob_sha1": git_blob,
                      "sha256": hashlib.sha256(blob).hexdigest()})
    manifest = {"schema": "grok-swarm-lab.upstream-source.v1",
                "repository": "https://github.com/dbccpage/local_green_global_red_lggr",
                "reviewed_commit": PIN,
                "checkout_commit_at_export": git("rev-parse", "HEAD").decode().strip(),
                "dependency_modified": False,
                "export_scope": "Tracked lggr/*.py recursively and root LICENSE only",
                "files": files}
    destination = LAB / "evidence" / "upstream" / "vendor_manifest.json"
    destination.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(files), "bytes": sum(f["size_bytes"] for f in files),
                      "pin": PIN, "manifest": str(destination)}, indent=2))


if __name__ == "__main__":
    main()
