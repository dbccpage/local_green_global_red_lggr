# Prompt — Round 5: Rust Code Implementation, Witness Test Suite & Lean 4 Proof Discharge

**Campaign ID:** `FABLE_5_1_QUANTUM_RELATIONAL_RSI_DERIVATION`  
**Target Model:** `claude-fable-5-1`  
**Round:** 5 (Tooling & Implementation Pass)  
**Governing Papers:** Monograph 012-000 (`012_rsi`) & Paper 006 (`006_finite_qm`)  
**Authority Notice:** *AuthorityEffect: None. This prompt establishes formal mathematical specifications, executable Rust code, and Lean 4 proof scripts. It carries no operational authority or institutional standing.*

---

## Host Execution Fence & Claim Discipline

```text
This process did not run Lean, Cargo, or a local solver. It has no tool channel.
Do not cite earlier text as an external empirical receipt.
Apply strict claim hygiene:
- State what is supported, what is not supported, the narrowest defensible claim, and the next check.
- Avoid forbidden promotional vocabulary (do not use: proves, guarantees, mathematically verifies,
  fundamentally, true intelligence, impossible, universal, flawless, perfectly, clearly, obviously,
  simply, merely, weaponized).
- Prefer 'shows in this model', 'guarantees under the declared assumptions', 'failure mode',
  'bounded no-go', 'checked by this oracle/test'.
```

---

## Round 5 Directives: Full Code Implementation & Proof Discharge

In Round 4, the composite synthesis and architecture were established, but stubs (`unimplemented!()`) remained in Rust and `sorry` markers remained in Lean 4.
This round completes the implementation pass by providing fully realized, compilable, self-contained code and proof scripts.

### 1. Complete Rust Implementation (`omega_quantum_physics::cptp_trajectory_verifier`)
Provide the complete, compilable contents of `cptp_trajectory_verifier.rs` (compatible with `num-rational = "0.4"`, `num-bigint = "0.4"`, and `num-traits = "0.2"`). Every method stub must be fully implemented with zero `unimplemented!()` calls:
1. `Matrix`:
   - `identity(n: usize) -> Self`
   - `matmul(&self, b: &Matrix) -> Matrix`
   - `dagger(&self) -> Matrix`
   - `add(&self, b: &Matrix) -> Matrix`
   - `trace(&self) -> QC`
2. `KrausChannel`:
   - `apply(&self, rho: &Matrix) -> Matrix`
   - `is_tp(&self) -> bool`
   - `is_unital(&self) -> bool`
3. `SimplicialNerve`:
   - `edges(&self) -> Vec<(usize, usize)>`
   - `phi_glue(&self) -> usize` (exact minimal edge mismatch search over support assignments)
   - `parity_class_nonzero(&self) -> bool` (GF(2) Gaussian elimination checking whether the all-ones context vector lies outside the incidence row space)
4. `RationalInterval`:
   - `ln_ratio(p: &Q, q: &Q, n: usize) -> Self` (Taylor series with exact tail bound $\frac{2x^{2n+3}}{(2n+3)(1-x^2)}$ where $x = \frac{q-p}{q+p}$)
   - `entropy_nats_diag(spectrum: &[Q], precision: u32) -> Self`
5. `mod tests`:
   Provide complete, runnable implementations of the 7 witness tests:
   - `qubit_m2_modal_collision_at_3`: Qubit $M=2$ POVM collision at $k^*=3$.
   - `bell_panel_m4_collision_at_5`: Bell state panel $M=4$ collision at $k^*=5$.
   - `werner_amplitude_damping_budget_2`: Werner state with $B_0=2$ terminating at 3rd purification attempt via `LiftBudgetExhaustion`.
   - `dephasing_fixes_diag_3_5_2_5`: Dephasing leaves $\operatorname{diag}(3/5, 2/5)$ invariant with $P_2 = 13/25$.
   - `cabello_phi_glue_is_1_parity_nonzero`: Cabello 18-ray system yields $\Phi_{\mathrm{glue}} = 1$ and `parity_class_nonzero == true`.
   - `two_node_tau1_refusal_at_2`: Two-node communicating complex with $\tau=1$ yields `latency_defect == 1` at $k=2$.
   - `entropy_diag_3_5_2_5_enclosure`: Certified enclosure with $L = \frac{13904738765}{20661046784}$ and $U = \frac{1911955961409}{2840893932800}$.

### 2. Complete Lean 4 Proofs (`OmegaQuantumRelationalRsi`)
Provide the complete, self-contained Lean 4 module discharging all `sorry` markers from Round 4:
1. `report_collision_horizon`: Complete the proof using `Fintype.exists_ne_map_eq_of_card_lt`, chain dominance under `hstep`, and `no_dominance_of_report_eq`.
2. `lift_budget_exhaustion`: Complete the well-founded induction proof on $\mathbb{N}$ showing that a strictly decreasing non-negative integer budget cannot experience more than $B_0$ purification steps.
3. `quantum_rsi_bounded_horizon`: Assemble the composite theorem combining `report_collision_horizon` and `lift_budget_exhaustion` without `sorry`.
Ensure only standard axioms (`propext`, `Quot.sound`, `Classical.choice`) are referenced.

---

## Required Response Format

Structure your response as an exhaustive, fully realized implementation record:
1. **Rust Implementation:** Complete, standalone `cptp_trajectory_verifier.rs` file ready to be saved and compiled with `cargo test`.
2. **Lean 4 Proofs:** Complete `OmegaQuantumRelationalRsi/Core.lean` file with all proofs discharged.
3. **Execution Instructions & Expected Receipt:** Exact cargo command and expected output.
4. **JSON Checkpoint Block:** End with a fenced ` ```json ` block containing:
   - `campaign_id`: `"QUANTUM_RELATIONAL_CPTP_TRAJECTORY_VERIFICATION"`
   - `round`: `5`
   - `status`: `"VERIFIED_IMPLEMENTATION_AND_PROOFS_COMPLETE"`
   - `rust_source`: `"omega_quantum_physics/src/cptp_trajectory_verifier.rs"`
   - `lean_source`: `"OmegaQuantumRelationalRsi/Core.lean"`
   - `tests_discharged`: list of 7 tests
   - `theorems_discharged`: list of 3 Lean 4 theorems
   - `claim_hygiene`: final 4-part summary.
