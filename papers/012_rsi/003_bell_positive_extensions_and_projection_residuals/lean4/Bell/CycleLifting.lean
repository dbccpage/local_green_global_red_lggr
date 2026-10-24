import Bell.CycleParity

/-! Exact two-fold lifting: path reconstruction, the frustrated closing edge,
and equality of packing and signed-extension problems after an unbiased lift. -/
noncomputable section
open scoped BigOperators
namespace Bell.CycleLifting
set_option maxHeartbeats 1000000
attribute [local instance] Classical.propDecidable
open Bell.LinearProgramming Bell.ContextualFraction Bell.SignedDuality

def parity : List Bool → Bool
  | [] => false
  | b :: bs => xor b (parity bs)

def walk (root : Bool) : List Bool → List Bool
  | [] => []
  | b :: bs => xor root b :: walk (xor root b) bs

def edges (root : Bool) : List Bool → List Bool
  | [] => []
  | b :: bs => xor root b :: edges b bs

def finish (root : Bool) : List Bool → Bool
  | [] => root
  | b :: bs => finish (xor root b) bs

theorem edges_walk (bs : List Bool) (root : Bool) : edges root (walk root bs) = bs := by
  induction bs generalizing root with
  | nil => rfl
  | cons b bs ih =>
    simp only [walk, edges, ih]
    cases root <;> cases b <;> rfl

theorem walk_edges (vs : List Bool) (root : Bool) : walk root (edges root vs) = vs := by
  induction vs generalizing root with
  | nil => rfl
  | cons b bs ih =>
    have h : xor root (xor root b) = b := by cases root <;> cases b <;> rfl
    simp only [edges, walk, h, ih]

theorem walk_global_flip (bs : List Bool) (root flip : Bool) :
    walk (xor root flip) bs = (walk root bs).map (fun b => xor b flip) := by
  induction bs generalizing root with
  | nil => rfl
  | cons b bs ih =>
    have he : xor (xor root flip) b = xor (xor root b) flip := by
      cases root <;> cases flip <;> cases b <;> rfl
    simp only [walk,he,ih,List.map_cons]

theorem finish_parity (bs : List Bool) (root : Bool) :
    finish root bs = xor root (parity bs) := by
  induction bs generalizing root with
  | nil => cases root <;> rfl
  | cons b bs ih =>
    simp only [finish, parity, ih]
    cases root <;> cases b <;> cases parity bs <;> rfl

theorem parity_append (bs cs : List Bool) :
    parity (bs ++ cs) = xor (parity bs) (parity cs) := by
  induction bs with
  | nil => simp [parity]
  | cons b bs ih =>
    simp only [List.cons_append, parity, ih]
    cases b <;> cases parity bs <;> cases parity cs <;> rfl

theorem closing_iff (bs : List Bool) (last : Bool) :
    parity (bs ++ [last]) = true ↔ last = !(parity bs) := by
  rw [parity_append]
  cases parity bs <;> cases last <;> decide

theorem closing_edge (bs : List Bool) (root : Bool) :
    !(xor root (finish root bs)) = !(parity bs) := by
  rw [finish_parity]
  cases root <;> cases parity bs <;> rfl

theorem reconstruction_unique (bs vs : List Bool) (root : Bool) :
    edges root vs = bs ↔ vs = walk root bs := by
  constructor
  · intro h; rw [← h, walk_edges]
  · intro h; rw [h, edges_walk]

def ones : List Bool → ℕ
  | [] => 0
  | b :: bs => (if b then 1 else 0) + ones bs

theorem parity_odd (bs : List Bool) : parity bs = true ↔ ones bs % 2 = 1 := by
  induction bs with
  | nil => simp [parity, ones]
  | cons b bs ih =>
    cases b <;> cases hp : parity bs <;> simp_all [parity, ones] <;> omega

theorem walk_length (root : Bool) (bs : List Bool) : (walk root bs).length = bs.length := by
  induction bs generalizing root with
  | nil => rfl
  | cons b bs ih => simp only [walk,List.length_cons,ih]

theorem edges_length (root : Bool) (bs : List Bool) : (edges root bs).length = bs.length := by
  induction bs generalizing root with
  | nil => rfl
  | cons b bs ih => simp only [edges,List.length_cons,ih]

