import Init.Omega

/-!
# Observer-Robust Control Core Formalization
Package: `019_observer_robust_control_of_obstruction_diagnostics`
Module: `ObserverRobustControlCore`

Defines:
- Coordinate extraction `getCoord`
- Weighted L1 norm `weightedNorm` Φ_1^O(c) = ∑ w_i * |c_i|
- Total unweighted L1 norm `totalNorm`
- Observer models and observer bundles
- Committed-state descent admissibility and bundle-relative control
- Fundamental coordinate projection inequality: w_k * |c_k| ≤ ‖c‖_{1, w}
- Coordinate bounding under observer admissibility
-/

namespace ObserverRobustControl

/-- Coordinate extraction for cochains and weight vectors. -/
def getCoord {α : Type} : List α → Nat → Option α
  | [], _ => none
  | x :: _, 0 => some x
  | _ :: xs, n + 1 => getCoord xs n

/-- Weighted L1 norm of an integer cochain under non-negative weights:
    ‖c‖_{1, w} = ∑ w_i * |c_i|. -/
def weightedNorm : List Nat → List Int → Nat
  | [], _ => 0
  | _, [] => 0
  | w :: ws, c :: cs => w * c.natAbs + weightedNorm ws cs

/-- Total unweighted L1 norm: ‖c‖_1 = ∑ |c_i|. -/
def totalNorm : List Int → Nat
  | [] => 0
  | c :: cs => c.natAbs + totalNorm cs

/-- An observer model with a name, coordinate weights, and resolution tolerance. -/
structure Observer where
  name : String
  weights : List Nat
  tol : Nat
  deriving Repr

/-- An observer bundle is a list of declared observer models. -/
abbrev ObserverBundle := List Observer

/-- Committed-State Descent Condition for an observer:
    Φ_1^O(c') ≤ Φ_1^O(c) + ε_O. -/
def AdmissibleObserver (obs : Observer) (c c' : List Int) : Prop :=
  weightedNorm obs.weights c' ≤ weightedNorm obs.weights c + obs.tol

/-- The Observer-Robust Control Criterion (Bundle Admissibility):
    A candidate transition c → c' is admitted if every observer in the bundle
    satisfies its committed descent law. -/
def BundleAdmissible (bundle : ObserverBundle) (c c' : List Int) : Prop :=
  ∀ obs ∈ bundle, AdmissibleObserver obs c c'

/-- Fundamental Coordinate Inequality:
    For any coordinate index k, the contribution w_k * |c_k| is bounded by the full norm. -/
theorem coord_le_weightedNorm (k : Nat) (ws : List Nat) (cs : List Int)
    (w : Nat) (v : Int)
    (hw : getCoord ws k = some w) (hc : getCoord cs k = some v) :
    w * v.natAbs ≤ weightedNorm ws cs := by
  induction k generalizing ws cs with
  | zero =>
    cases ws with
    | nil => simp [getCoord] at hw
    | cons w_hd w_tl =>
      cases cs with
      | nil => simp [getCoord] at hc
      | cons c_hd c_tl =>
        simp [getCoord] at hw hc
        cases hw
        cases hc
        simp [weightedNorm]
  | succ n ih =>
    cases ws with
    | nil => simp [getCoord] at hw
    | cons w_hd w_tl =>
      cases cs with
      | nil => simp [getCoord] at hc
      | cons c_hd c_tl =>
        simp [getCoord] at hw hc
        have h_sub := ih w_tl c_tl hw hc
        simp [weightedNorm]
        omega

/-- If an observer admits transition c → c', then the defect at any monitored coordinate k
    under c' is bounded by the observer's initial residual plus tolerance. -/
theorem observer_bounds_coordinate (obs : Observer) (c c' : List Int) (k : Nat)
    (w : Nat) (v' : Int)
    (hadm : AdmissibleObserver obs c c')
    (hw : getCoord obs.weights k = some w)
    (hc' : getCoord c' k = some v') :
    w * v'.natAbs ≤ weightedNorm obs.weights c + obs.tol := by
  have h_coord := coord_le_weightedNorm k obs.weights c' w v' hw hc'
  dsimp [AdmissibleObserver] at hadm
  omega

end ObserverRobustControl
