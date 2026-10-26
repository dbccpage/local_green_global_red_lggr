/- Finite content of the repair-selection controller.

The chain-complex bound and asymptotic convergence stay classical.
-/

structure Chan where
  geom : Rat
  sat : Rat
  curv : Rat
  rel : Rat
  xi : Rat

def signatureOk (c : Chan) : Bool :=
  if decide (c.geom = 0) && (decide (0 < c.curv) || decide (0 < c.xi)) then
    false
  else if decide (c.geom < 0) || decide (c.sat < 0) || decide (c.curv < 0) ||
      decide (c.rel < 0) || decide (c.xi < 0) || decide (1 < c.xi) then
    false
  else
    true

def ratioAdmits (geom curv rMax : Rat) : Bool :=
  if decide (geom < 0) || decide (curv < 0) || decide (rMax ≤ 0) then
    false
  else if decide (geom = 0) then
    decide (curv = 0)
  else
    decide (curv ≤ rMax * geom)

def descentOk (current candidate : Rat) : Bool :=
  decide (candidate ≤ current)

def passesGuards (curGeom candGeom candCurv rMax : Rat) : Bool :=
  if descentOk curGeom candGeom = false then
    false
  else
    ratioAdmits candGeom candCurv rMax

def half : Rat := 1 / 2

def liftAdmitted (dGeom dSat penalty : Rat) : Bool :=
  decide (penalty < dGeom + half * dSat)

structure Scored where
  score : Rat
  xi : Rat
  name : String

def better (a b : Scored) : Bool :=
  if decide (a.score < b.score) then
    true
  else if decide (b.score < a.score) then
    false
  else if decide (a.xi < b.xi) then
    true
  else if decide (b.xi < a.xi) then
    false
  else
    decide (a.name < b.name) || decide (a.name = b.name)

def select2 (eps : Rat) (a b : Scored) : Scored :=
  let fMin := if a.score ≤ b.score then a.score else b.score
  let aIn := decide (a.score ≤ fMin + eps)
  let bIn := decide (b.score ≤ fMin + eps)
  if aIn && !bIn then
    a
  else if bIn && !aIn then
    b
  else
    let xiMin := if a.xi ≤ b.xi then a.xi else b.xi
    let aXi := decide (a.xi ≤ xiMin + eps)
    let bXi := decide (b.xi ≤ xiMin + eps)
    if aXi && !bXi then
      a
    else if bXi && !aXi then
      b
    else if better a b then
      a
    else
      b

def allEq (tag : String) : List String → Bool
  | [] => true
  | t :: ts => (t == tag) && allEq tag ts

def anyEq (tag : String) : List String → Bool
  | [] => false
  | t :: ts => (t == tag) || anyEq tag ts

def stripInvalid : List String → List String
  | [] => []
  | t :: ts =>
    if t == "RefusedInvalidInput" then stripInvalid ts else t :: stripInvalid ts

def classify (tags : List String) : String :=
  if tags == [] then
    "RefusedStalled"
  else if allEq "RefusedInvalidInput" tags then
    "RefusedInvalidInput"
  else if allEq "RefusedTearing" (stripInvalid tags) && anyEq "RefusedTearing" (stripInvalid tags) then
    "RefusedTearing"
  else if allEq "RefusedDescentViolation" (stripInvalid tags) &&
      anyEq "RefusedDescentViolation" (stripInvalid tags) then
    "RefusedDescentViolation"
  else
    "RefusedStalled"

theorem zero_geom_rejects_curvature (c : Chan) (hg : c.geom = 0) (hc : 0 < c.curv) :
    signatureOk c = false := by
  simp [signatureOk, hg, hc]

theorem zero_geom_rejects_xi (c : Chan) (hg : c.geom = 0) (hx : 0 < c.xi) :
    signatureOk c = false := by
  simp [signatureOk, hg, hx]

theorem separated_sat_accepts :
    signatureOk ⟨0, 3, 0, 0, 0⟩ = true := by
  decide

theorem not_nonpos_of_pos {x : Rat} (h : 0 < x) : ¬ x ≤ 0 := by
  grind

theorem not_neg_of_pos {x : Rat} (h : 0 < x) : ¬ x < 0 := by
  grind

theorem not_neg_of_nonneg {x : Rat} (h : 0 ≤ x) : ¬ x < 0 := by
  grind

theorem ratio_infinite_rejects (curv rMax : Rat) (hc : 0 < curv) (hr : 0 < rMax) :
    ratioAdmits 0 curv rMax = false := by
  have hne : curv ≠ 0 := by grind
  have hcurv : ¬ curv < 0 := not_neg_of_pos hc
  have hzero : ¬ (0 : Rat) < 0 := by grind
  have hceil : ¬ rMax ≤ 0 := not_nonpos_of_pos hr
  simp [ratioAdmits, hne, hcurv, hzero, hceil]

