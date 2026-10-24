import Bell.Extension
import Bell.SmoothedComparison
import Mathlib.Analysis.SpecialFunctions.Sqrt

/-! Complete Bell tables from a shared coordinate and shared fair sign.
This constructs the local model, rather than assuming locality. -/
noncomputable section
open scoped BigOperators
namespace Bell.LocalGram
attribute [local instance] Classical.propDecidable

def sign (a : Bool) : ℝ := if a then -1 else 1
def response (u : ℝ) (a : Bool) : ℝ := (1+sign a*u)/2

theorem response_probability (u : ℝ) (hu : -1 ≤ u ∧ u ≤ 1) :
    Bell.Probability (response u) := by
  constructor
  · intro a; cases a <;> dsimp [response,sign] <;> linarith
  · simp only [Fintype.sum_bool,response,sign]; norm_num; ring

theorem signed_bounds (r : Bool) (u : ℝ) (hu : -1 ≤ u ∧ u ≤ 1) :
    -1 ≤ sign r*u ∧ sign r*u ≤ 1 := by
  cases r <;> dsimp [sign] <;> constructor <;> linarith

variable {D X Y : Type} [Fintype D] [Fintype X] [Fintype Y]

def correlation (w : D → ℝ) (u : X → D → ℝ) (v : Y → D → ℝ) (x : X) (y : Y) : ℝ :=
  ∑ t, w t * u x t * v y t

def table (c : X → Y → ℝ) : Bell.Behavior X Y Bool Bool :=
  fun x y a b => (1+sign a*sign b*c x y)/4

def model (w : D → ℝ) (hw : Bell.Probability w)
    (u : X → D → ℝ) (v : Y → D → ℝ)
    (hu : ∀ x t, -1 ≤ u x t ∧ u x t ≤ 1)
    (hv : ∀ y t, -1 ≤ v y t ∧ v y t ≤ 1) :
    Bell.LocalModel (table (correlation w u v)) where
  Hidden := D × Bool
  finiteHidden := inferInstance
  weight := fun l => w l.1/2
  probability := {
    nonneg := fun l => div_nonneg (hw.nonneg l.1) (by norm_num)
    total := by
      simp only [Fintype.sum_prod_type,Fintype.sum_bool]
      have h (t:D) : w t/2+w t/2 = w t := by ring
      simp_rw [h]; exact hw.total }
  alice := fun l x => response (sign l.2*u x l.1)
  bob := fun l y => response (sign l.2*v y l.1)
  alice_probability := fun l x => response_probability _ (signed_bounds l.2 _ (hu x l.1))
  bob_probability := fun l y => response_probability _ (signed_bounds l.2 _ (hv y l.1))
  reproduces := by
    intro x y a b
    simp only [Fintype.sum_prod_type,Fintype.sum_bool]
    have h (t:D) :
        w t/2*(response (sign true*u x t) a * response (sign true*v y t) b) +
        w t/2*(response (sign false*u x t) a * response (sign false*v y t) b) =
        w t/4 + sign a*sign b/4*(w t*u x t*v y t) := by
      dsimp [response,sign]; split_ifs <;> ring
    simp_rw [h]
    rw [Finset.sum_add_distrib,← Finset.sum_div,← Finset.mul_sum,hw.total]
    dsimp [table,correlation]; ring

theorem positive_extension (w : D → ℝ) (hw : Bell.Probability w)
    (u : X → D → ℝ) (v : Y → D → ℝ)
    (hu : ∀ x t, -1 ≤ u x t ∧ u x t ≤ 1)
    (hv : ∀ y t, -1 ≤ v y t ∧ v y t ≤ 1) :
    Bell.PositiveExtension (table (correlation w u v)) :=
  Bell.local_positive_extension (model w hw u v hu hv)

omit [Fintype X] [Fintype Y] in
theorem normalized_table_identity (c : X → Y → ℝ) (s : ℝ) (hs : s ≠ 0)
    (x : X) (y : Y) (a b : Bool) :
    table (fun x y => s*c x y) x y a b / s - (1-s)/s*(1/4) = table c x y a b :=
  Bell.SmoothedComparison.behavior_decomposition s (c x y) (sign a) (sign b) hs

