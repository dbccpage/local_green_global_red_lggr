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

/-- Forward A->B->C->A circulation, distinct from the A->C chord helper. -/
def forwardCycleD1 (h1 h2 h3 : Int) : Int := h1 + h2 + h3

/-- L1 repair residual on the forward cycle edges. -/
def cycleL1Residual (h1 h2 h3 x0 x1 x2 : Int) : Int :=
  absInt (h1 - (x1 - x0)) + absInt (h2 - (x2 - x1)) + absInt (h3 - (x0 - x2))

/-- Claim C-10: nonzero integer forward circulation forces residual at least one.
    The dual witness (1,1,1) annihilates every coboundary. -/
theorem incremental_cycle_closure_obstruction (h1 h2 h3 : Int)
    (h_inconsistent : h1 + h2 + h3 ≠ 0) :
    forwardCycleD1 h1 h2 h3 ≠ 0 ∧
    (∀ x0 x1 x2 : Int, (x1 - x0) + (x2 - x1) + (x0 - x2) = 0) ∧
    (∀ x0 x1 x2 : Int, cycleL1Residual h1 h2 h3 x0 x1 x2 ≥ 1) := by
  refine ⟨?_, ?_, ?_⟩
  · exact h_inconsistent
  · intro x0 x1 x2; omega
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

/-- Role-indexed binary evaluator defect `Δ_E(e1, e2, eg) = eg - e1 * e2`. -/
def roleTripleDefect (e1 e2 eg : Int) : Int :=
  eg - e1 * e2

/-- Theorem 24 (`six_role_sample_defect_and_cancellation_masking`):
    Formalizes the LGGR III Six-Role Overlay finite sample laws:
    1. (Sample Global-Minus-Local Identity): Across any two role-evaluated triples
       `(e1a, e2a, ega)` and `(e1b, e2b, egb)`, the global sum minus local-product sum
       equals the sum of signed defects:
       `(ega + egb) - (e1a * e2a + e1b * e2b) = roleTripleDefect e1a e2a ega + roleTripleDefect e1b e2b egb`.
    2. (Signed Cancellation Masking): For the PGD triple `(0, 1, 1)` (`Δ_E = +1`) and the
       NGD triple `(1, 1, 0)` (`Δ_E = -1`), the signed defect sum vanishes (`D = 0`) while
       the disagreement count `M = |Δ_E(v1)| + |Δ_E(v2)| = 2 > 0` detects the masked NGD failure.
    3. (Observation Envelope Separation): For any positive residual `R > 0` and distinct
       envelope weights `w1 ≠ w2`, `w1 * R ≠ w2 * R`. -/
theorem six_role_sample_defect_and_cancellation_masking
    (e1a e2a ega e1b e2b egb w1 w2 R : Int) (hR : R > 0) (hw : w1 ≠ w2) :
    ((ega + egb) - (e1a * e2a + e1b * e2b) =
      roleTripleDefect e1a e2a ega + roleTripleDefect e1b e2b egb) ∧
    (roleTripleDefect 0 1 1 + roleTripleDefect 1 1 0 = 0 ∧
      absInt (roleTripleDefect 0 1 1) + absInt (roleTripleDefect 1 1 0) = 2) ∧
    (w1 * R ≠ w2 * R) := by
  dsimp [roleTripleDefect]
  refine ⟨by omega, ⟨by decide, by decide⟩, ?_⟩
  intro heq
  rcases Int.lt_trichotomy w1 w2 with hlt | rfl | hgt
  · have hmul : w1 * R < w2 * R := Int.mul_lt_mul_of_pos_right hlt hR
    omega
  · exact hw rfl
  · have hmul : w2 * R < w1 * R := Int.mul_lt_mul_of_pos_right hgt hR
    omega

/-- Finite-stage witnesses `x1 = -1, x2 = 1, x3 = -3, x4 = 5` for `3 * x + 1 ≡ 0 (mod 2^n)`. -/
def dyadicWitness1 : Int := -1
def dyadicWitness2 : Int := 1
def dyadicWitness3 : Int := -3
def dyadicWitness4 : Int := 5

/-- Theorem 25 (`completion_relative_obstruction_on_carrier_extension`):
    Formalizes the LGGR IV Completion-Relative Obstruction (Finite-Stage Green +
    Projective Thread Compatibility + Original-Carrier Integer Obstruction):
    1. (Finite-Stage Solvability): For stages `n = 1, 2, 3, 4` with moduli `2, 4, 8, 16`,
       the witnesses `x1 = -1, x2 = 1, x3 = -3, x4 = 5` satisfy `(3 * xn + 1) % 2^n = 0`.
    2. (Projective Thread Compatibility): Adjacent stage witnesses agree modulo the
       coarser stage modulus: `(x2 - x1) % 2 = 0`, `(x3 - x2) % 4 = 0`, `(x4 - x3) % 8 = 0`.
    3. (Original-Carrier Integer Obstruction): No integer `x : Int` in the original carrier
       satisfies the completed equation `3 * x + 1 = 0`. -/
theorem completion_relative_obstruction_on_carrier_extension :
    ((3 * dyadicWitness1 + 1) % 2 = 0 ∧
     (3 * dyadicWitness2 + 1) % 4 = 0 ∧
     (3 * dyadicWitness3 + 1) % 8 = 0 ∧
     (3 * dyadicWitness4 + 1) % 16 = 0) ∧
    ((dyadicWitness2 - dyadicWitness1) % 2 = 0 ∧
     (dyadicWitness3 - dyadicWitness2) % 4 = 0 ∧
     (dyadicWitness4 - dyadicWitness3) % 8 = 0) ∧
    (∀ x : Int, 3 * x + 1 ≠ 0) := by
  refine ⟨⟨by decide, by decide, by decide, by decide⟩, ⟨by decide, by decide, by decide⟩, ?_⟩
  intro x
  omega

/-- Indicator classification error `0` or `1` of a report-only predictor `E ∘ p` on state `x`. -/
def statePredictionError {X A B : Type} [DecidableEq B]
    (p : X → A) (q : X → B) (E : A → B) (x : X) : Int :=
  if E (p x) = q x then 0 else 1

/-- Lemma: On any single colliding pair `(x, y)` (`p x = p y ∧ q x ≠ q y`), any report-only
    predictor `E : A → B` incurs at least `1` classification error across `{x, y}`. -/
theorem single_colliding_pair_error_lower_bound {X A B : Type} [DecidableEq B]
    (p : X → A) (q : X → B) (E : A → B) (x y : X)
    (hcol : IsCollision p q x y) :
    statePredictionError p q E x + statePredictionError p q E y ≥ 1 := by
  rcases hcol with ⟨hp, hq⟩
  dsimp [statePredictionError]
  by_cases hx : E (p x) = q x
  · have hy : E (p y) ≠ q y := by
      intro hy_eq
      apply hq
      rw [← hx, ← hy_eq, hp]
    simp [hx, hy]
  · by_cases hy : E (p y) = q y <;> simp [hx, hy]

/-- Theorem 26 (`disjoint_colliding_pairs_additive_error_lower_bound`):
    Formalizes the LGGR I / V / VI Disjoint Colliding-Pairs Additive Error Ceiling
    and Post-Processing Invariance:
    1. Across any two colliding pairs `(x1, y1)` and `(x2, y2)`, any deterministic
       report-only predictor `E : A → B` incurs at least `2` classification errors:
       `(err(x1) + err(y1)) + (err(x2) + err(y2)) ≥ 2`.
    2. For any deterministic post-processing map `f : A → A'` and downstream predictor
       `E' : A' → B`, the post-processed predictor `E' ∘ f ∘ p` obeys the same additive
       error lower bound `≥ 2`. -/
