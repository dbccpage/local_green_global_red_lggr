import Bell.SparseCertificates

/-! Passing from a complete measurement table to a subcover cannot increase
the available noncontextual packing mass or minimum signed negative mass. -/
noncomputable section
open scoped BigOperators
namespace Bell.ScenarioRestriction
open Bell.LinearProgramming Bell.ContextualFraction Bell.SignedDuality Bell.SparseCertificates
variable {G H I J : Type} [Fintype G] [Fintype H] [DecidableEq H]

theorem projected_mix (A : G → I → ℝ) (B : H → J → ℝ)
    (f : G → H) (r : J → I) (hc : ∀ g j, B (f g) j = A g (r j))
    (q : G → ℝ) (j : J) : mix B (push f q) j = mix A q (r j) := by
  rw [push_mix]
  simp_rw [hc]
  rfl

theorem restricted_packing (A : G → I → ℝ) (B : H → J → ℝ)
    (f : G → H) (r : J → I) (hc : ∀ g j, B (f g) j = A g (r j))
    (p : I → ℝ) (q : G → ℝ) (hq : Packing A p q) :
    Packing B (fun j => p (r j)) (push f q) := by
  refine ⟨push_nonnegative f q hq.1, ?_⟩
  intro j; rw [projected_mix A B f r hc]; exact hq.2 (r j)

theorem fraction_monotone (A : G → I → ℝ) (B : H → J → ℝ)
    (f : G → H) (r : J → I) (hc : ∀ g j, B (f g) j = A g (r j))
    (p : I → ℝ) (hp : ∀ i, 0 ≤ p i)
    (hb : BddAbove (weights B (fun j => p (r j)))) :
    fraction B (fun j => p (r j)) ≤ fraction A p := by
  have h : sSup (weights A p) ≤ sSup (weights B (fun j => p (r j))) := by
    apply csSup_le (weights_nonempty A p hp)
    rintro w ⟨q,hq,ht⟩
    apply le_csSup hb
    exact ⟨push f q,restricted_packing A B f r hc p q hq,by rw [push_total,ht]⟩
  dsimp [fraction]
  linarith

theorem signed_restriction (A : G → I → ℝ) (B : H → J → ℝ)
    (f : G → H) (r : J → I) (hc : ∀ g j, B (f g) j = A g (r j))
    (p : I → ℝ) (q : G → ℝ) (ht : ∑ g, q g = 1) (hq : mix A q = p) :
    (∑ h, push f q h = 1) ∧ mix B (push f q) = (fun j => p (r j)) ∧
      negativeMass (push f q) ≤ negativeMass q := by
  refine ⟨by rw [push_total,ht], ?_, push_negative_le f q⟩
  funext j; rw [projected_mix A B f r hc,congrFun hq (r j)]

end Bell.ScenarioRestriction