theorem collapsed_pair_passes (rMax : Rat) (hr : 0 < rMax) :
    ratioAdmits 0 0 rMax = true := by
  have hzero : ¬ (0 : Rat) < 0 := by grind
  have hceil : ¬ rMax ≤ 0 := not_nonpos_of_pos hr
  simp [ratioAdmits, hzero, hceil]

theorem ratio_positive_rejects (geom curv rMax : Rat)
    (hg : 0 < geom) (hc : 0 ≤ curv) (hr : 0 < rMax) (h : rMax * geom < curv) :
    ratioAdmits geom curv rMax = false := by
  have hne : geom ≠ 0 := by grind
  have hg0 : ¬ geom < 0 := not_neg_of_pos hg
  have hc0 : ¬ curv < 0 := not_neg_of_nonneg hc
  have hceil : ¬ rMax ≤ 0 := not_nonpos_of_pos hr
  have hnot : ¬ curv ≤ rMax * geom := by grind
  simp [ratioAdmits, hne, hg0, hc0, hceil, hnot]

theorem ratio_positive_admits (geom curv rMax : Rat)
    (hg : 0 < geom) (hc : 0 ≤ curv) (hr : 0 < rMax) (h : curv ≤ rMax * geom) :
    ratioAdmits geom curv rMax = true := by
  have hne : geom ≠ 0 := by grind
  have hg0 : ¬ geom < 0 := not_neg_of_pos hg
  have hc0 : ¬ curv < 0 := not_neg_of_nonneg hc
  have hceil : ¬ rMax ≤ 0 := not_nonpos_of_pos hr
  simp [ratioAdmits, hne, hg0, hc0, hceil, h]

theorem descent_rejects (current candidate : Rat) (h : current < candidate) :
    descentOk current candidate = false := by
  have hnot : ¬ candidate ≤ current := by grind
  simp [descentOk, hnot]

theorem tearing_after_descent (curGeom candGeom candCurv rMax : Rat)
    (hdesc : candGeom ≤ curGeom) (hratio : ratioAdmits candGeom candCurv rMax = false) :
    passesGuards curGeom candGeom candCurv rMax = false := by
  have hok : descentOk curGeom candGeom = true := by
    simp [descentOk, hdesc]
  simp [passesGuards, hok, hratio]

theorem deletion_shaped_passes (rMax : Rat) (hr : 0 < rMax) :
    passesGuards 3 0 0 rMax = true := by
  have hdesc : (0 : Rat) ≤ 3 := by grind
  have hzero : ¬ (0 : Rat) < 0 := by grind
  have hceil : ¬ rMax ≤ 0 := not_nonpos_of_pos hr
  simp [passesGuards, descentOk, ratioAdmits, hdesc, hzero, hceil]

theorem lift_rejects (dGeom dSat penalty : Rat) (h : dGeom + half * dSat ≤ penalty) :
    liftAdmitted dGeom dSat penalty = false := by
  have hnot : ¬ penalty < dGeom + half * dSat := by grind
  simp [liftAdmitted, hnot]

theorem lift_accepts (dGeom dSat penalty : Rat) (h : penalty < dGeom + half * dSat) :
    liftAdmitted dGeom dSat penalty = true := by
  simp [liftAdmitted, h]

theorem outside_eps_loses (eps : Rat) (a b : Scored) (he : 0 ≤ eps)
    (h : a.score + eps < b.score) : select2 eps a b = a := by
  have hmin : a.score ≤ b.score := by grind
  have ha : a.score ≤ a.score + eps := by grind
  have hb : ¬ b.score ≤ a.score + eps := by grind
  simp [select2, hmin, ha, hb]

theorem lower_xi_in_score_tie (eps : Rat) (a b : Scored) (he : 0 ≤ eps)
    (hs : a.score = b.score) (hx : a.xi + eps < b.xi) : select2 eps a b = a := by
  have hmin : a.score ≤ b.score := by grind
  have ha : a.score ≤ a.score + eps := by grind
  have hb : b.score ≤ a.score + eps := by grind
  have hxi : a.xi ≤ b.xi := by grind
  have haxi : a.xi ≤ a.xi + eps := by grind
  have hbxi : ¬ b.xi ≤ a.xi + eps := by grind
  simp [select2, hs, hxi, haxi, hbxi]

