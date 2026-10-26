/-!
Finite sentences for the rows still marked proved in Paper 026.
-/

namespace OperatorProposal

def sum3 (a b c : Int) : Int := a + b + c

def phiCycle (a b c : Int) : Nat := (sum3 a b c).natAbs

def gammaAllOnes (a b c : Int) : Nat := (sum3 a b c).natAbs

theorem triangle_coboundary_sums_zero (f0 f1 f2 : Int) :
    sum3 (f1 - f0) (f2 - f1) (f0 - f2) = 0 := by
  simp [sum3]
  omega

theorem gamma_independent_of_potential (w0 w1 w2 f0 f1 f2 : Int) :
    sum3 (w0 - (f1 - f0)) (w1 - (f2 - f1)) (w2 - (f0 - f2)) = sum3 w0 w1 w2 := by
  simp [sum3]
  omega

theorem phi_zero_implies_gamma_zero (a b c : Int) (h : phiCycle a b c = 0) :
    gammaAllOnes a b c = 0 := h

theorem exact_field_gamma_zero :
    phiCycle 2 (-1) (-1) = 0 ∧ gammaAllOnes 2 (-1) (-1) = 0 := by
  decide

theorem chart1_is_coboundary :
    ((1 : Int) - 0 = 1) ∧ ((1 : Int) - 1 = 0) := by
  decide

theorem chart2_is_coboundary :
    ((0 : Int) - 0 = 0) ∧ ((0 : Int) - 0 = 0) := by
  decide

theorem global_cycle_obstructed : phiCycle 1 0 0 = 1 := by
  decide

theorem zero_cycle_exact : phiCycle 0 0 0 = 0 := by
  decide

theorem global_step_not_descent : ¬ (phiCycle 1 0 0 < phiCycle 0 0 0) := by
  decide

theorem cyclic_shift_preserves_cycle_sum :
    phiCycle 1 0 0 = 1 ∧ phiCycle 0 1 0 = 1 ∧ phiCycle 0 0 1 = 1 := by
  decide

structure Step where
  name : String
  beforePhi : Int
  afterPhi : Int

def stepOk (s : Step) : Bool := decide (s.afterPhi < s.beforePhi)

def bridgeOk : List Step → Bool
  | [] => true
  | [_] => true
  | a :: b :: rest => decide (a.afterPhi = b.beforePhi) && bridgeOk (b :: rest)

def pathOk (steps : List Step) : Bool :=
  !steps.isEmpty && steps.all stepOk && bridgeOk steps

def erase (s : Step) : Step := { s with name := "Dummy" }

theorem stepOk_erase (s : Step) : stepOk (erase s) = stepOk s := rfl

theorem bridgeOk_erase (steps : List Step) : bridgeOk (steps.map erase) = bridgeOk steps := by
  induction steps with
  | nil => rfl
  | cons a rest ih =>
    cases rest with
    | nil => rfl
    | cons b rest2 =>
      simp only [bridgeOk, List.map, erase]
      have htail := ih
      simp only [List.map, erase] at htail
      rw [htail]

theorem all_stepOk_erase (steps : List Step) :
    (steps.map erase).all stepOk = steps.all stepOk := by
  induction steps with
  | nil => rfl
  | cons a rest ih =>
    simp [List.all, List.map, stepOk, erase, ih]

theorem map_isEmpty (steps : List Step) :
    (steps.map erase).isEmpty = steps.isEmpty := by
  cases steps <;> rfl

theorem pathOk_erase (steps : List Step) : pathOk (steps.map erase) = pathOk steps := by
  simp only [pathOk]
  rw [map_isEmpty, all_stepOk_erase, bridgeOk_erase]

def demoAuth : List Step :=
  [⟨"AuthOp_1", 3, 2⟩, ⟨"AuthOp_2", 2, 1⟩]

def demoErased : List Step :=
  [⟨"Dummy", 3, 2⟩, ⟨"Dummy", 2, 1⟩]

theorem both_paths_accept :
    pathOk demoAuth = true ∧ pathOk demoErased = true := by
  decide

