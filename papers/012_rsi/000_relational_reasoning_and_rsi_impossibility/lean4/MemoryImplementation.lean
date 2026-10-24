import EmbeddedLimits

namespace MemoryImplementation

def Compatible {O Y : Type} (rows : List (O × Y)) : Prop :=
  ∀ p ∈ rows, ∀ q ∈ rows, p.1 = q.1 → p.2 = q.2

instance {O Y : Type} [DecidableEq O] [DecidableEq Y] (rows : List (O × Y)) :
    Decidable (Compatible rows) := by
  unfold Compatible
  infer_instance

def appendChecked {O Y : Type} [DecidableEq O] [DecidableEq Y]
    (old fresh : List (O × Y)) : Option (List (O × Y)) :=
  if Compatible (old ++ fresh) then some (old ++ fresh) else none

theorem accepted_append_compatible {O Y : Type} [DecidableEq O] [DecidableEq Y]
    (old fresh next : List (O × Y)) (h : appendChecked old fresh = some next) :
    Compatible next := by
  unfold appendChecked at h
  split at h
  next hc => cases Option.some.inj h; exact hc
  next => cases h

theorem accepted_append_retains {O Y : Type} [DecidableEq O] [DecidableEq Y]
    (old fresh next : List (O × Y)) (h : appendChecked old fresh = some next) :
    ∀ entry ∈ old, entry ∈ next := by
  unfold appendChecked at h
  split at h
  next => cases Option.some.inj h; intro e he; exact List.mem_append_left fresh he
  next => cases h

def recallChecked {O Y : Type} [DecidableEq O] [DecidableEq Y]
    (rows : List (O × Y)) (label : O) (candidate : Y) : Option Y :=
  if (label, candidate) ∈ rows ∧ ∀ p ∈ rows, p.1 = label → p.2 = candidate
  then some candidate else none

theorem accepted_recall_sound {O Y : Type} [DecidableEq O] [DecidableEq Y]
    (rows : List (O × Y)) (label : O) (candidate value : Y)
    (h : recallChecked rows label candidate = some value) :
    (label, value) ∈ rows ∧ ∀ p ∈ rows, p.1 = label → p.2 = value := by
  unfold recallChecked at h
  split at h
  next hc => cases Option.some.inj h; exact hc
  next => cases h

theorem conflicting_append_refused :
    appendChecked [(false, false)] [(false, true)] = none := by decide

theorem stale_recall_refused :
    recallChecked [(false, false), (false, true)] false false = none := by decide

def swap (x : Bool × Bool) (act : Bool) : Bool × Bool :=
  if act then (x.2, x.1) else x

theorem run_updates_commute {X A M : Type} (step : X → A → X)
    (memory : X → M) (update : M → A → M)
    (commutes : ∀ x a, memory (step x a) = update (memory x) a) (x : X) (w : List A) :
    memory (EmbeddedLimits.runWord step x w) = EmbeddedLimits.runWord update (memory x) w := by
  induction w generalizing x with
  | nil => rfl
  | cons a rest ih =>
    change memory (EmbeddedLimits.runWord step (step x a) rest) =
      EmbeddedLimits.runWord update (update (memory x) a) rest
    rw [ih, commutes]

def encode (x : Bool × Bool) : Bool × Bool := (x.2, x.1)

theorem pair_memory_commutes (x : Bool × Bool) (a : Bool) :
    encode (swap x a) = swap (encode x) a := by
  cases a <;> rfl

theorem pair_memory_preserves_all_words (x : Bool × Bool) (w : List Bool) :
    (EmbeddedLimits.runWord swap x w).1 =
      (EmbeddedLimits.runWord swap (encode x) w).2 := by
  have h := congrArg Prod.snd (run_updates_commute swap encode swap pair_memory_commutes x w)
  exact h

theorem first_bit_memory_fails_after_swap :
    (false, false).1 = (false, true).1 ∧
      (swap (false, false) true).1 ≠ (swap (false, true) true).1 := by decide

def gated {X A : Type} (safe : X → Prop) [DecidablePred safe]
    (step : X → A → X) (x : X) (a : A) : X :=
  if safe (step x a) then step x a else x

theorem gated_preserves {X A : Type} (safe : X → Prop) [DecidablePred safe]
    (step : X → A → X) (x : X) (a : A) (hx : safe x) :
    safe (gated safe step x a) := by
  unfold gated
  split
  next h => exact h
  next => exact hx

theorem gated_run_preserves {X A : Type} (safe : X → Prop) [DecidablePred safe]
    (step : X → A → X) (x : X) (w : List A) (hx : safe x) :
    safe (EmbeddedLimits.runWord (gated safe step) x w) := by
  induction w generalizing x with
  | nil => exact hx
  | cons a rest ih => exact ih _ (gated_preserves safe step x a hx)

def admissible (x : Bool × Bool) : Prop := x ≠ (true, true)

instance (x : Bool × Bool) : Decidable (admissible x) := inferInstanceAs (Decidable (x ≠ (true, true)))

def overwrite (_x : Bool × Bool) (a : Bool × Bool) : Bool × Bool := a

theorem unsafe_overwrite_is_blocked :
    gated admissible overwrite (false, false) (true, true) = (false, false) := by decide

theorem concrete_gate_preserves_every_word (w : List (Bool × Bool)) :
    admissible (EmbeddedLimits.runWord (gated admissible overwrite) (false, false) w) :=
  gated_run_preserves admissible overwrite (false, false) w (by decide)

end MemoryImplementation
