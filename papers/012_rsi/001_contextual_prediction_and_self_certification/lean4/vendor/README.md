# Offline mathematical dependencies

`dependencies.tar.gz` contains the import closure used by the deposited LP proofs: Mathlib and its needed libraries, source files, upstream licenses and pins, and matching Lean 4.35.0 compiled artifacts. `manifest.json` enumerates each file's SHA-256 and size, the exact module set, upstream revisions, and archive digest. The bundle was built and tested on Windows. Upstream licenses apply to these dependencies independently of the paper's code license.

Lake extracts this archive into `lean4/.lake/vendor`; no remote dependency is configured. `tools/vendor_evidence.py` verifies the archive and the extracted cache. The pinned official Mathlib v4.35.0 revision is `56a005855ea17e0b0958f73ec801ae140b0a1679`. The toolchain must match the artifact version. Sources are supplied for rebuilding on other hosts.

The dependency archive and complete dated release ZIP are stored with Git LFS because they exceed GitHub's ordinary blob limit. Run `git lfs pull` after cloning to materialize those exact bytes before verification. The downloaded standalone ZIP itself needs neither Git nor Git LFS.
