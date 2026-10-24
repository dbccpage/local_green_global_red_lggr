# Consolidation into the two RSI papers

The records below describe their dated earlier editions. The current version 1.7.0 integration and paired version 1.1.0 companion are mapped in [embedded_research.md](embedded_research.md); current replay evidence is [embedded_verification.json](embedded_verification.json). Historical hashes and test counts are not reassigned.


The redundant `001_finite_obstruction_calculus/002_asi_no_go_theorem_epistemic_contextuality` package was retired on 22 October 2026. Its results already have an active home in this paper. The first RSI paper retains its current relational-reasoning and finite-horizon treatment. No third active paper or duplicate proof development is introduced.

## Where the material belongs

| Precursor material | Current home and boundary |
| --- | --- |
| Observation collisions and the failed inference from instantaneous loss to permanent privacy | This paper, section 3, `ResultII.lean` and `Bridge.lean`. The general finite-word preservation criterion is already proved here; it supplies the interface to memory research associated with paper 000. |
| Contextual probability tables, global sections and positive incompatibility witnesses | This paper, section 2, `ResultI.lean`, `ContextualDuality.lean`, the exact simplex and its independent certificate checkers. |
| Valid ledger prefixes, incomplete histories, relabeling invariance and self-certification limits | This paper, section 4 and `ResultIII.lean`; the pinning and digest-collision premises remain explicit. |
| Role identifiers, policy acceptance and delegated standing | This paper, section 5, `ResultIV.lean` and the unsafe-action counterexample in `Bridge.lean`. Policy acceptance does not prove semantic action safety. |
| Relational reasoning, bounded report trajectories and carrier budgets | [Paper 000](../../000_relational_reasoning_and_rsi_impossibility/README.md), in its currently checked-out version 1.0.0. Its earlier cited projection-recovery edition is not recreated by this consolidation. |
| Broad self-knowing claims, philosophical commentary and withdrawn claims | Retained only as attributed historical prose. The current conditional statements govern the successor; a general impossibility of intelligence, learning or self-knowledge is not inferred. |

The series treats records, agents, evaluators and measuring devices as parts of the world. A tip held outside one ledger is another physical record, not an observer outside the world. No qualia premise is required by these mathematical statements.

## Preserved source and corrections

The original monograph, README, mechanization map and bibliography were already retained byte for byte. This consolidation additionally preserves the [original correction log](precursor_change_log.md) and [superseded floating-point listings](precursor_legacy_float_kernel_listings.md). The latter are a historical defect archive, not executable dependencies or current evidence. Their old commands, scope labels and claims are not instructions for this package.

All four `ResultI` through `ResultIV` proof modules and the original 26-test file remain byte-identical to the precursor. The successor kernel has only its previously documented explanatory corrections and refusal of unknown certificate-basis strings relative to that kernel. Its stronger LP solver and proof modules were already present before this consolidation.

The [35-file disposition inventory](source_consolidation.json) binds the source bytes observed before removal, their original adaptation hashes, and the retained or superseding destination for each item. `source_lineage.json` keeps its original capture hashes. The loose precursor's toolchain identifier had changed after capture; that metadata difference is recorded explicitly rather than rewriting the original capture. Historical manifests, release wrappers and the old ZIP are superseded by the standalone successor package.

## Edition boundary

Version 1.6.1 is an editorial and packaging correction. It updates references to the removed directory and completes historical source custody. Solver definitions, proof statements, empirical assumptions and test definitions are unchanged. Existing dated reviews and verification reports continue to describe their own source versions. The series research dossier remains a separate research artifact, and this consolidation does not integrate it into either release or claim a live memory connection.
