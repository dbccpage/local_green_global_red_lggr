/-!
AVF-030-C11. Finite calibration completeness.

If a specification and a detector are constant on each block of a finite
partition, and the representative list meets every block, then they agree on
the representatives if and only if they agree on the whole carrier.

If one block is missed, flipping the specification on that block stays
class-constant, agrees on every representative, and disagrees on a witness
from the missed block.
-/

abbrev Class := List Nat

def carrier : List Class → List Nat
  | [] => []
  | c :: cs => c ++ carrier cs

def classConstant (classes : List Class) (f : Nat → Bool) : Prop :=
  ∀ c, c ∈ classes → ∀ a, a ∈ c → ∀ b, b ∈ c → f a = f b

def hits (classes : List Class) (reps : List Nat) : Prop :=
  ∀ c, c ∈ classes → ∃ r, r ∈ reps ∧ r ∈ c

def agreesOn (xs : List Nat) (f g : Nat → Bool) : Prop :=
  ∀ x, x ∈ xs → f x = g x

theorem mem_carrier {classes : List Class} {x : Nat} :
    x ∈ carrier classes ↔ ∃ c, c ∈ classes ∧ x ∈ c := by
  induction classes with
  | nil => simp [carrier]
  | cons c cs ih =>
    simp [carrier, List.mem_append, ih, List.mem_cons, exists_or, or_and_right]

theorem rep_mem_carrier {classes : List Class} {c : Class} {r : Nat}
    (hc : c ∈ classes) (hr : r ∈ c) : r ∈ carrier classes :=
  (mem_carrier).mpr ⟨c, hc, hr⟩

theorem calibration_from_representatives
    (classes : List Class) (reps : List Nat) (spec det : Nat → Bool)
    (hspec : classConstant classes spec) (hdet : classConstant classes det)
    (hhit : hits classes reps) (hagree : agreesOn reps spec det)
    (x : Nat) (hx : x ∈ carrier classes) : spec x = det x := by
  rcases (mem_carrier).mp hx with ⟨c, hc, hxc⟩
  rcases hhit c hc with ⟨r, hr, hrc⟩
  have hspecEq : spec x = spec r := hspec c hc x hxc r hrc
  have hdetEq : det x = det r := hdet c hc x hxc r hrc
  exact hspecEq.trans ((hagree r hr).trans hdetEq.symm)

theorem representatives_from_calibration
    (classes : List Class) (reps : List Nat) (spec det : Nat → Bool)
    (hcovered : ∀ r, r ∈ reps → r ∈ carrier classes)
    (hagree : agreesOn (carrier classes) spec det) : agreesOn reps spec det := by
  intro r hr
  exact hagree r (hcovered r hr)

def disjointClasses (classes : List Class) : Prop :=
  ∀ c1, c1 ∈ classes → ∀ c2, c2 ∈ classes → c1 ≠ c2 → ∀ x, x ∈ c1 → x ∉ c2

def flipOn (miss : Class) (spec : Nat → Bool) (x : Nat) : Bool :=
  if x ∈ miss then Bool.not (spec x) else spec x

theorem bool_not_ne (b : Bool) : b ≠ Bool.not b := by
  cases b <;> decide

