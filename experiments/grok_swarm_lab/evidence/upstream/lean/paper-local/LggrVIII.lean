/-!
# Local Green, Global Red VIII: Online Streaming Discovery, Prefix Admissibility, and Runtime Gluing

AuthorityEffect: None.

Formalization of the core mathematical claims of LGGR Volume VIII in Lean 4.35.0:
1. Online Report-Fiber Monotonicity, Postprocessing Invariance, and Verdict Ceilings:
   - `collision_monotonicity` (Claim C-01)
   - `postprocessing_preserves_streaming_collision` (Claim C-02)
   - `streaming_verdict_ceiling` (Claim C-03)
   - `streaming_evalDefect_partition` (Claim C-04)
2. Streaming Signed Drift Telescoping, Prefix vs Endpoint Admissibility, and Monotonic Early Stopping:
   - `streaming_chain_telescoping` (Claim C-05)
   - `online_prefix_strictly_stronger_than_endpoint` (Claim C-06)
   - `prefix_violation_monotonicity` (Claim C-07)
   - `streaming_unsigned_report_collision` (Claim C-08)
3. Streaming 1-Cochain Exactness, Incremental Cycle Closure Obstruction, and Runtime Gluing Certification:
   - `open_chain_exactness` (Claim C-09)
   - `incremental_cycle_closure_obstruction` (Claim C-10)
   - `boundary_sufficient_gluing_certifies_lggg` (Claim C-11)
   - `boundary_insufficiency_forces_defect` (Claim C-12)
-/

namespace LggrVIII

/-! ## Section 1: Streaming Report-Fiber Collisions, Postprocessing Invariance, and Defect Partition -/

/-- Two states form an explicit report collision for `(p, q)` if they share a report
    under `p` but have distinct query answers under `q`. -/
def IsCollision {X A B : Type} (p : X → A) (q : X → B) (x y : X) : Prop :=
  p x = p y ∧ q x ≠ q y

/-- A trace or collection of observed states `T : List X` contains an explicit report collision. -/
def HasCollision {X A B : Type} (p : X → A) (q : X → B) (T : List X) : Prop :=
  ∃ x ∈ T, ∃ y ∈ T, IsCollision p q x y

/-- Theorem 1 (`collision_monotonicity`, Claim C-01): Trace extension preserves existing
    report-fiber collisions. Any collision present in trace `T` persists in any extended trace `T'`. -/
theorem collision_monotonicity {X A B : Type} (p : X → A) (q : X → B)
    (T T' : List X) (hcol : HasCollision p q T) (hsub : ∀ z, z ∈ T → z ∈ T') :
    HasCollision p q T' := by
  rcases hcol with ⟨x, hx, y, hy, hxy⟩
  exact ⟨x, hsub x hx, y, hsub y hy, hxy⟩

/-- Theorem 2 (`postprocessing_preserves_streaming_collision`, Claim C-02): Deterministic
    postprocessing `f : A → A'` of streaming reports preserves all existing collisions
    and cannot restore report sufficiency. -/
