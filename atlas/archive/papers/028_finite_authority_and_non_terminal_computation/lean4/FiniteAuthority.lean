namespace FiniteAuthority

def allB {α : Type} (p : α → Bool) : List α → Bool
  | [] => true
  | a :: as => p a && allB p as

def anyB {α : Type} (p : α → Bool) : List α → Bool
  | [] => false
  | a :: as => p a || anyB p as

theorem allB_false {α : Type} (p : α → Bool) (l : List α) (h : allB p l = false) :
    ∃ a, a ∈ l ∧ p a = false := by
  induction l with
  | nil => simp [allB] at h
  | cons a as ih =>
    simp only [allB] at h
    cases hp : p a with
    | false => exact ⟨a, List.Mem.head as, hp⟩
    | true =>
      have hrest : allB p as = false := by simpa [hp] using h
      obtain ⟨b, hb, pb⟩ := ih hrest
      exact ⟨b, List.mem_cons_of_mem a hb, pb⟩

def rangePairs (n : Nat) : List (Nat × Nat) :=
  (List.range n).flatMap fun i => (List.range n).map fun j => (i, j)

theorem mem_rangePairs {n i j : Nat} (h : (i, j) ∈ rangePairs n) : i < n ∧ j < n := by
  simp only [rangePairs, List.mem_flatMap, List.mem_map, List.mem_range] at h
  rcases h with ⟨a, ha, b, hb, heq⟩
  cases heq
  exact ⟨ha, hb⟩

inductive Color where
  | green
  | red
  deriving DecidableEq, Repr

inductive Verdict where
  | pass
  | fail
  deriving DecidableEq, Repr

def symRel (edges : List (Nat × Nat)) (i j : Nat) : Bool :=
  i == j || edges.contains (i, j) || edges.contains (j, i)

def closeStep (rel : Nat → Nat → Bool) (k : Nat) : Nat → Nat → Bool :=
  fun i j => rel i j || (rel i k && rel k j)

def warshall : Nat → (Nat → Nat → Bool) → Nat → Nat → Bool
  | 0, rel => rel
  | n + 1, rel => closeStep (warshall n rel) n

def localOk (rel : Nat → Nat → Bool) (color : Nat → Color) (n : Nat) : Bool :=
  allB (fun p => !rel p.1 p.2 || color p.1 == color p.2) (rangePairs n)

def jointOk (rel : Nat → Nat → Bool) (color : Nat → Color) (verdict : Nat → Verdict) (n : Nat) : Bool :=
  allB (fun p => !rel p.1 p.2 || (color p.1 == color p.2 && verdict p.1 == verdict p.2)) (rangePairs n)

def lggr (rel : Nat → Nat → Bool) (color : Nat → Color) (verdict : Nat → Verdict) (n : Nat) : Bool :=
  localOk rel color n && !jointOk rel color verdict n

theorem allB_mem {α : Type} (p : α → Bool) :
    ∀ (l : List α) (a : α), a ∈ l → allB p l = true → p a = true
  | [], _, hm, _ => by simp at hm
  | b :: bs, a, hm, h => by
    simp only [allB] at h
    have hhead : p b = true := by
      cases hp : p b with
      | true => rfl
      | false => simp [hp] at h
    have htail : allB p bs = true := by simpa [hhead] using h
    cases List.mem_cons.mp hm with
    | inl heq =>
      subst heq
      exact hhead
    | inr hmem =>
      exact allB_mem p bs a hmem htail

theorem beq_false_ne {α : Type} [DecidableEq α] {a b : α} (h : ((a == b) = false)) : a ≠ b := by
  intro hab
  cases hab
  simp at h

theorem beq_true_eq {α : Type} [DecidableEq α] {a b : α} (h : ((a == b) = true)) : a = b :=
  of_decide_eq_true h