theorem sharpness
    (classes : List Class) (reps : List Nat) (spec : Nat → Bool)
    (miss : Class) (witness : Nat)
    (hspec : classConstant classes spec)
    (hdisj : disjointClasses classes)
    (hmiss : miss ∈ classes)
    (hwitness : witness ∈ miss)
    (hmissed : ¬ ∃ r, r ∈ reps ∧ r ∈ miss) :
    classConstant classes (flipOn miss spec) ∧
      agreesOn reps spec (flipOn miss spec) ∧
      spec witness ≠ flipOn miss spec witness := by
  refine ⟨?constant, ?agree, ?differ⟩
  · intro c hc a ha b hb
    by_cases hcm : c = miss
    · rw [hcm] at ha hb
      simp [flipOn, ha, hb, hspec miss hmiss a ha b hb]
    · have haOut : a ∉ miss := hdisj c hc miss hmiss hcm a ha
      have hbOut : b ∉ miss := hdisj c hc miss hmiss hcm b hb
      simp [flipOn, haOut, hbOut, hspec c hc a ha b hb]
  · intro r hr
    have hrOut : r ∉ miss := by
      intro hrm
      exact hmissed ⟨r, hr, hrm⟩
    simp [flipOn, hrOut]
  · have flipped : flipOn miss spec witness = Bool.not (spec witness) := by
      simp [flipOn, hwitness]
    rw [flipped]
    exact bool_not_ne (spec witness)

def exampleClasses : List Class := [[0], [1, 2], [3, 4]]

def exampleReps : List Nat := [0, 1, 3]

def omittedReps : List Nat := [0, 1]

def zeroSpec (x : Nat) : Bool := x == 0

theorem example_classes_disjoint : disjointClasses exampleClasses := by
  intro c1 hc1 c2 hc2 hne x hx1 hx2
  simp [exampleClasses] at hc1 hc2
  rcases hc1 with rfl | rfl | rfl <;> rcases hc2 with rfl | rfl | rfl
  · exact hne rfl
  · simp at hx1 hx2
    rcases hx2 with rfl | rfl <;> cases hx1
  · simp at hx1 hx2
    rcases hx2 with rfl | rfl <;> cases hx1
  · simp at hx1 hx2
    rcases hx1 with rfl | rfl <;> cases hx2
  · exact hne rfl
  · simp at hx1 hx2
    rcases hx1 with rfl | rfl <;> rcases hx2 with h | h <;> cases h
  · simp at hx1 hx2
    rcases hx1 with rfl | rfl <;> cases hx2
  · simp at hx1 hx2
    rcases hx2 with rfl | rfl <;> rcases hx1 with h | h <;> cases h
  · exact hne rfl

theorem example_reps_hit : hits exampleClasses exampleReps := by
  intro c hc
  simp [exampleClasses] at hc
  rcases hc with rfl | rfl | rfl
  · exact ⟨0, by simp [exampleReps], by simp⟩
  · exact ⟨1, by simp [exampleReps], by simp⟩
  · exact ⟨3, by simp [exampleReps], by simp⟩

theorem example_spec_constant : classConstant exampleClasses zeroSpec := by
  intro c hc a ha b hb
  simp [exampleClasses] at hc
  rcases hc with rfl | rfl | rfl
  · simp at ha hb
    subst ha
    subst hb
    rfl
  · simp at ha hb
    rcases ha with rfl | rfl <;> rcases hb with rfl | rfl <;> rfl
  · simp at ha hb
    rcases ha with rfl | rfl <;> rcases hb with rfl | rfl <;> rfl

theorem example_complete :
    agreesOn (carrier exampleClasses) zeroSpec zeroSpec :=
  calibration_from_representatives exampleClasses exampleReps zeroSpec zeroSpec
    example_spec_constant example_spec_constant example_reps_hit (by intro _ _; rfl)

theorem example_omits_last : ¬ ∃ r, r ∈ omittedReps ∧ r ∈ ([3, 4] : Class) := by
  intro h
  rcases h with ⟨r, hr, hm⟩
  simp [omittedReps] at hr
  rcases hr with rfl | rfl <;> simp at hm

theorem example_sharpness :
    classConstant exampleClasses (flipOn [3, 4] zeroSpec) ∧
      agreesOn omittedReps zeroSpec (flipOn [3, 4] zeroSpec) ∧
      zeroSpec 3 ≠ flipOn [3, 4] zeroSpec 3 :=
  sharpness exampleClasses omittedReps zeroSpec [3, 4] 3
    example_spec_constant example_classes_disjoint (by simp [exampleClasses]) (by simp)
    example_omits_last
