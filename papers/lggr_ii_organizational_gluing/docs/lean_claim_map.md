# Lean claim map

**Paper:** Local Green, Global Red II: Organizational Evaluator Gluing  
**Version:** 1.3.1  
**Checked:** 2026-10-15  
**Default build target:** `LGGR2`  
**Lean version:** `4.33.1`  
**Build result:** 11 jobs completed successfully  
**Axiom result:** 18 reports; 17 axiom-free; one uses only `Quot.sound`  
**Source scan:** no `sorry` or `admit` token in any `lean4/*.lean` source

The nested project formally mechanizes the finite Boolean, integer, conjunction, transport,
and quotient statements listed below. It does not formalize an empirical model
of any organization. The Python sample-based detector check implements the M7
premise by comparing the complete local product with `E_G`; Lean formally mechanizes the
underlying Boolean identity and the sufficient all-other-pass specialization.

## Declaration ledger

| Ledger ID | Declaration | Source | Status | Statement SHA-256 | Import-block SHA-256 |
|---|---|---|---|---|---|
| `M1` | `PaperAE005.orgDelta_range` | `lean4/03_non_additivity.lean` | `MECHANIZED` | `084c6222a8d47a7619ec0e59884ae77c6fca36a01032c81789ba1eb51858747a` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `M2` | `PaperAE005.orgDelta_is_negative_one_iff` | `lean4/03_non_additivity.lean` | `MECHANIZED` | `9492b4791fcc167f2705c6544e18a8db5f70b7f50b16d701a281f7279699f67f` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `M3` | `PaperAE005.weak_boundary_sufficiency_does_not_force_factorization` | `lean4/02_boundary_sufficiency.lean` | `MECHANIZED` | `e6a8f35cdf18328d62ac7f919aa1dd389c8af1234c4612b29809b97172462a39` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `M4` | `PaperAE005.product_sufficiency_iff_evaluator_factorization` | `lean4/02_boundary_sufficiency.lean` | `MECHANIZED` | `3ba529f63fdac4eda822566eb65265bfcedbef7997da9cf1c84311fdf0b22593` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `M5` | `PaperAE005.three_binary_defects_sum_can_leave_binary_range` | `lean4/03_non_additivity.lean` | `MECHANIZED` | `fdcff5ecc85682d4d2390124ab4b9a30053ffb00afbbadee55c7bfbe902ffbf4` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `M6` | `PaperAE005.zero_defect_does_not_imply_all_pass` | `lean4/05_detector_adequacy.lean` | `MECHANIZED` | `d26bc2949711243a818426d37f02f61b60b09c79a4ca5d62368289f4ba06b9ff` | `1ddd30b2dfe2bffcf2c09be01f71a0e9bb11137a82a12cfeed934602fa1b1b3e` |
| `M7` | `PaperAE005.aligned_validator_forces_zero_defect` | `lean4/05_detector_adequacy.lean` | `MECHANIZED` | `3dd0c5684725020ab517e532e0177891603ed35e3dce459d6525c71771fe7c9e` | `1ddd30b2dfe2bffcf2c09be01f71a0e9bb11137a82a12cfeed934602fa1b1b3e` |
| `M7` | `PaperAE005.aligned_validator_proxy_collapsing_detector` | `lean4/05_detector_adequacy.lean` | `MECHANIZED-SUPPORT` | `bf8c2e7fd90ecbac8ded3e1296eebda8512fc34e563f87ba28d09b9527a42b55` | `1ddd30b2dfe2bffcf2c09be01f71a0e9bb11137a82a12cfeed934602fa1b1b3e` |
| `M8` | `PaperAE005.boundary_carrier_mixing_blocks_quotient_factorization` | `lean4/04_carrier_boundary_obstruction.lean` | `MECHANIZED` | `5606ce40b7678ac61338d20c7bfedf010460013308fef02214afef36f01b2e6c` | `17f39545dc22a7d2697cf08dd5e6ba689e53e0c30086373a29f15a7045f6a971` |
| `M9` | `PaperAE005.boundary_carrier_mixing_forces_lggr` | `lean4/04_carrier_boundary_obstruction.lean` | `MECHANIZED` | `8625fdc9404f7192cf6bd04e0a52d01ec2b30e2566e2813885d57773f5119951` | `17f39545dc22a7d2697cf08dd5e6ba689e53e0c30086373a29f15a7045f6a971` |
| `D1` | `PaperAE005.governancePrerequisitesSatisfied` | `lean4/01_certified_closure.lean` | `MECHANIZED-DEFINITION` | `dd77364211fff3ddb462da8daed9cb471556d6228d2f64b797b1311c9d903a6c` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `D1` | `PaperAE005.governance_prerequisites_require_auth` | `lean4/01_certified_closure.lean` | `MECHANIZED` | `968615537bbb5450d9e350ddf50f6e69ebe0338f5cb2b91e595fed9d63a5e1e2` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

## Exact scope

- **M1–M2:** the signed difference of two Boolean bits and its negative case.
- **M3–M4:** one explicit weak-sufficiency counterexample and a conditional
  equivalence once weak recovery is assumed.
- **M5:** one finite witness that unrestricted scalar addition leaves the
  three-value defect range.
- **M6:** one zero-defect joint-failure witness.
- **M7:** `orgDelta eG eG = 0`; if one factor is `eG`, the supporting theorem
  assumes the remaining product is `true`. It does not say that copying one
  factor alone forces zero defect.
- **M8–M9:** quotient non-factorization and the induced negative-defect witness
  under the stated carrier-equality, mixing, and local-green hypotheses.
- **D1:** a Boolean conjunction and conjunction elimination.

## Hash convention

For each declaration, the statement hash is SHA-256 over UTF-8 source from the
declaration keyword (`theorem`, `def`, or `abbrev`) through the last non-space
character before its first `:=`. Line endings are normalized to LF. The import
hash is SHA-256 over the file's top-level `import ...` lines in source order,
each terminated by LF; a file with no import line hashes the empty byte string.
`verify_deposit.py` recomputes both columns and rejects missing, extra,
duplicated, or changed declaration rows.

## Current Lean check

The exact `lean4/*.lean`, `lakefile.lean`, `lake-manifest.json`, and
`lean-toolchain` files were copied to a short temporary path to avoid the
Windows path-length limit, then checked with:

```text
lake build LGGR2
lake env lean check_axioms.lean
```

The build completed on Lean 4.33.1 in 11 jobs. The explicit census printed 18
reports. Seventeen declarations were axiom-free;
`PaperAE005.boundary_carrier_mixing_blocks_quotient_factorization` used only
the standard quotient principle `Quot.sound`.
