import Bell.SparseCertificates

/-! The parity quotient of an unbiased binary frustrated cycle. All odd failure
patterns are retained. The quotient uses only the cycle contexts, not a full Bell table. -/
noncomputable section
open scoped BigOperators
namespace Bell.CycleParity
open Bell.LinearProgramming Bell.ContextualFraction Bell.SignedDuality Bell.SparseCertificates
variable (n : ℕ)
abbrev size := 2*(n+2)
def failures (s : Fin (size n) → Bool) : ℕ := ∑ i, if s i then 1 else 0
abbrev Global := {s : Fin (size n) → Bool // failures n s % 2 = 1}
abbrev Cell := Fin (size n) × Bool
def A (g : Global n) (i : Cell n) : ℝ := if g.val i.1 = i.2 then 1 else 0
def point (v : ℝ) (i : Cell n) : ℝ := if i.2 then (1-v)/2 else (1+v)/2
def cover (i : Cell n) : ℝ := if i.2 then 1 else 0
def M : ℝ := size n

theorem size_ge : 4 ≤ M n := by dsimp [M,size]; norm_cast; omega
theorem failures_bounds (g : Global n) : 1 ≤ failures n g.val ∧ failures n g.val ≤ size n-1 := by
  have hle : failures n g.val ≤ size n := by
    calc
      _ ≤ ∑ _i : Fin (size n), 1 := Finset.sum_le_sum (fun i _ => by split_ifs <;> omega)
      _ = _ := by simp
  have hp := g.property
  dsimp [size] at *
  omega

def oneBad (j : Fin (size n)) : Global n :=
  ⟨fun i => decide (i=j), by simp [failures]⟩
def allButOne (j : Fin (size n)) : Global n :=
  ⟨fun i => decide (i≠j), by
    simp [failures, Finset.sum_ite, Finset.filter_ne', Finset.card_erase_of_mem]
    dsimp [size]; omega⟩

theorem columns (g : Global n) : ∑ i, A n g i = M n := by
  simp only [Fintype.sum_prod_type, Fintype.sum_bool, A]
  have he (i : Fin (size n)) :
      (if g.val i = true then (1:ℝ) else 0) + (if g.val i = false then 1 else 0) = 1 := by
    cases g.val i <;> simp
  simp_rw [he]
  simp [M]

theorem oneBad_projects (i : Cell n) :
    (∑ j, A n (oneBad n j) i) = if i.2 then 1 else M n-1 := by
  rcases i with ⟨i,b⟩
  cases b <;> simp [A,oneBad, M, Finset.sum_ite, Finset.filter_ne,
    Finset.card_erase_of_mem, Nat.cast_sub (by dsimp [size]; omega : 1 ≤ size n)]
theorem allButOne_projects (i : Cell n) :
    (∑ j, A n (allButOne n j) i) = if i.2 then M n-1 else 1 := by
  rcases i with ⟨i,b⟩
  cases b <;> simp [A,allButOne,M,Finset.sum_ite, Finset.filter_ne,
    Finset.card_erase_of_mem, Nat.cast_sub (by dsimp [size]; omega : 1 ≤ size n)]
theorem cover_column (g : Global n) : pairing (cover n) (A n g) = failures n g.val := by
  simp only [pairing,Fintype.sum_prod_type,Fintype.sum_bool,cover,A]
  push_cast [failures]
  apply Finset.sum_congr rfl
  intro i _
  cases g.val i <;> norm_num
theorem cover_feasible : (∀ i, 0 ≤ cover n i) ∧ ∀ g, 1 ≤ pairing (cover n) (A n g) := by
  constructor
  · intro i; unfold cover; split_ifs <;> norm_num
  · intro g; rw [cover_column]; exact_mod_cast (failures_bounds n g).1
theorem cover_value (v : ℝ) : pairing (cover n) (point n v) = M n*(1-v)/2 := by
  simp [pairing,Fintype.sum_prod_type,cover,point,M]
  ring
theorem point_nonnegative (v : ℝ) (hv : -1 ≤ v) (h1 : v ≤ 1) : ∀ i, 0 ≤ point n v i := by
  intro i; unfold point; split_ifs <;> linarith
theorem point_total (v : ℝ) : ∑ i, point n v i = M n := by
  simp [Fintype.sum_prod_type,point,M]
  ring

def localPart (v : ℝ) := push (oneBad n) (fun _ => (1-v)/2)
theorem local_total (v : ℝ) : ∑ g, localPart n v g = M n*(1-v)/2 := by
  simp [localPart,push_total,M]; ring
theorem local_feasible (v : ℝ) (hv : M n-2 ≤ M n*v) (h1 : v ≤ 1) :
    Packing (A n) (point n v) (localPart n v) := by
  constructor
  · exact push_nonnegative _ _ (fun _ => by linarith)
  · intro i
    rw [localPart,push_mix,← Finset.mul_sum,oneBad_projects]
    cases h : i.2 <;> simp [point,h]; nlinarith

theorem contextual_fraction (v : ℝ) (hv : M n-2 ≤ M n*v) (h1 : v ≤ 1) :
    fraction (A n) (point n v) = 1-M n*(1-v)/2 := by
  have hm := size_ge n
  have hp := point_nonnegative n v (by nlinarith) h1
  have h := certificate_exact (A n) (point n v) (cover n) (localPart n v)
    (weights_bounded _ _ (M n) (by linarith) (columns n) (point_total n v)) hp
    (local_feasible n v hv h1) (cover_feasible n).1 (cover_feasible n).2
    (by rw [cover_value,local_total])
  rwa [local_total] at h

def positiveWeight (v : ℝ) := (M n-2+M n*v)/(2*M n*(M n-2))
def negativeWeight (v : ℝ) := (M n-2-M n*v)/(2*M n*(M n-2))
def support (j : Fin (size n) × Bool) : Global n :=
  if j.2 then allButOne n j.1 else oneBad n j.1
def weight (v : ℝ) (j : Fin (size n) × Bool) : ℝ :=
  if j.2 then negativeWeight n v else positiveWeight n v
def extension (v : ℝ) := push (support n) (weight n v)
def mass (v : ℝ) := (M n*v-M n+2)/(2*(M n-2))

theorem extension_total (v : ℝ) : ∑ g, extension n v g = 1 := by
  have hm := size_ge n
  have hm0 : M n ≠ 0 := by linarith
  have hm2 : M n-2 ≠ 0 := by linarith
  simp only [extension,push_total,weight,Fintype.sum_prod_type,Fintype.sum_bool,
    Bool.false_eq_true,ite_true,ite_false,Finset.sum_const,Finset.card_univ,
    Fintype.card_fin,nsmul_eq_mul]
  change M n*(negativeWeight n v+positiveWeight n v)=1
  dsimp [positiveWeight,negativeWeight]
  field_simp [hm0,hm2]
  ring

theorem extension_projects (v : ℝ) : mix (A n) (extension n v) = point n v := by
  funext i
  have hm := size_ge n
  have hm0 : M n ≠ 0 := by linarith
  have hm2 : M n-2 ≠ 0 := by linarith
  rw [extension,push_mix]
  simp only [Fintype.sum_prod_type,Fintype.sum_bool,weight,support,Bool.false_eq_true,
    ite_false,ite_true,Finset.sum_add_distrib,← Finset.mul_sum]
  rw [oneBad_projects,allButOne_projects]
  cases h : i.2 <;> simp only [h,Bool.false_eq_true,ite_false,ite_true,point]
  all_goals
    dsimp [positiveWeight,negativeWeight]
    field_simp [hm0,hm2]
    ring

theorem extension_mass_upper (v : ℝ) (hv : M n-2 ≤ M n*v) :
    negativeMass (extension n v) ≤ mass n v := by
  have hm := size_ge n
  have hm0 : M n ≠ 0 := by linarith
  have hm2 : M n-2 ≠ 0 := by linarith
  have hd : 0 < 2*M n*(M n-2) := mul_pos (by linarith) (by linarith)
  have hp : 0 ≤ positiveWeight n v := div_nonneg (by nlinarith) hd.le
  have hn : negativeWeight n v ≤ 0 := div_nonpos_of_nonpos_of_nonneg (by linarith) hd.le
  have h := push_negative_le (support n) (weight n v)
  simp only [weight,Fintype.sum_prod_type,Fintype.sum_bool,Bool.false_eq_true,ite_false,ite_true,
    max_eq_right (neg_nonpos.mpr hp),max_eq_left (neg_nonneg.mpr hn),add_zero] at h
  simp only [Finset.sum_const,Finset.card_univ,Fintype.card_fin,nsmul_eq_mul] at h
  change negativeMass (extension n v) ≤ _ at h
  have he : (size n:ℝ)*(-negativeWeight n v) = mass n v := by
    change M n*(-negativeWeight n v) = _
    dsimp [negativeWeight,mass]
    field_simp [hm0,hm2]
    ring
  rwa [he] at h

theorem negative_mass_lower (v : ℝ) (q : Global n → ℝ)
    (hq : mix (A n) q = point n v) (hn : ∑ g, q g = 1) : mass n v ≤ negativeMass q := by
  have hm := size_ge n
  let α : Cell n → ℝ := fun i => -cover n i/(M n-2)
  have he (p : Cell n → ℝ) : pairing α p = -pairing (cover n) p/(M n-2) := by
    simp only [pairing,α,div_mul_eq_mul_div,neg_mul,← Finset.sum_div,Finset.sum_neg_distrib]
  have hd (g : Global n) : -1 ≤ pairing α (A n g)+1/(M n-2) ∧
      pairing α (A n g)+1/(M n-2) ≤ 0 := by
    rw [he,cover_column]
    have hb := failures_bounds n g
    have hl : (1:ℝ) ≤ failures n g.val := by exact_mod_cast hb.1
    have hu : (failures n g.val:ℝ) ≤ M n-1 := by
      have hh : failures n g.val + 1 ≤ size n := by have := hb.2; omega
      have hr : (failures n g.val:ℝ)+1 ≤ M n := by dsimp [M]; exact_mod_cast hh
      linarith
    rw [← add_div]
    constructor
    · apply (le_div_iff₀ (by linarith : 0 < M n-2)).2
      linarith
    · exact div_nonpos_of_nonpos_of_nonneg (by linarith) (by linarith)
  have h := negative_mass_weak_duality (A n) (point n v) α q (1/(M n-2)) hq hn hd
  rw [he,cover_value] at h
  have hh : - (M n*(1-v)/2)/(M n-2)+1/(M n-2) = mass n v := by
    unfold mass
    field_simp [show M n-2 ≠ 0 by linarith]
    ring
  rwa [hh] at h

theorem exact_comparison (v : ℝ) (hv : M n-2 ≤ M n*v) (h1 : v ≤ 1) :
    negativeMass (extension n v) = mass n v ∧
    fraction (A n) (point n v) = (M n-2)*mass n v := by
  have hm := size_ge n
  constructor
  · exact le_antisymm (extension_mass_upper n v hv)
      (negative_mass_lower n v (extension n v) (extension_projects n v) (extension_total n v))
  · rw [contextual_fraction n v hv h1]
    unfold mass
    field_simp [show M n-2 ≠ 0 by linarith]
    ring

end Bell.CycleParity
