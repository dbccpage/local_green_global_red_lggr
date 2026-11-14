/-
Copyright (c) 2026 Jeremy H. Carroll. All rights reserved.
Released under Apache 2.0 license.
Authors: Jeremy H. Carroll

Paper: The Omega Tower: Role Non-Impersonation and Authority Preservation in Agentic AI
Module: RoleNonImpersonation.ExceptionPipeline
Description: Formalization of the refusal monad (exception monad), its Kleisli bind,
left-zero absorption, and the five-stage short-circuiting refusal propagation theorems.
-/

namespace RoleNonImpersonation

/-- The Refusal Monad M(X) = X + String, modeling computations that yield either
a valid value or an explicit, non-bypassable refusal. -/
inductive RefusalM (α : Type) where
  | success : α → RefusalM α
  | refusal : String → RefusalM α
  deriving DecidableEq, Repr

namespace RefusalM

def pure (x : α) : RefusalM α :=
  RefusalM.success x

/-- Kleisli bind for the Refusal Monad. -/
def bind (m : RefusalM α) (f : α → RefusalM β) : RefusalM β :=
  match m with
  | RefusalM.success a => f a
  | RefusalM.refusal err => RefusalM.refusal err

instance : Monad RefusalM where
  pure := RefusalM.pure
  bind := RefusalM.bind

/-- Left identity law: bind (pure x) f = f x. -/
@[simp]
theorem bind_pure (x : α) (f : α → RefusalM β) : RefusalM.bind (RefusalM.pure x) f = f x := by
  rfl

/-- Left-zero absorption law: a refusal cannot be bypassed by any subsequent function f. -/
@[simp]
theorem bindR_refusal_left_zero (err : String) (f : α → RefusalM β) :
    RefusalM.bind (RefusalM.refusal err) f = RefusalM.refusal err := by
  rfl

/-- Right identity law: bind m pure = m. -/
@[simp]
theorem bind_right_id (m : RefusalM α) : RefusalM.bind m RefusalM.pure = m := by
  cases m <;> rfl

/-- Associativity of Kleisli composition: bind (bind m f) g = bind m (fun x => bind (f x) g). -/
theorem bindR_assoc (m : RefusalM α) (f : α → RefusalM β) (g : β → RefusalM γ) :
    RefusalM.bind (RefusalM.bind m f) g = RefusalM.bind m (fun x => RefusalM.bind (f x) g) := by
  cases m with
  | success a => rfl
  | refusal err => rfl

/-- The five-stage pipeline:
  Stage 1 (Obstruction / R)
  Stage 2 (Transport / rho)
  Stage 3 (Descent / D)
  Stage 4 (Verification / V)
  Stage 5 (Terminalization / tau) -/
def pipeline5
    (s1 : α → RefusalM β)
    (s2 : β → RefusalM γ)
    (s3 : γ → RefusalM δ)
    (s4 : δ → RefusalM ε)
    (s5 : ε → RefusalM ζ)
    (init : α) : RefusalM ζ :=
  RefusalM.bind (s1 init) (fun b =>
    RefusalM.bind (s2 b) (fun c =>
      RefusalM.bind (s3 c) (fun d =>
        RefusalM.bind (s4 d) (fun e => s5 e))))

/-- Stage 1 Refusal Propagation Theorem:
If Stage 1 (Obstruction) refuses, the entire pipeline immediately yields that refusal. -/
theorem pipeline5_obstruction_refusal_propagates
    (s1 : α → RefusalM β) (s2 : β → RefusalM γ) (s3 : γ → RefusalM δ)
    (s4 : δ → RefusalM ε) (s5 : ε → RefusalM ζ) (init : α) (err : String)
    (h : s1 init = RefusalM.refusal err) :
    pipeline5 s1 s2 s3 s4 s5 init = RefusalM.refusal err := by
  unfold pipeline5
  rw [h]
  rfl

/-- Stage 2 Refusal Propagation Theorem:
If Stage 2 (Transport) refuses on b, the pipeline yields that refusal. -/
theorem pipeline5_transport_refusal_propagates
    (s1 : α → RefusalM β) (s2 : β → RefusalM γ) (s3 : γ → RefusalM δ)
    (s4 : δ → RefusalM ε) (s5 : ε → RefusalM ζ) (init : α) (b : β) (err : String)
    (h1 : s1 init = RefusalM.success b)
    (h2 : s2 b = RefusalM.refusal err) :
    pipeline5 s1 s2 s3 s4 s5 init = RefusalM.refusal err := by
  unfold pipeline5
  rw [h1]
  dsimp [RefusalM.bind]
  rw [h2]

/-- Stage 3 Refusal Propagation Theorem:
If Stage 3 (Descent) refuses on c, the pipeline yields that refusal. -/
theorem pipeline5_descent_refusal_propagates
    (s1 : α → RefusalM β) (s2 : β → RefusalM γ) (s3 : γ → RefusalM δ)
    (s4 : δ → RefusalM ε) (s5 : ε → RefusalM ζ) (init : α) (b : β) (c : γ) (err : String)
    (h1 : s1 init = RefusalM.success b)
    (h2 : s2 b = RefusalM.success c)
    (h3 : s3 c = RefusalM.refusal err) :
    pipeline5 s1 s2 s3 s4 s5 init = RefusalM.refusal err := by
  unfold pipeline5
  rw [h1]
  dsimp [RefusalM.bind]
  rw [h2]
  dsimp [RefusalM.bind]
  rw [h3]

/-- Stage 4 Refusal Propagation Theorem:
If Stage 4 (Verification) refuses on d, the pipeline yields that refusal. -/
theorem pipeline5_verify_refusal_propagates
    (s1 : α → RefusalM β) (s2 : β → RefusalM γ) (s3 : γ → RefusalM δ)
    (s4 : δ → RefusalM ε) (s5 : ε → RefusalM ζ) (init : α) (b : β) (c : γ) (d : δ) (err : String)
    (h1 : s1 init = RefusalM.success b)
    (h2 : s2 b = RefusalM.success c)
    (h3 : s3 c = RefusalM.success d)
    (h4 : s4 d = RefusalM.refusal err) :
    pipeline5 s1 s2 s3 s4 s5 init = RefusalM.refusal err := by
  unfold pipeline5
  rw [h1]
  dsimp [RefusalM.bind]
  rw [h2]
  dsimp [RefusalM.bind]
  rw [h3]
  dsimp [RefusalM.bind]
  rw [h4]

/-- Stage 5 Refusal Propagation Theorem:
If Stage 5 (Terminalization) refuses on e, the pipeline yields that refusal. -/
theorem pipeline5_terminal_refusal_propagates
    (s1 : α → RefusalM β) (s2 : β → RefusalM γ) (s3 : γ → RefusalM δ)
    (s4 : δ → RefusalM ε) (s5 : ε → RefusalM ζ) (init : α) (b : β) (c : γ) (d : δ) (e : ε) (err : String)
    (h1 : s1 init = RefusalM.success b)
    (h2 : s2 b = RefusalM.success c)
    (h3 : s3 c = RefusalM.success d)
    (h4 : s4 d = RefusalM.success e)
    (h5 : s5 e = RefusalM.refusal err) :
    pipeline5 s1 s2 s3 s4 s5 init = RefusalM.refusal err := by
  unfold pipeline5
  rw [h1]
  dsimp [RefusalM.bind]
  rw [h2]
  dsimp [RefusalM.bind]
  rw [h3]
  dsimp [RefusalM.bind]
  rw [h4]
  dsimp [RefusalM.bind]
  rw [h5]

end RefusalM

end RoleNonImpersonation
