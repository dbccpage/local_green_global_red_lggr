import Bell.PlanarQuantum

/-! A constructive finite real-symmetric Clifford family, embedded in complex
matrices. The dimension is deliberately nonminimal: one binary factor per
generator. No representation-existence premise is assumed. -/
noncomputable section
open scoped BigOperators ComplexConjugate
namespace Bell.Clifford
open Bell.QuantumExample

abbrev kron {a b : Type} (A : Matrix a a ℂ) (B : Matrix b b ℂ) :
    Matrix (a × b) (a × b) ℂ := Matrix.kroneckerMap (· * ·) A B

abbrev Carrier : ℕ → Type
  | 0 => Unit
  | n+1 => Bool × Carrier n

instance carrierFintype (n : ℕ) : Fintype (Carrier n) := by
  induction n with
  | zero => exact inferInstanceAs (Fintype Unit)
  | succ n ih => exact inferInstanceAs (Fintype (Bool × Carrier n))

instance carrierDecidableEq (n : ℕ) : DecidableEq (Carrier n) := by
  induction n with
  | zero => exact inferInstanceAs (DecidableEq Unit)
  | succ n ih => exact inferInstanceAs (DecidableEq (Bool × Carrier n))

instance carrierNonempty (n : ℕ) : Nonempty (Carrier n) := by
  induction n with
  | zero => exact inferInstanceAs (Nonempty Unit)
  | succ n ih => exact inferInstanceAs (Nonempty (Bool × Carrier n))

def gamma : (n : ℕ) → Fin n → Matrix (Carrier n) (Carrier n) ℂ
  | 0 => Fin.elim0
  | n+1 => Fin.cases (kron X 1)
      (fun i => kron Z (gamma n i))

theorem gamma_zero (n : ℕ) : gamma (n+1) 0 = kron X 1 := rfl

theorem gamma_succ (n : ℕ) (i : Fin n) :
    gamma (n+1) i.succ = kron Z (gamma n i) := rfl

theorem pauli_laws : X * X = 1 ∧ Z * Z = 1 ∧ X * Z = -(Z * X) := by
  constructor
  · ext i j; cases i <;> cases j <;> norm_num [X,Matrix.mul_apply,Matrix.one_apply]
  constructor
  · ext i j; cases i <;> cases j <;> norm_num [Z,Matrix.mul_apply,Matrix.one_apply]
  · ext i j; cases i <;> cases j <;> norm_num [X,Z,Matrix.mul_apply]

theorem pauli_hermitian : X.conjTranspose = X ∧ Z.conjTranspose = Z := by
  constructor <;> ext i j <;> cases i <;> cases j <;>
    norm_num [X,Z,Matrix.conjTranspose_apply]

theorem pauli_trace : Matrix.trace X = 0 ∧ Matrix.trace Z = 0 := by
  norm_num [Matrix.trace,Matrix.diag,X,Z]

theorem carrier_card (n : ℕ) : Fintype.card (Carrier n) = 2^n := by
  induction n with
  | zero => rfl
  | succ n ih =>
    change Fintype.card (Bool × Carrier n) = _
    simp [Fintype.card_prod,ih,pow_succ,mul_comm]

theorem gamma_hermitian (n : ℕ) (i : Fin n) :
    (gamma n i).conjTranspose = gamma n i := by
  induction n with
  | zero => exact Fin.elim0 i
  | succ n ih =>
    refine Fin.cases ?_ (fun j => ?_) i
    · rw [gamma_zero,Matrix.conjTranspose_kronecker,pauli_hermitian.1]
      simp
    · rw [gamma_succ,Matrix.conjTranspose_kronecker,pauli_hermitian.2,ih]

theorem gamma_square (n : ℕ) (i : Fin n) : gamma n i * gamma n i = 1 := by
  induction n with
  | zero => exact Fin.elim0 i
  | succ n ih =>
    refine Fin.cases ?_ (fun j => ?_) i
    · rw [gamma_zero,← Matrix.mul_kronecker_mul,pauli_laws.1]
      simp
    · rw [gamma_succ,← Matrix.mul_kronecker_mul,pauli_laws.2.1,ih]
      simp

theorem gamma_trace (n : ℕ) (i : Fin n) : Matrix.trace (gamma n i) = 0 := by
  cases n with
  | zero => exact Fin.elim0 i
  | succ n =>
    refine Fin.cases ?_ (fun j => ?_) i
    · rw [gamma_zero,Matrix.trace_kronecker,pauli_trace.1,zero_mul]
    · rw [gamma_succ,Matrix.trace_kronecker,pauli_trace.2,zero_mul]

theorem kron_neg_left {a b : Type} [Fintype a] [Fintype b]
    (A : Matrix a a ℂ) (B : Matrix b b ℂ) :
    kron (-A) B = -(kron A B) := by
  ext ⟨i,j⟩ ⟨r,s⟩
  exact neg_mul (A i r) (B j s)

theorem kron_neg_right {a b : Type} [Fintype a] [Fintype b]
    (A : Matrix a a ℂ) (B : Matrix b b ℂ) :
    kron A (-B) = -(kron A B) := by
  ext ⟨i,j⟩ ⟨r,s⟩
  exact mul_neg (A i r) (B j s)

theorem gamma_anticommute (n : ℕ) (i j : Fin n) (h : i ≠ j) :
    gamma n i * gamma n j = -(gamma n j * gamma n i) := by
  induction n with
  | zero => exact Fin.elim0 i
  | succ n ih =>
    revert h
    refine Fin.cases ?_ (fun a => ?_) i
    · refine Fin.cases (fun h => False.elim (h rfl)) (fun b h => ?_) j
      rw [gamma_zero,gamma_succ,← Matrix.mul_kronecker_mul,
        ← Matrix.mul_kronecker_mul,one_mul,mul_one,pauli_laws.2.2]
      exact kron_neg_left (Z*X) (gamma n b)
    · refine Fin.cases (fun h => ?_) (fun b h => ?_) j
      · rw [gamma_zero,gamma_succ,← Matrix.mul_kronecker_mul,
          ← Matrix.mul_kronecker_mul,one_mul,mul_one,pauli_laws.2.2]
        simpa only [neg_neg] using (congrArg Neg.neg (kron_neg_left (Z*X) (gamma n a))).symm
      · rw [gamma_succ,gamma_succ,← Matrix.mul_kronecker_mul,
          ← Matrix.mul_kronecker_mul,ih a b (fun he => h (congrArg Fin.succ he))]
        exact kron_neg_right (Z*Z) (gamma n b * gamma n a)

theorem gamma_trace_pair (n : ℕ) (i j : Fin n) :
    Matrix.trace (gamma n i * gamma n j) =
      if i = j then (Fintype.card (Carrier n) : ℂ) else 0 := by
  split_ifs with h
  · subst j; rw [gamma_square]; simp
  · have he := congrArg Matrix.trace (gamma_anticommute n i j h)
    rw [Matrix.trace_neg,Matrix.trace_mul_comm (gamma n j)] at he
    linear_combination (1/2:ℂ) * he

end Bell.Clifford