def applyAll {X : Type} : List (X → X) → X → X
  | [], x => x
  | T :: rest, x => applyAll rest (T x)

def wordOf {X : Type} (Fam : (X → X) → Prop) (W : List (X → X)) : Prop :=
  ∀ op ∈ W, Fam op

def ContEq {X Y : Type} (D : X → Y) (Fam : (X → X) → Prop) (x y : X) : Prop :=
  ∀ W, wordOf Fam W → D (applyAll W x) = D (applyAll W y)

theorem contEq_refl {X Y : Type} (D : X → Y) (Fam : (X → X) → Prop) (x : X) :
    ContEq D Fam x x := by
  intro _ _
  rfl

theorem contEq_symm {X Y : Type} (D : X → Y) (Fam : (X → X) → Prop) {x y : X}
    (h : ContEq D Fam x y) : ContEq D Fam y x := by
  intro W hW
  exact (h W hW).symm

theorem contEq_trans {X Y : Type} (D : X → Y) (Fam : (X → X) → Prop) {x y z : X}
    (hxy : ContEq D Fam x y) (hyz : ContEq D Fam y z) : ContEq D Fam x z := by
  intro W hW
  exact (hxy W hW).trans (hyz W hW)

theorem contEq_in_kernel {X Y : Type} (D : X → Y) (Fam : (X → X) → Prop) {x y : X}
    (h : ContEq D Fam x y) : D x = D y := by
  have hempty : wordOf Fam ([] : List (X → X)) := by
    intro _ hop
    cases hop
  simpa [applyAll] using h [] hempty

theorem contEq_stable {X Y : Type} (D : X → Y) (Fam : (X → X) → Prop)
    {x y : X} {S : X → X} (hS : Fam S) (h : ContEq D Fam x y) :
    ContEq D Fam (S x) (S y) := by
  intro W hW
  have hWord : wordOf Fam (S :: W) := by
    intro op hop
    rcases List.mem_cons.mp hop with rfl | hrest
    · exact hS
    · exact hW op hrest
  have hEq := h (S :: W) hWord
  simpa [applyAll] using hEq

theorem contEq_maximal {X Y : Type} (D : X → Y) (Fam : (X → X) → Prop)
    (R : X → X → Prop)
    (hker : ∀ {x y : X}, R x y → D x = D y)
    (hstab : ∀ {x y : X} {S : X → X}, R x y → Fam S → R (S x) (S y))
    {x y : X} (hxy : R x y) : ContEq D Fam x y := by
  intro W hW
  have hpreserve : ∀ (W : List (X → X)), wordOf Fam W → ∀ x y, R x y → R (applyAll W x) (applyAll W y) := by
    intro W hW
    induction W with
    | nil =>
      intro x y hxy
      simpa [applyAll] using hxy
    | cons S rest ih =>
      intro x y hxy
      have hS : Fam S := hW S (List.Mem.head rest)
      have hrest : wordOf Fam rest := by
        intro op hop
        exact hW op (List.mem_cons_of_mem S hop)
      have htail := ih hrest (S x) (S y) (hstab hxy hS)
      simpa [applyAll] using htail
  exact hker (hpreserve W hW x y hxy)

abbrev Tri := Int × Int × Int

def phiTri (w : Tri) : Nat := (w.1 + w.2.1 + w.2.2).natAbs

def translate (w : Tri) : Tri := (w.1 + 1, w.2.1, w.2.2)

def transFam : (Tri → Tri) → Prop := fun T => T = translate

theorem same_phi_split_by_translation :
    phiTri (1, 0, 0) = 1 ∧ phiTri (-1, 0, 0) = 1 ∧
    phiTri (translate (1, 0, 0)) = 2 ∧ phiTri (translate (-1, 0, 0)) = 0 := by
  decide

theorem translation_splits_kernel :
    ¬ ContEq phiTri transFam (1, 0, 0) (-1, 0, 0) := by
  intro h
  have hW : wordOf transFam [translate] := by
    intro op hop
    simp at hop
    simpa [transFam] using hop
  have hEq := h [translate] hW
  simp [applyAll, translate, phiTri] at hEq

end OperatorProposal
