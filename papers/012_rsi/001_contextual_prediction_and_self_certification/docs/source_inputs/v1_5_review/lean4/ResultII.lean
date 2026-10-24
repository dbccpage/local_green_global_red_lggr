/-!
# Result II: the fiber lemma and the one-step boundary

Mechanised: Lemma II (needs no vector space), its corollary for a boundary
map with a nontrivial fiber, and the swap-dynamics witness that the
instantaneous kernel does not give privacy over time.

Not mechanised: Proposition II-open (privacy over time) is OPEN in the
manuscript. Only the recorded counterexample to the version 1.0.0 claim is
checked here, plus the fact that the swap map does not satisfy the
intertwining condition.
-/
namespace EpistemicNoGo.ResultII

/-- Lemma II. If `E w = E w'` and `q w ≠ q w'`, no `f` satisfies `f ∘ E = q`. -/
theorem fiber_lemma {W K A : Type} (E : W → K) (q : W → A) (w w' : W)
    (hE : E w = E w') (hq : q w ≠ q w') :
    ¬ ∃ f : K → A, ∀ x, f (E x) = q x := by
  intro ⟨f, hf⟩
  apply hq
  rw [← hf w, ← hf w', hE]

/-- Corollary II, stated without vector spaces: a boundary map with two
distinct states of one image admits no predictor of the full state that reads
only the boundary. -/
theorem no_perfect_peer_prediction {S B : Type} (π : S → B) (s s' : S)
    (hne : s ≠ s') (hπ : π s = π s') :
    ¬ ∃ f : B → S, ∀ x, f (π x) = x :=
  fiber_lemma π id s s' hπ hne

/-- A fiber over a report that holds two states. -/
def HasPrivateFiber {S B : Type} (π : S → B) : Prop :=
  ∃ s s', s ≠ s' ∧ π s = π s'

theorem private_fiber_blocks_prediction {S B : Type} (π : S → B)
    (h : HasPrivateFiber π) : ¬ ∃ f : B → S, ∀ x, f (π x) = x := by
  obtain ⟨s, s', hne, hπ⟩ := h
  exact no_perfect_peer_prediction π s s' hne hπ

/-! ### The instance `K = F2 × F2`, `π (a, b) = a` -/

abbrev K2 := Bool × Bool

def proj : K2 → Bool := fun s => s.1

/-- The kernel of `proj` is nonzero: `(false, true)` and `(false, false)` share
a report. -/
theorem proj_has_private_fiber : HasPrivateFiber proj :=
  ⟨(false, false), (false, true), by decide, rfl⟩

theorem proj_no_perfect_prediction : ¬ ∃ f : Bool → K2, ∀ x, f (proj x) = x :=
  private_fiber_blocks_prediction proj proj_has_private_fiber

/-! ### The swap-dynamics witness (falsifier of version 1.0.0, Prop 2.4) -/

/-- Swap dynamics `F (a, b) = (b, a)`. -/
def swap : K2 → K2 := fun s => (s.2, s.1)

/-- The coordinate hidden at time 0 is the report at time 1. -/
theorem hidden_at_zero_is_report_at_one (s : K2) : proj (swap s) = s.2 := rfl

/-- The intertwining condition `π ∘ F = F̄ ∘ π` fails for the swap dynamics:
no report-level map `F̄` exists. -/
theorem swap_not_intertwined : ¬ ∃ Fbar : Bool → Bool, ∀ s, proj (swap s) = Fbar (proj s) := by
  intro ⟨Fbar, h⟩
  have h1 := h (false, false)
  have h2 := h (false, true)
  simp only [proj, swap] at h1 h2
  rw [← h1] at h2
  exact absurd h2 (by decide)

/-- Hence the report at time 1 is not a function of the report at time 0, and
the instantaneous kernel statement does not imply privacy over time. -/
theorem kernel_does_not_give_privacy_over_time :
    HasPrivateFiber proj ∧ (¬ ∃ Fbar : Bool → Bool, ∀ s, proj (swap s) = Fbar (proj s)) :=
  ⟨proj_has_private_fiber, swap_not_intertwined⟩

end EpistemicNoGo.ResultII
