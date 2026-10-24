import ResultII
import ResultIII
import ResultIV

/-! Connections to the RSI companion. No declarations from the sibling package
are imported. Policy acceptance and semantic safety are deliberately distinct. -/
namespace EpistemicNoGo.Bridge

def runWord {S U : Type} (step : U → S → S) : List U → S → S
  | [], s => s
  | u :: us, s => runWord step us (step u s)

def PreservesFibers {S U B : Type} (report : S → B) (step : U → S → S) : Prop :=
  ∀ u s t, report s = report t → report (step u s) = report (step u t)

theorem report_eq_after_word {S U B : Type} (report : S → B) (step : U → S → S)
    (h : PreservesFibers report step) (word : List U) (s t : S)
    (heq : report s = report t) :
    report (runWord step word s) = report (runWord step word t) := by
  induction word generalizing s t with
  | nil => exact heq
  | cons u us ih => exact ih (step u s) (step u t) (h u s t heq)

theorem fibers_preserved_iff_all_words {S U B : Type}
    (report : S → B) (step : U → S → S) :
    PreservesFibers report step ↔
      ∀ (word : List U) (s t : S), report s = report t →
        report (runWord step word s) = report (runWord step word t) := by
  constructor
  · exact fun h word s t heq => report_eq_after_word report step h word s t heq
  · intro h u s t heq
    exact h [u] s t heq

theorem intertwining_preserves_fibers {S U B : Type}
    (report : S → B) (step : U → S → S) (reduced : U → B → B)
    (h : ∀ u s, report (step u s) = reduced u (report s)) :
    PreservesFibers report step := by
  intro u s t heq
  rw [h, h, heq]

theorem future_task_collision_blocks_prediction {S U B Q : Type}
    (report : S → B) (step : U → S → S) (task : S → Q)
    (s t : S) (heq : report s = report t) (word : List U)
    (hne : task (runWord step word s) ≠ task (runWord step word t)) :
    ¬ ∃ predict : B → Q, ∀ z, predict (report z) = task (runWord step word z) :=
  ResultII.fiber_lemma report (fun z => task (runWord step word z)) s t heq hne

/-- With no integrity hypothesis, the same externally pinned tip can accept
different histories, even histories of different lengths. -/
theorem pinned_tip_can_collide :
    ResultIII.completeAgainst (fun _ _ => 0) 0 0 [] = true ∧
    ResultIII.completeAgainst (fun _ _ => 0) 0 0 [(7, 0)] = true ∧
    ([] : List ResultIII.Entry) ≠ [(7, 0)] := by
  decide

def actionSafe (action : Nat) : Prop := action = 0

/-- A real successful policy-model evaluation together with a concrete unsafe
action. The packet gate has no action argument or action-safety premise. -/
theorem provenance_pass_can_be_unsafe :
    (∃ receipt, ResultIV.verify ResultIV.distinctStringsPacket
      (ResultIV.Policy.strict ["root:R"]) = .ok receipt) ∧ ¬ actionSafe 1 := by
  exact ⟨ResultIV.distinct_strings_pass, by change ¬ (1 : Nat) = 0; decide⟩

end EpistemicNoGo.Bridge
