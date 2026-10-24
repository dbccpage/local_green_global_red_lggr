import Bell.CyclicProfile
import Bell.GramQuantum
import Bell.ChainWitness

/-! Actual complete quantum Bell tables from the cyclic profiles. -/
noncomputable section
open scoped BigOperators
namespace Bell.SmoothedFamily
attribute [local instance] Classical.propDecidable
local instance (priority := high) : DecidableEq Bool := Classical.decEq Bool
local instance (priority := high) (n : ℕ) : DecidableEq (Fin n) := Classical.decEq (Fin n)
open Bell.CyclicProfile

abbrev Period (k : ℕ) := Fin (2*(2*k*k))
variable (k : ℕ) [Fact (2 ≤ k)]

theorem k_lower : 2 ≤ k := Fact.out

instance periodNeZero : NeZero (2*(2*k*k)) := ⟨by have := k_lower k; nlinarith⟩

def scale : ℝ := (4*(k:ℝ)^2)*Bell.SmoothedComparison.normSquare k
def position (r : ℕ) : Period k := ⟨r%(2*(2*k*k)), Nat.mod_lt _ (by have := k_lower k; nlinarith)⟩
def rawVector (r : ℕ) (t : Period k) : ℝ := profile k (2*k*k) (t+position k r)
def vector (r : ℕ) (t : Period k) : ℝ := rawVector k r t / Real.sqrt (scale k)
def correlation (r s : ℕ) : ℝ := ∑ t, vector k r t * vector k s t
def behavior (n : ℕ) : Bell.ChainWitness.Table n :=
  Bell.LocalGram.table (fun x y => correlation k (2*x.val) (2*y.val+1))

theorem scale_positive : 0 < scale k := by
  have hkR : (2:ℝ) ≤ k := by exact_mod_cast k_lower k
  have hs := (Bell.SmoothedComparison.norm_bounds k hkR).1
  unfold scale
  positivity

theorem vector_unit (r : ℕ) : ∑ t, vector k r t^2 = 1 := by
  apply Bell.LocalGram.normalized_vector _ _ (scale_positive k)
  exact shifted_norm k (k_lower k) (position k r)

def quantumModel (n : ℕ) : Bell.GramQuantum.Model (behavior k n) :=
  Bell.GramQuantum.model (2*(2*k*k)) (fun x : Fin (n+1) => vector k (2*x.val))
    (fun y : Fin (n+1) => vector k (2*y.val+1)) (fun _ => vector_unit k _) (fun _ => vector_unit k _)

theorem quantum_realization (n : ℕ) : Nonempty (Bell.GramQuantum.Model (behavior k n)) :=
  ⟨quantumModel k n⟩

theorem nonnegative (n : ℕ) (x y : Fin (n+1)) (a b : Bool) : 0 ≤ behavior k n x y a b :=
  Bell.GramQuantum.model_nonnegative (quantumModel k n) x y a b

def uniform (_ : Period k) : ℝ := 1/(4*(k:ℝ)^2)

theorem uniform_probability : Bell.Probability (uniform k) := by
  have hk0 : (k:ℝ) ≠ 0 := by have := k_lower k; exact_mod_cast (show k ≠ 0 by nlinarith)
  refine ⟨fun _ => by unfold uniform; positivity,?_⟩
  simp only [uniform,Finset.sum_const,Finset.card_univ,Fintype.card_fin,nsmul_eq_mul]
  push_cast
  field_simp
  ring

theorem raw_bounds (r : ℕ) (t : Period k) : -1 ≤ rawVector k r t ∧ rawVector k r t ≤ 1 :=
  Bell.CyclicProfile.raw_bounds k (2*k*k) _ (by have := k_lower k; nlinarith)

