/-!
Lean companion to Local Green, Global Red III.

This file covers the paper's finite integer statements. The real exponential
kernel theorem remains a prose theorem with explicit hypotheses.
-/

namespace LGGR3

def defect (e1 e2 eg : Int) : Int :=
  eg - e1 * e2

theorem defect_range
    (e1 e2 eg : Int)
    (h1 : e1 = 0 ∨ e1 = 1)
    (h2 : e2 = 0 ∨ e2 = 1)
    (hg : eg = 0 ∨ eg = 1) :
    defect e1 e2 eg = -1 ∨
    defect e1 e2 eg = 0 ∨
    defect e1 e2 eg = 1 := by
  rcases h1 with rfl | rfl <;>
  rcases h2 with rfl | rfl <;>
  rcases hg with rfl | rfl <;>
  decide

theorem local_green_global_red :
    defect 1 1 0 = -1 := by
  rfl

def globalSum (samples : List (Int × Int × Int)) : Int :=
  samples.map (fun (_, _, eg) => eg) |>.sum

def localSum (samples : List (Int × Int × Int)) : Int :=
  samples.map (fun (e1, e2, _) => e1 * e2) |>.sum

def defectSum (samples : List (Int × Int × Int)) : Int :=
  samples.map (fun (e1, e2, eg) => defect e1 e2 eg) |>.sum

theorem global_sub_local_eq_defect_sum
    (samples : List (Int × Int × Int)) :
    globalSum samples - localSum samples = defectSum samples := by
  induction samples with
  | nil => rfl
  | cons head tail ih =>
    rcases head with ⟨e1, e2, eg⟩
    simp only [globalSum, localSum, defectSum, List.map_cons, List.sum_cons]
    simp only [globalSum, localSum, defectSum] at ih
    unfold defect at ih ⊢
    omega

theorem binary_defect_cancellation :
    defect 0 1 1 = 1 ∧
    defect 1 1 0 = -1 ∧
    defect 0 1 1 + defect 1 1 0 = 0 ∧
    defect 0 1 1 ≠ 0 ∧
    defect 1 1 0 ≠ 0 := by
  decide

def phoneSamples : List (Int × Int × Int) :=
  [(1, 1, 1), (1, 1, 0), (1, 1, 0), (0, 1, 0), (0, 0, 0)]

theorem phone_totals :
    globalSum phoneSamples = 1 ∧
    localSum phoneSamples = 3 ∧
    defectSum phoneSamples = -2 := by
  decide

def kernelResidual (composed product : Int) : Int :=
  composed - product

def scaledWeights (scale : Int) (weights : List Int) : List Int :=
  weights.map fun weight => scale * weight

def pairwiseProducts (left right : List Int) : List Int :=
  left.flatMap fun scale => scaledWeights scale right

def boundaryProducts (groups : List (List Int × List Int)) : List Int :=
  groups.flatMap fun group => pairwiseProducts group.1 group.2

def groupConvolution (groups : List (List Int × List Int)) : Int :=
  (groups.map fun group => group.1.sum * group.2.sum).sum

private theorem scaled_weights_sum (scale : Int) (weights : List Int) :
    (scaledWeights scale weights).sum = scale * weights.sum := by
  induction weights with
  | nil =>
    simp [scaledWeights]
  | cons weight rest ih =>
    simp only [scaledWeights, List.map_cons, List.sum_cons] at ih ⊢
    rw [ih, Int.mul_add]

private theorem pairwise_products_sum (left right : List Int) :
    (pairwiseProducts left right).sum = left.sum * right.sum := by
  induction left with
  | nil =>
    simp [pairwiseProducts]
  | cons scale rest ih =>
    simp only [pairwiseProducts, List.flatMap_cons, List.sum_append, List.sum_cons] at ih ⊢
    rw [scaled_weights_sum, ih, Int.add_mul]

private theorem boundary_products_sum (groups : List (List Int × List Int)) :
    (boundaryProducts groups).sum = groupConvolution groups := by
  induction groups with
  | nil =>
    simp [boundaryProducts, groupConvolution]
  | cons group rest ih =>
    simp only [boundaryProducts, groupConvolution, List.flatMap_cons, List.map_cons,
      List.sum_cons, List.sum_append] at ih ⊢
    rw [pairwise_products_sum, ih]

theorem factorized_integer_kernel_has_zero_residual
    (groups : List (List Int × List Int))
    (composite : List Int)
    (h : composite = boundaryProducts groups) :
    kernelResidual composite.sum (groupConvolution groups) = 0 := by
  unfold kernelResidual
  rw [h, boundary_products_sum]
  exact Int.sub_self (groupConvolution groups)

inductive Role where
  | finiteObstruction
  | foundations
  | representation
  | observer
  | continuumShadow
  | action
  deriving DecidableEq, Repr

def roles : List Role :=
  [.finiteObstruction, .foundations, .representation,
   .observer, .continuumShadow, .action]

theorem six_roles : roles.length = 6 := by
  rfl

def observerScore (weight residual : Int) : Int :=
  weight * residual

theorem observer_weights_can_change_a_score :
    observerScore 1 1 ≠ observerScore 2 1 := by
  decide

theorem fixed_observation_preserves_defect
    (e1 e2 eg e1' e2' eg' : Int)
    (h1 : e1' = e1) (h2 : e2' = e2) (hg : eg' = eg) :
    defect e1' e2' eg' = defect e1 e2 eg := by
  subst e1'
  subst e2'
  subst eg'
  rfl

structure Carrier where
  classId : Nat
  itemId : Nat
  deriving DecidableEq

def sameClass (x y : Carrier) : Prop :=
  x.classId = y.classId

def carrierSetoid : Setoid Carrier where
  r := sameClass
  iseqv := {
    refl := fun _ => rfl
    symm := fun h => h.symm
    trans := fun hxy hyz => hxy.trans hyz
  }

theorem quotient_evaluator_obstruction
    {X : Type u} (s : Setoid X)
    (evaluate : X → Bool)
    (x y : X)
    (hxy : s.r x y)
    (hx : evaluate x = true)
    (hy : evaluate y = false) :
    ¬ ∃ descended : Quotient s → Bool,
        ∀ z, descended (Quotient.mk s z) = evaluate z := by
  intro ⟨descended, hdesc⟩
  have hq : Quotient.mk s x = Quotient.mk s y :=
    Quotient.sound hxy
  have ex := hdesc x
  have ey := hdesc y
  rw [hx] at ex
  rw [hy] at ey
  rw [hq] at ex
  rw [ex] at ey
  contradiction

theorem quotient_evaluator_constant
    {X : Type u} (s : Setoid X)
    (evaluate : X → Bool)
    (descended : Quotient s → Bool)
    (hdesc : ∀ z, descended (Quotient.mk s z) = evaluate z)
    (x y : X)
    (hxy : s.r x y) :
    evaluate x = evaluate y := by
  have hq : Quotient.mk s x = Quotient.mk s y :=
    Quotient.sound hxy
  calc
    evaluate x = descended (Quotient.mk s x) := (hdesc x).symm
    _ = descended (Quotient.mk s y) := by rw [hq]
    _ = evaluate y := hdesc y

theorem quotient_obstruction_has_a_witness :
    ∃ evaluate : Carrier → Bool, ∃ x y : Carrier,
      sameClass x y ∧ evaluate x = true ∧ evaluate y = false := by
  let x : Carrier := ⟨1, 0⟩
  let y : Carrier := ⟨1, 1⟩
  let evaluate : Carrier → Bool := fun z => z.itemId == 0
  exact ⟨evaluate, x, y, rfl, rfl, rfl⟩

end LGGR3
