import Bell.Averaging
import Bell.CHSH
import Mathlib.MeasureTheory.Integral.Bochner.Basic

/-! Actual probability integrals instantiate the positive normalized averaging
interface. Boundedness and integrability follow from response probabilities. -/
noncomputable section
open scoped BigOperators
open MeasureTheory
namespace Bell.Integral

variable {Λ : Type} [MeasurableSpace Λ]

/-- Bounded measurable real functions form an algebra. -/
def functions : Subalgebra ℝ (Λ → ℝ) where
  carrier := {f | Measurable f ∧ ∃ C : ℝ, 0 ≤ C ∧ ∀ l, |f l| ≤ C}
  zero_mem' := ⟨measurable_const, 0, le_rfl, by simp⟩
  one_mem' := ⟨measurable_const, 1, by norm_num, by simp⟩
  add_mem' := by
    rintro f g ⟨hf, C, hC, hfc⟩ ⟨hg, D, hD, hgd⟩
    refine ⟨hf.add hg, C + D, add_nonneg hC hD, fun l => ?_⟩
    exact (abs_add_le _ _).trans (add_le_add (hfc l) (hgd l))
  mul_mem' := by
    rintro f g ⟨hf, C, hC, hfc⟩ ⟨hg, D, hD, hgd⟩
    refine ⟨hf.mul hg, C * D, mul_nonneg hC hD, fun l => ?_⟩
    simpa only [Pi.mul_apply, abs_mul] using mul_le_mul (hfc l) (hgd l) (abs_nonneg _) hC
  algebraMap_mem' := by
    intro c
    exact ⟨measurable_const, |c|, abs_nonneg c, fun _ => le_rfl⟩

theorem functions_integrable (μ : Measure Λ) [IsFiniteMeasure μ] (f : functions (Λ := Λ)) :
    Integrable f.val μ := by
  obtain ⟨hf, C, _, hC⟩ := f.property
  exact ⟨hf.aestronglyMeasurable, HasFiniteIntegral.of_bounded (ae_of_all μ (by
    intro l
    simpa only [Real.norm_eq_abs] using hC l))⟩

/-- This is the Bochner integral, not an axiomatized expectation. -/
def average (μ : Measure Λ) [IsFiniteMeasure μ] : functions (Λ := Λ) →ₗ[ℝ] ℝ where
  toFun := fun f => ∫ l, f.val l ∂μ
  map_add' := by
    intro f g
    exact integral_add (functions_integrable μ f) (functions_integrable μ g)
  map_smul' := by intro c f; simp [integral_const_mul]

theorem average_one (μ : Measure Λ) [IsProbabilityMeasure μ] : average μ 1 = 1 := by
  simp [average]

theorem average_nonnegative (μ : Measure Λ) [IsFiniteMeasure μ]
    (f : functions (Λ := Λ)) (hf : ∀ l, 0 ≤ f.val l) : 0 ≤ average μ f :=
  integral_nonneg hf

omit [MeasurableSpace Λ] in
theorem response_bounded {I : Type} [Fintype I] (r : I → Λ → ℝ)
    (hn : ∀ i l, 0 ≤ r i l) (ht : ∀ l, ∑ i, r i l = 1) (i : I) (l : Λ) :
    |r i l| ≤ 1 := by
  rw [abs_of_nonneg (hn i l), ← ht l]
  exact Finset.single_le_sum (fun j _ => hn j l) (Finset.mem_univ i)

structure Model {X Y A B : Type} [Fintype X] [Fintype Y] [Fintype A] [Fintype B]
    (p : Behavior X Y A B) (μ : Measure Λ) where
  alice : X → A → Λ → ℝ
  bob : Y → B → Λ → ℝ
  alice_measurable : ∀ x a, Measurable (alice x a)
  bob_measurable : ∀ y b, Measurable (bob y b)
  alice_nonnegative : ∀ x a l, 0 ≤ alice x a l
  bob_nonnegative : ∀ y b l, 0 ≤ bob y b l
  alice_total : ∀ x l, ∑ a, alice x a l = 1
  bob_total : ∀ y l, ∑ b, bob y b l = 1
  reproduces : ∀ x y a b, p x y a b = ∫ l, alice x a l * bob y b l ∂μ