theorem name_orders_exact_tie (eps : Rat) (a b : Scored) (he : 0 ≤ eps)
    (hs : a.score = b.score) (hx : a.xi = b.xi) (hn : a.name < b.name) :
    select2 eps a b = a := by
  have hmin : a.score ≤ b.score := by grind
  have ha : a.score ≤ a.score + eps := by grind
  have hb : b.score ≤ a.score + eps := by grind
  have hxi : a.xi ≤ b.xi := by grind
  have haxi : a.xi ≤ a.xi + eps := by grind
  have hbxi : b.xi ≤ a.xi + eps := by grind
  have hnotScore : ¬ a.score < b.score := by grind
  have hnotScoreB : ¬ b.score < a.score := by grind
  have hnotXi : ¬ a.xi < b.xi := by grind
  have hnotXiB : ¬ b.xi < a.xi := by grind
  have hbetter : better a b = true := by
    simp [better, hnotScore, hnotScoreB, hnotXi, hnotXiB, hn]
  simp [select2, hs, hx, hbetter]

theorem empty_is_stalled : classify [] = "RefusedStalled" := by
  simp [classify]

theorem strip_uniform (tag : String) (tags : List String)
    (hall : allEq tag tags = true) (hdiff : tag ≠ "RefusedInvalidInput") :
    stripInvalid tags = tags := by
  induction tags with
  | nil => rfl
  | cons t ts ih =>
    simp [allEq] at hall
    rcases hall with ⟨ht, hts⟩
    have hkeep : (t == "RefusedInvalidInput") = false := by
      subst ht
      simpa using hdiff
    simp [stripInvalid, hkeep, ih hts]

theorem any_of_uniform (tag : String) (tags : List String) (hne : tags ≠ [])
    (hall : allEq tag tags = true) : anyEq tag tags = true := by
  cases tags with
  | nil => exact absurd rfl hne
  | cons t ts =>
    simp [allEq, anyEq] at hall ⊢
    exact Or.inl hall.1

theorem not_invalid_uniform (tag : String) (tags : List String) (hne : tags ≠ [])
    (hall : allEq tag tags = true) (hdiff : tag ≠ "RefusedInvalidInput") :
    allEq "RefusedInvalidInput" tags = false := by
  cases tags with
  | nil => exact absurd rfl hne
  | cons t ts =>
    simp [allEq] at hall
    rcases hall with ⟨ht, _⟩
    subst ht
    simp [allEq, hdiff]

theorem not_other_uniform (tag other : String) (tags : List String) (hne : tags ≠ [])
    (hall : allEq tag tags = true) (hdiff : tag ≠ other) :
    allEq other tags = false := by
  cases tags with
  | nil => exact absurd rfl hne
  | cons t ts =>
    simp [allEq] at hall
    rcases hall with ⟨ht, _⟩
    subst ht
    have hbeq : (t == other) = false := by simpa using hdiff
    simp [allEq, hbeq]

theorem classify_uniform (tag : String) (tags : List String) (hne : tags ≠ [])
    (hall : allEq tag tags = true) (hdiff : tag ≠ "RefusedInvalidInput")
    (htag : tag = "RefusedTearing" ∨ tag = "RefusedDescentViolation") :
    classify tags = tag := by
  have hstrip := strip_uniform tag tags hall hdiff
  have hnot := not_invalid_uniform tag tags hne hall hdiff
  have hany := any_of_uniform tag tags hne hall
  have hempty : (tags == []) = false := by
    cases tags with
    | nil => exact absurd rfl hne
    | cons _ _ => simp
  cases htag with
  | inl htear =>
    subst htear
    simp [classify, hempty, hnot, hstrip, hall, hany]
  | inr hdesc =>
    subst hdesc
    have hnotTear : allEq "RefusedTearing" tags = false :=
      not_other_uniform "RefusedDescentViolation" "RefusedTearing" tags hne hall (by decide)
    simp [classify, hempty, hnot, hstrip, hall, hany, hnotTear]

theorem classify_all_tearing (tags : List String) (hne : tags ≠ [])
    (hall : allEq "RefusedTearing" tags = true) :
    classify tags = "RefusedTearing" := by
  have hdiff : ("RefusedTearing" : String) ≠ "RefusedInvalidInput" := by decide
  exact classify_uniform "RefusedTearing" tags hne hall hdiff (Or.inl rfl)

theorem classify_all_descent (tags : List String) (hne : tags ≠ [])
    (hall : allEq "RefusedDescentViolation" tags = true) :
    classify tags = "RefusedDescentViolation" := by
  have hdiff : ("RefusedDescentViolation" : String) ≠ "RefusedInvalidInput" := by decide
  exact classify_uniform "RefusedDescentViolation" tags hne hall hdiff (Or.inr rfl)

theorem classify_all_invalid (tags : List String) (hne : tags ≠ [])
    (hall : allEq "RefusedInvalidInput" tags = true) :
    classify tags = "RefusedInvalidInput" := by
  have hempty : (tags == []) = false := by
    cases tags with
    | nil => exact absurd rfl hne
    | cons _ _ => simp
  simp [classify, hempty, hall]

theorem mixed_stalls :
    classify ["RefusedTearing", "RefusedDescentViolation"] = "RefusedStalled" := by
  decide
