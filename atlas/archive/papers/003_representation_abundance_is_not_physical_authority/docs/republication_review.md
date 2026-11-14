# Republication review repair: 2026-10-10

Prepared version: 2.1.2. Reviewed base: df84a59644c2a6837756273ccedd7b1233525407.

| Review issue | Repair |
| :--- | :--- |
| Extra reverse cochain values bypass local checks. | One stored orientation per edge, canonical signed traversal, rejection of extra values and tolerances. |
| Zero-tolerance sharpness and backtracking walks. | Zero attains zero. False-green and sharpness constructions require edge-simple cycles; the general closed-walk upper bound remains. |
| Swapped retained predictions pass plenitude extension checks. | Retained candidate content is unchanged by identifier, including hidden model parameters. |
| Candidate receipts are promoted to ACCEPTED without family context. | Candidate receipts remain SURVIVOR. FamilySelectionResult binds evidence ID, declared alternatives, family verdict, and selected ID. |
| Lean support is narrower than the written statements. | Manuscript and ledger separate written proofs, eight supporting mechanized components, and unmechanized graph/family correspondences. |
| Property identification is conflated with model uniqueness. | Written observation-factorization proposition and shared-property/local-flag examples; no new Lean mechanization claimed. |
| Counts, DOI metadata, and release checks disagree. | 33 core regressions and 23 integrity cases; version DOI pending, concept lineage retained; canonical ZIP and post-subprocess custody checks. |

## Scoped verification

Python 3.12.10: all four added reviewer regressions failed on the reviewed core before repair. After repair, 33 core tests and 23 synthetic release-integrity cases passed. The integrity fixtures test controlled mutations; they do not assert that a published archive was corrupt.

The named verification command completed with exit 0:

```powershell
py -3.12 verify_deposit.py --test code/tests/test_representation_abundance.py --test code/tests/test_release_integrity.py --lean
```

Lean 4.33.1 compiled a byte-checked source copy in a short temporary directory, avoiding a native Windows path-length failure. The census covered all eight expected supporting declarations with only the allowed standard kernel axioms. This does not mechanize the full rational graph, family quotient, or selector semantics.

The 14-page PDF was rebuilt from canonical Markdown. All 32 TOC destinations matched rendered page indices, with zero missing-character or overfull-box warnings. Compiler log, auxiliary, and TOC files are retained in the release.

The selected archive is separately checked using:

```powershell
py -3.12 tools/rebuild_release.py . --check
```

The check does not regenerate its input. The final archive is also qualified from an isolated extraction; the original ZIP is copied into that paper directory so the verifier checks that selected object as well as its extracted payload.

No full repository test suite, Rust replay, external empirical validation, Zenodo upload, public-record comparison, or publication was performed. The checklist gate checked repository metadata only: 9 channels, 52 checks, AuthorityEffect None.

## Checked source digests

```json
{
  "code/mod_representation_abundance_core.py": "6cea299bc3ca21c5209b13bde29a4dfb51bce79a248715bebdea0d4c3e31d80c",
  "code/deposit_paths.py": "d25f89869ba386966b6c3dd425a40962446763bf08d6129ced3c75c79d707939",
  "code/tests/test_representation_abundance.py": "cafe29cf957ffcbfa80ad1c8c7b398b1a6d6b9f0c512c644d945794e975bf5ba",
  "code/tests/test_release_integrity.py": "b91dd0fb8f1d733f73dfedb5335b5198fce038bd5addd1752a24df5e589edc61",
  "lean4/Representation.lean": "f7e513883be1f5a7f2b64da2ec35b4ad4fc0fe406abf5c1e35c743c0be32cf85",
  "lean4/Census.lean": "1304776c8ca133daf5fb9399a02a3f81f32ce9243d837a98a740f7b7809fc741",
  "verify_deposit.py": "68fc59577f8fd1dbab57d59f66389e3cdb716c0b6358812b34d86b5a29776533",
  "tools/rebuild_release.py": "82fb7330636940bb69a87a3113b55a72b3fc9d032d7f9d964f33357ddfda3e7c",
  "representation_abundance_is_not_physical_authority.md": "ea398bd72cf91cd57bbe63a1bf7032a100942932fb53c40be44981f08e2f62d6",
  "representation_abundance_is_not_physical_authority.pdf": "afe17bf162a387c6e989fbea2bb6c185b6489ba2d249fc489f5e5de96ff3c1ce"
}
```

## Title-block follow-up

The title block now contains only Author, Date, and Version, each on its own line. The PDF was rebuilt and its title block, TOC destinations, and compiler warnings were checked again. Executable Python, tests, verifier, release tool, and Lean sources remain byte-identical to commit dbb169f77; their previously recorded test/build results are retained without another test run. The revised archive is checked for canonical bytes and payload integrity from an isolated extraction.