theorem lggr_has_global_split
    (rel : Nat → Nat → Bool) (color : Nat → Color) (verdict : Nat → Verdict) (n : Nat)
    (h : lggr rel color verdict n = true) :
    ∃ i j, i < n ∧ j < n ∧ rel i j = true ∧ color i = color j ∧ verdict i ≠ verdict j := by
  have hLocal : localOk rel color n = true := by
    cases hloc : localOk rel color n with
    | false => simp [lggr, hloc] at h
    | true => rfl
  have hJoint : jointOk rel color verdict n = false := by
    cases hjoint : jointOk rel color verdict n with
    | true => simp [lggr, hLocal, hjoint] at h
    | false => rfl
  have hAll : allB (fun p => !rel p.1 p.2 || (color p.1 == color p.2 && verdict p.1 == verdict p.2)) (rangePairs n) = false := by
    simpa [jointOk] using hJoint
  obtain ⟨p, hp, hpred⟩ := allB_false _ (rangePairs n) hAll
  have hbounds := mem_rangePairs hp
  have hLocalAll :
      allB (fun q => !rel q.1 q.2 || color q.1 == color q.2) (rangePairs n) = true := by
    simpa [localOk] using hLocal
  have hlocalP : (!rel p.1 p.2 || color p.1 == color p.2) = true :=
    allB_mem (fun q => !rel q.1 q.2 || color q.1 == color q.2) (rangePairs n) p hp hLocalAll
  cases hr : rel p.1 p.2 with
  | false => simp [hr] at hpred
  | true =>
    cases hc : color p.1 == color p.2 with
    | false => simp [hr, hc] at hlocalP
    | true =>
      cases hv : verdict p.1 == verdict p.2 with
      | true => simp [hr, hc, hv] at hpred
      | false =>
        exact ⟨p.1, p.2, hbounds.1, hbounds.2, hr, beq_true_eq hc, beq_false_ne hv⟩

def twoRel : Nat → Nat → Bool := warshall 2 (symRel [(0, 1)])

def twoColor : Nat → Color
  | _ => Color.green

def twoVerdict : Nat → Verdict
  | 0 => Verdict.pass
  | _ => Verdict.fail

theorem two_point_lggr : lggr twoRel twoColor twoVerdict 2 = true := by
  decide

theorem two_point_has_split :
    anyB (fun p => twoRel p.1 p.2 && twoVerdict p.1 != twoVerdict p.2) (rangePairs 2) = true := by
  decide

def threeRel : Nat → Nat → Bool := fun _ _ => true

def threeColor : Nat → Color
  | 2 => Color.red
  | _ => Color.green

def threeVerdict : Nat → Verdict
  | 1 => Verdict.fail
  | _ => Verdict.pass

theorem three_point_not_lggr : lggr threeRel threeColor threeVerdict 3 = false := by
  decide

def countNew (seen : List Nat) : List Nat → Nat
  | [] => 0
  | a :: as =>
    match seen.contains a with
    | true => countNew seen as
    | false => countNew (a :: seen) as + 1

def distinctCount (l : List Nat) : Nat := countNew [] l

theorem distinct_pos (l : List Nat) (h : l ≠ []) : 0 < distinctCount l := by
  cases l with
  | nil => exact absurd rfl h
  | cons a as =>
    have hempty : ([] : List Nat).contains a = false := by
      unfold List.contains
      rfl
    have hstep : distinctCount (a :: as) = countNew [a] as + 1 := by
      simp only [distinctCount, countNew, hempty]
    omega

theorem sum_sub_one (ds : List Nat) (h : ∀ d ∈ ds, 1 ≤ d) :
    ds.sum = ds.length + (ds.map (· - 1)).sum := by
  induction ds with
  | nil => simp
  | cons d rest ih =>
    have hd : 1 ≤ d := h d (List.Mem.head rest)
    have hrest : ∀ x ∈ rest, 1 ≤ x := fun x hx => h x (List.mem_cons_of_mem d hx)
    have ih' := ih hrest
    simp only [List.sum_cons, List.length_cons, List.map_cons, List.sum_cons]
    have hcancel : d - 1 + 1 = d := Nat.sub_add_cancel hd
    omega

def refinedSize (fibers : List (List Nat)) : Nat :=
  (fibers.map distinctCount).sum

def classIncrease (fibers : List (List Nat)) : Nat :=
  ((fibers.map distinctCount).map (· - 1)).sum

