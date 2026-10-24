import Bell.SmoothedFamily
import Bell.ContinuumShadows

/-! All hypotheses of the comparison envelope discharged by actual complete
finite Bell tables, POVMs, density matrices and signed optimal extensions. -/
noncomputable section
open scoped BigOperators
namespace Bell.CompleteQuantumUnbounded
attribute [local instance] Classical.propDecidable
local instance (priority := high) : DecidableEq Bool := Classical.decEq Bool
local instance (priority := high) (n : ℕ) : DecidableEq (Fin n) := Classical.decEq (Fin n)
open Bell.SmoothedFamily Bell.SmoothedComparison Bell.SignedDuality
variable (k : ℕ) [Fact (2 ≤ k)]

theorem optimum_exists (n : ℕ) :
    ∃ q : Bell.ChainWitness.Global n → ℝ,
      Bell.marginal q=behavior k n ∧ (∑ g, q g=1) ∧
      (∀ q', Bell.marginal q'=behavior k n → (∑ g, q' g=1) →
        negativeMass q ≤ negativeMass q') := by
  obtain ⟨w,hw,hm,_⟩ := signed_certificate k n
  obtain ⟨q,_,_,hq,hs,_,_,ho⟩ :=
    bell_negative_mass_duality (behavior k n) ⟨w,hm,hw⟩
  exact ⟨q,hq,hs,ho⟩

def optimizer (n : ℕ) : Bell.ChainWitness.Global n → ℝ :=
  Classical.choose (optimum_exists k n)
def minimumMass (n : ℕ) : ℝ := negativeMass (optimizer k n)

theorem optimizer_properties (n : ℕ) :
    Bell.marginal (optimizer k n)=behavior k n ∧ (∑ g, optimizer k n g=1) ∧
    (∀ q', Bell.marginal q'=behavior k n → (∑ g, q' g=1) →
      minimumMass k n ≤ negativeMass q') :=
  Classical.choose_spec (optimum_exists k n)

theorem minimum_mass_bounds (n : ℕ) :
    0 ≤ minimumMass k n ∧ minimumMass k n ≤ massCap k := by
  constructor
  · exact Finset.sum_nonneg (fun _ _ => le_max_right _ _)
  · obtain ⟨q,hs,hm,hb⟩ := signed_certificate k n
    exact ((optimizer_properties k n).2.2 q hm hs).trans hb

theorem minimum_mass_positive (n : ℕ) (hn : n+1=k*k) :
    0 < minimumMass k n := by
  have hm := (minimum_mass_bounds k n).1
  by_contra h
  have hz : minimumMass k n=0 := le_antisymm (le_of_not_gt h) hm
  have hq : ∀ g, 0 ≤ optimizer k n g := by
    intro g
    have hsingle := Finset.single_le_sum (s:=Finset.univ)
      (f:=fun g => max (-optimizer k n g) 0)
      (fun _ _ => le_max_right _ _) (Finset.mem_univ g)
    change max (-optimizer k n g) 0 ≤ minimumMass k n at hsingle
    rw [hz] at hsingle
    have := le_max_left (-optimizer k n g) 0
    linarith
  have hh : (∑ g, optimizer k n g) ≤
      Bell.ChainWitness.score (Bell.marginal (optimizer k n)) := by
    rw [Bell.ChainWitness.score_marginal]
    exact Finset.sum_le_sum (fun g _ => by
      simpa only [mul_one] using mul_le_mul_of_nonneg_left
        (Bell.ChainWitness.count_lower n g) (hq g))
  rw [(optimizer_properties k n).1,(optimizer_properties k n).2.1,chain_score k n hn] at hh
  have hkR : (2:ℝ) ≤ k := by exact_mod_cast k_lower k
  have hf := fractionFloor_positive (k:ℝ) hkR
  unfold fractionFloor at hf
  linarith

theorem comparison (n : ℕ) (hn : n+1=k*k) :
    ratioFloor k * minimumMass k n ≤ contextualFraction k n := by
  have hkR : (2:ℝ) ≤ k := by exact_mod_cast k_lower k
  exact comparison_from_certificates k _ _ hkR
    (minimum_mass_bounds k n).2 (fraction_lower k n hn)

theorem ratio_bound (n : ℕ) (hn : n+1=k*k) :
    ratioFloor k ≤ contextualFraction k n / minimumMass k n :=
  (le_div_iff₀ (minimum_mass_positive k n hn)).2 (comparison k n hn)

/-- The quantum predicate is inhabited by a constructed density and both POVMs;
the negative mass is an attained optimum, not a supplied certificate parameter. -/
theorem quantum_unbounded :
    ∀ C : ℝ, 0 ≤ C → ∃ (n : ℕ) (p : Bell.ChainWitness.Table n)
      (q : Bell.ChainWitness.Global n → ℝ),
      Nonempty (Bell.GramQuantum.Model p) ∧
      Bell.marginal q=p ∧ (∑ g, q g=1) ∧
      (∀ q', Bell.marginal q'=p → (∑ g, q' g=1) → negativeMass q ≤ negativeMass q') ∧
      0 < negativeMass q ∧
      C < Bell.ContextualFraction.fraction Bell.Repair.vertex (Bell.Repair.flatten p) /
        negativeMass q := by
  intro C hC
  obtain ⟨k,hk⟩ := exists_nat_gt (C+4)
  have hkR : (2:ℝ) ≤ k := by linarith
  have hkN : 2 ≤ k := by exact_mod_cast hkR
  let : Fact (2 ≤ k) := ⟨hkN⟩
  let n := k*k-1
  have hn : n+1=k*k := Nat.sub_add_cancel (by nlinarith [hkN])
  refine ⟨n,behavior k n,optimizer k n,quantum_realization k n,
    (optimizer_properties k n).1,(optimizer_properties k n).2.1,
    (optimizer_properties k n).2.2,minimum_mass_positive k n hn,?_⟩
  have hr := ratio_grows (k:ℝ) hkR
  exact lt_of_lt_of_le (by linarith : C < ratioFloor k) (ratio_bound k n hn)

/-- Both actual optima approach their scalar endpoint with a declared real-metric cutoff. -/
theorem finite_shadow_error (n : ℕ) (hn : n+1=k*k) (ε : ℝ) (hε : 0 < ε)
    (hcut : 2/ε < (k:ℝ)) :
    |contextualFraction k n-1| < ε ∧ |minimumMass k n| < ε := by
  have hkR : (2:ℝ) ≤ k := by exact_mod_cast k_lower k
  exact Bell.ContinuumShadows.shadow_error_bound k _ _ ε hkR hε hcut
    (fraction_lower k n hn)
    (Bell.ChainWitness.fraction_le_one n (behavior k n) (nonnegative k n))
    (minimum_mass_bounds k n).1 (minimum_mass_bounds k n).2

end Bell.CompleteQuantumUnbounded