def Pattern (m : ℕ) := {p : List Bool × Bool // p.1.length = m ∧ parity (p.1 ++ [p.2]) = true}
def Vertices (m : ℕ) := {v : Bool × List Bool // v.2.length = m}

def reconstruct (m : ℕ) (p : Pattern m × Bool) : Vertices m :=
  ⟨(p.2,walk p.2 p.1.val.1),by rw [walk_length]; exact p.1.property.1⟩

def failures (m : ℕ) (v : Vertices m) : Pattern m × Bool :=
  (⟨(edges v.val.1 v.val.2,!(parity (edges v.val.1 v.val.2))),
    by constructor
       · rw [edges_length]; exact v.property
       · exact (closing_iff _ _).2 rfl⟩, v.val.1)

theorem failures_reconstruct (m : ℕ) (p : Pattern m × Bool) :
    failures m (reconstruct m p) = p := by
  apply Prod.ext
  · apply Subtype.ext
    apply Prod.ext
    · exact edges_walk _ _
    · dsimp [failures,reconstruct]
      rw [edges_walk]
      exact ((closing_iff _ _).1 p.1.property.2).symm
  · rfl

theorem reconstruct_failures (m : ℕ) (v : Vertices m) :
    reconstruct m (failures m v) = v := by
  apply Subtype.ext
  apply Prod.ext
  · rfl
  · exact walk_edges _ _

/-- Every odd frustrated-cycle pattern has exactly two vertex assignments,
indexed by its root outcome. -/
def cycleEquiv (m : ℕ) : Pattern m × Bool ≃ Vertices m where
  toFun := reconstruct m
  invFun := failures m
  left_inv := failures_reconstruct m
  right_inv := reconstruct_failures m

def decode (twist : Bool) (failure left : Bool) : Bool × Bool :=
  (left,xor left (xor failure twist))

def encode (twist : Bool) (outcome : Bool × Bool) : Bool × Bool :=
  (xor (xor outcome.1 outcome.2) twist,outcome.1)

theorem encode_decode (twist failure left : Bool) :
    encode twist (decode twist failure left) = (failure,left) := by
  cases twist <;> cases failure <;> cases left <;> rfl

theorem decode_encode (twist : Bool) (outcome : Bool × Bool) :
    decode twist (encode twist outcome).1 (encode twist outcome).2 = outcome := by
  rcases outcome with ⟨a,b⟩
  cases twist <;> cases a <;> cases b <;> rfl

variable {G E : Type} [Fintype G] [Fintype E]

def quotient (label : G → E → Bool) (g : G) (i : E × Bool) : ℝ :=
  if label g i.1 = i.2 then 1 else 0

def incidence (label base : G → E → Bool) (g : G × Bool)
    (i : (E × Bool) × Bool) : ℝ :=
  if label g.1 i.1.1 = i.1.2 ∧ xor (base g.1 i.1.1) g.2 = i.2 then 1 else 0

def lift (q : G → ℝ) (g : G × Bool) : ℝ := q g.1 / 2
def down (q : G × Bool → ℝ) (g : G) : ℝ := q (g,true) + q (g,false)
def unbiased (p : E × Bool → ℝ) (i : (E × Bool) × Bool) : ℝ := p i.1 / 2

omit [Fintype G] in
theorem down_lift (q : G → ℝ) : down (lift q) = q := by
  funext g; dsimp [down,lift]; ring

theorem lift_total (q : G → ℝ) : ∑ g, lift q g = ∑ g, q g := by
  simp only [Fintype.sum_prod_type, Fintype.sum_bool, lift]
  congr 1; funext g; ring

theorem down_total (q : G × Bool → ℝ) : ∑ g, down q g = ∑ g, q g := by
  simp only [Fintype.sum_prod_type, Fintype.sum_bool, down]

omit [Fintype E] in
theorem lift_mix (label base : G → E → Bool) (q : G → ℝ)
    (i : (E × Bool) × Bool) :
    mix (incidence label base) (lift q) i = mix (quotient label) q i.1 / 2 := by
  simp only [mix, Fintype.sum_prod_type, Fintype.sum_bool, lift, Finset.sum_div]
  apply Finset.sum_congr rfl
  intro g _
  dsimp [incidence,quotient]
  cases base g i.1.1 <;> cases i.2 <;> by_cases h : label g i.1.1 = i.1.2 <;> simp [h]

omit [Fintype E] in
theorem down_mix (label base : G → E → Bool) (q : G × Bool → ℝ) (i : E × Bool) :
    mix (quotient label) (down q) i =
      mix (incidence label base) q (i,true) + mix (incidence label base) q (i,false) := by
  simp only [mix, Fintype.sum_prod_type, Fintype.sum_bool, ← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro g _
  dsimp [incidence,quotient,down]
  cases base g i.1 <;> by_cases h : label g i.1 = i.2 <;> simp [h,add_comm]

theorem lift_negative (q : G → ℝ) : negativeMass (lift q) = negativeMass q := by
  simp only [negativeMass, Fintype.sum_prod_type, Fintype.sum_bool, lift]
  apply Finset.sum_congr rfl
  intro g _
  by_cases h : 0 ≤ q g
  · rw [max_eq_right (by linarith), max_eq_right (by linarith)]; ring
  · rw [max_eq_left (by linarith), max_eq_left (by linarith)]; ring

theorem down_negative (q : G × Bool → ℝ) : negativeMass (down q) ≤ negativeMass q := by
  simp only [negativeMass, Fintype.sum_prod_type, Fintype.sum_bool, down]
  apply Finset.sum_le_sum
  intro g _
  apply max_le
  · have := le_max_left (-q (g,true)) 0; have := le_max_left (-q (g,false)) 0; linarith
  · exact add_nonneg (le_max_right _ _) (le_max_right _ _)

omit [Fintype E] in
theorem packing_lift (label base : G → E → Bool) (p : E × Bool → ℝ) (q : G → ℝ)
    (hq : Packing (quotient label) p q) :
    Packing (incidence label base) (unbiased p) (lift q) := by
  refine ⟨fun g => div_nonneg (hq.1 g.1) (by norm_num), ?_⟩
  intro i; rw [lift_mix]; exact div_le_div_of_nonneg_right (hq.2 i.1) (by norm_num)

omit [Fintype E] in
theorem packing_down (label base : G → E → Bool) (p : E × Bool → ℝ)
    (q : G × Bool → ℝ) (hq : Packing (incidence label base) (unbiased p) q) :
    Packing (quotient label) p (down q) := by
  refine ⟨fun g => add_nonneg (hq.1 (g,true)) (hq.1 (g,false)), ?_⟩
  intro i
  rw [down_mix label base]
  have h1 := hq.2 (i,true); have h2 := hq.2 (i,false)
  dsimp [unbiased] at h1 h2
  linarith

omit [Fintype E] in
theorem packing_weights_equal (label base : G → E → Bool) (p : E × Bool → ℝ) :
    weights (incidence label base) (unbiased p) = weights (quotient label) p := by
  ext w
  constructor
  · rintro ⟨q,hq,ht⟩
    exact ⟨down q,packing_down label base p q hq,by rw [down_total,ht]⟩
  · rintro ⟨q,hq,ht⟩
    exact ⟨lift q,packing_lift label base p q hq,by rw [lift_total,ht]⟩

omit [Fintype E] in
theorem fraction_equal (label base : G → E → Bool) (p : E × Bool → ℝ) :
    fraction (incidence label base) (unbiased p) = fraction (quotient label) p := by
  simp only [fraction,packing_weights_equal]

omit [Fintype E] in
/-- Equality of feasibility at every negative-mass budget implies equality of
the minimum, whenever either problem attains it. -/
theorem signed_budget_iff (label base : G → E → Bool) (p : E × Bool → ℝ) (N : ℝ) :
    (∃ q, (∑ g, q g = 1) ∧ mix (incidence label base) q = unbiased p ∧ negativeMass q ≤ N) ↔
    (∃ q, (∑ g, q g = 1) ∧ mix (quotient label) q = p ∧ negativeMass q ≤ N) := by
  constructor
  · rintro ⟨q,ht,hp,hn⟩
    refine ⟨down q,by rw [down_total,ht],?_,le_trans (down_negative q) hn⟩
    funext i
    rw [down_mix label base, congrFun hp (i,true), congrFun hp (i,false)]
    dsimp [unbiased]; ring
  · rintro ⟨q,ht,hp,hn⟩
    refine ⟨lift q,by rw [lift_total,ht],?_,by rwa [lift_negative]⟩
    funext i; rw [lift_mix,congrFun hp i.1]; rfl

def cycleLabel (n : ℕ) (g : Bell.CycleParity.Global n)
    (i : Fin (Bell.CycleParity.size n)) : Bool := g.val i

theorem cycle_fraction_equal (n : ℕ) [Fintype (Bell.CycleParity.Global n)]
    (base : Bell.CycleParity.Global n → Fin (Bell.CycleParity.size n) → Bool) (v : ℝ) :
    fraction (incidence (cycleLabel n) base) (unbiased (Bell.CycleParity.point n v)) =
      fraction (Bell.CycleParity.A n) (Bell.CycleParity.point n v) :=
  fraction_equal (cycleLabel n) base (Bell.CycleParity.point n v)

theorem cycle_signed_budget (n : ℕ) [Fintype (Bell.CycleParity.Global n)]
    (base : Bell.CycleParity.Global n → Fin (Bell.CycleParity.size n) → Bool) (v N : ℝ) :
    (∃ q, (∑ g, q g = 1) ∧ mix (incidence (cycleLabel n) base) q =
      unbiased (Bell.CycleParity.point n v) ∧ negativeMass q ≤ N) ↔
    (∃ q, (∑ g, q g = 1) ∧ mix (Bell.CycleParity.A n) q =
      Bell.CycleParity.point n v ∧ negativeMass q ≤ N) :=
  signed_budget_iff (cycleLabel n) base (Bell.CycleParity.point n v) N

end Bell.CycleLifting