theorem postprocessing_preserves_streaming_collision {X A A' B : Type}
    (p : X → A) (f : A → A') (q : X → B) (T : List X)
    (hcol : HasCollision p q T) :
    HasCollision (fun z => f (p z)) q T := by
  rcases hcol with ⟨x, hx, y, hy, hp, hq⟩
  refine ⟨x, hx, y, hy, ?_, hq⟩
  exact congrArg f hp

/-- Theorem 3 (`streaming_verdict_ceiling`, Claim C-03): For any report-only streaming evaluator
    `E : A → B` and any trace `T` containing a collision, `E` must disagree with `q` on at
    least one observed state in `T`. -/
theorem streaming_verdict_ceiling {X A B : Type} [DecidableEq B]
    (p : X → A) (q : X → B) (E : A → B) (T : List X)
    (hcol : HasCollision p q T) :
    ∃ x ∈ T, E (p x) ≠ q x := by
  rcases hcol with ⟨x, hx, y, hy, hp, hq⟩
  by_cases he : E (p x) = q x
  · refine ⟨y, hy, ?_⟩
    intro he_y
    apply hq
    rw [← he, ← he_y, hp]
  · exact ⟨x, hx, he⟩

/-- Boolean indicator as integer `0` or `1`. -/
def boolToInt (b : Bool) : Int :=
  if b then 1 else 0

/-- Streaming evaluator defect `Δ_E = E_g - L_k` between global integration verdict `eg`
    and cumulative local prefix verdict `lk`. -/
def streamingEvalDefect (lk eg : Bool) : Int :=
  boolToInt eg - boolToInt lk

/-- Theorem 4 (`streaming_evalDefect_partition`, Claim C-04): For all Boolean pairs `(lk, eg)`
    representing cumulative local pass `lk` and downstream global verdict `eg` at any streaming
    step `k`, the defect `Δ_E = boolToInt eg - boolToInt lk` lies in `{-1, 0, 1}`, and equals `-1`
    (NGD: local green, global red) if and only if `lk = true ∧ eg = false`. -/
theorem streaming_evalDefect_partition (lk eg : Bool) :
    (streamingEvalDefect lk eg = -1 ∨ streamingEvalDefect lk eg = 0 ∨ streamingEvalDefect lk eg = 1) ∧
    (streamingEvalDefect lk eg = -1 ↔ (lk = true ∧ eg = false)) := by
  cases lk <;> cases eg <;> decide

/-! ## Section 2: Streaming Signed Drift Telescoping, Prefix vs Endpoint Admissibility, and Monotonic Early Stopping -/

/-- Exact integer absolute value `|a|`. -/
def absInt (a : Int) : Int :=
  if a ≥ 0 then a else -a

/-- Consecutive signed differences along a state history: `[x1 - x0, x2 - x1, ...]`. -/
def stepDiffs : Int → List Int → List Int
  | _, [] => []
  | x, y :: ys => (y - x) :: stepDiffs y ys

/-- Sum of an integer list. -/
def sumInt : List Int → Int
  | [] => 0
  | a :: as => a + sumInt as

/-- Final endpoint state reached by a chain starting at `x0` followed by transitions `xs`. -/
def endpointState (x0 : Int) : List Int → Int
  | [] => x0
  | y :: ys => endpointState y ys

/-- Theorem 5 (`streaming_chain_telescoping`, Claim C-05): For any initial state `x0` and any
    streaming chain of subsequent states `xs`, the cumulative signed drift `sumInt (stepDiffs x0 xs)`
    equals the endpoint state difference `endpointState x0 xs - x0`. -/
theorem streaming_chain_telescoping (x0 : Int) (xs : List Int) :
    sumInt (stepDiffs x0 xs) = endpointState x0 xs - x0 := by
  induction xs generalizing x0 with
  | nil =>
    dsimp [stepDiffs, sumInt, endpointState]
    omega
  | cons y ys ih =>
    dsimp [stepDiffs, sumInt, endpointState]
    rw [ih y]
    omega

/-- Final endpoint of a non-empty state history. -/
def historyEndpoint : List Int → Int
  | [] => 0
  | [x] => x
  | _ :: y :: ys => historyEndpoint (y :: ys)

/-- Endpoint boundedness: final state is within distance `B` of start state `x0`. -/
def EndpointBounded (B : Int) (H : List Int) : Prop :=
  match H with
  | [] => True
  | x0 :: _ => absInt (historyEndpoint H - x0) ≤ B

/-- Online prefix boundedness: every state visited in `H` is within distance `B` of start state `x0`. -/
def PrefixBounded (B : Int) (H : List Int) : Prop :=
  match H with
  | [] => True
  | x0 :: _ => ∀ x ∈ H, absInt (x - x0) ≤ B

/-- The endpoint of a non-empty history is an element of that history. -/
theorem historyEndpoint_mem (x0 : Int) (xs : List Int) :
    historyEndpoint (x0 :: xs) ∈ x0 :: xs := by
  induction xs generalizing x0 with
  | nil =>
    dsimp [historyEndpoint]
    exact List.Mem.head []
  | cons y ys ih =>
    dsimp [historyEndpoint]
    have hy : historyEndpoint (y :: ys) ∈ y :: ys := ih y
    exact List.Mem.tail x0 hy

/-- Online prefix boundedness implies endpoint boundedness. -/
theorem prefix_implies_endpoint (B : Int) (H : List Int) (h : PrefixBounded B H) :
    EndpointBounded B H := by
  cases H with
  | nil => trivial
  | cons x0 xs =>
    dsimp [EndpointBounded]
    dsimp [PrefixBounded] at h
    have hmem := historyEndpoint_mem x0 xs
    exact h (historyEndpoint (x0 :: xs)) hmem

/-- Theorem 6 (`online_prefix_strictly_stronger_than_endpoint`, Claim C-06): Online prefix
    boundedness implies endpoint boundedness, but the converse fails on the excursion history
    `[0, 1, 2, 1]` with budget `B = 1`. -/
theorem online_prefix_strictly_stronger_than_endpoint :
    (∀ (B : Int) (H : List Int), PrefixBounded B H → EndpointBounded B H) ∧
    (EndpointBounded 1 [0, 1, 2, 1] ∧ ¬ PrefixBounded 1 [0, 1, 2, 1]) := by
  refine ⟨prefix_implies_endpoint, ?_, ?_⟩
  · dsimp [EndpointBounded, historyEndpoint, absInt]
    omega
  · intro h
    dsimp [PrefixBounded] at h
    have h2 : (2 : Int) ∈ [0, 1, 2, 1] := by decide
    have hbound := h 2 h2
    dsimp [absInt] at hbound
    omega

/-- Theorem 7 (`prefix_violation_monotonicity`, Claim C-07): Once a prefix violation occurs
    at any step, no extension `H ++ H'` can restore prefix admissibility, establishing the
    soundness of online early stopping. -/
theorem prefix_violation_monotonicity (B : Int) (H H' : List Int)
    (hviol : ¬ PrefixBounded B H) :
    ¬ PrefixBounded B (H ++ H') := by
  cases H with
  | nil =>
    dsimp [PrefixBounded] at hviol
    contradiction
  | cons x0 xs =>
    intro hext
    apply hviol
    dsimp [PrefixBounded] at hext ⊢
    intro x hx
    have hx_ext : x ∈ (x0 :: xs) ++ H' := List.mem_append_left H' hx
    exact hext x hx_ext

/-- Consecutive unsigned step magnitudes along a history. -/
def unsignedStepMagnitudes : Int → List Int → List Int
  | _, [] => []
  | x, y :: ys => absInt (y - x) :: unsignedStepMagnitudes y ys

/-- Streaming unsigned magnitude report of a history. -/
def unsignedHistoryReport : List Int → List Int
  | [] => []
  | x0 :: xs => unsignedStepMagnitudes x0 xs

/-- Global endpoint query: final state within distance 1 of start state. -/
def endpointHistoryQuery (H : List Int) : Bool :=
  match H with
  | [] => true
  | x0 :: _ => decide (absInt (historyEndpoint H - x0) ≤ 1)

/-- Theorem 8 (`streaming_unsigned_report_collision`, Claim C-08): The safe history `[0, 1, 0]`
    and excursion history `[0, 1, 2]` produce identical streaming unsigned magnitude reports
    `[1, 1]` while diverging on the endpoint query, forming an explicit report collision. -/
theorem streaming_unsigned_report_collision :
    IsCollision unsignedHistoryReport endpointHistoryQuery [0, 1, 0] [0, 1, 2] := by
  dsimp [IsCollision, unsignedHistoryReport, unsignedStepMagnitudes, endpointHistoryQuery,
         historyEndpoint, absInt]
  decide

/-! ## Section 3: 1-Cochain Exactness, Cycle Closure Obstruction, and Runtime Gluing -/

/-- Coboundary operator on the 2-edge tree: vertex potentials `(x0, x1, x2)` to edges
    `(x1 - x0, x2 - x1)`. -/
def openChainD0 (x0 x1 x2 : Int) : Int × Int :=
  (x1 - x0, x2 - x1)

/-- Circulation operator on acyclic tree is identically zero (no 1-cycles). -/
def openChainD1 (_e : Int × Int) : Int :=
  0

/-- L1 repair residual for the 2-edge open tree. -/
def openChainResidual (h1 h2 x0 x1 x2 : Int) : Int :=
  absInt (h1 - (x1 - x0)) + absInt (h2 - (x2 - x1))

/-- Theorem 9 (`open_chain_exactness`, Claim C-09): Any acyclic streaming tree of 1-cochains
    `(h1, h2)` has zero circulation `openChainD1 = 0`, is an exact coboundary under potential
    `(0, h1, h1 + h2)`, and achieves zero L1 repair residual. -/
theorem open_chain_exactness (h1 h2 : Int) :
    openChainD1 (h1, h2) = 0 ∧
    openChainD0 0 h1 (h1 + h2) = (h1, h2) ∧
    openChainResidual h1 h2 0 h1 (h1 + h2) = 0 := by
  dsimp [openChainD1, openChainD0, openChainResidual, absInt]
  refine ⟨rfl, ?_, ?_⟩
  · ext <;> omega
  · omega

/-- Circulation operator on the 3-cycle: `cycleD1 (h1, h2, h3) = h1 + h2 - h3`. -/
def cycleD1 (h1 h2 h3 : Int) : Int :=
  h1 + h2 - h3

/-- L1 repair residual for 3-cycle under integer vertex potentials `(x0, x1, x2)`. -/
def cycleL1Residual (h1 h2 h3 x0 x1 x2 : Int) : Int :=
  absInt (h1 - (x1 - x0)) + absInt (h2 - (x2 - x1)) + absInt (h3 - (x2 - x0))

/-- Theorem 10 (`incremental_cycle_closure_obstruction`, Claim C-10): Closing an open chain with
    a third edge `h3` yields circulation `cycleD1 h1 h2 h3 = h1 + h2 - h3`. If `h1 + h2 ≠ h3`,
    then `cycleD1 ≠ 0`, the dual witness `z = (1, 1, -1)` annihilates coboundaries, and certifies
    an L1 repair residual `cycleL1Residual ≥ 1` for all integer potentials `(x0, x1, x2)`. -/
theorem incremental_cycle_closure_obstruction (h1 h2 h3 : Int) (h_inconsistent : h1 + h2 ≠ h3) :
    cycleD1 h1 h2 h3 ≠ 0 ∧
    (∀ x0 x1 x2 : Int, 1 * (x1 - x0) + 1 * (x2 - x1) + (-1) * (x2 - x0) = 0) ∧
    (∀ x0 x1 x2 : Int, cycleL1Residual h1 h2 h3 x0 x1 x2 ≥ 1) := by
  refine ⟨?_, ?_, ?_⟩
  · dsimp [cycleD1]
    omega
  · intro x0 x1 x2
    omega
  · intro x0 x1 x2
    dsimp [cycleL1Residual, absInt]
    omega

/-- Two-stage evaluator defect: `Δ_E = boolToInt eg - boolToInt e1 * boolToInt e2`. -/
def evalDefect2 (e1 e2 eg : Bool) : Int :=
  boolToInt eg - boolToInt e1 * boolToInt e2

/-- Theorem 11 (`boundary_sufficient_gluing_certifies_lggg`, Claim C-11): When intermediate
    boundary summaries are sufficient for the global invariant (satisfying G1–G4 composition
    `eg = (e1 && e2)`), if all local stage checks pass (`e1 = true` and `e2 = true`), then global
    integration passes (`eg = true`) and the evaluator defect vanishes (`evalDefect2 e1 e2 eg = 0`),
    certifying composable LGGG. -/
theorem boundary_sufficient_gluing_certifies_lggg (e1 e2 eg : Bool)
    (h_gluing : eg = (e1 && e2)) (he1 : e1 = true) (he2 : e2 = true) :
    eg = true ∧ evalDefect2 e1 e2 eg = 0 := by
  subst he1 he2 h_gluing
  decide

/-- Theorem 12 (`boundary_insufficiency_forces_defect`, Claim C-12): If a realized report fiber
    contains an explicit collision between two execution traces `x` and `y` where both pass local
    checks (`el_x = true` and `el_y = true`) but disagree on the global oracle (`eg_x ≠ eg_y`),
    then at least one branch incurs the LGGR obstruction defect `Δ_E = -1` (NGD: local green, global red). -/
theorem boundary_insufficiency_forces_defect (el_x el_y eg_x eg_y : Bool)
    (hl_x : el_x = true) (hl_y : el_y = true) (hdiff : eg_x ≠ eg_y) :
    streamingEvalDefect el_x eg_x = -1 ∨ streamingEvalDefect el_y eg_y = -1 := by
  subst hl_x hl_y
  cases eg_x <;> cases eg_y
  · contradiction
  · left; decide
  · right; decide
  · contradiction

/-- Theorem 13 (`streaming_closed_nonexact_cohomology`): On a 4-vertex complex with 5 directed edges
    `(e01, e12, e02, e23, e03)` where Triangle `(0, 1, 2)` is filled by a 2-cell (`cycleD1 h01 h12 h02`)
    while Loop `(0, 2, 3)` surrounds an unfilled topological hole:
    1. Every coboundary `D0 x` vanishes on the filled 2-cell (`D1 (D0 x) = 0`),
    2. The streaming 1-cochain `h = (0, 0, 0, 1, 0)` is closed on the filled 2-cell (`cycleD1 0 0 0 = 0`),
    3. Yet `h` is not in `im(D0)` because its circulation around the unfilled loop `(0, 2, 3)` is nonzero,
       exhibiting a `CLOSED_NONEXACT` first cohomology obstruction (`H^1 ≠ 0`). -/
theorem streaming_closed_nonexact_cohomology :
    (∀ x0 x1 x2 : Int, cycleD1 (x1 - x0) (x2 - x1) (x2 - x0) = 0) ∧
    cycleD1 0 0 0 = 0 ∧
    (¬ ∃ x0 x1 x2 x3 : Int,
      x1 - x0 = (0 : Int) ∧
      x2 - x1 = (0 : Int) ∧
      x2 - x0 = (0 : Int) ∧
      x3 - x2 = (1 : Int) ∧
      x3 - x0 = (0 : Int)) := by
  refine ⟨?_, rfl, ?_⟩
  · intro x0 x1 x2
    dsimp [cycleD1]
    omega
  · rintro ⟨x0, x1, x2, x3, h01, h12, h02, h23, h03⟩
    omega

/-- Lossy coarse-graining projection that drops the closing chord `h3` of a 3-cycle. -/
def lossyChordDrop (h1 h2 _h3 : Int) : Int × Int :=
  (h1, h2)

/-- Theorem 14 (`streaming_transport_projection_vs_retraction`):
    1. (Lossy Projection Masking): The frustrated 3-cycle cochain `(1, 1, 1)` is nonrepairable in
       the source (`cycleD1 1 1 1 ≠ 0`), yet its image `lossyChordDrop 1 1 1 = (1, 1)` under the
       chord-dropping projection is repairable on the open 2-edge tree (`openChainD0 0 1 2 = (1, 1)`).
    2. (Retraction Reflection): For any chain map `F1 : α → β` with a left inverse `G1 : β → α`
       (`∀ h, G1 (F1 h) = h`) and target coboundary operator `Dt : γ → β` commuting with `G1`
       via `G0 : γ → δ` (`∀ y, G1 (Dt y) = Ds (G0 y)`), target repairability (`∃ y, Dt y = F1 h`)
       implies source repairability (`∃ x, Ds x = h`). -/
theorem streaming_transport_projection_vs_retraction :
    (cycleD1 1 1 1 ≠ 0 ∧ openChainD0 0 1 2 = lossyChordDrop 1 1 1) ∧
    (∀ {α β γ δ : Type} (Ds : δ → α) (Dt : γ → β) (F1 : α → β) (G1 : β → α) (G0 : γ → δ),
      (∀ h : α, G1 (F1 h) = h) →
      (∀ y : γ, G1 (Dt y) = Ds (G0 y)) →
      ∀ h : α, (∃ y : γ, Dt y = F1 h) → (∃ x : δ, Ds x = h)) := by
  refine ⟨⟨by decide, rfl⟩, ?_⟩
  intro α β γ δ Ds Dt F1 G1 G0 h_left h_comm h ⟨y, hy⟩
  refine ⟨G0 y, ?_⟩
  rw [← h_comm y, hy, h_left h]

/-- Theorem 15 (`non_injective_projection_blocks_retraction`):
    1. (Kernel Collision Blocks Left Inverse): For any projection `F1 : α → β`, if two distinct
       source cochains `ha ≠ hb` collide under `F1` (`F1 ha = F1 hb`), then no left-inverse
       retraction `G1 : β → α` can satisfy `∀ h, G1 (F1 h) = h`.
    2. (Chord-Dropping Instantiation): Because the exact 3-cycle cochain `(1, 1, 2)` and the
       frustrated 3-cycle cochain `(1, 1, 1)` collide under `lossyChordDrop`, no left inverse
       exists for `lossyChordDrop`. -/
theorem non_injective_projection_blocks_retraction :
    (∀ {α β : Type} (F1 : α → β) (ha hb : α),
      ha ≠ hb → F1 ha = F1 hb → ¬ (∃ G1 : β → α, ∀ h : α, G1 (F1 h) = h)) ∧
    ¬ (∃ G1 : (Int × Int) → (Int × Int × Int),
      ∀ h : Int × Int × Int, G1 (lossyChordDrop h.1 h.2.1 h.2.2) = h) := by
  refine ⟨?_, ?_⟩
  · intro α β F1 ha hb h_neq h_coll ⟨G1, h_left⟩
    apply h_neq
    calc
      ha = G1 (F1 ha) := (h_left ha).symm
      _ = G1 (F1 hb) := by rw [h_coll]
      _ = hb := h_left hb
  · rintro ⟨G1, h_left⟩
    have h1 : G1 (lossyChordDrop 1 1 2) = ((1 : Int), (1 : Int), (2 : Int)) :=
      h_left ((1 : Int), (1 : Int), (2 : Int))
    have h2 : G1 (lossyChordDrop 1 1 1) = ((1 : Int), (1 : Int), (1 : Int)) :=
      h_left ((1 : Int), (1 : Int), (1 : Int))
    have h_eq : lossyChordDrop 1 1 2 = lossyChordDrop 1 1 1 := rfl
    rw [h_eq] at h1
    rw [h1] at h2
    nomatch h2

/-- Integer maximum and minimum helpers for online observer-fiber diameter tracking. -/
def maxInt (a b : Int) : Int :=
  if a ≥ b then a else b

def minInt (a b : Int) : Int :=
  if a ≤ b then a else b

/-- Theorem 16 (`streaming_observer_fiber_minimax_monotonicity`):
    When an observer fiber already contains target values `q_min ≤ q_max` (with twice-minimax
    error floor `q_max - q_min`), observing an additional state with target value `q_new` on the
    same fiber updates the fiber bounds to `minInt q_min q_new` and `maxInt q_max q_new`, and the
    twice-minimax error floor is monotonically non-decreasing:
    `maxInt q_max q_new - minInt q_min q_new ≥ q_max - q_min ≥ 0`. -/
theorem streaming_observer_fiber_minimax_monotonicity (q_min q_max q_new : Int)
    (h_ord : q_min ≤ q_max) :
    maxInt q_max q_new - minInt q_min q_new ≥ q_max - q_min ∧
    q_max - q_min ≥ 0 := by
  dsimp [maxInt, minInt]
  split <;> split <;> omega

/-- Theorem 17 (`cross_branch_audit_splice_budget_breach`):
    Two stage traces with cumulative deltas `d1` and `d2` can each satisfy the budget bound
    `|d1| ≤ B` and `|d2| ≤ B` in isolation (`COMPOSABLE_LGGG`), while their spliced composition
    has cumulative delta `d1 + d2` violating `|d1 + d2| > B` (`cross_branch_lggr_discovered`). -/
theorem cross_branch_audit_splice_budget_breach :
    ∃ d1 d2 B : Int,
      B > 0 ∧
      absInt d1 ≤ B ∧
      absInt d2 ≤ B ∧
      absInt (d1 + d2) > B := by
  refine ⟨2, 2, 3, ?_⟩
  decide

/-- Theorem 18 (`multi_stage_gluing_associativity_and_defect_bound`):
    1. (Associativity of G2 Signed Delta & Multiplicative Local Acceptance):
       Across three stages with signed deltas `(d1, d2, d3)` and local acceptance bits `(e1, e2, e3)`,
       both `(d1 + d2) + d3 = d1 + (d2 + d3)` and `(e1 && e2) && e3 = e1 && (e2 && e3)` hold.
    2. (Non-Associativity of Thresholded Budget Gluing):
       For budget threshold `B = 2` and stage deltas `(2, 2, -2)`, grouping `d1 + (d2 + d3)` yields
       intermediate sum `|2 + (-2)| = 0 ≤ 2` and total `|2 + 0| = 2 ≤ 2`, whereas the left-prefix
       grouping `(d1 + d2) + d3` hits intermediate prefix `|2 + 2| = 4 > 2`. -/
theorem multi_stage_gluing_associativity_and_defect_bound :
    (∀ d1 d2 d3 : Int, (d1 + d2) + d3 = d1 + (d2 + d3)) ∧
    (∀ e1 e2 e3 : Bool, ((e1 && e2) && e3) = (e1 && (e2 && e3))) ∧
    (let B : Int := 2
     let d1 : Int := 2
     let d2 : Int := 2
     let d3 : Int := -2
     absInt (d2 + d3) ≤ B ∧
     absInt (d1 + (d2 + d3)) ≤ B ∧
     absInt (d1 + d2) > B) := by
  refine ⟨?_, ?_, by decide⟩
  · intro d1 d2 d3
    omega
  · intro e1 e2 e3
    cases e1 <;> cases e2 <;> cases e3 <;> rfl

/-- Theorem 19 (`coarsened_macro_stage_masks_internal_prefix_breach`):
    For a 3-step state trajectory `x0 → x1 → x2 → x3` with cumulative budget `B`,
    coarsening steps 2 and 3 into a single macro-step `x1 → x3` checks only `|x1 - x0| ≤ B`
    and `|x3 - x0| ≤ B`. Every fine-grained prefix-bounded trajectory satisfies the coarsened
    check, whereas the trajectory `(0, 1, 3, 1)` with `B = 2` passes the coarsened check
    (`|1 - 0| ≤ 2` and `|1 - 0| ≤ 2`) while violating the internal prefix `|3 - 0| = 3 > 2`. -/
theorem coarsened_macro_stage_masks_internal_prefix_breach :
    (∀ B x0 x1 x2 x3 : Int,
      (absInt (x1 - x0) ≤ B ∧ absInt (x2 - x0) ≤ B ∧ absInt (x3 - x0) ≤ B) →
      (absInt (x1 - x0) ≤ B ∧ absInt (x3 - x0) ≤ B)) ∧
    (let B : Int := 2
     let x0 : Int := 0
     let x1 : Int := 1
     let x2 : Int := 3
     let x3 : Int := 1
     (absInt (x1 - x0) ≤ B ∧ absInt (x3 - x0) ≤ B) ∧
     absInt (x2 - x0) > B) := by
  refine ⟨?_, by decide⟩
  intro B x0 x1 x2 x3 ⟨h1, _, h3⟩
  exact ⟨h1, h3⟩

/-- Theorem 20 (`minimal_metadata_refinement_eliminates_collision`):
    Given a base report map `p : α → β`, an auxiliary metadata feature map `m : α → γ`, and a
    protected query `q : α → δ`:
    1. If `x` and `y` collide under `p` (`IsCollision p q x y`), enriching the report to the
       product map `p_ext z = (p z, m z)` eliminates the collision between `x` and `y` whenever
       `m x ≠ m y` (`¬ IsCollision (fun z => (p z, m z)) q x y`).
    2. Conversely, any collision under the enriched map `(p, m)` projects to a collision under the
       coarse map `p`. -/
theorem minimal_metadata_refinement_eliminates_collision
    {α β γ δ : Type} (p : α → β) (m : α → γ) (q : α → δ) (x y : α) :
    (m x ≠ m y → ¬ IsCollision (fun z => (p z, m z)) q x y) ∧
    (IsCollision (fun z => (p z, m z)) q x y → IsCollision p q x y) := by
  refine ⟨?_, ?_⟩
  · intro h_m_neq ⟨h_pair_eq, _⟩
    have h_m_eq : m x = m y := congrArg Prod.snd h_pair_eq
    exact h_m_neq h_m_eq
  · intro ⟨h_pair_eq, h_q_neq⟩
    exact ⟨congrArg Prod.fst h_pair_eq, h_q_neq⟩

/-- Conventional local-step + endpoint baseline checker vs. full LGGR G1-G4 + obligation checker. -/
def conventionalAccepts (local_ok endpoint_ok : Bool) : Bool :=
  local_ok && endpoint_ok

def lggrFullAccepts (local_ok endpoint_ok prefix_ok scope_ok obligations_clear : Bool) : Bool :=
  local_ok && endpoint_ok && prefix_ok && scope_ok && obligations_clear

/-- Theorem 21 (`deferred_obligation_and_scope_migration_separation`):
    1. (Obligation Retention Monotonicity): For non-negative step obligation counts `o1 ≥ 1` and
       `o2 ≥ 0`, the cumulative retained obligation count `o1 + o2 ≥ 1` remains strictly positive
       even when the subsequent step introduces zero new obligations (`o2 = 0`).
    2. (Strict Soundness Refinement & False-Acceptance Separation): Full LGGR acceptance implies
       conventional local+endpoint acceptance, whereas mid-flight prefix breaches (`prefix_ok = false`),
       silent representation/scope migrations (`scope_ok = false`), or unresolved deferred obligations
       (`obligations_clear = false`) cause conventional false acceptance (`conventionalAccepts = true`
       while `lggrFullAccepts = false`). -/
theorem deferred_obligation_and_scope_migration_separation :
    (∀ o1 o2 : Int, o1 ≥ 1 → o2 ≥ 0 → o1 + o2 ≥ 1) ∧
    (∀ loc ep pref sc ob : Bool,
      lggrFullAccepts loc ep pref sc ob = true → conventionalAccepts loc ep = true) ∧
    (conventionalAccepts true true = true ∧ lggrFullAccepts true true false true true = false) ∧
    (conventionalAccepts true true = true ∧ lggrFullAccepts true true true false true = false) ∧
    (conventionalAccepts true true = true ∧ lggrFullAccepts true true true true false = false) := by
  refine ⟨?_, ?_, by decide, by decide, by decide⟩
  · intro o1 o2 ho1 ho2
    omega
  · intro loc ep pref sc ob
    cases loc <;> cases ep <;> cases pref <;> cases sc <;> cases ob <;> decide

/-- Weighted 3-edge L1 residual under non-negative edge weights `(w1, w2, w3)`. -/
def weightedL1Cost3 (w1 w2 w3 r1 r2 r3 : Int) : Int :=
  w1 * absInt r1 + w2 * absInt r2 + w3 * absInt r3

/-- Theorem 22 (`l1_dual_witness_subgradient_weight_sensitivity`):
    1. (Dual Feasibility Under Non-Negative Weight Increases): If a dual witness `(z1, z2, z3)`
       satisfies `|zi| ≤ wi` and weight increments satisfy `dwi ≥ 0`, then `|zi| ≤ wi + dwi`.
    2. (Monotonicity of Weighted L1 Residual): For any residual vector `(r1, r2, r3)` and
       non-negative weight increments `dw1, dw2, dw3 ≥ 0`, the weighted L1 cost satisfies
       `weightedL1Cost3 (w1 + dw1) (w2 + dw2) (w3 + dw3) r1 r2 r3 - weightedL1Cost3 w1 w2 w3 r1 r2 r3 = dw1 * |r1| + dw2 * |r2| + dw3 * |r3| ≥ 0`. -/
theorem l1_dual_witness_subgradient_weight_sensitivity
    (w1 w2 w3 dw1 dw2 dw3 z1 z2 z3 r1 r2 r3 : Int)
    (hw1 : absInt z1 ≤ w1) (hw2 : absInt z2 ≤ w2) (hw3 : absInt z3 ≤ w3)
    (hdw1 : dw1 ≥ 0) (hdw2 : dw2 ≥ 0) (hdw3 : dw3 ≥ 0) :
    (absInt z1 ≤ w1 + dw1 ∧ absInt z2 ≤ w2 + dw2 ∧ absInt z3 ≤ w3 + dw3) ∧
    weightedL1Cost3 (w1 + dw1) (w2 + dw2) (w3 + dw3) r1 r2 r3 -
      weightedL1Cost3 w1 w2 w3 r1 r2 r3 =
      dw1 * absInt r1 + dw2 * absInt r2 + dw3 * absInt r3 := by
  dsimp [weightedL1Cost3] at *
  refine ⟨⟨by omega, by omega, by omega⟩, ?_⟩
  have h1 : (w1 + dw1) * absInt r1 = w1 * absInt r1 + dw1 * absInt r1 := Int.add_mul w1 dw1 (absInt r1)
  have h2 : (w2 + dw2) * absInt r2 = w2 * absInt r2 + dw2 * absInt r2 := Int.add_mul w2 dw2 (absInt r2)
  have h3 : (w3 + dw3) * absInt r3 = w3 * absInt r3 + dw3 * absInt r3 := Int.add_mul w3 dw3 (absInt r3)
  omega

/-- Theorem 23 (`cycle_bottleneck_weight_pivot_threshold`):
    Consider a frustrated cycle (or coupled cycle cut) with nonzero defect magnitude `d > 0`,
    where breaking the active chord `e` incurs cost `w_e * d` while breaking the alternative
    tree cut incurs cost `C_alt * d`:
    1. Below the critical weight (`w_e < C_alt`), breaking `e` is strictly cheaper (`w_e * d < C_alt * d`),
    2. At the critical weight (`w_e = C_alt`), both bases achieve identical repair cost (`w_e * d = C_alt * d`),
    3. Above the critical weight (`w_e > C_alt`), pivoting `e` into the spanning tree and breaking the
       alternative cut is strictly cheaper (`C_alt * d < w_e * d`). -/
theorem cycle_bottleneck_weight_pivot_threshold (w_e C_alt d : Int) (hd : d > 0) :
    (w_e < C_alt → w_e * d < C_alt * d) ∧
    (w_e = C_alt → w_e * d = C_alt * d) ∧
    (w_e > C_alt → C_alt * d < w_e * d) := by
  refine ⟨?_, ?_, ?_⟩
  · intro h_lt
    exact Int.mul_lt_mul_of_pos_right h_lt hd
  · intro h_eq
    rw [h_eq]
  · intro h_gt
    exact Int.mul_lt_mul_of_pos_right h_gt hd

end LggrVIII
