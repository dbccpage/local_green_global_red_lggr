/-!
# Result I at support level: the 4-cycle (PR box) and a classical mixture

Scope. This file mechanises the support-level content of Result I on the
Bell cover with settings in `Bool`:

* the PR-box support has no global assignment lying in every context's
  support (strong contextuality);
* a positive-weight joint measure on global assignments cannot marginalise
  into the PR-box supports;
* a classical mixture of two deterministic assignments has a global section.

Not mechanised here: the exact l1 defect, its dual witness, linear-programming
duality over the rationals, and the Rust kernel that computes them. Those are
COMPUTED by the repository kernel and replayed by its own checker.
-/
namespace EpistemicNoGo.ResultI

/-- A global assignment on the Bell cover: Alice's outcome per setting and
Bob's outcome per setting. -/
structure Assign where
  a : Bool → Bool
  b : Bool → Bool

/-- Support of the PR box in context `(x, y)`: outcomes `(u, v)` with
`u xor v = x and y`. -/
def prSupport (x y u v : Bool) : Prop := xor u v = (x && y)

/-- The global assignment `g` restricted to context `(x, y)` lies in the PR
support of that context. -/
def inSupport (g : Assign) (x y : Bool) : Prop := prSupport x y (g.a x) (g.b y)

/-- Strong contextuality of the PR box: no global assignment lies in the
support of every context. -/
theorem pr_box_no_global_assignment (a0 a1 b0 b1 : Bool) :
    ¬ (prSupport false false a0 b0 ∧ prSupport false true a0 b1 ∧
       prSupport true false a1 b0 ∧ prSupport true true a1 b1) := by
  unfold prSupport
  revert a0 a1 b0 b1
  decide

/-- Restated on structured assignments. -/
theorem pr_box_no_supported_assignment (g : Assign) :
    ¬ (inSupport g false false ∧ inSupport g false true ∧
       inSupport g true false ∧ inSupport g true true) := by
  intro ⟨h1, h2, h3, h4⟩
  exact pr_box_no_global_assignment (g.a false) (g.a true) (g.b false) (g.b true)
    ⟨h1, h2, h3, h4⟩

/-- A finitely supported natural-weight measure on global assignments. -/
abbrev Joint := List (Assign × Nat)

/-- A joint measure is supported in the PR box when every positive-weight
entry lies in the support of every context. This is the support-level
condition for the joint to marginalise to the PR-box tables, which put zero
weight outside their supports. -/
def MarginalisesIntoPR (p : Joint) : Prop :=
  ∀ e, e ∈ p → 0 < e.2 →
    inSupport e.1 false false ∧ inSupport e.1 false true ∧
    inSupport e.1 true false ∧ inSupport e.1 true true

/-- Support-level corollary: every entry of such a joint has weight zero, so
the joint has no positive mass and cannot be a probability distribution. -/
theorem no_positive_joint_into_pr (p : Joint) (h : MarginalisesIntoPR p) :
    ∀ e, e ∈ p → e.2 = 0 := by
  intro e he
  by_cases hz : e.2 = 0
  · exact hz
  · exact absurd (h e he (Nat.pos_of_ne_zero hz)) (by
      intro ⟨h1, h2, h3, h4⟩
      exact pr_box_no_supported_assignment e.1 ⟨h1, h2, h3, h4⟩)

/-- Total mass of a joint. -/
def totalMass (p : Joint) : Nat := (p.map (fun e => e.2)).foldl (· + ·) 0

theorem foldl_add_zero (l : List Nat) (hl : ∀ n, n ∈ l → n = 0) (acc : Nat) :
    l.foldl (· + ·) acc = acc := by
  induction l generalizing acc with
  | nil => rfl
  | cons x xs ih =>
    have hx : x = 0 := hl x (by simp)
    simp only [List.foldl_cons, hx, Nat.add_zero]
    exact ih (fun n hn => hl n (by simp [hn])) acc

theorem mass_zero_into_pr (p : Joint) (h : MarginalisesIntoPR p) : totalMass p = 0 := by
  unfold totalMass
  apply foldl_add_zero
  intro n hn
  simp only [List.mem_map] at hn
  obtain ⟨e, he, rfl⟩ := hn
  exact no_positive_joint_into_pr p h e he

/-! ### The classical side of the dichotomy -/

/-- Two deterministic global assignments: everything false, everything true. -/
def gFalse : Assign := ⟨fun _ => false, fun _ => false⟩
def gTrue : Assign := ⟨fun _ => true, fun _ => true⟩

/-- The classical mixture: each deterministic assignment with weight one. -/
def classicalJoint : Joint := [(gFalse, 1), (gTrue, 1)]

/-- Marginal weight of an outcome pair `(u, v)` in context `(x, y)`. -/
def margWeight (p : Joint) (x y u v : Bool) : Nat :=
  (p.filter (fun e => decide (e.1.a x = u ∧ e.1.b y = v))).foldl (fun s e => s + e.2) 0

/-- The context table of the classical mixture: weight one on each equal
pair and zero on each unequal pair, in every context. -/
def classicalTable (u v : Bool) : Nat := if u = v then 1 else 0

/-- The classical mixture is a global section: it marginalises exactly to the
context tables, in all four contexts and for all four outcome pairs. -/
theorem classical_joint_is_global_section :
    ∀ x y u v : Bool, margWeight classicalJoint x y u v = classicalTable u v := by
  decide

end EpistemicNoGo.ResultI