def Model.asAveraged {X Y A B : Type} [Fintype X] [Fintype Y] [Fintype A] [Fintype B]
    {p : Behavior X Y A B} {μ : Measure Λ} [IsProbabilityMeasure μ] (m : Model p μ) :
    AveragedModel p where
  Hidden := Λ
  functions := functions
  average := average μ
  average_one := average_one μ
  average_nonnegative := average_nonnegative μ
  alice := fun x a => ⟨m.alice x a, m.alice_measurable x a, 1, by norm_num,
    response_bounded (m.alice x) (m.alice_nonnegative x) (m.alice_total x) a⟩
  bob := fun y b => ⟨m.bob y b, m.bob_measurable y b, 1, by norm_num,
    response_bounded (m.bob y) (m.bob_nonnegative y) (m.bob_total y) b⟩
  alice_nonnegative := m.alice_nonnegative
  bob_nonnegative := m.bob_nonnegative
  alice_total := by intro x; apply Subtype.ext; funext l; simpa using m.alice_total x l
  bob_total := by intro y; apply Subtype.ext; funext l; simpa using m.bob_total y l
  reproduces := m.reproduces

theorem probability_integral_positive_extension {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] {p : Behavior X Y A B} {μ : Measure Λ}
    [IsProbabilityMeasure μ] (m : Model p μ) : PositiveExtension p :=
  averaged_positive_extension m.asAveraged


/-- Finite probability weights induce an actual measure. -/
def atomicMeasure {I : Type} [Fintype I] [MeasurableSpace I] (w : I → ℝ) : Measure I :=
  ∑ i, ENNReal.ofReal (w i) • Measure.dirac i

theorem atomicMeasure_probability {I : Type} [Fintype I] [MeasurableSpace I]
    (w : I → ℝ) (hw : Probability w) : IsProbabilityMeasure (atomicMeasure w) := by
  constructor
  simp only [atomicMeasure, Measure.finsetSum_apply,
    Measure.smul_apply, Measure.dirac_apply_of_mem (Set.mem_univ _), smul_eq_mul, mul_one]
  rw [← ENNReal.ofReal_sum_of_nonneg (fun i _ => hw.nonneg i), hw.total]
  norm_num

theorem atomicMeasure_integral {I : Type} [Fintype I] [MeasurableSpace I]
    [MeasurableSingletonClass I] (w : I → ℝ) (hw : ∀ i, 0 ≤ w i) (f : I → ℝ) :
    (∫ i, f i ∂atomicMeasure w) = ∑ i, w i * f i := by
  unfold atomicMeasure
  rw [integral_finsetSum_measure (fun i _ =>
    (integrable_dirac (by simp)).smul_measure ENNReal.ofReal_ne_top)]
  simp only [integral_smul_measure, integral_dirac, ENNReal.toReal_ofReal (hw _), smul_eq_mul]

/-- Existence of a setting-independent probability integral model. -/
def HasModel {X Y A B : Type} [Fintype X] [Fintype Y] [Fintype A] [Fintype B]
    (p : Behavior X Y A B) : Prop :=
  ∃ (Λ : Type) (mΛ : MeasurableSpace Λ) (μ : @Measure Λ mΛ),
    @IsProbabilityMeasure Λ mΛ μ ∧ Nonempty (@Model Λ mΛ X Y A B _ _ _ _ p μ)

theorem finite_model_as_integral {X Y A B : Type} [Fintype X] [Fintype Y]
    [Fintype A] [Fintype B] {p : Behavior X Y A B} (m : LocalModel p) : HasModel p := by
  let : MeasurableSpace m.Hidden := ⊤
  let μ := atomicMeasure m.weight
  refine ⟨m.Hidden, inferInstance, μ, atomicMeasure_probability m.weight m.probability, ?_⟩
  refine ⟨{
    alice := fun x a l => m.alice l x a
    bob := fun y b l => m.bob l y b
    alice_measurable := fun _ _ => measurable_of_finite _
    bob_measurable := fun _ _ => measurable_of_finite _
    alice_nonnegative := fun x a l => (m.alice_probability l x).nonneg a
    bob_nonnegative := fun y b l => (m.bob_probability l y).nonneg b
    alice_total := fun x l => (m.alice_probability l x).total
    bob_total := fun y l => (m.bob_probability l y).total
    reproduces := ?_ }⟩
  intro x y a b
  rw [show μ = atomicMeasure m.weight from rfl,
    atomicMeasure_integral m.weight m.probability.nonneg]
  exact m.reproduces x y a b

theorem positive_extension_iff_probability_integral {X Y A B : Type}
    [Fintype X] [Fintype Y] [Fintype A] [Fintype B] (p : Behavior X Y A B) :
    PositiveExtension p ↔ HasModel p := by
  constructor
  · intro hp
    obtain ⟨m⟩ := positive_extension_local hp
    exact finite_model_as_integral m
  · rintro ⟨Λ, mΛ, μ, hμ, ⟨m⟩⟩
    let := mΛ
    let := hμ
    exact probability_integral_positive_extension m


theorem probability_integral_chsh {p : CHSH.Table} {μ : Measure Λ}
    [IsProbabilityMeasure μ] (m : Model p μ) : |CHSH.score p| ≤ 2 :=
  CHSH.positive_extension_chsh p (probability_integral_positive_extension m)

end Bell.Integral


