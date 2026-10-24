import Bell.RampSums
import Bell.LocalGram
import Mathlib.Data.ZMod.Basic

/-! Assembly of the finite smoothed cyclic profile from its actual entries. -/
noncomputable section
open scoped BigOperators
namespace Bell.CyclicProfile

def half (k t : ℕ) : ℝ := if t < k then Bell.RampSums.ramp k t else 1
def raw (k m t : ℕ) : ℝ := if t < m then half k t else -half k (t-m)

theorem half_zero (k : ℕ) (hk : 0 < k) : half k 0 = -1 := by
  simp [half,hk,Bell.RampSums.ramp]

theorem half_bounds (k t : ℕ) (hk : 0 < k) : -1 ≤ half k t ∧ half k t ≤ 1 := by
  unfold half
  split_ifs with h
  · exact Bell.RampSums.ramp_bounds k t hk h.le
  · norm_num

theorem raw_bounds (k m t : ℕ) (hk : 0 < k) : -1 ≤ raw k m t ∧ raw k m t ≤ 1 := by
  unfold raw
  split_ifs
  · exact half_bounds k t hk
  · obtain ⟨h1,h2⟩ := half_bounds k (t-m) hk
    constructor <;> linarith

theorem raw_first (k m t : ℕ) (ht : t < m) : raw k m t = half k t := by
  simp [raw,ht]

theorem raw_second (k m t : ℕ) : raw k m (m+t) = -half k t := by
  simp [raw,Nat.not_lt.mpr (Nat.le_add_right m t)]

theorem raw_antiperiodic (k m t : ℕ) (_hm : 0 < m) (ht : t < 2*m) :
    raw k m ((t+m)%(2*m)) = -raw k m t := by
  by_cases h : t < m
  · have hmod : (t+m)%(2*m) = m+t := by rw [Nat.mod_eq_of_lt (by omega)]; omega
    rw [hmod,raw_second,raw_first k m t h]
  · have hmod : (t+m)%(2*m) = t-m := by
      have he : t+m = (t-m)+2*m := by omega
      rw [he,Nat.add_mod_right,Nat.mod_eq_of_lt (by omega)]
    rw [hmod,raw_first k m (t-m) (by omega)]
    simp [raw,h]

theorem half_square_sum (k m : ℕ) (hkm : k ≤ m) :
    (∑ t ∈ Finset.range m, half k t^2) =
      (∑ t ∈ Finset.range k, Bell.RampSums.ramp k t^2) + (m-k:ℕ) := by
  conv_lhs => rw [← Nat.add_sub_of_le hkm]
  rw [Finset.sum_range_add]
  congr 1
  · apply Finset.sum_congr rfl
    intro t ht
    simp [half,Finset.mem_range.mp ht]
  · simp [half,Nat.not_lt.mpr (Nat.le_add_right k _)]

theorem raw_square_sum (k m : ℕ) :
    (∑ t ∈ Finset.range (2*m), raw k m t^2) =
      2*(∑ t ∈ Finset.range m, half k t^2) := by
  rw [two_mul,Finset.sum_range_add]
  have h1 : (∑ t ∈ Finset.range m, raw k m t^2) = ∑ t ∈ Finset.range m, half k t^2 := by
    apply Finset.sum_congr rfl
    intro t ht
    rw [raw_first k m t (Finset.mem_range.mp ht)]
  have h2 : (∑ t ∈ Finset.range m, raw k m (m+t)^2) = ∑ t ∈ Finset.range m, half k t^2 := by
    simp_rw [raw_second,neg_sq]
  rw [h1,h2]; ring

theorem half_step (k t : ℕ) (hk : 0 < k) :
    half k (t+1)-half k t = if t < k then 2/(k:ℝ) else 0 := by
  by_cases h : t < k
  · by_cases hs : t+1 < k
    · simp only [half,ite_eq_left h,ite_eq_left hs]
      exact Bell.RampSums.ramp_difference k t
    · have he : t+1=k := by omega
      have hr : Bell.RampSums.ramp k k = 1 := by
        have hk0 : (k:ℝ) ≠ 0 := by exact_mod_cast (Nat.ne_of_gt hk)
        norm_num [Bell.RampSums.ramp,hk0]
      simp only [half,ite_eq_left h,ite_eq_right hs]
      rw [← hr]
      simpa only [he] using Bell.RampSums.ramp_difference k t
  · simp [half,h,show ¬t+1<k by omega]

