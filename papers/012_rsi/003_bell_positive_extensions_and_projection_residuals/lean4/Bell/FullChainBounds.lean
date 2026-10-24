import Bell.ChainAnalysis
import Bell.SignedDuality

/-! Every full-table signed extension obeys each pulled-back CHSH inequality.
For equally spaced planar chains this prevents an unbounded large-setting ratio. -/
noncomputable section
open scoped BigOperators
namespace Bell.FullChainBounds
open Bell.ChainAnalysis
variable {G : Type} [Fintype G]

def K (a a' b b' : G → Bool) (g : G) : ℝ :=
  Bell.CHSH.sign (a g)*Bell.CHSH.sign (b g) +
  Bell.CHSH.sign (a' g)*Bell.CHSH.sign (b g) +
  Bell.CHSH.sign (a' g)*Bell.CHSH.sign (b' g) -
  Bell.CHSH.sign (a g)*Bell.CHSH.sign (b' g)

omit [Fintype G] in
theorem deterministic (a a' b b' : G → Bool) (g : G) : |K a a' b b' g| = 2 := by
  unfold K
  cases a g <;> cases a' g <;> cases b g <;> cases b' g <;> norm_num [Bell.CHSH.sign]

theorem signed_chsh (q : G → ℝ) (hq : ∑ g, q g = 1) (a a' b b' : G → Bool) :
    ∑ g, q g*K a a' b b' g ≤ 2*(1+2*Bell.SignedDuality.negativeMass q) := by
  calc
    _ ≤ ∑ g, |q g*K a a' b b' g| := Finset.sum_le_sum (fun g _ => le_abs_self _)
    _ = ∑ g, |q g| * 2 := by simp_rw [abs_mul,deterministic]
    _ = _ := by rw [← Finset.sum_mul,Bell.SignedDuality.signed_norm_identity q hq]; ring

def correlation (q : G → ℝ) (a b : G → Bool) : ℝ :=
  ∑ g, q g*Bell.CHSH.sign (a g)*Bell.CHSH.sign (b g)

theorem score_identity (q : G → ℝ) (a a' b b' : G → Bool) :
    (∑ g, q g*K a a' b b' g) = correlation q a b + correlation q a' b +
      correlation q a' b' - correlation q a b' := by
  simp [K,correlation,mul_add,mul_sub,mul_assoc,Finset.sum_add_distrib,Finset.sum_sub_distrib]

theorem quantum_grid_bound (n : ℕ) (hn : 4 ≤ n) (q : G → ℝ) (hq : ∑ g, q g = 1)
    (a a' b b' : G → Bool)
    (hab : correlation q a b = Real.cos (bobLow n))
    (ha'b : correlation q a' b = Real.cos (alice n-bobLow n))
    (ha'b' : correlation q a' b' = Real.cos (alice n-bobHigh n))
    (hab' : correlation q a b' = Real.cos (bobHigh n)) :
    (2*Real.sqrt 2-2-6*Real.pi/n)/4 ≤ Bell.SignedDuality.negativeMass q := by
  have h := signed_chsh q hq a a' b b'
  rw [score_identity,hab,ha'b,ha'b',hab'] at h
  exact full_grid_mass_bound n hn _ h

theorem complete_chain_cap (n : ℕ) (hn : 64 ≤ n) (q : G → ℝ) (hq : ∑ g, q g = 1)
    (a a' b b' : G → Bool) (CF : ℝ) (hCF : CF ≤ 1)
    (hab : correlation q a b = Real.cos (bobLow n))
    (ha'b : correlation q a' b = Real.cos (alice n-bobLow n))
    (ha'b' : correlation q a' b' = Real.cos (alice n-bobHigh n))
    (hab' : correlation q a b' = Real.cos (bobHigh n)) :
    CF ≤ (160/17)*Bell.SignedDuality.negativeMass q := by
  have h := signed_chsh q hq a a' b b'
  rw [score_identity,hab,ha'b,ha'b',hab'] at h
  exact full_grid_uniform_bound n hn CF _ hCF h

end Bell.FullChainBounds