theorem local_visibility_identity (r s : ℕ) :
    (∑ t, uniform k t * rawVector k r t * rawVector k s t) =
      Bell.SmoothedComparison.normSquare k * correlation k r s := by
  have hs := scale_positive k
  have hk0 : (k:ℝ) ≠ 0 := by have := k_lower k; exact_mod_cast (show k ≠ 0 by nlinarith)
  have hc : correlation k r s = (∑ t, rawVector k r t*rawVector k s t)/scale k :=
    Bell.LocalGram.normalized_inner _ _ _ hs.le
  rw [hc]
  have he : (∑ t, uniform k t * rawVector k r t * rawVector k s t) =
      (∑ t, rawVector k r t*rawVector k s t)/(4*(k:ℝ)^2) := by
    rw [Finset.sum_div]
    apply Finset.sum_congr rfl
    intro t _
    unfold uniform
    ring
  rw [he]
  have hn : Bell.SmoothedComparison.normSquare k ≠ 0 := by
    have hkR : (2:ℝ) ≤ k := by exact_mod_cast k_lower k
    have := (Bell.SmoothedComparison.norm_bounds k hkR).1
    linarith
  unfold scale
  field_simp

theorem positive_visibility (n : ℕ) :
    Bell.PositiveExtension (Bell.LocalGram.table (fun x y : Fin (n+1) =>
      Bell.SmoothedComparison.normSquare k * correlation k (2*x.val) (2*y.val+1))) := by
  have h := Bell.LocalGram.positive_extension (uniform k) (uniform_probability k)
    (fun (x : Fin (n+1)) => rawVector k (2*x.val))
    (fun (y : Fin (n+1)) => rawVector k (2*y.val+1))
    (fun _ _ => raw_bounds k _ _) (fun _ _ => raw_bounds k _ _)
  have he : Bell.LocalGram.correlation (uniform k)
      (fun (x : Fin (n+1)) => rawVector k (2*x.val))
      (fun (y : Fin (n+1)) => rawVector k (2*y.val+1)) =
      (fun x y => Bell.SmoothedComparison.normSquare k * correlation k (2*x.val) (2*y.val+1)) := by
    funext x y
    exact local_visibility_identity k _ _
  rw [he] at h
  exact h

theorem signed_certificate (n : ℕ) :
    ∃ q : Bell.ChainWitness.Global n → ℝ, (∑ g, q g=1) ∧
      Bell.marginal q=behavior k n ∧
      Bell.SignedDuality.negativeMass q ≤ Bell.SmoothedComparison.massCap k := by
  have hkR : (2:ℝ) ≤ k := by exact_mod_cast k_lower k
  obtain ⟨hs0,hs1⟩ := Bell.SmoothedComparison.norm_bounds k hkR
  exact Bell.LocalGram.signed_extension _ _ (by linarith) hs1.le (positive_visibility k n)

theorem position_add (r s : ℕ) : position k (r+s) = position k r+position k s := by
  apply Fin.ext
  change (r+s)%(2*(2*k*k)) = (r%(2*(2*k*k))+s%(2*(2*k*k)))%(2*(2*k*k))
  exact Nat.add_mod _ _ _

theorem position_step : position k 1 = step (2*k*k) (by have := k_lower k; nlinarith) := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt (by have := k_lower k; nlinarith)

theorem position_half : position k (2*k*k) = halfTurn (2*k*k) (by have := k_lower k; nlinarith) := by
  apply Fin.ext
  exact Nat.mod_eq_of_lt (by have := k_lower k; nlinarith)

def visibility : ℝ := 1-1/((k:ℝ)^3*Bell.SmoothedComparison.normSquare k)

theorem adjacent_correlation (r : ℕ) : correlation k r (r+1) = visibility k := by
  have hs := scale_positive k
  have hc := adjacent_inner k (k_lower k) (position k r)
  have hi : correlation k r (r+1) =
      (∑ t, rawVector k r t*rawVector k (r+1) t)/scale k :=
    Bell.LocalGram.normalized_inner _ _ _ hs.le
  rw [hi]
  simp only [rawVector,position_add,position_step,← add_assoc]
  rw [hc]
  have hk0 : (k:ℝ) ≠ 0 := by have := k_lower k; exact_mod_cast (show k ≠ 0 by nlinarith)
  have hn : Bell.SmoothedComparison.normSquare k ≠ 0 := by
    have hkR : (2:ℝ) ≤ k := by exact_mod_cast k_lower k
    have := (Bell.SmoothedComparison.norm_bounds k hkR).1
    linarith
  unfold scale visibility
  field_simp