theorem marginal_signed (l w : Bell.Assignment X Y Bool Bool → ℝ) (s : ℝ)
    (x : X) (y : Y) (a b : Bool) :
    Bell.marginal (Bell.SmoothedComparison.signed l w s) x y a b =
      Bell.marginal l x y a b / s - (1-s)/s*Bell.marginal w x y a b := by
  classical
  simp only [Bell.marginal, Bell.SmoothedComparison.signed,
    Finset.sum_div,Finset.mul_sum,← Finset.sum_sub_distrib]
  apply Finset.sum_congr rfl
  intro g _
  split_ifs <;> ring

theorem white_positive_extension :
    Bell.PositiveExtension (fun (_ : X) (_ : Y) (_ _ : Bool) => (1:ℝ)/4) := by
  have hw : Bell.Probability (fun (_ : Unit) => (1:ℝ)) :=
    ⟨fun _ => by norm_num, by simp⟩
  have h := positive_extension (fun (_ : Unit) => (1:ℝ)) hw
    (fun (_ : X) (_ : Unit) => 0) (fun (_ : Y) (_ : Unit) => 0)
    (fun _ _ => by norm_num) (fun _ _ => by norm_num)
  have he : table (correlation (fun (_ : Unit) => (1:ℝ))
      (fun (_ : X) (_ : Unit) => 0) (fun (_ : Y) (_ : Unit) => 0)) =
      (fun _ _ _ _ => (1:ℝ)/4) := by
    funext x y a b
    simp [table,correlation]
  rw [he] at h
  exact h

/-- Any local visibility s > 0 gives an explicit full-assignment signed model
for the normalized table, with negative mass at most (1-s)/s. -/
theorem signed_extension (c : X → Y → ℝ) (s : ℝ) (hs : 0 < s) (hs1 : s ≤ 1)
    (hl : Bell.PositiveExtension (table (fun x y => s*c x y))) :
    ∃ q : Bell.Assignment X Y Bool Bool → ℝ,
      (∑ g, q g = 1) ∧ Bell.marginal q = table c ∧
      Bell.SignedDuality.negativeMass q ≤ (1-s)/s := by
  obtain ⟨l,hlp,hle⟩ := hl
  obtain ⟨w,hwp,hwe⟩ := white_positive_extension (X := X) (Y := Y)
  refine ⟨Bell.SmoothedComparison.signed l w s,
    Bell.SmoothedComparison.signed_total l w s hs hlp.total hwp.total, ?_,
    Bell.SmoothedComparison.signed_mass_bound l w s hs hs1 hlp.nonneg hwp.nonneg hwp.total⟩
  funext x y a b
  rw [marginal_signed,hle,hwe]
  exact normalized_table_identity c s hs.ne' x y a b

omit [Fintype X] [Fintype Y] in
theorem normalized_vector (u : D → ℝ) (S : ℝ) (hS : 0 < S)
    (hu : ∑ t, u t^2 = S) : ∑ t, (u t / Real.sqrt S)^2 = 1 := by
  simp only [div_pow,Real.sq_sqrt hS.le,← Finset.sum_div,hu]
  exact div_self hS.ne'

omit [Fintype X] [Fintype Y] in
theorem normalized_inner (u v : D → ℝ) (S : ℝ) (hS : 0 ≤ S) :
    (∑ t, (u t/Real.sqrt S)*(v t/Real.sqrt S)) = (∑ t, u t*v t)/S := by
  simp only [div_mul_div_comm,← pow_two,Real.sq_sqrt hS,Finset.sum_div]

omit [Fintype X] [Fintype Y] in
theorem inner_bounds (u v : D → ℝ) (S : ℝ)
    (hu : ∑ t, u t^2 = S) (hv : ∑ t, v t^2 = S) :
    -S ≤ ∑ t, u t*v t ∧ (∑ t, u t*v t) ≤ S := by
  have hm := Finset.sum_nonneg (s := Finset.univ) (fun t _ => sq_nonneg (u t-v t))
  have hp := Finset.sum_nonneg (s := Finset.univ) (fun t _ => sq_nonneg (u t+v t))
  simp only [sub_sq,add_sq,Finset.sum_add_distrib,Finset.sum_sub_distrib,
    mul_assoc,← Finset.mul_sum,hu,hv] at hm hp
  constructor <;> linarith

end Bell.LocalGram
