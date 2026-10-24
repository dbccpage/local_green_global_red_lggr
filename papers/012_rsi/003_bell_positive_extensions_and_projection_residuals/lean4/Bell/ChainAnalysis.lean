import Bell.PlanarQuantum

/-! Continuous bounds used to separate cycle-only and complete-table chains. -/
noncomputable section
namespace Bell.ChainAnalysis
open Real
set_option maxHeartbeats 1000000

theorem cosine_quadratic (x : ℝ) (hx : |x| ≤ 1) : 1-x^2 ≤ cos x := by
  have h := (abs_le.mp (Real.cos_bound hx)).1
  have hs : x^2 ≤ 1 := (sq_le_one_iff_abs_le_one x).mpr hx
  have hp : x^4 ≤ x^2 := by nlinarith [sq_nonneg (x^2), sq_nonneg x]
  have he : |x|^4=x^4 := by
    calc |x|^4 = (|x|^2)^2 := by ring
         _ = (x^2)^2 := by rw [sq_abs]
         _ = x^4 := by ring
  rw [he] at h
  nlinarith [sq_nonneg x]

theorem sine_small (x : ℝ) (hx : |x| ≤ 1) : |sin x| ≤ 2*|x| := by
  let r := |x|
  have hr : 0 ≤ r := abs_nonneg x
  have hr1 : r ≤ 1 := hx
  have hrπ : r ≤ π := by linarith [Real.two_le_pi]
  rw [Real.abs_sin_eq_sin_abs_of_abs_le_pi hrπ]
  have hb := (abs_le.mp (Real.sin_bound (x := r) (by simpa [abs_of_nonneg hr] using hr1))).2
  have h3 : 0 ≤ r^3 := pow_nonneg hr _
  have h5 : r^5 ≤ r := by
    calc r^5 = r*r^4 := by ring
         _ ≤ r*1 := mul_le_mul_of_nonneg_left (pow_le_one₀ hr hr1) hr
         _ = r := mul_one _
  change sin r ≤ 2*r
  rw [abs_of_nonneg hr] at hb
  nlinarith

theorem cosine_close (x y : ℝ) (h : |x-y| ≤ 2) : |cos x-cos y| ≤ 2*|x-y| := by
  have hh : |(x-y)/2| ≤ 1 := by rw [abs_div]; norm_num; linarith
  rw [Real.cos_sub_cos,abs_mul,abs_mul]
  have h1 := Real.abs_sin_le_one ((x+y)/2)
  have h2 := sine_small ((x-y)/2) hh
  calc
    |(-2:ℝ)| * |sin ((x+y)/2)| * |sin ((x-y)/2)| ≤ 2*(2*|(x-y)/2|) := by
      norm_num
      nlinarith [abs_nonneg (sin ((x-y)/2)),abs_nonneg (sin ((x+y)/2))]
    _ = 2*|x-y| := by rw [abs_div]; norm_num; ring

def score (a b c : ℝ) := cos b + cos (a-b) + cos (a-c) - cos c

theorem score_perturbation (a b c ε : ℝ) (_hε : 0 ≤ ε) (hsmall : ε ≤ 1)
    (ha : |a-π/2| ≤ ε) (hb : |b-π/4| ≤ ε) (hc : |c-3*π/4| ≤ ε) :
    2*Real.sqrt 2-12*ε ≤ score a b c := by
  have haa := abs_le.mp ha
  have hbb := abs_le.mp hb
  have hcc := abs_le.mp hc
  have hab : |(a-b)-π/4| ≤ 2*ε := abs_le.mpr ⟨by linarith,by linarith⟩
  have hac : |(a-c)-(-π/4)| ≤ 2*ε := abs_le.mpr ⟨by linarith,by linarith⟩
  simp only [neg_div] at hac
  have h1 := abs_le.mp (cosine_close b (π/4) (by linarith))
  have h2 := abs_le.mp (cosine_close (a-b) (π/4) (by linarith))
  have h3 := abs_le.mp (cosine_close (a-c) (-(π/4)) (by linarith))
  have h4 := abs_le.mp (cosine_close c (3*π/4) (by linarith))
  have ht : cos (3*π/4) = -Real.sqrt 2/2 := by
    rw [show 3*π/4=π-π/4 by ring,Real.cos_pi_sub,Real.cos_pi_div_four]
    ring
  simp only [Real.cos_pi_div_four,ht,neg_div,Real.cos_neg] at h1 h2 h3 h4
  unfold score
  linarith