theorem position_zero : position k 0 = 0 := by apply Fin.ext; simp [position]

theorem correlation_comm (r s : ℕ) : correlation k r s = correlation k s r := by
  unfold correlation
  apply Finset.sum_congr rfl
  intro t _
  ring

theorem half_vector (t : Period k) :
    vector k (2*k*k) t = -vector k 0 t := by
  unfold vector rawVector
  simp only [position_half,position_zero,add_zero,
    profile_antiperiodic k (2*k*k) (by have := k_lower k; nlinarith)]
  ring

theorem half_correlation (r : ℕ) :
    correlation k r (2*k*k) = -correlation k r 0 := by
  unfold correlation
  simp only [half_vector,mul_neg,Finset.sum_neg_distrib]

theorem closing_correlation (n : ℕ) (hn : n+1=k*k) :
    correlation k 0 (2*n+1) = -visibility k := by
  have hpos : 2*n+1+1=2*k*k := by nlinarith [hn]
  have h := adjacent_correlation k (2*n+1)
  rw [hpos,half_correlation,correlation_comm k (2*n+1) 0] at h
  linarith

theorem diagonal_failure (n : ℕ) (i : Fin (n+1)) :
    Bell.ChainWitness.mismatch (behavior k n) i i = (1-visibility k)/2 := by
  dsimp [Bell.ChainWitness.mismatch,behavior,Bell.LocalGram.table,Bell.LocalGram.sign]
  rw [adjacent_correlation]
  ring

theorem successor_failure (n : ℕ) (i : Fin n) :
    Bell.ChainWitness.mismatch (behavior k n) i.succ i.castSucc = (1-visibility k)/2 := by
  have hi : 2*(i.val+1) = (2*i.val+1)+1 := by ring
  dsimp [Bell.ChainWitness.mismatch,behavior,Bell.LocalGram.table,Bell.LocalGram.sign]
  rw [hi,correlation_comm,adjacent_correlation]
  ring

theorem closing_failure (n : ℕ) (hn : n+1=k*k) :
    Bell.ChainWitness.matching (behavior k n) 0 (Fin.last n) = (1-visibility k)/2 := by
  dsimp [Bell.ChainWitness.matching,behavior,Bell.LocalGram.table,Bell.LocalGram.sign]
  rw [closing_correlation k n hn]
  ring

theorem chain_score (n : ℕ) (hn : n+1=k*k) :
    Bell.ChainWitness.score (behavior k n) =
      1/((k:ℝ)*Bell.SmoothedComparison.normSquare k) := by
  simp only [Bell.ChainWitness.score,diagonal_failure,successor_failure,
    closing_failure k n hn,Finset.sum_const,Finset.card_univ,Fintype.card_fin,nsmul_eq_mul]
  have hnR : (n:ℝ)+1=(k:ℝ)^2 := by rw [pow_two]; exact_mod_cast hn
  have hk0 : (k:ℝ) ≠ 0 := by have := k_lower k; exact_mod_cast (show k ≠ 0 by nlinarith)
  have hs0 : Bell.SmoothedComparison.normSquare k ≠ 0 := by
    have hkR : (2:ℝ) ≤ k := by exact_mod_cast k_lower k
    have := (Bell.SmoothedComparison.norm_bounds k hkR).1
    linarith
  unfold visibility
  push_cast
  field_simp
  nlinarith

def contextualFraction (n : ℕ) : ℝ :=
  Bell.ContextualFraction.fraction Bell.Repair.vertex (Bell.Repair.flatten (behavior k n))

theorem fraction_lower (n : ℕ) (hn : n+1=k*k) :
    Bell.SmoothedComparison.fractionFloor k ≤ contextualFraction k n := by
  have h := Bell.ChainWitness.fraction_lower n (behavior k n) (nonnegative k n)
  rw [chain_score k n hn] at h
  exact h

end Bell.SmoothedFamily
