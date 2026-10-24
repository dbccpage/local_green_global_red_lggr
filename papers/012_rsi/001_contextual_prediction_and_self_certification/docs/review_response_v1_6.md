# Response to the supplied v1.6.0 review

Date: 2026-10-21. Version: 1.6.0.

## Section 3.3 clarification

The actual error is now explicitly defined as the common-state-space norm of the reference trajectory minus its approximation and bounded above by E(t). The displayed equality defines the upper envelope, not the actual trajectory error. E0 must bound the initial error, and the post-switch value is used at a switch instant. The existing envelope formula is unchanged. This is a clarification of the conditional comparison argument, not a new Lean ODE theorem.

The equation spine registers the added error inequality; the existing document builder regenerates Markdown-bound TeX, text, PDF and render evidence. The PDF remains 13 pages. Its title page and revised Section 3.3 were visually inspected without finding clipping or overlap. The fresh compiler log reports no missing glyphs or overfull horizontal boxes.

## Review evidence and fresh local replay

The supplied review was scoped to its attachments. Its 86 passes and four missing-file failures remain valid historical observations; it did not independently verify the new Lean modules or the author's 95-case execution comparison.

For this clarification, all 30 entries in the supplied review packet's SHA256SUMS were checked. Its current Python modules and three earlier test files match this package byte for byte. Replaying the supplied independent oracle reproduced all 9,313 small LP cases, 19 certificate checks and 16 uncertainty checks. These are finite checks, not general completeness or universal refinement proofs.

Against the complete local package, the three earlier named test files now pass all 90 tests, and the certificate/uncertainty files pass another 53: 143 total, with no failures or skips. The live 95-case Lean/Python replay also passes. The existing Lean build and 113-named-theorem census pass with only the approved axioms. These fresh local checks are separate from the external reviewer's evidence and do not retroactively extend that review's scope.

## Subsequent Lean 4.35.0 migration

At the author's request, the active paper now pins Lean 4.35.0 and the matching official Mathlib v4.35.0 revision 56a005855ea17e0b0958f73ec801ae140b0a1679. The existing verification tools, not new development gates, replay the migration. All 143 Python tests and 95 complete execution comparisons pass. The named census remains 113 theorems; the full census has 796 declarations in 13 modules. Compared with the earlier 800-declaration census, three generated decidability auxiliaries are renamed and four compiler-generated `toCtorIdx` declarations are absent. No named theorem is removed.

The four original proof modules and retained historical verification/source records are unchanged. The new runtime and command output are recorded separately in `verification_run_v160_lean435.json`. The offline bundle is rebuilt for 4.35.0 rather than relabeling old compiled artifacts. The two large archives use Git LFS for repository transport; the standalone release remains offline after installing the declared prerequisites.

## Necessary-capacity extension

The supplied capacity-exclusion prototype and its synthetic examples replay successfully, including the future exclusion interval 4 < t <= 6 and compatibility at t = 4. Its source files in the supplied review packet were not edited. The extension is not integrated into this small manuscript clarification and is not claimed as Lean-formalized.

Any application to experience still requires an independently justified necessity premise covering every admissible alternative and sound observation or forward-state enclosures. An inconsistent background is not evidence of physical absence; a compatible capacity does not establish experience; certificate expiry does not establish recovery. No clinical, human-data or consciousness-identity claim is introduced.

No DOI deposit, external publication, or new development gate is performed by this clarification.
