# Bell positive-extension release 0.2.0

The final standalone ZIP passed verification from a clean extraction on 23 October 2026. The extraction contained no pre-existing proof cache and no sibling paper dependencies. Its default verifier freshly compiled the Bell source modules and compared every named theorem's axiom dependencies with the recorded census.

- Lean 4.35.0: 48 named theorems; no custom axioms or admitted proofs. Standard dependencies are propext, Quot.sound and Classical.choice.
- Exact Python certificate tests: 21 passed.
- Original reproduction: five exact CHSH parameters, fourteen numerical LP solves, five two-qubit matrix checks, all 64 deterministic Mermin assignments, and finite observer examples passed.
- Notebook: all Python cells executed successfully.
- Payload: 40 files plus the two manifest controls; the verifier confirmed unchanged payload bytes after all checks.
- PDF: 17 pages, source digest checked; pages 1, 3, 11, 15, 16 and 17 visually inspected.

The proof coverage includes the finite stochastic positive-extension equivalence and the arbitrary-latent-carrier averaging formulation; CHSH local, signed-extension, total-variation and uncertainty bounds; exact finite scalar observer minimax and midpoint attainment; and refinement, deterministic recursion and finite conditional-randomization error limits.

The probability-integral instance, quantum operator calculations, general LP duality, tangent-cone results and arbitrary-measure randomized expectations are outside this census. See the package's `docs/formalization.md` for exact premises and declaration mappings.

Archive: `bell_positive_extensions_v0.2.0.zip` (301812739 bytes).

SHA-256: `f104d95f7fef9ca9738e567568cd50032fd46ca6e26da01c7fe6a67ea1f9c7c2`.

The companion JSON records exact commands, working directories, timestamps, durations, extraction path and numerical tolerances. Raw command output is retained in `2026_10_23_bell_lean_logs/`. The original supplied Bell draft remains byte-preserved in the package.
