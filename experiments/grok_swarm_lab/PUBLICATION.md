# Verified experiment distribution

The experiment source, report and evidence were included byte for byte in
commit `2d7e0aa95106fe2349cf0f18c3e262c2e2a3167c`, merged through PR #47
as `103daa366d4cd9ef06fc0def10edee497f547d8e`. PR #49 subsequently removed
those unpacked files from Git tracking as part of its scratch-directory cleanup.

This publication retains the complete experiment in the original verified
[source/evidence ZIP](dist/lggr-swarm-lab-2026-10-24.zip) and its
[SHA-256 checksum](dist/lggr-swarm-lab-2026-10-24.zip.sha256). The archive
contains 1,014 members and is 6,093,877 bytes. SHA-256:

```
fd233b5e24a388c996a0fc4a63a53175efce6dad89c412a169b487b68da26a9a
```

All 1,014 archive members match the earlier committed files exactly. Inside the
archive, `MANIFEST.sha256`, frozen protocol/controller records and source
manifests describe that sealed distribution. Publication metadata and the
archive itself sit outside that original manifest. No archived source or trace
has changed. The five generated Lean `.olean` outputs swept into PR #47 are
excluded from the archive; their source and compilation logs remain inside it.

To inspect or run the distribution with Python 3.10 or newer, start in this
publication directory and extract into a new directory:

```text
python -m zipfile -e dist/lggr-swarm-lab-2026-10-24.zip dist/extracted
cd dist/extracted/grok_swarm_lab
python -m unittest discover -s tests -v
python -m lggr_swarm_lab demo --output demo-results
```

The extracted `REPORT.md` contains the six-part report and null B/C comparison;
`README.md` documents offline benchmarking and replay. No API key is required.
The archive's `evidence/completion-audit.json` binds its runtime, tests and final
traces to the recorded clean execution: 67 application tests passed, the repeated
48-case evaluation matched, and interactive, fixed-trace and native-proposal
replay passed. PR #48 review also reran all 67 tests from a fresh extraction and
replayed one native, one interactive and one fixed trace successfully.

The report retains two failing original pinned upstream tests and a separate,
changing-checkout diagnostic with four failures. Those historical results are
not claims of passing hosted CI or a completely passing current upstream suite.
The root martingale receipt repairs in PR #48 do not modify the archived runtime,
which remains pinned to its original LGGR dependency.