theorem raw_step_first (k m t : ℕ) (hk : 0 < k) (hkm : k ≤ m) (ht : t < m) :
    raw k m ((t+1)%(2*m))-raw k m t = half k (t+1)-half k t := by
  rw [Nat.mod_eq_of_lt (by omega),raw_first k m t ht]
  by_cases h : t+1 < m
  · rw [raw_first k m (t+1) h]
  · have he : t+1=m := by omega
    rw [he]
    simp only [raw,lt_self_iff_false,ite_false,Nat.sub_self,half_zero k hk]
    rw [show half k m = 1 by simp [half,Nat.not_lt.mpr hkm]]
    ring

theorem raw_step_second (k m t : ℕ) (hk : 0 < k) (hkm : k ≤ m) (ht : t < m) :
    raw k m ((m+t+1)%(2*m))-raw k m (m+t) = -(half k (t+1)-half k t) := by
  rw [raw_second]
  by_cases h : t+1 < m
  · rw [Nat.mod_eq_of_lt (by omega),show m+t+1=m+(t+1) by omega,raw_second]
    ring
  · have he : t+1=m := by omega
    have he2 : m+t+1=2*m := by omega
    rw [he2,Nat.mod_self,raw_first k m 0 (by omega),half_zero k hk,he]
    simp only [half,ite_eq_right (Nat.not_lt.mpr hkm)]
    ring

theorem half_energy (k m : ℕ) (hk : 0 < k) (hkm : k ≤ m) :
    (∑ t ∈ Finset.range m, (half k (t+1)-half k t)^2) = 4/(k:ℝ) := by
  simp_rw [half_step k _ hk]
  conv_lhs => rw [← Nat.add_sub_of_le hkm]
  rw [Finset.sum_range_add]
  have h1 : (∑ t ∈ Finset.range k, (if t<k then 2/(k:ℝ) else 0)^2) =
      (k:ℝ)*(2/(k:ℝ))^2 := by
    simp only [Finset.sum_congr rfl (fun t ht =>
      congrArg (fun x:ℝ => x^2) (ite_eq_left (Finset.mem_range.mp ht))),
      Finset.sum_const,Finset.card_range,nsmul_eq_mul]
  rw [h1]
  have h2 : (∑ t ∈ Finset.range (m-k), (if k+t<k then 2/(k:ℝ) else 0)^2) = 0 := by
    simp [Nat.not_lt.mpr (Nat.le_add_right k _)]
  rw [h2,add_zero]
  have hk0 : (k:ℝ) ≠ 0 := by exact_mod_cast (Nat.ne_of_gt hk)
  field_simp
  ring

theorem raw_energy (k m : ℕ) (hk : 0 < k) (hkm : k ≤ m) :
    (∑ t ∈ Finset.range (2*m), (raw k m ((t+1)%(2*m))-raw k m t)^2) = 8/(k:ℝ) := by
  rw [two_mul,Finset.sum_range_add]
  simp only [← two_mul m]
  have h1 : (∑ t ∈ Finset.range m, (raw k m ((t+1)%(2*m))-raw k m t)^2) =
      ∑ t ∈ Finset.range m, (half k (t+1)-half k t)^2 := by
    apply Finset.sum_congr rfl
    intro t ht
    rw [raw_step_first k m t hk hkm (Finset.mem_range.mp ht)]
  have h2 : (∑ t ∈ Finset.range m, (raw k m ((m+t+1)%(2*m))-raw k m (m+t))^2) =
      ∑ t ∈ Finset.range m, (half k (t+1)-half k t)^2 := by
    apply Finset.sum_congr rfl
    intro t ht
    rw [raw_step_second k m t hk hkm (Finset.mem_range.mp ht),neg_sq]
  rw [h1,h2,half_energy k m hk hkm]
  ring

def profile (k m : ℕ) (t : Fin (2*m)) : ℝ := raw k m t.val

