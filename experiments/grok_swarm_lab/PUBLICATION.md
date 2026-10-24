# Verified experiment distribution

The experiment source, report and evidence were already included byte for byte
in commit `2d7e0aa95106fe2349cf0f18c3e262c2e2a3167c`, merged through PR #47
as `103daa366d4cd9ef06fc0def10edee497f547d8e`.

This publication adds the original verified [source/evidence ZIP](dist/lggr-swarm-lab-2026-10-24.zip)
and its [SHA-256 checksum](dist/lggr-swarm-lab-2026-10-24.zip.sha256). The archive
contains 1,014 members and is 6,093,877 bytes. SHA-256:

```
fd233b5e24a388c996a0fc4a63a53175efce6dad89c412a169b487b68da26a9a
```

All 1,014 archive members match the earlier committed files exactly. The
original `MANIFEST.sha256`, frozen protocol/controller records and source
manifests describe that sealed distribution. Publication metadata and the
archive itself sit outside that original manifest; no frozen source or trace
is changed. A scoped `.gitattributes` prevents newline conversion on checkout.
Five generated Lean `.olean` outputs accidentally swept into PR #47 are removed;
their exact source and successful compilation logs remain.

The archive's runtime, tests and final traces are bound to the clean execution
by `evidence/completion-audit.json`: 67 application tests passed; the repeated
48-case evaluation matched; interactive, fixed-trace and native-proposal replay
passed. The report retains two failing original pinned upstream tests and a
separate, changing-checkout diagnostic with four failures. Those are not claims
of passing hosted CI or a completely passing upstream suite.

See [REPORT.md](REPORT.md) for the null B/C comparison and
[README.md](README.md) for offline run commands. No API key is required.
