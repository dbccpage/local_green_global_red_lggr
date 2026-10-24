# Glossary

**AuthorityEffect: None.** These words mean what the `lggr` receipts mean on a supplied finite table. They are not a permission to merge, deploy, or spend.

**Carrier.** The states you actually handed the monitor. A decoder or a ceiling is about those rows. Unobserved states stay unobserved.

**Report.** What the next stage is allowed to see. In the fiber monitor this is the argument named `report`. Two states with the same canonical report are in one fiber.

**Query.** The protected question. The monitor does not invent it from a local pass. You declare it.

**Fiber.** The set of supplied states that share one report. The query is constant on a fiber when every state in it has the same query. Otherwise the receipt carries a colliding pair.

**Decoder.** A map from realized reports to queries that agrees with the supplied table. `DECODER_VERIFIED` says that map exists for the rows you submitted. It does not extend the table.

**Global sample.** A 0/1 verdict for the declared global question, supplied from outside the stage that proposes the step. `evaluator_defect` computes `Delta_E = E_g - E_1 E_2` in `{-1, 0, 1}`.

**NGD, ZDR, PGD.** The Volume I–III names for that delta. `NGD` (`-1`) is local green and global red. `ZDR` (`0`) is agreement, including joint rejection. `PGD` (`+1`) is local red and global green. Volumes V–VI use a different convention, where all-green means zero observed defect scores. Lessons 02 and 06 use the I–III delta. Do not swap the two conventions when you read those volumes.

**LGGG and LGGR.** Contract labels on the streaming monitors. `COMPOSABLE_LGGG` means that, on the rows so far, the check the monitor was given still holds. `OBSTRUCTED_LGGR` means a collision, a defect, a prefix breach, or another declared failure has been seen. The label is about the supplied stream.

**Endpoint and every prefix.** `query_scope="endpoint"` asks whether the final signed total stays inside the bound. `query_scope="every_prefix"` asks whether every partial total does. `0 → 1 → 2 → 1` with bound 1 can pass the endpoint query and fail the prefix query. `BudgetPolicy` defaults to endpoint because that is the source report's question. Pick the scope that matches the requirement you have.

**Closure and exactness.** A cycle defect is the signed sum of edge values around a closed loop. Exact rational ℓ1 repair distance is the certified cost of changing those values onto a coboundary. `EXACT` on `classify_cochain` means the cochain is a coboundary in the supplied complex. That is a different claim from "the swarm is wrong about the world."

**Retraction.** `verify_transport` checks a commuting square. Forward commutation preserves repairs. A checked left inverse is what carries nonrepairability the other way. A lossy map can commute and still leave reflection uncertified.

**Fiber width and half-spread.** For a target `f` and a report fiber, the width is the max of `f` on that fiber minus the min. The half-spread is half of that. `StreamingRSIFiberCeilingMonitor` checks generations of a predictor that factors through a fixed report. On those generations the worst-case error stays at or above the half-spread. A refined report that splits the fiber can lower it. A declared domain restriction is the other move that changes which states are in the carrier. Another internal generation that still sees the same report does not.

**Three stop reasons.** Lesson 08 uses the finite transition harness's names as a reading of receipts this package emits. `REPORT_COLLISION` is lesson 01. `LIFT_BUDGET_EXHAUSTION` is the budget stop in lesson 03. `OVERLAP_GLUING_REFUSAL` is the cycle defect or the missing retraction in lessons 04 and 05. Adding agents can delay a repeated report out to the product of the report-alphabet sizes. The joint report still only carries that product alphabet. The machine-checked statements live in paper 000. This course does not reimplement that harness.

**Authority and obligations.** Identifiers on a policy are supplied names, not authentication. A changed authority id or policy digest yields `AUTHORITY_REQUIRED` on the witness audit. An open obligation is retained. `audit_history` then uses status `WITNESS_INCOMPLETE`. The streaming summary can still list the obligation next to a greener primary status. Read `unresolved_obligations` either way. No API in this course clears the list.

**Two signals.** The stage that proposes a change is not the stage that supplies the global sample. A panel the swarm selects is evidence the host may read. It is not a grant. `AuthorityEffect` on every receipt in this course is the string `None`.

**Institutions.** Paper 002 studies records that keep a disagreement available for later comparison. Its four-role council protocol remains proposed. This course does not run a council. The operational piece you can use today is the obligation list and the external global sample: do not collapse two different queries into one pass, and do not let the proposer sign that pass.