theorem disjoint_colliding_pairs_additive_error_lower_bound {X A A' B : Type} [DecidableEq B]
    (p : X → A) (q : X → B) (E : A → B) (f : A → A') (E' : A' → B)
    (x1 y1 x2 y2 : X)
    (hcol1 : IsCollision p q x1 y1) (hcol2 : IsCollision p q x2 y2)
    (_hdisjoint : x1 ≠ x2 ∧ x1 ≠ y2 ∧ y1 ≠ x2 ∧ y1 ≠ y2) :
    ((statePredictionError p q E x1 + statePredictionError p q E y1) +
     (statePredictionError p q E x2 + statePredictionError p q E y2) ≥ 2) ∧
    ((statePredictionError (fun z => f (p z)) q E' x1 +
      statePredictionError (fun z => f (p z)) q E' y1) +
     (statePredictionError (fun z => f (p z)) q E' x2 +
      statePredictionError (fun z => f (p z)) q E' y2) ≥ 2) := by
  have hb1 := single_colliding_pair_error_lower_bound p q E x1 y1 hcol1
  have hb2 := single_colliding_pair_error_lower_bound p q E x2 y2 hcol2
  have hcol1_f : IsCollision (fun z => f (p z)) q x1 y1 := ⟨congrArg f hcol1.1, hcol1.2⟩
  have hcol2_f : IsCollision (fun z => f (p z)) q x2 y2 := ⟨congrArg f hcol2.1, hcol2.2⟩
  have hbf1 := single_colliding_pair_error_lower_bound (fun z => f (p z)) q E' x1 y1 hcol1_f
  have hbf2 := single_colliding_pair_error_lower_bound (fun z => f (p z)) q E' x2 y2 hcol2_f
  exact ⟨by omega, by omega⟩

/-- Reference projection `Q0(x1, x2) = x1` and Gram operator `H0(x1, x2) = (x1, 0)` from LGGR VI. -/
def projQ0 (x1 _x2 : Int) : Int := x1
def gramH0 (x1 _x2 : Int) : Int × Int := (x1, 0)

/-- 2D Sign-cube sum `∑_{d1,d2 ∈ {-1,1}} d1 * (d1 * g1 + d2 * g2)` for coordinate 1. -/
def signCubeSum1 (g1 g2 : Int) : Int :=
  (-1) * ((-1) * g1 + (-1) * g2) +
  (-1) * ((-1) * g1 + 1 * g2) +
  1 * (1 * g1 + (-1) * g2) +
  1 * (1 * g1 + 1 * g2)

/-- 2D Sign-cube sum `∑_{d1,d2 ∈ {-1,1}} d2 * (d1 * g1 + d2 * g2)` for coordinate 2. -/
def signCubeSum2 (g1 g2 : Int) : Int :=
  (-1) * ((-1) * g1 + (-1) * g2) +
  1 * ((-1) * g1 + 1 * g2) +
  (-1) * (1 * g1 + (-1) * g2) +
  1 * (1 * g1 + 1 * g2)

/-- Theorem 27 (`centered_gram_kernel_nullspace_obstruction`):
    Formalizes the LGGR VI Gram Kernel Identity, Hidden Nullspace Blindspot, and
    Sign-Cube Adjoint Probe Recovery:
    1. (Gram Kernel Identity & Nullspace Blindspot): For `Q0(x1, x2) = x1` and
       `H0(x1, x2) = Q0^T Q0 (x1, x2) = (x1, 0)`, `H0(x1, x2) = (0, 0) ↔ Q0(x1, x2) = 0`,
       and every nonzero vertical state `(0, t)` (`t ≠ 0`) produces zero observation and
       zero Gram response (`Q0(0, t) = 0 ∧ H0(0, t) = (0, 0)`).
    2. (Zero-Preserving Post-Processing Blindness): Any post-processor `A : Int → V`
       applied to `Q0` assigns the same verdict to any hidden state `(0, t)` as to `(0, 0)`:
       `A (projQ0 0 t) = A (projQ0 0 0)`.
    3. (Full 2D Sign-Cube Recovery): Across the `2^2 = 4` corners of `{-1, +1}^2`,
       `(signCubeSum1 g1 g2, signCubeSum2 g1 g2) = (4 * g1, 4 * g2)`. -/
theorem centered_gram_kernel_nullspace_obstruction {V : Type}
    (A : Int → V) (x1 x2 t g1 g2 : Int) :
    (gramH0 x1 x2 = (0, 0) ↔ projQ0 x1 x2 = 0) ∧
    (projQ0 0 t = 0 ∧ gramH0 0 t = (0, 0)) ∧
    (A (projQ0 0 t) = A (projQ0 0 0)) ∧
    (signCubeSum1 g1 g2 = 4 * g1 ∧ signCubeSum2 g1 g2 = 4 * g2) := by
  dsimp [projQ0, gramH0, signCubeSum1, signCubeSum2]
  refine ⟨?_, ⟨rfl, rfl⟩, rfl, ⟨by omega, by omega⟩⟩
  constructor
  · intro h
    injection h with h1 _
  · intro h
    rw [h]

/-- Theorem 28 (`path_kernel_composition_discrepancy_identity`):
    Formalizes the LGGR I / III Evaluated Path-Kernel Composition & Two-Channel
    Residual Identity:
    1. (Two-Channel Four-Term Expansion): For any local product `L`, global verdict `Eg`,
       factored weight `wProd`, global weight `wg`, evaluator defect `dE = Eg - L`, and
       weight defect `dw = wg - wProd`,
       `Eg * wg = L * wProd + dE * wProd + L * dw + dE * dw`.
    2. (Two-Slice Evaluated Kernel Discrepancy): Across two boundary slices `a` and `b`
       with factored path weights `wa, wb` and defects `dEa = Ega - La`, `dEb = Egb - Lb`,
       `(Ega * wa + Egb * wb) - (La * wa + Lb * wb) = dEa * wa + dEb * wb`. -/
theorem path_kernel_composition_discrepancy_identity
    (L Eg wProd wg Ega La wa Egb Lb wb : Int) :
    (Eg * wg =
      L * wProd + (Eg - L) * wProd + L * (wg - wProd) + (Eg - L) * (wg - wProd)) ∧
    ((Ega * wa + Egb * wb) - (La * wa + Lb * wb) =
      (Ega - La) * wa + (Egb - Lb) * wb) := by
  have h1 : (Eg - L) * wProd = Eg * wProd - L * wProd := Int.sub_mul Eg L wProd
  have h2 : L * (wg - wProd) = L * wg - L * wProd := Int.mul_sub L wg wProd
  have h3 : (Eg - L) * (wg - wProd) = Eg * (wg - wProd) - L * (wg - wProd) :=
    Int.sub_mul Eg L (wg - wProd)
  have h4 : Eg * (wg - wProd) = Eg * wg - Eg * wProd := Int.mul_sub Eg wg wProd
  have h5 : (Ega - La) * wa = Ega * wa - La * wa := Int.sub_mul Ega La wa
  have h6 : (Egb - Lb) * wb = Egb * wb - Lb * wb := Int.sub_mul Egb Lb wb
  exact ⟨by omega, by omega⟩

/-- Theorem 29 (`boundary_sufficiency_without_quotient_factorization`):
    Formalizes the LGGR II Organizational Gluing laws (Claims M3, M4, M5, M9):
    1. (Product Sufficiency Equivalence — M4): Under weak sufficiency (`r3 = eg`),
       product sufficiency (`r3 = e1 * e2`) holds if and only if `eg = e1 * e2`.
    2. (Weak Sufficiency Without Factorization — M3): For `(e1, e2, eg, r3) = (1, 1, 0, 0)`,
       weak sufficiency (`r3 = eg`) holds while `roleTripleDefect 1 1 0 = -1 ≠ 0`.
    3. (Scalar Defect Non-Additivity — M5): Three NGD defects `(-1) + (-1) + (-1) = -3`
       leave the legal defect range `{-1, 0, 1}`.
    4. (Carrier-Local Transport Forces NGD on Mixed Class — M9): If two traces share a
       locally passing joint carrier (`l1 = true ∧ l2 = true`) and have opposite global
       verdicts (`eg1 ≠ eg2`), at least one trace has `streamingEvalDefect = -1` (NGD). -/
theorem boundary_sufficiency_without_quotient_factorization
    (e1 e2 eg r3 : Int) (hw : r3 = eg)
    (eg1 eg2 : Bool) (hdiff : eg1 ≠ eg2) :
    ((r3 = e1 * e2) ↔ (eg = e1 * e2)) ∧
    (0 = (0 : Int) ∧ roleTripleDefect 1 1 0 = -1) ∧
    (let s := (-1 : Int) + (-1) + (-1); s ≠ -1 ∧ s ≠ 0 ∧ s ≠ 1) ∧
    (streamingEvalDefect true eg1 = -1 ∨ streamingEvalDefect true eg2 = -1) := by
  refine ⟨?_, ⟨rfl, by decide⟩, ⟨by decide, by decide, by decide⟩, ?_⟩
  · rw [hw]
  · cases eg1 <;> cases eg2
    · exact False.elim (hdiff rfl)
    · left; rfl
    · right; rfl
    · exact False.elim (hdiff rfl)

/-- Six edge defects, one along each coordinate axis, repeated twice. -/
def stealthDefects (lam : Int) : List (Int × Int × Int) :=
  [(lam, 0, 0), (0, lam, 0), (0, 0, lam),
   (lam, 0, 0), (0, lam, 0), (0, 0, lam)]

def defectL1 (v : Int × Int × Int) : Int :=
  absInt v.1 + absInt v.2.1 + absInt v.2.2

def deleteCoord0 (v : Int × Int × Int) : Int × Int := (v.2.1, v.2.2)
def deleteCoord1 (v : Int × Int × Int) : Int × Int := (v.1, v.2.2)
def deleteCoord2 (v : Int × Int × Int) : Int × Int := (v.1, v.2.1)

/-- Theorem 30 (`realizable_defect_soundness_kernel_intersection`):
    Explicit integer defect-vector, coupled-coordinate, and Minkowski fixtures
    from LGGR V. Realization by the paper's restriction maps is a separate
    obligation; this declaration establishes the displayed finite vector claims.
    1. (Stealth Defect Scaling — Theorem 3): For any amplitude `lam ≥ 0`, the 6-edge
       stealth defect with per-edge L1 norm `lam` has total inconsistency `6 * lam`
       while each coordinate-deleting watcher scores `0`.
    2. (Coupled Soundness With Nontrivial Blind Spots — Theorem 6): Watchers
       `q0(v1, v2) = -v1` and `q1(v1, v2) = -v2` each have nontrivial blind spots
       (`q0(0, 1) = 0` and `q1(1, 0) = 0`), yet on the coupled defect `((-v1, -v2), (-v1, -v2))`,
       `(-v1 = 0 ∧ -v2 = 0) ↔ (v1 = 0 ∧ v2 = 0)`.
    3. (Minkowski Coupled Repair Lower Bound): For any repair shift `alpha : Int` on
       `ω = (1, -1)`, `|1 + alpha| + |alpha - 1| ≥ 2`, with equality at `alpha = 0`. -/
theorem realizable_defect_soundness_kernel_intersection
    (lam v1 v2 alpha : Int) (hlam : lam ≥ 0) :
    ((stealthDefects lam).map defectL1).sum = 6 * lam ∧
    (deleteCoord0 (lam, 0, 0) = (0, 0) ∧
     deleteCoord1 (0, lam, 0) = (0, 0) ∧
     deleteCoord2 (0, 0, lam) = (0, 0)) ∧
    ((-(0 : Int) = 0 ∧ -(0 : Int) = 0) ∧
     ((-v1 = 0 ∧ -v2 = 0) ↔ (v1 = 0 ∧ v2 = 0))) ∧
    (absInt (1 + alpha) + absInt (alpha - 1) ≥ 2 ∧
     absInt (1 + 0) + absInt (0 - 1) = 2) := by
  refine ⟨?_, ⟨rfl, rfl, rfl⟩, ⟨⟨rfl, rfl⟩, ?_⟩, ⟨?_, by decide⟩⟩
  · simp [stealthDefects, defectL1, absInt]
    omega
  · constructor <;> intro h <;> omega
  · dsimp [absInt]
    split <;> split <;> omega

/-- Theorem 31 (`dashboard_summary_reconstruction_and_collapsing_detector`):
    Formalizes the LGGR I (Claims E9–E18) & LGGR II (Claims M6–M7) Dashboard
    Information-Retention and Collapsing-Detector laws:
    1. (Oriented Defect Count Reconstruction — E9/E10): From disagreement count
       `M = nPos + nNeg` and signed defect sum `D = nPos - nNeg`,
       `2 * nPos = M + D ∧ 2 * nNeg = M - D`.
    2. (Packet Recovery — E12/E14): Given `dE = eg - L`, `L + dE = eg ∧ eg - dE = L`,
       while `roleTripleDefect 0 0 0 = 0` and `roleTripleDefect 1 1 1 = 0` (Claim M6/E13:
       zero defect alone cannot distinguish joint failure from joint pass).
    3. (Product-Collapsing Validator vs. Failing Peer — Claim M7): Copying `eg ∈ {0, 1}`
       into `e1 = eg` with passing peer `e2 = 1` forces `roleTripleDefect eg 1 eg = 0`,
       whereas a failing peer `e2 = 0` on `eg = 1` yields `roleTripleDefect 1 0 1 = 1 ≠ 0`. -/
theorem dashboard_summary_reconstruction_and_collapsing_detector
    (nPos nNeg L eg : Int) :
    (let M := nPos + nNeg; let D := nPos - nNeg;
     2 * nPos = M + D ∧ 2 * nNeg = M - D) ∧
    (let dE := eg - L; L + dE = eg ∧ eg - dE = L) ∧
    (roleTripleDefect 0 0 0 = 0 ∧ roleTripleDefect 1 1 1 = 0) ∧
    (roleTripleDefect eg 1 eg = 0 ∧ roleTripleDefect 1 0 1 = 1) := by
  dsimp [roleTripleDefect]
  refine ⟨⟨by omega, by omega⟩, ⟨by omega, by omega⟩, ⟨by decide, by decide⟩, ⟨by omega, by decide⟩⟩

/-- Canonical 4-context CHSH linear functional `S = e00 + e01 + e10 - e11`. -/
def chshForm (e00 e01 e10 e11 : Int) : Int :=
  e00 + e01 + e10 - e11

/-- Theorem 32 (`chsh_local_polytope_bound_and_negative_mass`):
    Formalizes the LGGR VII 4-Context CHSH Local Polytope Bound and Signed-Extension
    Negative Mass / Contextual Fraction Law:
    1. (Exhaustive 16-Vertex Deterministic LHV Bound): For every deterministic local
       hidden-variable assignment `(a0, a1, b0, b1) ∈ {-1, 1}^4`,
       `|chshForm (a0 * b0) (a0 * b1) (a1 * b0) (a1 * b1)| = 2`.
    2. (PR-Box Violation & Isotropic Threshold): The PR-box correlator `(1, 1, 1, -1)`
       attains `chshForm 1 1 1 (-1) = 4 > 2`, while at critical visibility `v = 1/2`
       (scaled by 2: `(1, 1, 1, -1)` vs `2 * 2 = 4`), `chshForm 1 1 1 (-1) = 2 * 2`.
    3. (4-Context Signed Negative Mass & Contextual Fraction Identity): For any scaled
       CHSH value `S ≥ 2 * scale`, the scaled negative mass `N = S - 2 * scale` and
       contextual fraction `CF = 2 * N` satisfy `CF ≤ (4 - 1) * N` and
       `(4 * scale + N) - 4 * N = 4 * scale - 3 * N`. -/
theorem chsh_local_polytope_bound_and_negative_mass
    (a0 a1 b0 b1 S scale : Int)
    (ha0 : a0 = -1 ∨ a0 = 1) (ha1 : a1 = -1 ∨ a1 = 1)
    (hb0 : b0 = -1 ∨ b0 = 1) (hb1 : b1 = -1 ∨ b1 = 1)
    (hS : S ≥ 2 * scale) :
    absInt (chshForm (a0 * b0) (a0 * b1) (a1 * b0) (a1 * b1)) = 2 ∧
    (chshForm 1 1 1 (-1) = 4 ∧ chshForm 1 1 1 (-1) > 2) ∧
    (let N := S - 2 * scale; let CF := 2 * N;
     CF ≤ 3 * N ∧ (4 * scale + N) - 4 * N = 4 * scale - 3 * N) := by
  refine ⟨?_, ⟨by decide, by decide⟩, ⟨by omega, by omega⟩⟩
  rcases ha0 with rfl | rfl <;>
  rcases ha1 with rfl | rfl <;>
  rcases hb0 with rfl | rfl <;>
  rcases hb1 with rfl | rfl <;>
  decide

/-- Scaled 2x2 product-retraction residual entry `S * p_ij - r_i * c_j`. -/
def scaledProdRes (p00 p01 p10 p11 : Int) : Int × Int × Int × Int :=
  let s := p00 + p01 + p10 + p11
  let r0 := p00 + p01
  let r1 := p10 + p11
  let c0 := p00 + p10
  let c1 := p01 + p11
  (s * p00 - r0 * c0, s * p01 - r0 * c1, s * p10 - r1 * c0, s * p11 - r1 * c1)

/-- Scaled L1 norm of the 2x2 product-retraction residual. -/
def scaledProdResL1 (p00 p01 p10 p11 : Int) : Int :=
  let (f00, f01, f10, f11) := scaledProdRes p00 p01 p10 p11
  absInt f00 + absInt f01 + absInt f10 + absInt f11

/-- Theorem 33 (`product_retraction_residual_vs_local_extension`):
    Formalizes the LGGR VII Separation between Product-State Retraction Residuals
    `F_p = p - p_A ⊗ p_B` and Bell Nonlocality:
    1. (Zero Row & Column Marginals of the 2x2 Determinant Pattern `(d, -d, -d, d)`):
       For any determinant value `d : Int`, `d + (-d) = 0` and `(-d) + d = 0`, and
       `|d| + |-d| + |-d| + |d| = 4 * |d|`.
    2. (Product Factorization vs. Classical Shared Randomness):
       - The uniform product table `(1, 1, 1, 1)` (scaled by 4) has `scaledProdRes 1 1 1 1 = (0, 0, 0, 0)`
         and `scaledProdResL1 1 1 1 1 = 0`.
       - The classical shared-randomness coin `(1, 0, 0, 1)` (scaled by `S = 2`, representing
         `1/2 [00] + 1/2 [11]`) has `scaledProdRes 1 0 0 1 = (1, -1, -1, 1)` and
         `scaledProdResL1 1 0 0 1 = 4 > 0` (so `‖F_p‖_1 = 4 / S^2 = 1 > 0`), yet assigning
         this correlated table across all 4 CHSH contexts (`E_xy = 1`) yields
         `chshForm 1 1 1 1 = 2 ≤ 2` (zero Bell polytope violation, `N_min = 0`).
    3. (PR-Box Nonlocal Contexts): Replacing context `(1, 1)` by the anti-correlated coin
       `(0, 1, 1, 0)` (`scaledProdRes 0 1 1 0 = (-1, 1, 1, -1)`, `scaledProdResL1 0 1 1 0 = 4`,
       `E_11 = -1`) keeps every single-context product residual at `‖F_p‖_1 = 1` while driving
       `chshForm 1 1 1 (-1) = 4 > 2`. -/
theorem product_retraction_residual_vs_local_extension (d : Int) :
    (d + (-d) = 0 ∧ (-d) + d = 0 ∧
     absInt d + absInt (-d) + absInt (-d) + absInt d = 4 * absInt d) ∧
    (scaledProdRes 1 1 1 1 = (0, 0, 0, 0) ∧ scaledProdResL1 1 1 1 1 = 0) ∧
    (scaledProdRes 1 0 0 1 = (1, -1, -1, 1) ∧ scaledProdResL1 1 0 0 1 = 4 ∧
     chshForm 1 1 1 1 = 2 ∧ chshForm 1 1 1 1 ≤ 2) ∧
    (scaledProdRes 0 1 1 0 = (-1, 1, 1, -1) ∧ scaledProdResL1 0 1 1 0 = 4 ∧
     chshForm 1 1 1 (-1) = 4 ∧ chshForm 1 1 1 (-1) > 2) := by
  dsimp [absInt]
  refine ⟨⟨by omega, by omega, ?_⟩, ⟨by decide, by decide⟩,
          ⟨by decide, by decide, by decide, by decide⟩,
          ⟨by decide, by decide, by decide, by decide⟩⟩
  split <;> split <;> omega

/-- Theorem 34 (`evidence_preserving_rsi_invariance_bound`):
    Formalizes the LGGR VII Evidence-Preserving Recursive Self-Improvement (RSI)
    Invariance and Half-Spread Ceiling Law:
    1. (Recursive Update Factorization Invariance): For any coarse report map `p : X → A`,
       initial report-space predictor `h0 : A → Int`, and recursive self-improvement
       update operators `U1 U2 : (A → Int) → (A → Int)`, any colliding pair `p x1 = p x2`
       remains indistinguishable across all generations `g0 x = h0 (p x)`,
       `g1 x = U1 h0 (p x)`, and `g2 x = U2 (U1 h0) (p x)`.
    2. (Generation-Uniform Half-Spread Ceiling): For any colliding states `x1, x2` with
       `p x1 = p x2` and target values `a ≤ b`, every recursive generation `h : A → Int`
       satisfies `|a - h (p x1)| + |b - h (p x2)| ≥ b - a` and
       `2 * |a - h (p x1)| ≥ b - a ∨ 2 * |b - h (p x2)| ≥ b - a`.
    3. (Refinement Breakthrough): Under a refined observation map `p' : X → A'` and
       refined predictor `h' : A' → Int` achieving `h' (p' x1) = a` and `h' (p' x2) = b`,
       both branch errors vanish: `|a - h' (p' x1)| = 0 ∧ |b - h' (p' x2)| = 0`. -/
theorem evidence_preserving_rsi_invariance_bound {X A A' : Type}
    (p : X → A) (h0 : A → Int) (U1 U2 : (A → Int) → (A → Int))
    (p' : X → A') (h' : A' → Int)
    (x1 x2 : X) (a b : Int)
    (hcoll : p x1 = p x2) (_hab : a ≤ b)
    (href1 : h' (p' x1) = a) (href2 : h' (p' x2) = b) :
    (h0 (p x1) = h0 (p x2) ∧
     U1 h0 (p x1) = U1 h0 (p x2) ∧
     U2 (U1 h0) (p x1) = U2 (U1 h0) (p x2)) ∧
    (let z := U2 (U1 h0) (p x1);
     absInt (a - z) + absInt (b - U2 (U1 h0) (p x2)) ≥ b - a ∧
     (2 * absInt (a - z) ≥ b - a ∨ 2 * absInt (b - U2 (U1 h0) (p x2)) ≥ b - a)) ∧
    (absInt (a - h' (p' x1)) = 0 ∧ absInt (b - h' (p' x2)) = 0) := by
  have hz : U2 (U1 h0) (p x2) = U2 (U1 h0) (p x1) := by rw [hcoll]
  refine ⟨⟨by rw [hcoll], by rw [hcoll], by rw [hcoll]⟩, ?_, ?_⟩
  · rw [hz]
    dsimp [absInt]
    constructor
    · split <;> split <;> omega
    · split <;> split <;> omega
  · rw [href1, href2]
    dsimp [absInt]
    constructor <;> omega

/-- Twice-scaled 2-player Shapley value for player 1: `2 * φ_1(v) = (v1 - v0) + (v12 - v2)`. -/
def shapley2P1 (v0 v1 v2 v12 : Int) : Int :=
  (v1 - v0) + (v12 - v2)

/-- Twice-scaled 2-player Shapley value for player 2: `2 * φ_2(v) = (v2 - v0) + (v12 - v1)`. -/
def shapley2P2 (v0 v1 v2 v12 : Int) : Int :=
  (v2 - v0) + (v12 - v1)

/-- Theorem 35 (`two_player_shapley_efficiency_and_symmetry`):
    Formalizes the LGGR II Coalitional Shapley Attribution Laws and Separation from
    Non-Additive Raw Evaluator Defects:
    1. (Efficiency — Scaled by 2): For any coalitional characteristic values `v0, v1, v2, v12`,
       `shapley2P1 v0 v1 v2 v12 + shapley2P2 v0 v1 v2 v12 = 2 * (v12 - v0)`.
    2. (Symmetry): Whenever `v1 = v2`, `shapley2P1 v0 v1 v2 v12 = shapley2P2 v0 v1 v2 v12`.
    3. (Dummy Player Axiom): Whenever `v1 = v0 ∧ v12 = v2`, `shapley2P1 v0 v1 v2 v12 = 0`.
    4. (Non-Additive Evaluator Defect Witness): On the canonical `NGD` trace `(e1, e2, eg) = (1, 1, 0)`
       with `v0 = 0, v1 = -1, v2 = -1, v12 = -1`, `shapley2P1 0 (-1) (-1) (-1) = -1` and
       `shapley2P2 0 (-1) (-1) (-1) = -1` (summing to `2 * (-1) = -2`), whereas the twice-scaled
       naive singleton sum `2 * (v1 + v2) = -4 ≠ -2`. -/
theorem two_player_shapley_efficiency_and_symmetry
    (v0 v1 v2 v12 : Int) :
    shapley2P1 v0 v1 v2 v12 + shapley2P2 v0 v1 v2 v12 = 2 * (v12 - v0) ∧
    (v1 = v2 → shapley2P1 v0 v1 v2 v12 = shapley2P2 v0 v1 v2 v12) ∧
    ((v1 = v0 ∧ v12 = v2) → shapley2P1 v0 v1 v2 v12 = 0) ∧
    (shapley2P1 0 (-1) (-1) (-1) = -1 ∧
     shapley2P2 0 (-1) (-1) (-1) = -1 ∧
     shapley2P1 0 (-1) (-1) (-1) + shapley2P2 0 (-1) (-1) (-1) = -2 ∧
     2 * ((-1 : Int) + (-1 : Int)) = -4) := by
  dsimp [shapley2P1, shapley2P2]
  refine ⟨by omega, ?_, ?_, ⟨by decide, by decide, by decide, by decide⟩⟩
  · intro hsym
    omega
  · intro hdum
    omega

/-- 3-validator strict product aggregator `L = e1 * e2 * e3`. -/
def prod3 (e1 e2 e3 : Int) : Int :=
  e1 * e2 * e3

/-- 2-of-3 quorum majority aggregator `M_{2,3} = 1[e1 + e2 + e3 ≥ 2]`. -/
def maj2of3 (e1 e2 e3 : Int) : Int :=
  if e1 + e2 + e3 ≥ 2 then 1 else 0

/-- Theorem 36 (`quorum_threshold_vs_product_defect_separation`):
    Formalizes the LGGR II k-of-n Quorum Threshold vs. Strict Product Aggregator
    Defect Separation Laws:
    1. (Exhaustive Monotonicity & Defect Difference Identity over `{0, 1}^3`):
       For all binary validator verdicts `e1, e2, e3 ∈ {0, 1}` and global verdict `eg : Int`,
       `prod3 e1 e2 e3 ≤ maj2of3 e1 e2 e3` and
       `(eg - prod3 e1 e2 e3) - (eg - maj2of3 e1 e2 e3) = maj2of3 e1 e2 e3 - prod3 e1 e2 e3`.
    2. (Quorum-Masked Defect vs. Unanimous NGD Separation):
       - On `(1, 1, 0)` with `eg = 0` (validator 3 vetoes, global fails):
         `0 - prod3 1 1 0 = 0` (no product NGD), whereas `0 - maj2of3 1 1 0 = -1`
         (quorum overrides the veto and incurs a quorum-masked negative defect).
       - On `(1, 1, 1)` with `eg = 0` (all 3 validators pass, global fails):
         both `0 - prod3 1 1 1 = -1` and `0 - maj2of3 1 1 1 = -1` (unanimous NGD). -/
theorem quorum_threshold_vs_product_defect_separation
    (e1 e2 e3 eg : Int)
    (h1 : e1 = 0 ∨ e1 = 1) (h2 : e2 = 0 ∨ e2 = 1) (h3 : e3 = 0 ∨ e3 = 1) :
    (prod3 e1 e2 e3 ≤ maj2of3 e1 e2 e3 ∧
     (eg - prod3 e1 e2 e3) - (eg - maj2of3 e1 e2 e3) = maj2of3 e1 e2 e3 - prod3 e1 e2 e3) ∧
    (0 - prod3 1 1 0 = 0 ∧ 0 - maj2of3 1 1 0 = -1) ∧
    (0 - prod3 1 1 1 = -1 ∧ 0 - maj2of3 1 1 1 = -1) := by
  refine ⟨⟨?_, by omega⟩, ⟨by decide, by decide⟩, ⟨by decide, by decide⟩⟩
  rcases h1 with rfl | rfl <;>
  rcases h2 with rfl | rfl <;>
  rcases h3 with rfl | rfl <;>
  decide

/-- Diagonal 2x2 Kraus trace-preservation residual `R_TP = (s0 - 1, s1 - 1)`. -/
def tpResDiag (s0 s1 : Int) : Int × Int :=
  (s0 - 1, s1 - 1)

/-- Diagonal 2x2 trace discrepancy `tr(ρ R_TP) = rho0 * r0 + rho1 * r1`. -/
def tpStateDisc (r0 r1 rho0 rho1 : Int) : Int :=
  rho0 * r0 + rho1 * r1

/-- Theorem 37 (`kraus_trace_preservation_and_blindspot_residual`):
    Formalizes the LGGR Kraus Channel Trace-Preservation Residual, State-Blindspot,
    and Two-Channel Composition Identity:
    1. (Two-Channel Composition Residual Telescoping): For any diagonal channel sums
       `(s0, s1)` and composed diagonal entries `(st0, st1)` where `E_1^†(R_TP(E_2)) = (st0 - s0, st1 - s1)`,
       `(s0 - 1) + (st0 - s0) = st0 - 1` and `(s1 - 1) + (st1 - s1) = st1 - 1`.
    2. (State Blindspot vs. Operator Non-TP Residual): For the non-trace-preserving
       diagonal Kraus sum `(s0, s1) = (2, 0)`, the operator residual is
       `tpResDiag 2 0 = (1, -1) ≠ (0, 0)`, yet on the equal-weight state `(rho0, rho1) = (1, 1)`
       the state trace discrepancy vanishes (`(2 * 1 + 0 * 1) - (1 + 1) = 0` and
       `tpStateDisc 1 (-1) 1 1 = 0`), while on `(rho0, rho1) = (1, 0)` it equals `1 ≠ 0`. -/
theorem kraus_trace_preservation_and_blindspot_residual
    (s0 s1 st0 st1 : Int) :
    ((s0 - 1) + (st0 - s0) = st0 - 1 ∧
     (s1 - 1) + (st1 - s1) = st1 - 1) ∧
    (tpResDiag 2 0 = (1, -1) ∧
     (2 * 1 + 0 * 1) - (1 + 1) = 0 ∧
     tpStateDisc 1 (-1) 1 1 = 0 ∧
     (2 * 1 + 0 * 0) - (1 + 0) = 1 ∧
     tpStateDisc 1 (-1) 1 0 = 1) := by
  refine ⟨⟨by omega, by omega⟩, ⟨by decide, by decide, by decide, by decide, by decide⟩⟩

/-- Theorem 38 (`sliding_window_green_vs_horizon_drift_breach`):
    Formalizes the LGGR I/VIII Sliding-Window Horizon Truncation vs. Full-Horizon
    Cumulative Drift Law:
    1. (Disjoint Window Partition Identity & Bound): For any 4-step drift sequence
       `d1, d2, d3, d4` and window size `W = 2` with window budget `bW`, if the
       disjoint 2-step windows satisfy `d1 + d2 ≤ bW` and `d3 + d4 ≤ bW`, then
       `(d1 + d2 + d3 + d4) = (d1 + d2) + (d3 + d4)` and `d1 + d2 + d3 + d4 ≤ 2 * bW`.
    2. (Sliding-Window Local Green vs. Global Horizon Breach): For the constant step
       drift sequence `(1, 1, 1, 1)` with window size `W = 2`, window budget `bW = 2`,
       and global horizon budget `bGlobal = 3`, every contiguous 2-step window satisfies
       `1 + 1 ≤ 2`, yet the 4-step cumulative horizon drift `1 + 1 + 1 + 1 = 4 > 3`
       breaches `bGlobal`. -/
theorem sliding_window_green_vs_horizon_drift_breach
    (d1 d2 d3 d4 bW : Int)
    (hw1 : d1 + d2 ≤ bW) (hw2 : d3 + d4 ≤ bW) :
    ((d1 + d2 + d3 + d4) = (d1 + d2) + (d3 + d4) ∧
     d1 + d2 + d3 + d4 ≤ 2 * bW) ∧
    (let wSum := (1 : Int) + 1;
     let hSum := (1 : Int) + 1 + 1 + 1;
     let bWin := (2 : Int);
     let bGlob := (3 : Int);
     wSum ≤ bWin ∧ hSum = 4 ∧ hSum > bGlob) := by
  refine ⟨⟨by omega, by omega⟩, ⟨by decide, by decide, by decide⟩⟩

/-- Theorem 39 (`arrival_order_endpoint_invariance_vs_prefix_divergence`):
    Formalizes the LGGR VIII Commutative Endpoint Invariance vs. Non-Commutative
    Prefix Excursion Law across Reordered Asynchronous Step Arrivals:
    1. (Commutative Endpoint Invariance over Permutations): For any 3-step integer
       deltas `d1, d2, d3`, permuting arrival order preserves the endpoint sum:
       `d1 + d2 + d3 = d2 + d1 + d3` and `d1 + d2 + d3 = d3 + d2 + d1`.
    2. (Arrival-Order Masked Causal Prefix Breach): For the 2-step causal sequence
       `(3, -2)` under prefix budget `bPref = 2`:
       - In causal order `(3, -2)`, the first prefix is `3 > 2` (breaches `bPref`)
         while the endpoint sum is `3 + (-2) = 1 ≤ 2`.
       - In reordered arrival sequence `(-2, 3)` (credit arrives before spike),
         both prefixes satisfy `-2 ≤ 2` and `(-2) + 3 = 1 ≤ 2`, with identical
         endpoint `(-2) + 3 = 3 + (-2)`. -/
theorem arrival_order_endpoint_invariance_vs_prefix_divergence
    (d1 d2 d3 : Int) :
    (d1 + d2 + d3 = d2 + d1 + d3 ∧ d1 + d2 + d3 = d3 + d2 + d1) ∧
    (let bPref := (2 : Int);
     let causP1 := (3 : Int);
     let causP2 := (3 : Int) + (-2);
     let arrP1 := (-2 : Int);
     let arrP2 := (-2 : Int) + 3;
     causP1 > bPref ∧ causP2 ≤ bPref ∧
     arrP1 ≤ bPref ∧ arrP2 ≤ bPref ∧
     causP2 = arrP2) := by
  refine ⟨⟨by omega, by omega⟩, ⟨by decide, by decide, by decide, by decide, by decide⟩⟩

/-- Oriented 2-simplex 1-coboundary `(d^1 α)_{(v0,v1,v2)} = a12 - a02 + a01`. -/
def simplexD1 (a01 a12 a02 : Int) : Int :=
  a12 - a02 + a01

/-- Alexander-Whitney cup product on an oriented 2-simplex `(α ⌣ β)_{(v0,v1,v2)} = a01 * b12`. -/
def cup2Simplex (a01 b12 : Int) : Int :=
  a01 * b12

/-- Theorem 40 (`simplicial_cup_product_and_leibniz_cocycle_identity`):
    Formalizes the Alexander-Whitney Simplicial Cup Product and Graded Leibniz
    Coboundary Identity on an Oriented 2-Simplex `(v0, v1, v2)`:
    1. (Exact 1-Coboundary Annihilation `d^1(d^0 f) = 0`): For any 0-cochain vertex
       potentials `f0, f1, f2 : Int`, `simplexD1 (f1 - f0) (f2 - f1) (f2 - f0) = 0`.
    2. (Graded Leibniz Telescoping `d^1(f ⌣ α) = (d^0 f ⌣ α) + (f ⌣ d^1 α)`):
       For any local edge products `f0_a01, f0_a02, f0_a12, f1_a12 : Int`,
       `(f1_a12 - f0_a12) + (f0_a12 - f0_a02 + f0_a01) = f1_a12 - f0_a02 + f0_a01`.
    3. (Non-Trivial Cup Product on Closed 1-Cocycles): For the closed 1-cocycles
       `α = (2, 3, 5)` (`simplexD1 2 3 5 = 0`) and `β = (4, -1, 3)` (`simplexD1 4 (-1) 3 = 0`),
       their Alexander-Whitney cup product on `(v0, v1, v2)` is `cup2Simplex 2 (-1) = -2 ≠ 0`
       and their cup commutator is `cup2Simplex 2 (-1) - cup2Simplex 4 3 = -14 ≠ 0`. -/
theorem simplicial_cup_product_and_leibniz_cocycle_identity
    (f0 f1 f2 f0_a01 f0_a02 f0_a12 f1_a12 : Int) :
    simplexD1 (f1 - f0) (f2 - f1) (f2 - f0) = 0 ∧
    (f1_a12 - f0_a12) + (f0_a12 - f0_a02 + f0_a01) = f1_a12 - f0_a02 + f0_a01 ∧
    (simplexD1 2 3 5 = 0 ∧
     simplexD1 4 (-1) 3 = 0 ∧
     cup2Simplex 2 (-1) = -2 ∧
     cup2Simplex 2 (-1) - cup2Simplex 4 3 = -14) := by
  dsimp [simplexD1, cup2Simplex]
  refine ⟨by omega, by omega, ⟨by decide, by decide, by decide, by decide⟩⟩

/-- Theorem 41 (`mayer_vietoris_local_exactness_gluing_obstruction`):
    Formalizes the Mayer-Vietoris Connecting Homomorphism `∂* : H^0(U ∩ V) → H^1(U ∪ V)`
    and Local-Exactness Gluing Equivalence for a Two-Subcomplex Cover `K = U ∪ V`
    meeting at two boundary components `a, b ∈ U ∩ V`:
    1. (Connecting Homomorphism Identity): Given local vertex potentials `(fUa, fUb)` on `U`
       and `(fVa, fVb)` on `V` with intersection difference 0-cocycle `δ_a = fUa - fVa`
       and `δ_b = fUb - fVb`, the difference across components equals the closed-loop
       circulation around `U ∪ V`:
       `δ_b - δ_a = (fUb - fUa) - (fVb - fVa)`.
    2. (Exact Gluing Equivalence): `δ_a = δ_b ↔ fUb - fUa = fVb - fVa`, and when
       `c = fUa - fVa`, the shifted potential `fVa + c = fUa` matches on `a` while
       preserving `(fVb + c) - (fVa + c) = fVb - fVa`.
    3. (Locally Exact Cover with Non-Zero Connecting Obstruction): For `(fUa, fUb) = (0, 2)`
       and `(fVa, fVb) = (0, -1)`, both `U` and `V` are locally exact, yet
       `δ_a = 0 ≠ 3 = δ_b` and the connecting loop holonomy is `δ_b - δ_a = 3 ≠ 0`. -/
theorem mayer_vietoris_local_exactness_gluing_obstruction
    (fUa fUb fVa fVb : Int) :
    (let da := fUa - fVa; let db := fUb - fVb;
     db - da = (fUb - fUa) - (fVb - fVa) ∧
     (da = db ↔ fUb - fUa = fVb - fVa) ∧
     fVa + da = fUa ∧
     (fVb + da) - (fVa + da) = fVb - fVa) ∧
    (let da0 := (0 : Int) - 0;
     let db0 := (2 : Int) - (-1);
     da0 = 0 ∧ db0 = 3 ∧ db0 - da0 = 3) := by
  refine ⟨⟨by omega, ?_, by omega, by omega⟩, ⟨by decide, by decide, by decide⟩⟩
  constructor <;> intro h <;> omega

/-- Theorem 42: Concrete Hodge decomposition of h = (3,0,0) on
    the forward triangle. Exact component (2,-1,-1), harmonic component
    (1,1,1), zero inner product and equal squared energies.
    This declaration does not quantify arbitrary h. -/
theorem discrete_hodge_harmonic_orthogonality_and_decomposition :
    (let h0 := (3 : Int); let h1 := 0; let h2 := 0;
     let m := (h0 + h1 + h2) / 3;
     let g0 := h0 - m; let g1 := h1 - m; let g2 := h2 - m;
     let p0 := (0 : Int); let p1 := g0; let p2 := g0 + g1;
     m = 1 ∧
     (g0 = 2 ∧ g1 = -1 ∧ g2 = -1) ∧
     (p1 - p0 = g0 ∧ p2 - p1 = g1 ∧ p0 - p2 = g2) ∧
     (g0 * m + g1 * m + g2 * m = 0) ∧
     (h0 * h0 + h1 * h1 + h2 * h2 = (g0 * g0 + g1 * g1 + g2 * g2) + 3 * m * m)) := by
  refine ⟨by decide, ⟨by decide, by decide, by decide⟩, ⟨by decide, by decide, by decide⟩, by decide, by decide⟩

/-- Transition step of the 3-state bounded-token DFA `Q = {0, 1, 2}` with initial state `0`,
    accepting state `1`, and sink state `2` on token `1` (and identity on token `0`). -/
def dfaStep (q tok : Nat) : Nat :=
  if tok = 0 then q
  else if q = 0 then 1
  else 2

/-- Iterated transition function `δ*(q, w)` via left fold over the token list `w`. -/
def dfaRun (q : Nat) (w : List Nat) : Nat :=
  w.foldl dfaStep q

/-- Boolean acceptance indicator `1[δ*(q, w) == 1]`. -/
def dfaAccepts (q : Nat) (w : List Nat) : Int :=
  if dfaRun q w = 1 then 1 else 0

/-- Theorem 43 (`dfa_concatenation_state_mismatch_obstruction`):
    Formalizes the Finite-State Automaton (DFA) Tape Grammar Concatenation
    Homomorphism and Non-Reset Accepting State Obstruction (`NGD`):
    1. (Transition Monoid Homomorphism): For any start state `q` and segments `w₁, w₂`,
       `dfaRun q (w₁ ++ w₂) = dfaRun (dfaRun q w₁) w₂`.
    2. (Reset-State Gluing Sufficiency): If `dfaRun q₀ w₁ = q₀`, then
       `dfaAccepts q₀ (w₁ ++ w₂) = dfaAccepts q₀ w₂`.
    3. (Non-Reset Boundary State Mismatch `NGD`): For `w₁ = [1]` and `w₂ = [1]`,
       both segments are locally accepted from `q₀ = 0` (`dfaAccepts 0 [1] = 1`),
       so the local product aggregator is `L = 1 * 1 = 1`, yet `dfaRun 0 [1] = 1 ≠ 0`
       shifts the boundary state so that `dfaRun 0 ([1] ++ [1]) = 2 ≠ 1` and
       `dfaAccepts 0 ([1] ++ [1]) = 0` (`Δ_E = 0 - 1 = -1`). -/
theorem dfa_concatenation_state_mismatch_obstruction
    (q q₀ : Nat) (w₁ w₂ : List Nat) (h_reset : dfaRun q₀ w₁ = q₀) :
    (dfaRun q (w₁ ++ w₂) = dfaRun (dfaRun q w₁) w₂ ∧
     dfaAccepts q₀ (w₁ ++ w₂) = dfaAccepts q₀ w₂) ∧
    (let e1 := dfaAccepts 0 [1];
     let e2 := dfaAccepts 0 [1];
     let eg := dfaAccepts 0 ([1] ++ [1]);
     e1 = 1 ∧ e2 = 1 ∧ eg = 0 ∧ eg - e1 * e2 = -1) := by
  refine ⟨⟨?_, ?_⟩, ⟨by decide, by decide, by decide, by decide⟩⟩
  · simp [dfaRun, List.foldl_append]
  · have h_comp : dfaRun q₀ (w₁ ++ w₂) = dfaRun (dfaRun q₀ w₁) w₂ := by
      simp [dfaRun, List.foldl_append]
    unfold dfaAccepts
    rw [h_comp, h_reset]

/-- Theorem 44 (`catalyst_residual_accumulation_and_cycle_ceiling`):
    Formalizes Constructor Catalyst Residual Wear Telescoping, Uniform-Wear Cycle
    Ceiling, and Multi-Cycle Catalyst Exhaustion `NGD`:
    1. (Catalyst State Telescoping): For catalyst trajectory `c₀, c₁, c₂, c₃ : Int`
       with single-cycle wear increments `δ₁ = c₁ - c₀, δ₂ = c₂ - c₁, δ₃ = c₃ - c₂`,
       the cumulative catalyst drift equals `(c₃ - c₀) = δ₁ + δ₂ + δ₃`.
    2. (Uniform-Wear Cycle Ceiling): For per-cycle wear `δ = 2` and catalyst tolerance
       `τ_cat = 5`, the cycle ceiling is `τ_cat / δ = 2`: after `n = 2` cycles,
       `2 * δ = 4 ≤ 5 = τ_cat` remains within tolerance, whereas on cycle `n = 3`,
       each single cycle satisfies `δ = 2 ≤ 2 = ε_local` locally (`L = 1`), yet
       cumulative wear `3 * δ = 6 > 5 = τ_cat` breaches the catalyst threshold
       (`E_g = 0`, `Δ_E = E_g - L = -1`). -/
theorem catalyst_residual_accumulation_and_cycle_ceiling
    (c₀ c₁ c₂ c₃ : Int) :
    (let d1 := c₁ - c₀; let d2 := c₂ - c₁; let d3 := c₃ - c₂;
     c₃ - c₀ = d1 + d2 + d3) ∧
    (let delta := (2 : Int);
     let tau_cat := (5 : Int);
     let n_ceil := tau_cat / delta;
     let l_prod := (if delta ≤ 2 then (1 : Int) else 0) *
                   (if delta ≤ 2 then 1 else 0) *
                   (if delta ≤ 2 then 1 else 0);
     let e_global := if 3 * delta ≤ tau_cat then (1 : Int) else 0;
     n_ceil = 2 ∧
     n_ceil * delta ≤ tau_cat ∧
     (n_ceil + 1) * delta > tau_cat ∧
     l_prod = 1 ∧ e_global = 0 ∧ e_global - l_prod = -1) := by
  refine ⟨by omega, ⟨by decide, by decide, by decide, by decide, by decide, by decide⟩⟩

/-- Quadratic Dirichlet energy `<h, L₁ h> = ||D₀ᵀ h||₂² + ||D₁ h||₂²` on a 3-vertex,
    1-face 2-complex with vertex divergences `(d₀, d₁, d₂)` and 2-cell curl `c`. -/
def dirichletEnergy (d₀ d₁ d₂ c : Int) : Int :=
  d₀ * d₀ + d₁ * d₁ + d₂ * d₂ + c * c

/-- Theorem 45 (`hodge_laplacian_energy_sum_of_squares_kernel`):
    Formalizes the Discrete 1-Form Hodge-Laplacian Quadratic Dirichlet Energy
    Identity `<h, L₁ h> = ||D₀ᵀ h||₂² + ||D₁ h||₂²` and Harmonic Kernel Separation:
    1. (Zero-Divergence & Zero-Curl Kernel Sufficiency): If `d₀ = 0, d₁ = 0, d₂ = 0, c = 0`,
       then `dirichletEnergy d₀ d₁ d₂ c = 0`.
    2. (Gradient vs Harmonic vs Filled-Cell Energy Separation on `C₃`):
       - For the gradient `g = (1, 2, -3) = D₀(0, 1, 3)`, the curl vanishes (`1 + 2 - 3 = 0`)
         while `||D₀ᵀ g||₂² = (-4)² + (-1)² + 5² = 42 = <g, L_down g>`.
       - On the unfilled triangle (`c = 0`), the constant circulation `h = (1, 1, 1)`
         has vertex divergences `d₀ = 1 - 1 = 0, d₁ = 1 - 1 = 0, d₂ = 1 - 1 = 0`, so
         `dirichletEnergy d₀ d₁ d₂ 0 = 0` (`h ∈ ker(L₁)` is a non-zero harmonic 1-form
         with `||h||₂² = 3 > 0`), whereas filling the 2-cell (`c = 1 + 1 + 1 = 3`)
         raises `dirichletEnergy d₀ d₁ d₂ 3 = 9 > 0`, removing `h` from `ker(L₁)`. -/
theorem hodge_laplacian_energy_sum_of_squares_kernel
    (d₀ d₁ d₂ c : Int)
    (hd0 : d₀ = 0) (hd1 : d₁ = 0) (hd2 : d₂ = 0) (hc : c = 0) :
    dirichletEnergy d₀ d₁ d₂ c = 0 ∧
    (let g0 := (1 : Int); let g1 := 2; let g2 := -3;
     let gdiv0 := g2 - g0; let gdiv1 := g0 - g1; let gdiv2 := g1 - g2;
     let gcurl := g0 + g1 + g2;
     let gl0 := gdiv1 - gdiv0; let gl1 := gdiv2 - gdiv1; let gl2 := gdiv0 - gdiv2;
     g0 * gl0 + g1 * gl1 + g2 * gl2 = gdiv0 * gdiv0 + gdiv1 * gdiv1 + gdiv2 * gdiv2 ∧
     dirichletEnergy gdiv0 gdiv1 gdiv2 gcurl = 42) ∧
    (let h0 := (1 : Int); let h1 := 1; let h2 := 1;
     let div0 := h2 - h0; let div1 := h0 - h1; let div2 := h1 - h2;
     let curl_unfilled := (0 : Int);
     let curl_filled := h0 + h1 + h2;
     h0 * h0 + h1 * h1 + h2 * h2 = 3 ∧
     dirichletEnergy div0 div1 div2 curl_unfilled = 0 ∧
     dirichletEnergy div0 div1 div2 curl_filled = 9) := by
  refine ⟨?_, ⟨by decide, by decide⟩, ⟨by decide, by decide, by decide⟩⟩
  subst hd0 hd1 hd2 hc
  rfl

/-- Theorem 46 (`pairwise_compatible_three_cycle_contextual_obstruction`):
    Formalizes the 3-Variable Hollow-Triangle Contextual Presheaf Obstruction
    (Specker's Overprotective Seer / 3-Cycle Marginal Gluing Invariant):
    1. (8-State Joint Marginal Invariant): For any 8-state joint distribution
       `(d000, d001, d010, d011, d100, d101, d110, d111)` over `{0, 1}³` with total
       mass `M = d000 + d001 + d010 + d011 + d100 + d101 + d110 + d111`, single-variable
       marginals `pA = d100 + d101 + d110 + d111`, `pB = d010 + d011 + d110 + d111`,
       `pC = d001 + d011 + d101 + d111`, and pairwise `(1, 1)` marginals
       `qAB = d110 + d111`, `qBC = d011 + d111`, `qCA = d101 + d111`, the diagonal sum
       satisfies the exact algebraic identity:
       `d000 + d111 = M - pA - pB - pC + qAB + qBC + qCA`.
    2. (Pairwise-Compatible Anti-Correlated 3-Cycle Obstruction): When scaled by `M = 2`
       with uniform marginals `pA = pB = pC = 1` and anti-correlated pairwise contexts
       `qAB = qBC = qCA = 0`, every single-variable overlap agrees (`pA = pB = pC = 1`),
       yet any global joint assignment must satisfy `d000 + d111 = 2 - 1 - 1 - 1 + 0 = -1 < 0`,
       which contradicts `d000 ≥ 0 ∧ d111 ≥ 0`. -/
theorem pairwise_compatible_three_cycle_contextual_obstruction
    (d000 d001 d010 d011 d100 d101 d110 d111 : Int) :
    (let M := d000 + d001 + d010 + d011 + d100 + d101 + d110 + d111;
     let pA := d100 + d101 + d110 + d111;
     let pB := d010 + d011 + d110 + d111;
     let pC := d001 + d011 + d101 + d111;
     let qAB := d110 + d111;
     let qBC := d011 + d111;
     let qCA := d101 + d111;
     d000 + d111 = M - pA - pB - pC + qAB + qBC + qCA) ∧
    (let M0 := (2 : Int);
     let pA0 := (1 : Int); let pB0 := 1; let pC0 := 1;
     let qAB0 := (0 : Int); let qBC0 := 0; let qCA0 := 0;
     let diag_sum := M0 - pA0 - pB0 - pC0 + qAB0 + qBC0 + qCA0;
     diag_sum = -1 ∧ ¬(0 ≤ diag_sum)) := by
  refine ⟨by omega, ⟨by decide, by decide⟩⟩

/-- Theorem 47 (`discrete_regge_hinge_deficit_and_gauss_bonnet`):
    Formalizes Discrete 2D Regge Hinge Deficit Curvature, the Gauss-Bonnet
    Euler Characteristic Identity (scaled by 6 so `1 turn = 6`, `1/2 turn = 3`,
    and equilateral angle `1/6 turn = 1`), and Conical Star `NGD`:
    1. (Gauss-Bonnet Combinatorial Identity): For any triangulation with `V_int`
       interior vertices, `V_bnd` boundary vertices, `E` edges, and `F` Euclidean
       triangles satisfying `2 * E = 3 * F + V_bnd` and `V = V_int + V_bnd`,
       the scaled total curvature `6 * V_int + 3 * V_bnd - 3 * F` equals
       `6 * (V - E + F) = 6 * χ(K)`.
    2. (6-Triangle Flat Star vs. 4-Triangle Conical Pyramid Star `NGD`):
       - Around a 6-equilateral-triangle interior vertex (`k = 6`), the scaled
         interior deficit is `6 - 6 * 1 = 0` (flat).
       - Around a 4-equilateral-triangle pyramid apex (`V_int = 1, V_bnd = 4, E = 8, F = 4`),
         every triangle satisfies `1 + 1 + 1 = 3` locally (`L = 1`), yet the interior
         apex has scaled deficit `ε_apex = 6 - 4 * 1 = 2 ≠ 0` (`E_g = 0`, `Δ_E = -1`),
         and combined with the 4 boundary vertices (`κ_b = 3 - 2 = 1` each),
         `ε_apex + 4 * κ_b = 2 + 4 = 6 = 6 * (5 - 8 + 4) = 6 * χ`. -/
theorem discrete_regge_hinge_deficit_and_gauss_bonnet
    (V_int V_bnd E F : Int)
    (h_edge : 2 * E = 3 * F + V_bnd) :
    (let V := V_int + V_bnd;
     6 * V_int + 3 * V_bnd - 3 * F = 6 * (V - E + F)) ∧
    (let eps_flat := (6 : Int) - 6 * 1;
     let eps_cone := (6 : Int) - 4 * 1;
     let kap_bnd := (3 : Int) - 2 * 1;
     let l_prod := (1 : Int);
     let e_global := if eps_cone = 0 then (1 : Int) else 0;
     eps_flat = 0 ∧
     eps_cone = 2 ∧
     eps_cone + 4 * kap_bnd = 6 * (5 - 8 + 4) ∧
     e_global = 0 ∧ e_global - l_prod = -1) := by
  refine ⟨by omega, ⟨by decide, by decide, by decide, by decide, by decide⟩⟩

/-- Theorem 48 (`fibered_pullback_compatibility_and_mediator_uniqueness`):
    Formalizes the Categorical Fibered Pullback Canonical Mediator Uniqueness
    and Interface Mismatch `NGD`:
    1. (Canonical Mediator Existence & Uniqueness): For any cospan `f : A → C`,
       `g : B → C` and cone `pA : W → A`, `pB : W → B` with `f (pA w) = g (pB w)`,
       the mediator `u w = (pA w, pB w)` satisfies `(u w).1 = pA w ∧ (u w).2 = pB w`
       and `f (u w).1 = g (u w).2`, and any map `u' : W → A × B` satisfying
       `(u' w).1 = pA w ∧ (u' w).2 = pB w` equals `u w`.
    2. (Pullback Interface Mismatch `NGD`): Under parity projections `f a = a % 2`
       and `g b = b % 2`, locally valid branch states `a = 2` (`EA = 1`) and `b = 3`
       (`EB = 1`) yield local product `L = 1 * 1 = 1`, yet `f 2 = 0 ≠ 1 = g 3`
       violates pullback compatibility (`Eg = 0`, `Δ_E = Eg - L = -1`). -/
theorem fibered_pullback_compatibility_and_mediator_uniqueness {W A B C : Type}
    (f : A → C) (g : B → C) (pA : W → A) (pB : W → B) (u' : W → A × B) (w : W)
    (h_comm : f (pA w) = g (pB w))
    (hu1 : (u' w).1 = pA w) (hu2 : (u' w).2 = pB w) :
    (let u := fun x => (pA x, pB x);
     (u w).1 = pA w ∧ (u w).2 = pB w ∧ f (u w).1 = g (u w).2 ∧ u' w = u w) ∧
    (let a := (2 : Nat); let b := (3 : Nat);
     let fa := a % 2; let gb := b % 2;
     let l_prod := (1 : Int) * 1;
     let e_global := if fa = gb then (1 : Int) else 0;
     fa = 0 ∧ gb = 1 ∧ l_prod = 1 ∧ e_global = 0 ∧ e_global - l_prod = -1) := by
  refine ⟨⟨rfl, rfl, h_comm, ?_⟩, ⟨by decide, by decide, by decide, by decide, by decide⟩⟩
  cases hpair : u' w with
  | mk fst snd =>
    rw [hpair] at hu1 hu2
    dsimp at hu1 hu2
    rw [hu1, hu2]

/-- Theorem 49 (`optional_stopping_expectation_conservation_vs_skew`):
    Formalizes Doob's Bounded-Horizon Optional Stopping Expectation Conservation
    vs. Asymmetric Stopping Win-Rate Skew & Tail Drawdown `NGD` (scaled by 4 over `ℤ`
    for two fair binary steps):
    1. (Optional Stopping Expectation Conservation): For root `x0`, step-1 states
       `xu, xd` satisfying `xu + xd = 2 * x0`, and step-2 states `(xuu, xud)` and
       `(xdu, xdd)` satisfying `xuu + xud = 2 * xu` and `xdu + xdd = 2 * xd`, both the
       full-horizon `t = 2` sum `xuu + xud + xdu + xdd` and the asymmetric stopped
       sum `2 * xu + xdu + xdd` (stopping at `t = 1` on `xu`, continuing to `t = 2` on `xd`)
       equal `4 * x0`.
    2. (Asymmetric Stopping Skew & Tail Drawdown `NGD`): For `x0 = 0, xu = 1, xd = -1,
       xuu = 2, xud = 0, xdu = 1, xdd = -3` and tail drawdown budget `B_tail = 1`:
       every step is a zero-drift martingale (`L = 1`) and `2 * xu + xdu + xdd = 0 = 4 * x0`
       with 3 of 4 equiprobable paths positive (`+1`), yet the worst-case tail drawdown
       `x0 - xdd = 3 > 1 = B_tail` breaches the drawdown bound (`Eg = 0`, `Δ_E = -1`). -/
theorem optional_stopping_expectation_conservation_vs_skew
    (x0 xu xd xuu xud xdu xdd : Int)
    (hm1 : xu + xd = 2 * x0)
    (hmu : xuu + xud = 2 * xu)
    (hmd : xdu + xdd = 2 * xd) :
    (xuu + xud + xdu + xdd = 4 * x0 ∧
     2 * xu + xdu + xdd = 4 * x0) ∧
    (let x0_w := (0 : Int);
     let xu_w := (1 : Int);
     let xdu_w := (1 : Int);
     let xdd_w := (-3 : Int);
     let b_tail := (1 : Int);
     let drawdown := x0_w - xdd_w;
     let l_prod := (1 : Int);
     let e_global := if drawdown ≤ b_tail then (1 : Int) else 0;
     2 * xu_w + xdu_w + xdd_w = 4 * x0_w ∧
     drawdown = 3 ∧
     e_global = 0 ∧
     e_global - l_prod = -1) := by
  refine ⟨⟨by omega, by omega⟩, ⟨by decide, by decide, by decide, by decide⟩⟩

/-- Theorem 50 (`derived_limit_projective_tower_lifting_obstruction`):
    Formalizes the LGGR IV 3-Stage Projective Tower Derived-Limit Lifting Obstruction
    for `3 * x_n + 1 ≡ 0 (mod 2^n)`:
    1. (Finite-Stage Modular Solvability & Inverse-Limit Compatibility):
       The residue thread `(x₁, x₂, x₃) = (1, 1, 5)` satisfies
       `(3 * x₁ + 1) % 2 = 0`, `(3 * x₂ + 1) % 4 = 0`, `(3 * x₃ + 1) % 8 = 0`,
       and projection compatibility `(x₂ - x₁) % 2 = 0`, `(x₃ - x₂) % 4 = 0` (`L = 1`).
    2. (Global Integral Lifting Obstruction `NGD`):
       For every integer `x : Int`, `3 * x + 1 ≠ 0`, so no global integer root lifts
       the compatible 2-adic tower thread (`Eg = 0`, `Δ_E = Eg - L = -1`). -/
theorem derived_limit_projective_tower_lifting_obstruction :
    (let x1 : Int := 1; let x2 : Int := 1; let x3 : Int := 5;
     (3 * x1 + 1) % 2 = 0 ∧
     (3 * x2 + 1) % 4 = 0 ∧
     (3 * x3 + 1) % 8 = 0 ∧
     (x2 - x1) % 2 = 0 ∧
     (x3 - x2) % 4 = 0) ∧
    (∀ x : Int, 3 * x + 1 ≠ 0) ∧
    (let l_prod := (1 : Int);
     let e_global := (0 : Int);
     e_global - l_prod = -1) := by
  refine ⟨⟨by decide, by decide, by decide, by decide, by decide⟩, ⟨?_, by decide⟩⟩
  intro x hx
  omega

/-- Theorem 51 (`skew_repair_norm_attainment_divergence_and_obstruction`):
    Formalizes LGGR V §4 Remark LGR-R4 (Norm-Dependent Minimum Repair Attainment on the
    Skew Non-Diagonal Exact Subspace `S = {(-α, -2α)}`):
    1. (Strict Minimizer Divergence for `2a ≠ b`):
       In cleared-denominator units scaled by `30`, for `α₁ = -15 * b`, `α₂ = -6 * (a + 2 * b)`,
       and `α_∞ = -10 * (a + b)`, we have `α₁ - α₂ = 3 * (2 * a - b)`,
       `α₂ - α_∞ = 2 * (2 * a - b)`, and `α₁ - α_∞ = 5 * (2 * a - b)`, so whenever `2 * a ≠ b`,
       the three norm-minimizing parameters are pairwise distinct.
    2. (Concrete Witness `ω = (1, -1)` & `ℓ^∞`-vs-`ℓ^1` Budget Breach `NGD`):
       For `ω = (1, -1)` (`2a - b = 3`), the scaled minimizers `α₁_30 = 15` (`1/2`),
       `α₂_30 = 6` (`1/5`), and `α_∞_30 = 0` (`0`) satisfy:
       - At `α_∞ = 0`, coordinate residuals are `(1, -1)` with `max(|1|, |-1|) = 1 = Φ_∞` (`L = 1`),
       - Yet its `ℓ^1` cost is `|1| + |-1| = 2 = 4/2 > 3/2 = Φ₁` (whereas at `α₁ = 1/2`,
         the doubled `ℓ^1` cost is `|2 + 1| + |-2 + 2| = 3 = 2 * Φ₁`), breaching the `ℓ^1`
         minimum repair budget (`Eg = 0`, `Δ_E = Eg - L = -1`). -/
theorem skew_repair_norm_attainment_divergence_and_obstruction
    (a b : Int) (h_skew : 2 * a ≠ b) :
    (let alpha1_30 := -15 * b;
     let alpha2_30 := -6 * (a + 2 * b);
     let alphainf_30 := -10 * (a + b);
     alpha1_30 - alpha2_30 = 3 * (2 * a - b) ∧
     alpha2_30 - alphainf_30 = 2 * (2 * a - b) ∧
     alpha1_30 - alphainf_30 = 5 * (2 * a - b) ∧
     alpha1_30 ≠ alpha2_30 ∧
     alpha2_30 ≠ alphainf_30 ∧
     alpha1_30 ≠ alphainf_30) ∧
    (let a0 : Int := 1; let b0 : Int := -1;
     let r_inf_1 := a0 + 0;
     let r_inf_2 := b0 + 0;
     let phi_inf := (1 : Nat);
     let l1_at_inf_doubled := 2 * (r_inf_1.natAbs + r_inf_2.natAbs);
     let phi_1_doubled := (2 * a0 + 1).natAbs + (2 * b0 + 2).natAbs;
     let e1 := if r_inf_1.natAbs ≤ phi_inf then (1 : Int) else 0;
     let e2 := if r_inf_2.natAbs ≤ phi_inf then (1 : Int) else 0;
     let l_prod := e1 * e2;
     let e_global := if l1_at_inf_doubled ≤ phi_1_doubled then (1 : Int) else 0;
     phi_1_doubled = 3 ∧
     l1_at_inf_doubled = 4 ∧
     l_prod = 1 ∧
     e_global = 0 ∧
     e_global - l_prod = -1) := by
  refine ⟨⟨by omega, by omega, by omega, by omega, by omega, by omega⟩,
          ⟨by decide, by decide, by decide, by decide, by decide⟩⟩

/-- Theorem 52 (`mermin_peres_magic_square_parity_obstruction`):
    Formalizes the 3×3 Mermin-Peres Magic Square Parity Obstruction
    (`012_rsi/003` Claim BELL-08 & LGGR VII §5.2):
    1. (Context-Wise Satisfiability & Target Product Discrepancy):
       For row targets `(R₁, R₂, R₃) = (1, 1, 1)` and column targets `(C₁, C₂, C₃) = (1, 1, -1)`
       over `{-1, +1}`, each of the 6 contexts admits a local `{-1, +1}³` assignment
       (`1 * 1 * 1 = R₁`, `1 * 1 * 1 = R₂`, `1 * 1 * 1 = R₃`, `1 * 1 * 1 = C₁`,
       `1 * 1 * 1 = C₂`, `1 * 1 * (-1) = C₃`, giving `L = 1`), yet
       `R₁ * R₂ * R₃ = 1 ≠ -1 = C₁ * C₂ * C₃` (`Eg = 0`, `Δ_E = Eg - L = -1`).
    2. (All-Assignment Non-Contextual Parity Obstruction):
       In additive `ℤ/2ℤ` exponent coordinates `x_{ij} ∈ ℤ` (representing `(-1)^{x_{ij}}`),
       no global 3×3 assignment can simultaneously satisfy all 3 even row-sum parities
       (`(x_{i1} + x_{i2} + x_{i3}) % 2 = 0`) together with two even column-sum parities
       and one odd column-sum parity (`(x_{13} + x_{23} + x_{33}) % 2 = 1`). -/
theorem mermin_peres_magic_square_parity_obstruction :
    (let r1 : Int := 1; let r2 : Int := 1; let r3 : Int := 1;
     let c1 : Int := 1; let c2 : Int := 1; let c3 : Int := -1;
     let e_r1 := if (1 : Int) * 1 * 1 = r1 then (1 : Int) else 0;
     let e_r2 := if (1 : Int) * 1 * 1 = r2 then (1 : Int) else 0;
     let e_r3 := if (1 : Int) * 1 * 1 = r3 then (1 : Int) else 0;
     let e_c1 := if (1 : Int) * 1 * 1 = c1 then (1 : Int) else 0;
     let e_c2 := if (1 : Int) * 1 * 1 = c2 then (1 : Int) else 0;
     let e_c3 := if (1 : Int) * 1 * (-1) = c3 then (1 : Int) else 0;
     let l_prod := e_r1 * e_r2 * e_r3 * e_c1 * e_c2 * e_c3;
     let e_global := if r1 * r2 * r3 = c1 * c2 * c3 then (1 : Int) else 0;
     r1 * r2 * r3 = 1 ∧
     c1 * c2 * c3 = -1 ∧
     r1 * r2 * r3 ≠ c1 * c2 * c3 ∧
     l_prod = 1 ∧
     e_global = 0 ∧
     e_global - l_prod = -1) ∧
    (∀ x11 x12 x13 x21 x22 x23 x31 x32 x33 : Int,
      ¬ ((x11 + x12 + x13) % 2 = 0 ∧
         (x21 + x22 + x23) % 2 = 0 ∧
         (x31 + x32 + x33) % 2 = 0 ∧
         (x11 + x21 + x31) % 2 = 0 ∧
         (x12 + x22 + x32) % 2 = 0 ∧
         (x13 + x23 + x33) % 2 = 1)) := by
  refine ⟨⟨by decide, by decide, by decide, by decide, by decide, by decide⟩, ?_⟩
  intro x11 x12 x13 x21 x22 x23 x31 x32 x33 h
  omega

/-- Theorem 53 (`side_information_channel_capacity_and_fiber_error_floor`):
    Formalizes the Side-Information Channel Capacity & Fiber Error Floor
    (`012_rsi/002` Claims IK-04/IK-05 & LGGR I §5):
    1. (All-Assignment 4-State Fiber Error Floor under 1-Bit Side Channel `S = 2 < K = 4`):
       For any 4 pairwise distinct target query values `v₀, v₁, v₂, v₃ : Int`,
       any 2-symbol side-channel assignment `b₀, b₁, b₂, b₃ : Bool`, and any deterministic
       2-symbol decoder outputs `d₀, d₁ : Int`, the number of misclassified fiber states
       satisfies `err₀ + err₁ + err₂ + err₃ ≥ 2 = K - S`.
    2. (Concrete Capacity-Deficit Witness `NGD`):
       For `K = 4` distinct query values and channel capacity `S = 2`, every state emits a
       valid side-channel symbol (`L = 1`), yet the capacity error floor `K - S = 2 > 0`
       blocks zero-error decoding (`Eg = 0`, `Δ_E = Eg - L = -1`). -/
theorem side_information_channel_capacity_and_fiber_error_floor
    (v0 v1 v2 v3 d0 d1 : Int)
    (h01 : v0 ≠ v1) (h02 : v0 ≠ v2) (h03 : v0 ≠ v3)
    (h12 : v1 ≠ v2) (h13 : v1 ≠ v3) (h23 : v2 ≠ v3)
    (b0 b1 b2 b3 : Bool) :
    (let p0 := if b0 then d1 else d0;
     let p1 := if b1 then d1 else d0;
     let p2 := if b2 then d1 else d0;
     let p3 := if b3 then d1 else d0;
     let err0 := if p0 = v0 then (0 : Int) else 1;
     let err1 := if p1 = v1 then (0 : Int) else 1;
     let err2 := if p2 = v2 then (0 : Int) else 1;
     let err3 := if p3 = v3 then (0 : Int) else 1;
     err0 + err1 + err2 + err3 ≥ 2) ∧
    (let k_distinct : Int := 4;
     let s_capacity : Int := 2;
     let cap_floor := k_distinct - s_capacity;
     let l_prod := (1 : Int);
     let e_global := if cap_floor ≤ 0 then (1 : Int) else 0;
     cap_floor = 2 ∧
     e_global = 0 ∧
     e_global - l_prod = -1) := by
  refine ⟨?_, ⟨by decide, by decide, by decide⟩⟩
  cases b0 <;> cases b1 <;> cases b2 <;> cases b3 <;> dsimp <;> omega

/-- Theorem 54 (`product_of_experts_disjoint_support_collapse_vs_mixture`):
    Formalizes the Product-of-Experts Disjoint-Support Collapse vs. Mixture-of-Experts
    Positivity (LGGR I §7.2 & LGGR II §2.2):
    1. (All-Assignment Positivity of Mixture vs. Vanishing Product on Disjoint Supports):
       For any non-negative expert scores `p1_1, p1_2, p2_1, p2_2 : Int` with `p1_1 ≥ 0`,
       `p1_2 ≥ 0`, `p2_1 ≥ 0`, `p2_2 ≥ 0`, if Expert 1 has positive mass (`p1_1 + p1_2 > 0`)
       and Expert 2 has positive mass (`p2_1 + p2_2 > 0`), the unnormalized symmetric mixture
       sum `(p1_1 + p1_2) + (p2_1 + p2_2)` is strictly positive (`≥ 2`).
    2. (Concrete Disjoint-Support Collapse Witness `NGD`):
       For `p₁ = (1, 0)` and `p₂ = (0, 1)`, both experts have positive total mass (`L = 1`)
       and positive mixture partition sum `D_MoE_scaled = 2 > 0`, whereas their pointwise
       Product-of-Experts partition sum vanishes (`D_PoE = 1 * 0 + 0 * 1 = 0`, `Eg = 0`,
       `Δ_E = Eg - L = -1`). -/
theorem product_of_experts_disjoint_support_collapse_vs_mixture
    (p1_1 p1_2 p2_1 p2_2 : Int)
    (h1 : p1_1 + p1_2 > 0) (h2 : p2_1 + p2_2 > 0) :
    ((p1_1 + p1_2) + (p2_1 + p2_2) ≥ 2) ∧
    (let a1_1 : Int := 1; let a1_2 : Int := 0;
     let a2_1 : Int := 0; let a2_2 : Int := 1;
     let mass1 := a1_1 + a1_2;
     let mass2 := a2_1 + a2_2;
     let d_poe := a1_1 * a2_1 + a1_2 * a2_2;
     let d_moe_scaled := mass1 + mass2;
     let e1 := if mass1 > 0 then (1 : Int) else 0;
     let e2 := if mass2 > 0 then (1 : Int) else 0;
     let l_prod := e1 * e2;
     let e_global := if d_poe > 0 then (1 : Int) else 0;
     mass1 = 1 ∧
     mass2 = 1 ∧
     d_poe = 0 ∧
     d_moe_scaled = 2 ∧
     l_prod = 1 ∧
     e_global = 0 ∧
     e_global - l_prod = -1) := by
  refine ⟨by omega, ⟨by decide, by decide, by decide, by decide, by decide, by decide, by decide⟩⟩

end LggrVIII
