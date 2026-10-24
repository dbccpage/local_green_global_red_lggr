# Development history

The authoritative final experiment is `evaluation/`, with its unchanged source
freeze and independent protocol freeze. Final development/demo paths are named
in REPORT.md. Earlier `demo-smoke/`, `development-benchmark-smoke/`, `demo/` and
`development-benchmark/` outputs were executed before final provenance and
controller-argument hardening. Their receipts describe those earlier executions;
they are not claimed to replay against later source. They were never evaluation
labels and were not silently overwritten.

`commands/tests-final.*` retains a real failed test run (66 tests, one failure).
The old test constructed a partial fake native envelope without the newly
required planner input/response binding. It was changed to inject the same
forged local-pass fields through deterministic fixture proposals. The intended
SQL recomputation assertions remain; separate tests exercise native provenance.
`commands/tests-final-v2.*` records the subsequent 67 passing tests.

`native/pre-freeze-v0/` retains an early host trace with overly broad native
labels for deterministic effects. `native/pre-freeze-v1/` retains the corrected
native labels before the final detecting-boundary wording change. The final
`native/run.json` reexecutes the same three genuine recorded role proposals under
the final host code. These local SQL reexecutions and offline replays made no new
native model dispatch. Only planner, orders and refunds response events receive
native labels; integration and judging are deterministic host operations.

The final native role sequence was planner (`math_upstream`), followed by orders
(`adversarial`) and refunds (`math_upstream`, reused). The three role prompts were
actual collaboration turns. Engineering/review turns are separate work and not
included in the native demonstration's three-role cap or tool-attempt counts.
The roles share the parent model/context and do not establish blindness or
statistical independence. Provider token usage and monetary cost are unmeasured.

`commands/clean-extraction.*` retains an environmental failure before package
execution: Windows denied access inside the sandbox's automatically selected
temporary directory. The verification helper was changed to extract into a
fresh, ordinary directory inside this lab's `dist/`, with checked path containment
before cleanup. No frozen runtime, fixtures, oracle or test expectation changed.
The subsequent `commands/clean-extraction-v2.*` and `clean-extraction.json` record
the actual independent extraction/run results. The final archive adds these
verification receipts; the release audit binds its runtime/test/trace bytes to
those that were executed in the clean extraction.
