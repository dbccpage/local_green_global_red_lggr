import Init.Omega
import ObserverRobustControlCore

/-!
# Joint Detector Adequacy and Bounded Coordinate Diagnostics
Package: `019_observer_robust_control_of_obstruction_diagnostics`
Module: `JointDetectorAdequacy`

Formalizes:
- Coordinate coverage for weighted input norms
- Proposition 4.3: weighted input-coordinate bound (`bundle_relative_non_tearing`)
- Corollary: Unit-weight uniform coordinate defect bounding (`bundle_non_tearing_unit_bound`)
- Detection and fail-closed rejection of fake repairs (coordinate defect dumping exceeding initial budget)
- Contrast / Necessity: Blind mode transfer vulnerability theorem
- Concrete verification: The 3-cycle disjoint classes model (Reviewer's counterexample)
-/

namespace ObserverRobustControl

/-- Coordinate coverage over input coordinates k < m.
    For every coordinate k < m, there exists an observer in the bundle whose weight
    on coordinate k is strictly positive. -/
def JointlyAdequate (bundle : ObserverBundle) (m : Nat) : Prop :=
  ∀ (k : Nat), k < m → ∃ obs ∈ bundle, ∃ w, getCoord obs.weights k = some w ∧ w > 0

/-- Proposition 4.3: weighted input-norm coordinate estimate.
    Assume the observer bundle satisfies Joint Detector Adequacy over m coordinates.
    If a transition c → c' is BundleAdmissible, then for every coordinate k < m,
    the defect under c' is uniformly bounded by an observer in the bundle:
    w * |c'_k| ≤ weightedNorm obs.weights c + obs.tol.
    This theorem uses weightedNorm, with no quotient minimization.
    It does not bound arbitrary raw cochains by a quotient seminorm, and does not
    preclude norm-reducing transfers between monitored coordinates. -/
theorem bundle_relative_non_tearing (bundle : ObserverBundle) (m : Nat)
    (c c' : List Int)
    (hadeq : JointlyAdequate bundle m)
    (hadm : BundleAdmissible bundle c c') :
    ∀ (k : Nat), k < m →
      ∀ (v' : Int), getCoord c' k = some v' →
        ∃ obs ∈ bundle, ∃ w > 0,
          w * v'.natAbs ≤ weightedNorm obs.weights c + obs.tol := by
  intro k hk v' hc'
  rcases hadeq k hk with ⟨obs, hobs_in, w, hw, hw_pos⟩
  have hadm_obs := hadm obs hobs_in
  have hbound := observer_bounds_coordinate obs c c' k w v' hadm_obs hw hc'
  exact ⟨obs, hobs_in, w, hw_pos, hbound⟩

/-- Unit-Weight Non-Tearing Corollary:
    When the observer's weight is at least 1, the absolute defect |c'_k| is directly bounded. -/
theorem bundle_non_tearing_unit_bound (bundle : ObserverBundle) (m : Nat)
    (c c' : List Int)
    (hadeq : JointlyAdequate bundle m)
    (hadm : BundleAdmissible bundle c c') :
    ∀ (k : Nat), k < m →
      ∀ (v' : Int), getCoord c' k = some v' →
        ∃ obs ∈ bundle,
          v'.natAbs ≤ weightedNorm obs.weights c + obs.tol := by
  intro k hk v' hc'
  rcases bundle_relative_non_tearing bundle m c c' hadeq hadm k hk v' hc' with ⟨obs, hobs_in, w, hw_pos, hbound⟩
  have h_w_ge_1 : w ≥ 1 := hw_pos
  have h_le : 1 * v'.natAbs ≤ w * v'.natAbs := Nat.mul_le_mul_right v'.natAbs h_w_ge_1
  have h_final : v'.natAbs ≤ weightedNorm obs.weights c + obs.tol := by omega
  exact ⟨obs, hobs_in, h_final⟩

/-- Rejection of Fake Repair / Spoofing:
    If an operator attempts to transfer a defect exceeding an observer's budget into a monitored coordinate,
    the transition is strictly rejected (not BundleAdmissible). -/
theorem transfer_detected_and_rejected (bundle : ObserverBundle) (obs : Observer)
    (c c' : List Int) (k : Nat) (w : Nat) (v' : Int)
    (hobs_in : obs ∈ bundle)
    (hw : getCoord obs.weights k = some w)
    (hc' : getCoord c' k = some v')
    (hexcess : w * v'.natAbs > weightedNorm obs.weights c + obs.tol) :
    ¬ BundleAdmissible bundle c c' := by
  intro hadm
  have hadm_obs := hadm obs hobs_in
  have hbound := observer_bounds_coordinate obs c c' k w v' hadm_obs hw hc'
  omega

/-!
### Concrete 3-Cycle Disjoint Classes Model (Reviewer's Counterexample)

Three cycle coordinates: 0, 1, 2.
Observer 1 monitors coordinate 0 with weight 1 (and weight 0 on 1 and 2).
Observer 2 monitors coordinate 1 with weight 1 (and weight 0 on 0 and 2).
Coordinate 2 is a shared blind mode (weight 0 for both observers).
-/

def O1 : Observer := ⟨"O1", [1, 0, 0], 0⟩
def O2 : Observer := ⟨"O2", [0, 1, 0], 0⟩
def O3 : Observer := ⟨"O3", [0, 0, 1], 0⟩

def blindBundle : ObserverBundle := [O1, O2]
def adequateBundle : ObserverBundle := [O1, O2, O3]

/-- The blind bundle has weight 0 on coordinate 2 for all observers. -/
theorem blindBundle_unmonitored_coord2 :
    ∀ obs ∈ blindBundle, getCoord obs.weights 2 = some 0 := by
  intro obs hobs
  simp [blindBundle] at hobs
  rcases hobs with rfl | rfl
  · rfl
  · rfl

/-- Theorem: In the blind bundle, transferring defect to coordinate 2 (from [1, 1, 0] to [0, 0, K])
    is ADMITTED for ANY K, because neither observer monitors coordinate 2. -/
theorem blind_transfer_admitted (K : Nat) :
    BundleAdmissible blindBundle [1, 1, 0] [0, 0, (K : Int)] := by
  intro obs hobs
  simp [blindBundle] at hobs
  rcases hobs with rfl | rfl
  · dsimp [O1, AdmissibleObserver, weightedNorm]
    omega
  · dsimp [O2, AdmissibleObserver, weightedNorm]
    omega

/-- Theorem: Under Joint Detector Adequacy (adequateBundle), the same transfer to [0, 0, K]
    is CAUGHT AND REJECTED for any K ≥ 1. -/
theorem adequate_bundle_rejects_transfer (K : Nat) (hK : K ≥ 1) :
    ¬ BundleAdmissible adequateBundle [1, 1, 0] [0, 0, (K : Int)] := by
  intro hadm
  have hadm_O3 := hadm O3 (by simp [adequateBundle])
  dsimp [O3, AdmissibleObserver, weightedNorm] at hadm_O3
  omega

/-- Verification that adequateBundle is indeed Jointly Adequate on all 3 coordinates. -/
theorem adequateBundle_is_jointly_adequate : JointlyAdequate adequateBundle 3 := by
  intro k hk
  cases k with
  | zero =>
    refine ⟨O1, by simp [adequateBundle], 1, rfl, by decide⟩
  | succ k1 =>
    cases k1 with
    | zero =>
      refine ⟨O2, by simp [adequateBundle], 1, rfl, by decide⟩
    | succ k2 =>
      cases k2 with
      | zero =>
        refine ⟨O3, by simp [adequateBundle], 1, rfl, by decide⟩
      | succ k3 =>
        omega

/-- Worst-case weighted residual across a bundle: sup_O Φ_1^O(c). -/
def worstPhi : ObserverBundle → List Int → Nat
  | [], _ => 0
  | obs :: rest, c => max (weightedNorm obs.weights c) (worstPhi rest c)

/-- A transition is ceiling-admitted at M when it is bundle-admissible and the
    worst-case weighted residual of the image is at most M. -/
def CeilingAdmitted (bundle : ObserverBundle) (c c' : List Int) (M : Nat) : Prop :=
  BundleAdmissible bundle c c' ∧ worstPhi bundle c' ≤ M

theorem worstPhi_ge_mem (bundle : ObserverBundle) (c : List Int) (obs : Observer)
    (h : obs ∈ bundle) : weightedNorm obs.weights c ≤ worstPhi bundle c := by
  induction bundle with
  | nil => cases h
  | cons hd tl ih =>
    dsimp [worstPhi]
    rcases List.mem_cons.mp h with rfl | htl
    · exact Nat.le_max_left _ _
    · exact Nat.le_trans (ih htl) (Nat.le_max_right _ _)

/-- Accepted ceiling: every observer's weighted norm of c' is at most M. -/
theorem ceiling_bounds_each (bundle : ObserverBundle) (c c' : List Int) (M : Nat)
    (obs : Observer) (hceil : CeilingAdmitted bundle c c' M) (hobs : obs ∈ bundle) :
    weightedNorm obs.weights c' ≤ M := by
  rcases hceil with ⟨_, hM⟩
  exact Nat.le_trans (worstPhi_ge_mem bundle c' obs hobs) hM

/-- A transition that exceeds M on any observer is not ceiling-admitted. -/
theorem excess_not_ceiling (bundle : ObserverBundle) (c c' : List Int) (M : Nat)
    (obs : Observer) (hobs : obs ∈ bundle)
    (hexcess : weightedNorm obs.weights c' > M) :
    ¬ CeilingAdmitted bundle c c' M := by
  intro hceil
  have hle := ceiling_bounds_each bundle c c' M obs hceil hobs
  omega

/-- An empty bundle covers no positive coordinate count. -/
theorem empty_not_jointly_adequate (m : Nat) (hm : 0 < m) : ¬ JointlyAdequate [] m := by
  intro h
  rcases h 0 hm with ⟨obs, hmem, _⟩
  cases hmem

end ObserverRobustControl