def alice (n : ℕ) : ℝ := (n/2:ℕ)*π/n
def bobLow (n : ℕ) : ℝ := ((n/4:ℕ)+1/2:ℝ)*π/n
def bobHigh (n : ℕ) : ℝ := ((3*n/4:ℕ)+1/2:ℝ)*π/n

theorem grid_rounding (n : ℕ) (hn : 0 < n) :
    |alice n-π/2| ≤ π/(2*n) ∧ |bobLow n-π/4| ≤ π/(2*n) ∧
    |bobHigh n-3*π/4| ≤ π/(2*n) := by
  have hnr : (0:ℝ) < n := by exact_mod_cast hn
  have hπ := Real.pi_pos
  have a1 : 2*(n/2) ≤ n := Nat.mul_div_le n 2
  have a2 : n ≤ 2*(n/2)+1 := by omega
  have b1 : 4*(n/4) ≤ n := Nat.mul_div_le n 4
  have b2 : n ≤ 4*(n/4)+3 := by omega
  have c1 : 4*(3*n/4) ≤ 3*n := Nat.mul_div_le (3*n) 4
  have c2 : 3*n ≤ 4*(3*n/4)+3 := by omega
  have ar1 : 2*(n/2:ℕ) ≤ (n:ℝ) := by exact_mod_cast a1
  have ar2 : (n:ℝ) ≤ 2*(n/2:ℕ)+1 := by exact_mod_cast a2
  have br1 : 4*(n/4:ℕ) ≤ (n:ℝ) := by exact_mod_cast b1
  have br2 : (n:ℝ) ≤ 4*(n/4:ℕ)+3 := by exact_mod_cast b2
  have cr1 : 4*(3*n/4:ℕ) ≤ (3*n:ℝ) := by exact_mod_cast c1
  have cr2 : (3*n:ℝ) ≤ 4*(3*n/4:ℕ)+3 := by exact_mod_cast c2
  dsimp [alice,bobLow,bobHigh]
  constructor
  · apply abs_le.mpr
    constructor <;> field_simp <;> nlinarith
  constructor <;> apply abs_le.mpr <;> constructor <;> field_simp <;> nlinarith

theorem full_grid_score (n : ℕ) (hn : 4 ≤ n) :
    2*Real.sqrt 2-6*π/n ≤ score (alice n) (bobLow n) (bobHigh n) := by
  have hnr : (4:ℝ) ≤ n := by exact_mod_cast hn
  have hround := grid_rounding n (by omega)
  have he := score_perturbation (alice n) (bobLow n) (bobHigh n) (π/(2*n))
    (by positivity) (by apply (div_le_one (by positivity)).2; linarith [Real.pi_le_four])
    hround.1 hround.2.1 hround.2.2
  convert he using 1; ring

theorem full_grid_mass_bound (n : ℕ) (hn : 4 ≤ n) (N : ℝ)
    (hS : score (alice n) (bobLow n) (bobHigh n) ≤ 2*(1+2*N)) :
    (2*Real.sqrt 2-2-6*π/n)/4 ≤ N := by
  have h := full_grid_score n hn
  linarith

theorem full_grid_uniform_bound (n : ℕ) (hn : 64 ≤ n) (CF N : ℝ) (hCF : CF ≤ 1)
    (hS : score (alice n) (bobLow n) (bobHigh n) ≤ 2*(1+2*N)) : CF ≤ (160/17)*N := by
  have hnr : (64:ℝ) ≤ n := by exact_mod_cast hn
  have hs : (7/5:ℝ) ≤ Real.sqrt 2 := by
    have hsq := Real.sq_sqrt (by norm_num : (0:ℝ) ≤ 2)
    have hp := Real.sqrt_nonneg (2:ℝ)
    nlinarith
  have hb := full_grid_mass_bound n (by omega) N hS
  have hpi : 6*π/(n:ℝ) ≤ 3/8 := by
    apply (div_le_iff₀ (by positivity)).2
    nlinarith [Real.pi_le_four]
  nlinarith

end Bell.ChainAnalysis