theorem profile_norm (k : ℕ) (hk : 2 ≤ k) :
    (∑ t : Fin (2*(2*k*k)), profile k (2*k*k) t^2) =
      (4*(k:ℝ)^2)*Bell.SmoothedComparison.normSquare k := by
  rw [show (∑ t : Fin (2*(2*k*k)), profile k (2*k*k) t^2) =
      ∑ t ∈ Finset.range (2*(2*k*k)), raw k (2*k*k) t^2 from
        Fin.sum_univ_eq_sum_range (fun t => raw k (2*k*k) t^2) (2*(2*k*k))]
  rw [raw_square_sum,half_square_sum k (2*k*k) (by nlinarith)]
  exact Bell.RampSums.full_square_sum k hk

theorem shift_sum (k m : ℕ) [NeZero (2*m)] (j : Fin (2*m)) (F : ℝ → ℝ) :
    (∑ t, F (profile k m (t+j))) = ∑ t, F (profile k m t) :=
  Fintype.sum_equiv (Equiv.addRight j) _ _ (fun _ => rfl)

def step (m : ℕ) (hm : 0 < m) : Fin (2*m) := ⟨1,by omega⟩
def halfTurn (m : ℕ) (hm : 0 < m) : Fin (2*m) := ⟨m,by omega⟩

theorem profile_antiperiodic (k m : ℕ) (hm : 0 < m) (t : Fin (2*m)) :
    profile k m (t+halfTurn m hm) = -profile k m t := by
  simp only [profile,Fin.val_add,halfTurn]
  exact raw_antiperiodic k m t.val hm t.isLt

theorem profile_energy (k m : ℕ) (hk : 0 < k) (hkm : k ≤ m) :
    (∑ t : Fin (2*m), (profile k m (t+step m (lt_of_lt_of_le hk hkm))-profile k m t)^2) =
      8/(k:ℝ) := by
  simp only [profile,Fin.val_add,step]
  calc
    _ = ∑ t ∈ Finset.range (2*m), (raw k m ((t+1)%(2*m))-raw k m t)^2 :=
      Fin.sum_univ_eq_sum_range (fun t => (raw k m ((t+1)%(2*m))-raw k m t)^2) (2*m)
    _ = _ := raw_energy k m hk hkm

theorem translated_energy (k m : ℕ) [NeZero (2*m)] (hk : 0 < k) (hkm : k ≤ m)
    (j : Fin (2*m)) :
    (∑ t : Fin (2*m), (profile k m (t+j+step m (lt_of_lt_of_le hk hkm))-profile k m (t+j))^2) =
      8/(k:ℝ) := by
  calc
    _ = ∑ t, (profile k m (t+step m (lt_of_lt_of_le hk hkm))-profile k m t)^2 :=
      Fintype.sum_equiv (Equiv.addRight j) _ _ (fun _ => rfl)
    _ = _ := profile_energy k m hk hkm

theorem shifted_norm (k : ℕ) [NeZero (2*(2*k*k))] (hk : 2 ≤ k)
    (j : Fin (2*(2*k*k))) :
    (∑ t, profile k (2*k*k) (t+j)^2) =
      (4*(k:ℝ)^2)*Bell.SmoothedComparison.normSquare k := by
  rw [shift_sum k (2*k*k) j (fun x => x^2)]
  exact profile_norm k hk

theorem adjacent_inner (k : ℕ) [NeZero (2*(2*k*k))] (hk : 2 ≤ k)
    (j : Fin (2*(2*k*k))) :
    (∑ t, profile k (2*k*k) (t+j)*profile k (2*k*k)
      (t+j+step (2*k*k) (by nlinarith))) =
      (4*(k:ℝ)^2)*Bell.SmoothedComparison.normSquare k - 4/(k:ℝ) := by
  have he := translated_energy k (2*k*k) (by omega) (by nlinarith) j
  have h0 := shifted_norm k hk j
  have h1 := shifted_norm k hk (j+step (2*k*k) (by nlinarith))
  simp only [sub_sq,Finset.sum_add_distrib,Finset.sum_sub_distrib,mul_assoc,
    ← Finset.mul_sum] at he
  simp only [← add_assoc] at h1
  rw [h0,h1] at he
  have hc : (∑ t, profile k (2*k*k) (t+j+step (2*k*k) (by nlinarith))*profile k (2*k*k) (t+j)) =
      ∑ t, profile k (2*k*k) (t+j)*profile k (2*k*k) (t+j+step (2*k*k) (by nlinarith)) := by
    apply Finset.sum_congr rfl; intro t _; ring
  rw [hc] at he
  linear_combination (-1/2:ℝ)*he

end Bell.CyclicProfile
