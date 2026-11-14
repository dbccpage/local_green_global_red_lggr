# Publication preparation review

Reviewed 2026-10-16 against source baseline `a93efbd5f432bc91f88e27d85c1ad99436147b52`.

The public candidate is **Conditional density lifts and a primal–dual alignment statistic**, version 2.0.4.
Its PDF is `density_lift.pdf`; its standalone archive is
`density_lift.zip`. No Zenodo upload or newly assigned version DOI is claimed.

## Mathematical and editorial changes

Proved the compact coordinate selector and the primal-dual trace-distance bound. Distinguished those prose proofs from discrete Lean statements. Corrected unbound or approximate zero certificates, strict integer validation and overflowed mass handling.

The public manuscript uses standard mathematical terminology and verified external
book references. Prior manuscripts, metadata and archives remain byte-for-byte
under `history/` and are excluded from the new ZIP. All deleted tracked publication
files were matched by SHA-256 against that historical copy.

## Executed validation

- Cold ZIP extraction: `python -I verify_deposit.py --lean --archive <original-archive>` passed.
- Each local `code/tests/test_*.py` was run separately with `--runxfail`, explicit writable `--basetemp`, and no cache plugin: **33 passed**, no skips.
- Pinned `leanprover/lean4:v4.33.1`: Lake build and a complete census of **43 explicit named declarations** replayed. Only the declared standard kernel axioms were allowed. Real-valued prose theorems are not represented as mechanized when the package only proves discrete cases.
- Isolated wheel installation with declared build dependencies and import from outside the repository passed.
- Markdown lint passed for all 28 active Markdown files across the four papers. Ruff correctness rules `E9,F63,F7,F82` passed for all 48 active Python files.
- PDF: **3 pages**, zero missing glyphs, zero overfull boxes above 10 pt. Every page was visually inspected. Source, TeX, PDF and renderer hashes agree.
- Complete ZIP bytes, Unix member attributes, membership, order, timestamps, both manifests and external sidecar agree with a deterministic reconstruction. Stale source, omitted census requests, extra files and resealed ZIP suffixes have rejecting regression tests.

Exact replay output, archive digest, render binding and the broader checklist
result are in [verification_results.json](verification_results.json).

## DOI lineage

DataCite verified the previous record `10.5281/zenodo.20192297`
and concept `10.5281/zenodo.20192296` on 2026-10-16. Metadata records both prior-version
and concept relationships. The new version DOI remains unassigned.

## Publication checklist limits

The repository's 52-item checklist on a clean extracted payload returned
**BLOCKED: 18 PASS, 3 FAIL, 25 NOT_VERIFIED, 6 NOT_APPLICABLE**.
The failures A03/D01/D03 require an internal mechanism inventory or retired claim
ledger and explicit test locators in public prose. The inventory rule requires
`AuthorityEffect: None`, which conflicts with the user's public-language boundary.
The public manuscript was not filled with that vocabulary to obtain a passing label.
The unverified entries include mathematical/referee assessment, runtime coverage,
render regeneration, visual review, execution evidence and author authorization;
this report records the executions actually performed without promoting imported
reports into independent verification. The package verifier is a separate bounded
integrity check and does pass.

The invoked [publication skill](../../../../../../.agents/skills/governance-research-paper-edit-publish/SKILL.md)
says publication “stops for the human author.” This is a prepared candidate for
author review, not a claim that all 52 obligations or external publication are complete.