theorem increase_formula (fibers : List (List Nat)) (h : ∀ f ∈ fibers, f ≠ []) :
    refinedSize fibers = fibers.length + classIncrease fibers := by
  let ds := fibers.map distinctCount
  have hcounts : ∀ d ∈ ds, 1 ≤ d := by
    intro d hd
    simp only [ds, List.mem_map] at hd
    rcases hd with ⟨f, hf, rfl⟩
    exact Nat.succ_le_of_lt (distinct_pos f (h f hf))
  have hsum := sum_sub_one ds hcounts
  calc
    refinedSize fibers = ds.sum := by simp [refinedSize, ds]
    _ = ds.length + (ds.map (· - 1)).sum := hsum
    _ = fibers.length + classIncrease fibers := by simp [ds, classIncrease]

def demoFibers : List (List Nat) := [[0, 1, 0], [2, 2]]

theorem demo_fibers_nonempty : ∀ f ∈ demoFibers, f ≠ [] := by
  decide

theorem demo_increase : classIncrease demoFibers = 1 := by
  decide

theorem demo_refined : refinedSize demoFibers = 3 := by
  decide

theorem demo_formula : refinedSize demoFibers = demoFibers.length + classIncrease demoFibers :=
  increase_formula demoFibers demo_fibers_nonempty

theorem demo_split_verdicts : ∃ u v, u ∈ [0, 1, 0] ∧ v ∈ [0, 1, 0] ∧ u ≠ v :=
  ⟨0, 1, by simp, by simp, by decide⟩

inductive HaltStatus where
  | authority
  | checklistCertified
  | refusal
  | nonAuthorityHalt
  | proposalOnly
  deriving DecidableEq, Repr

def evalHalt (halted : Bool) (gatesPassed : Option Bool) (witnessOk : Option Bool) : HaltStatus :=
  if !halted then HaltStatus.proposalOnly
  else
    match gatesPassed with
    | none => HaltStatus.nonAuthorityHalt
    | some false => HaltStatus.refusal
    | some true =>
      match witnessOk with
      | none => HaltStatus.checklistCertified
      | some false => HaltStatus.refusal
      | some true => HaltStatus.authority

theorem halt_alone_not_authority :
    evalHalt true none none = HaltStatus.nonAuthorityHalt := rfl

theorem gates_without_witness_not_authority :
    evalHalt true (some true) none = HaltStatus.checklistCertified := rfl

theorem gates_and_witness_authority :
    evalHalt true (some true) (some true) = HaltStatus.authority := rfl

theorem witness_mismatch_refuses :
    evalHalt true (some true) (some false) = HaltStatus.refusal := rfl

theorem unhalted_is_proposal :
    evalHalt false (some true) (some true) = HaltStatus.proposalOnly := rfl

inductive CounterfeitStatus where
  | counterfeitRefusal
  | verifierRefusal
  | nonAuthorityHalt
  | proposalOnly
  | checklistCertified
  | authority
  | gateRefusal
  deriving DecidableEq, Repr

def evalCounterfeit
    (halted residualPos surface : Bool)
    (gatesPassed : Option Bool)
    (witnessOk : Option Bool) : CounterfeitStatus :=
  if !halted then CounterfeitStatus.proposalOnly
  else if residualPos then
    if surface then CounterfeitStatus.counterfeitRefusal else CounterfeitStatus.verifierRefusal
  else
    match gatesPassed with
    | none => CounterfeitStatus.nonAuthorityHalt
    | some false =>
      if surface then CounterfeitStatus.counterfeitRefusal else CounterfeitStatus.gateRefusal
    | some true =>
      match witnessOk with
      | none => CounterfeitStatus.checklistCertified
      | some false => CounterfeitStatus.counterfeitRefusal
      | some true => CounterfeitStatus.authority

theorem residual_surface_counterfeit :
    evalCounterfeit true true true none none = CounterfeitStatus.counterfeitRefusal := rfl

theorem residual_plain_refuses :
    evalCounterfeit true true false none none = CounterfeitStatus.verifierRefusal := rfl

theorem zero_residual_no_gates :
    evalCounterfeit true false false none none = CounterfeitStatus.nonAuthorityHalt := rfl

theorem zero_residual_gates_checklist :
    evalCounterfeit true false false (some true) none = CounterfeitStatus.checklistCertified := rfl

theorem zero_residual_witness_authority :
    evalCounterfeit true false false (some true) (some true) = CounterfeitStatus.authority := rfl

theorem unhalted_counterfeit_is_proposal :
    evalCounterfeit false false false none none = CounterfeitStatus.proposalOnly := rfl

end FiniteAuthority
