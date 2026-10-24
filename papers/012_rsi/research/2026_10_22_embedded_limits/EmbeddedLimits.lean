/-! Constructive, task-relative limits for records inside a declared world model.
These theorems do not identify truth with a permission policy or introduce an
observer outside the world. They do not prove physical model adequacy.
-/
namespace EmbeddedLimits

def Determined {X O : Type} (record : X → O) (p : X → Prop) (x : X) : Prop :=
  ∀ y, record y = record x → p y

theorem determined_is_true {X O : Type} {r : X → O} {p : X → Prop} {x : X}
    (h : Determined r p x) : p x := h x rfl

theorem positive_introspection {X O : Type} {r : X → O} {p : X → Prop} {x : X}
    (h : Determined r p x) : Determined r (Determined r p) x := by
  intro y hy z hz
  exact h z (Eq.trans hz hy)

theorem own_record_is_determined {X O : Type} (r : X → O) (x : X) :
    Determined r (fun y => r y = r x) x := by
  intro y hy
  exact hy

theorem refinement_preserves_determination {X O P : Type} {r : X → O} {s : X → P}
    (h : ∀ x y, s x = s y → r x = r y) {p : X → Prop} {x : X}
    (known : Determined r p x) : Determined s p x := by
  intro y hy
  exact known y (h y x hy)

def FiberConstant {X O Y : Type} (r : X → O) (f : X → Y) : Prop :=
  ∀ x y, r x = r y → f x = f y

theorem decoder_implies_fiber_constant {X O Y : Type} {r : X → O} {f : X → Y}
    (d : O → Y) (h : ∀ x, d (r x) = f x) : FiberConstant r f := by
  intro x y same
  exact Eq.trans (Eq.symm (h x)) (Eq.trans (congrArg d same) (h y))

theorem section_constructs_decoder {X O Y : Type} {r : X → O} {f : X → Y}
    (representative : O → X) (hsection : ∀ x, r (representative (r x)) = r x)
    (h : FiberConstant r f) : ∃ d : O → Y, ∀ x, d (r x) = f x := by
  exact ⟨fun o => f (representative o), fun x => h (representative (r x)) x (hsection x)⟩

theorem recoverable_iff_fiber_constant {X O Y : Type} {r : X → O} {f : X → Y}
    (representative : O → X) (hsection : ∀ x, r (representative (r x)) = r x) :
    (∃ d : O → Y, ∀ x, d (r x) = f x) ↔ FiberConstant r f := by
  constructor
  · intro ⟨d, hd⟩
    exact decoder_implies_fiber_constant d hd
  · exact section_constructs_decoder representative hsection

theorem postprocessing_cannot_separate {X O P : Type} {r : X → O}
    (a : O → P) {x y : X} (h : r x = r y) : a (r x) = a (r y) := congrArg a h

theorem collision_excludes_exact_decoder {X O Y : Type} {r : X → O} {f : X → Y}
    {x y : X} (same : r x = r y) (different : f x ≠ f y) :
    ¬ ∃ d : O → Y, ∀ z, d (r z) = f z := by
  intro ⟨d, hd⟩
  exact different (decoder_implies_fiber_constant d hd x y same)

theorem added_task_requires_refinement {X M Y : Type} {m : X → M} {f : X → Y}
    (d : M → Y) (h : ∀ x, d (m x) = f x) :
    ∀ x y, m x = m y → f x = f y := decoder_implies_fiber_constant d h

def runWord {X A : Type} (step : X → A → X) : X → List A → X
  | x, [] => x
  | x, a :: rest => runWord step (step x a) rest

def FutureEq {X A Y : Type} (step : X → A → X) (readout : X → Y) (x y : X) : Prop :=
  ∀ word, readout (runWord step x word) = readout (runWord step y word)

theorem future_eq_refl {X A Y : Type} (step : X → A → X) (readout : X → Y) (x : X) :
    FutureEq step readout x x := fun _ => rfl

theorem future_eq_symm {X A Y : Type} {step : X → A → X} {readout : X → Y} {x y : X}
    (h : FutureEq step readout x y) : FutureEq step readout y x := fun w => Eq.symm (h w)

theorem future_eq_trans {X A Y : Type} {step : X → A → X} {readout : X → Y} {x y z : X}
    (h : FutureEq step readout x y) (g : FutureEq step readout y z) :
    FutureEq step readout x z := fun w => Eq.trans (h w) (g w)

theorem future_eq_preserves_readout {X A Y : Type} {step : X → A → X} {readout : X → Y}
    {x y : X} (h : FutureEq step readout x y) : readout x = readout y := h []

theorem future_eq_stable {X A Y : Type} {step : X → A → X} {readout : X → Y}
    {x y : X} (h : FutureEq step readout x y) (a : A) :
    FutureEq step readout (step x a) (step y a) := fun w => h (a :: w)

theorem stable_relation_refines_future_eq {X A Y : Type} (step : X → A → X) (readout : X → Y)
    (R : X → X → Prop) (observable : ∀ x y, R x y → readout x = readout y)
    (stable : ∀ x y a, R x y → R (step x a) (step y a)) {x y : X} (h : R x y) :
    FutureEq step readout x y := by
  intro word
  induction word generalizing x y with
  | nil => exact observable x y h
  | cons a rest ih => exact ih (stable x y a h)

theorem implemented_memory_preserves_future {X A M Y : Type} (step : X → A → X)
    (memory : X → M) (update : M → A → M) (decode : M → Y) (readout : X → Y)
    (reads : ∀ x, decode (memory x) = readout x)
    (updates : ∀ x a, memory (step x a) = update (memory x) a)
    {x y : X} (same : memory x = memory y) : FutureEq step readout x y := by
  apply stable_relation_refines_future_eq step readout (fun u v => memory u = memory v)
  · intro u v huv
    exact Eq.trans (Eq.symm (reads u)) (Eq.trans (congrArg decode huv) (reads v))
  · intro u v a huv
    exact Eq.trans (updates u a) (Eq.trans (congrArg (fun m => update m a) huv) (Eq.symm (updates v a)))
  · exact same

theorem bool_cannot_equal_its_negation (b : Bool) : b ≠ !b := by
  cases b <;> decide

theorem anti_prediction_not_universal {X : Type} (predict : X → Bool) (x : X) :
    predict x ≠ !(predict x) := bool_cannot_equal_its_negation (predict x)

theorem fiber_soundness_is_maximal {X O : Type} (r : X → O) (safe : X → Prop)
    (gate : O → Prop) (sound : ∀ x, gate (r x) → safe x) {x : X}
    (accepted : gate (r x)) : Determined r safe x := by
  intro y same
  exact sound y (same ▸ accepted)

end EmbeddedLimits
