namespace LiveMemory

def consistent {K V : Type} (rows : List (K × V)) : Prop :=
  ∀ p ∈ rows, ∀ q ∈ rows, p.1 = q.1 → p.2 = q.2

instance {K V : Type} [DecidableEq K] [DecidableEq V] (rows : List (K × V)) :
    Decidable (consistent rows) := by unfold consistent; infer_instance

def supported {K V : Type} (source : K × V → Prop) (rows : List (K × V)) : Prop :=
  ∀ p ∈ rows, source p

instance {K V : Type} (source : K × V → Prop) [DecidablePred source]
    (rows : List (K × V)) : Decidable (supported source rows) := by
  unfold supported; infer_instance

def update {K V : Type} [DecidableEq K] [DecidableEq V]
    (source : K × V → Prop) [DecidablePred source] (old fresh : List (K × V)) :=
  if consistent (old ++ fresh) ∧ supported source (old ++ fresh)
  then some (old ++ fresh) else none

theorem update_sound {K V : Type} [DecidableEq K] [DecidableEq V]
    (source : K × V → Prop) [DecidablePred source] (old fresh next : List (K × V))
    (h : update source old fresh = some next) : consistent next ∧ supported source next := by
  unfold update at h
  split at h
  next good => cases Option.some.inj h; exact good
  next => cases h

theorem update_retains {K V : Type} [DecidableEq K] [DecidableEq V]
    (source : K × V → Prop) [DecidablePred source] (old fresh next : List (K × V))
    (h : update source old fresh = some next) : ∀ p ∈ old, p ∈ next := by
  unfold update at h
  split at h
  next => cases Option.some.inj h; intro p hp; exact List.mem_append_left fresh hp
  next => cases h

def commit {S : Type} (old : S) (candidate : Option S) : S := candidate.getD old

theorem refused_update_preserves {S : Type} (old : S) : commit old none = old := rfl

def checkedRecall {K V : Type} [DecidableEq K] [DecidableEq V]
    (source : K × V → Prop) [DecidablePred source] (rows : List (K × V))
    (binding : Bool) (key : K) (value : V) : Option V :=
  if binding = true ∧ consistent rows ∧ supported source rows ∧ (key, value) ∈ rows
  then some value else none

theorem recall_sound {K V : Type} [DecidableEq K] [DecidableEq V]
    (source : K × V → Prop) [DecidablePred source] (rows : List (K × V))
    (binding : Bool) (key : K) (value answer : V)
    (h : checkedRecall source rows binding key value = some answer) :
    binding = true ∧ source (key, answer) ∧
      ∀ p ∈ rows, p.1 = key → p.2 = answer := by
  unfold checkedRecall at h
  split at h
  next good =>
    cases Option.some.inj h
    obtain ⟨hb, hc, hs, hm⟩ := good
    exact ⟨hb, hs _ hm, fun p hp eq => hc p hp (key, value) hm eq⟩
  next => cases h

theorem changed_binding_refuses {K V : Type} [DecidableEq K] [DecidableEq V]
    (source : K × V → Prop) [DecidablePred source] (rows : List (K × V))
    (key : K) (value : V) : checkedRecall source rows false key value = none := by
  simp [checkedRecall]

theorem missing_support_refuses {K V : Type} [DecidableEq K] [DecidableEq V]
    (source : K × V → Prop) [DecidablePred source] (rows : List (K × V))
    (binding : Bool) (key : K) (value : V) (h : ¬ supported source rows) :
    checkedRecall source rows binding key value = none := by simp [checkedRecall, h]

theorem exact_reload_preserves_recall {K V : Type} [DecidableEq K] [DecidableEq V]
    (source : K × V → Prop) [DecidablePred source] (before after : List (K × V))
    (binding : Bool) (key : K) (value : V) (h : after = before) :
    checkedRecall source after binding key value = checkedRecall source before binding key value := by rw [h]

theorem conflict_refused : update (fun _ : Bool × Bool => True)
    [(false, false)] [(false, true)] = none := by decide

end LiveMemory
