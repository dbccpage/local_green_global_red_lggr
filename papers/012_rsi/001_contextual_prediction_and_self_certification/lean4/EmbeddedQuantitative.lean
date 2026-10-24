import MindContracts
import EmbeddedLimits

open scoped BigOperators
namespace EpistemicNoGo.EmbeddedQuantitative

theorem midpoint_error {lo hi value : ℝ} (hl : lo ≤ value) (hh : value ≤ hi) :
    |value - (lo + hi) / 2| ≤ (hi - lo) / 2 := by
  apply abs_le.mpr
  constructor <;> linarith

theorem fiber_pair_lower_bound {X O : Type} (r : X → O) (f : X → ℝ)
    (decode : O → ℝ) (x y : X) (same : r x = r y) (bound : ℝ)
    (hx : |f x - decode (r x)| ≤ bound) (hy : |f y - decode (r y)| ≤ bound) :
    |f x - f y| / 2 ≤ bound := by
  rw [← same] at hy
  have h := abs_sub_le (f x) (decode (r x)) (f y)
  rw [abs_sub_comm (decode (r x)) (f y)] at h
  linarith

theorem midpoint_decoder_attains {X O : Type} (r : X → O) (f : X → ℝ)
    (lo hi : O → ℝ) (radius : ℝ)
    (low : ∀ x, lo (r x) ≤ f x) (high : ∀ x, f x ≤ hi (r x))
    (width : ∀ x, (hi (r x) - lo (r x)) / 2 ≤ radius) :
    ∀ x, |f x - (lo (r x) + hi (r x)) / 2| ≤ radius := by
  intro x
  exact (midpoint_error (low x) (high x)).trans (width x)

theorem attained_fiber_minimax {X O : Type} (r : X → O) (f : X → ℝ)
    (lo hi : O → ℝ) (radius : ℝ)
    (low : ∀ x, lo (r x) ≤ f x) (high : ∀ x, f x ≤ hi (r x))
    (width : ∀ x, (hi (r x) - lo (r x)) / 2 ≤ radius)
    (x y : X) (same : r x = r y) (witness : |f x - f y| / 2 = radius) :
    (∃ decode : O → ℝ, ∀ z, |f z - decode (r z)| ≤ radius) ∧
    (∀ decode : O → ℝ, ∀ bound : ℝ,
      (∀ z, |f z - decode (r z)| ≤ bound) → radius ≤ bound) := by
  constructor
  · exact ⟨fun o => (lo o + hi o) / 2, midpoint_decoder_attains r f lo hi radius low high width⟩
  · intro decode bound h
    rw [← witness]
    exact fiber_pair_lower_bound r f decode x y same bound (h x) (h y)

theorem future_classes_require_memory {X A M Y C : Type} [Fintype M] [Fintype C]
    (step : X → A → X) (memory : X → M) (update : M → A → M)
    (decode : M → Y) (readout : X → Y) (representative : C → X)
    (reads : ∀ x, decode (memory x) = readout x)
    (updates : ∀ x a, memory (step x a) = update (memory x) a)
    (distinct : ∀ i j, EmbeddedLimits.FutureEq step readout (representative i) (representative j) → i = j) :
    Fintype.card C ≤ Fintype.card M := by
  apply Fintype.card_le_of_injective (fun c => memory (representative c))
  intro i j same
  exact distinct i j (EmbeddedLimits.implemented_memory_preserves_future
    step memory update decode readout reads updates same)

noncomputable def tv {I : Type*} [Fintype I] (p q : I → ℝ) : ℝ :=
  (∑ i, |p i - q i|) / 2

theorem bounded_loss_tv {I : Type*} [Fintype I] (p q loss : I → ℝ)
    (mass : ∑ i, p i = ∑ i, q i)
    (range : ∀ i, 0 ≤ loss i ∧ loss i ≤ 1) :
    |(∑ i, p i * loss i) - ∑ i, q i * loss i| ≤ tv p q := by
  have center : (∑ i, p i * loss i) - ∑ i, q i * loss i =
      ∑ i, (p i - q i) * (loss i - 1 / 2) := by
    simp only [mul_sub, sub_mul, Finset.sum_sub_distrib, ← Finset.sum_mul]
    rw [mass]
    ring
  rw [center]
  calc
    |∑ i, (p i - q i) * (loss i - 1 / 2)| ≤ ∑ i, |(p i - q i) * (loss i - 1 / 2)| :=
      Finset.abs_sum_le_sum_abs _ _
    _ ≤ ∑ i, |p i - q i| * (1 / 2) := by
      apply Finset.sum_le_sum
      intro i _
      rw [abs_mul]
      apply mul_le_mul_of_nonneg_left _ (abs_nonneg _)
      apply abs_le.mpr
      constructor <;> linarith [(range i).1, (range i).2]
    _ = tv p q := by rw [← Finset.sum_mul]; unfold tv; ring

noncomputable def simulate {I J : Type*} [Fintype I] (kernel : I → J → ℝ) (p : I → ℝ) (j : J) : ℝ :=
  ∑ i, p i * kernel i j

theorem stochastic_simulation_mass {I J : Type*} [Fintype I] [Fintype J]
    (kernel : I → J → ℝ) (p : I → ℝ) (rows : ∀ i, ∑ j, kernel i j = 1) :
    ∑ j, simulate kernel p j = ∑ i, p i := by
  unfold simulate
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro i _
  rw [← Finset.mul_sum, rows i, mul_one]

theorem stochastic_simulation_nonnegative {I J : Type*} [Fintype I]
    (kernel : I → J → ℝ) (p : I → ℝ)
    (hk : ∀ i j, 0 ≤ kernel i j) (hp : ∀ i, 0 ≤ p i) :
    ∀ j, 0 ≤ simulate kernel p j := by
  intro j
  exact Finset.sum_nonneg (fun i _ => mul_nonneg (hp i) (hk i j))

theorem simulation_loss_transfer {T I J : Type*} [Fintype I] [Fintype J]
    (kernel : I → J → ℝ) (source : T → I → ℝ) (target loss : T → J → ℝ)
    (rows : ∀ i, ∑ j, kernel i j = 1)
    (mass : ∀ t, ∑ i, source t i = ∑ j, target t j)
    (range : ∀ t j, 0 ≤ loss t j ∧ loss t j ≤ 1) (epsilon : ℝ)
    (error : ∀ t, tv (simulate kernel (source t)) (target t) ≤ epsilon) :
    ∀ t, |(∑ j, simulate kernel (source t) j * loss t j) -
      ∑ j, target t j * loss t j| ≤ epsilon := by
  intro t
  apply (bounded_loss_tv _ _ _ _ (range t)).trans (error t)
  rw [stochastic_simulation_mass kernel (source t) rows, mass t]

end EpistemicNoGo.EmbeddedQuantitative
