# Output: round_5_implementation_and_proof_discharge.md

- **Timestamp:** 2026-10-17T01:07:13.097056
- **Model:** claude-fable-5-1
- **Round:** 5
- **Duration:** 370.1s
- **Tokens:** In=78726, Out=32768
- **Source Prompt:** `C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\prompts\quantum_relational_rsi\round_5_implementation_and_proof_discharge.md`
- **Continued From:** `C:\Users\a343o\source\repos\the_symbol_game\omega_engine_atlas\coda_atlas\prompts\quantum_relational_rsi\outputs\20261017_005630_round_4_round_4_synthesis_and_executable_verification_claude-fable-5-1.md`

---

## Thinking Trace

```text

```

---

## Response Content

# Round 5 Record — Rust Implementation, Witness Suite, Lean 4 Proof Discharge

**Campaign:** `FABLE_5_1_QUANTUM_RELATIONAL_RSI_DERIVATION` · **Round 5 (tooling pass)**
**Execution note:** No Cargo, Lean, or solver ran. The two files below are written to compile and pass as-is; they have not been compiled, type-checked, or executed here. Every expected test value is a hand-derived quantity from Rounds 1–3 (re-checked by hand in this round); every expected Lean elaboration is a hand-traced tactic script. A mismatch on execution is to be treated as a defect in either the derivation or the code, per Round 4.

**Corrections applied in this round.**
1. **Werner witness Kraus operators.** The Round 2 table used $\mathcal{D}_{1/2}$, whose Kraus operators need $\sqrt{5/8}$, not representable over Gaussian rationals. The witness is modified to the full Pauli twirl on qubit 1 (Kraus $\tfrac12 P\otimes I$), which is unital and rational; it sends $|\Psi^-\rangle$ to $I/4$ ($P_2 = 1/4$ instead of $7/16$). Terminal, $k^*=5$, and the "third purification attempt" structure are unchanged; the witness now saturates Theorem Q.2(b) exactly (2 bits removed with $B_0=2$).
2. **Qubit $M=2$ witness third step.** Round 1 used $H$ (entries $1/\sqrt2$). Replaced by the full depolarizing channel (rational Kraus), which also lands on report 0 by tie-break. $k^*=3$ unchanged.
3. **Dephasing realization.** $\tfrac12(\rho+Z\rho Z)$ needs $1/\sqrt2$ Kraus weights; realized instead as the pinching $\{P_0,P_1\}$, which is the same channel.
4. **Lean `quantum_rsi_bounded_horizon`.** The Round 4 signature was not provable as stated: with no purification steps and $B_0=0$ it demands an obstruction at index 0 that need not exist. Round 4's Theorem Q.Master clause (iii) was stated for *purification-only* trajectories; the Lean theorem now carries that hypothesis (`hpur : ∀ k, k ≤ B 0 → pur k`) and drops the unused `hmono`/`hclaim`. Routed as a correction, not a new result.
5. **Lean `entropy_transcendental_of_baker`.** Also discharged (not listed among the three in the prompt, but it carried a `sorry` in Round 4). It remains conditional on the `BakerLinearForms` hypothesis.

---

## 1. Rust implementation — `omega_quantum_physics/src/fable51.rs`

**Cargo.toml dependencies (declared):**
```toml
[dependencies]
num-rational = "0.4"
num-bigint   = "0.4"
num-traits   = "0.2"
```
**Float discipline:** no `f32`/`f64` token occurs in the file (checkable by `grep -nE 'f32|f64' src/fable51.rs`, expected empty). `#![forbid(clippy::float_arithmetic)]` is to be placed in `lib.rs`.

```rust
//! omega_quantum_physics::fable51
//! Exact-rational companion harness for campaign FABLE_5_1 (Rounds 1-3 witnesses).
//! All scalars are Gaussian rationals over num_rational::BigRational. No floats.

use num_bigint::BigInt;
use num_rational::BigRational;
use num_traits::{One, Zero};
use std::collections::{HashMap, HashSet};

pub type Q = BigRational;

/// Rational n/d (d != 0), auto-reduced by BigRational::new.
pub fn q(n: i64, d: i64) -> Q {
    Q::new(BigInt::from(n), BigInt::from(d))
}
/// Integer as rational.
pub fn qi(n: i64) -> Q {
    Q::from_integer(BigInt::from(n))
}
/// x^e by repeated multiplication (avoids relying on Pow impls).
fn pow_q(x: &Q, e: u32) -> Q {
    let mut r = Q::one();
    for _ in 0..e {
        r = r * x.clone();
    }
    r
}

// ---------------------------------------------------------------------------
// Gaussian rationals
// ---------------------------------------------------------------------------

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct QC {
    pub re: Q,
    pub im: Q,
}
impl QC {
    pub fn zero() -> Self { QC { re: Q::zero(), im: Q::zero() } }
    pub fn one() -> Self { QC { re: Q::one(), im: Q::zero() } }
    pub fn real(r: Q) -> Self { QC { re: r, im: Q::zero() } }
    pub fn imag(i: Q) -> Self { QC { re: Q::zero(), im: i } }
    pub fn is_zero(&self) -> bool { self.re.is_zero() && self.im.is_zero() }
    pub fn conj(&self) -> Self { QC { re: self.re.clone(), im: -self.im.clone() } }
    pub fn add(&self, o: &QC) -> QC {
        QC { re: self.re.clone() + o.re.clone(), im: self.im.clone() + o.im.clone() }
    }
    pub fn sub(&self, o: &QC) -> QC {
        QC { re: self.re.clone() - o.re.clone(), im: self.im.clone() - o.im.clone() }
    }
    pub fn mul(&self, o: &QC) -> QC {
        QC {
            re: self.re.clone() * o.re.clone() - self.im.clone() * o.im.clone(),
            im: self.re.clone() * o.im.clone() + self.im.clone() * o.re.clone(),
        }
    }
    pub fn scale(&self, c: &Q) -> QC {
        QC { re: self.re.clone() * c.clone(), im: self.im.clone() * c.clone() }
    }
}

// ---------------------------------------------------------------------------
// Matrices (row-major, n rows x m cols)
// ---------------------------------------------------------------------------

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Matrix {
    pub n: usize,
    pub m: usize,
    pub a: Vec<QC>,
}

impl Matrix {
    pub fn zeros(n: usize, m: usize) -> Self {
        Matrix { n, m, a: vec![QC::zero(); n * m] }
    }

    pub fn identity(n: usize) -> Self {
        let mut z = Matrix::zeros(n, n);
        for i in 0..n {
            z.a[i * n + i] = QC::one();
        }
        z
    }

    pub fn from_rows(rows: Vec<Vec<QC>>) -> Self {
        let n = rows.len();
        let m = if n == 0 { 0 } else { rows[0].len() };
        let mut a = Vec::with_capacity(n * m);
        for r in rows {
            assert_eq!(r.len(), m, "ragged rows");
            a.extend(r);
        }
        Matrix { n, m, a }
    }

    pub fn from_real_rows(rows: &[Vec<Q>]) -> Self {
        Matrix::from_rows(
            rows.iter().map(|r| r.iter().map(|x| QC::real(x.clone())).collect()).collect(),
        )
    }

    /// Projector |v><v| / norm_sq for an integer vector v (handles 1/sqrt(2) amplitudes exactly).
    pub fn proj_unnormalized(v: &[i64], norm_sq: i64) -> Self {
        let n = v.len();
        let mut z = Matrix::zeros(n, n);
        for i in 0..n {
            for j in 0..n {
                z.a[i * n + j] = QC::real(q(v[i] * v[j], norm_sq));
            }
        }
        z
    }

    pub fn at(&self, i: usize, j: usize) -> &QC {
        &self.a[i * self.m + j]
    }

    pub fn matmul(&self, b: &Matrix) -> Matrix {
        assert_eq!(self.m, b.n, "matmul shape mismatch");
        let mut out = Matrix::zeros(self.n, b.m);
        for i in 0..self.n {
            for j in 0..b.m {
                let mut s = QC::zero();
                for k in 0..self.m {
                    s = s.add(&self.at(i, k).mul(b.at(k, j)));
                }
                out.a[i * b.m + j] = s;
            }
        }
        out
    }

    pub fn dagger(&self) -> Matrix {
        let mut out = Matrix::zeros(self.m, self.n);
        for i in 0..self.n {
            for j in 0..self.m {
                out.a[j * self.n + i] = self.at(i, j).conj();
            }
        }
        out
    }

    pub fn add(&self, b: &Matrix) -> Matrix {
        assert!(self.n == b.n && self.m == b.m, "add shape mismatch");
        Matrix {
            n: self.n,
            m: self.m,
            a: self.a.iter().zip(b.a.iter()).map(|(x, y)| x.add(y)).collect(),
        }
    }

    pub fn trace(&self) -> QC {
        assert_eq!(self.n, self.m, "trace of non-square");
        let mut s = QC::zero();
        for i in 0..self.n {
            s = s.add(self.at(i, i));
        }
        s
    }

    /// Real scalar multiple.
    pub fn scale(&self, c: &Q) -> Matrix {
        Matrix { n: self.n, m: self.m, a: self.a.iter().map(|x| x.scale(c)).collect() }
    }

    /// Kronecker product.
    pub fn kron(&self, b: &Matrix) -> Matrix {
        let (n1, m1, n2, m2) = (self.n, self.m, b.n, b.m);
        let mut out = Matrix::zeros(n1 * n2, m1 * m2);
        for i1 in 0..n1 {
            for j1 in 0..m1 {
                for i2 in 0..n2 {
                    for j2 in 0..m2 {
                        out.a[(i1 * n2 + i2) * (m1 * m2) + (j1 * m2 + j2)] =
                            self.at(i1, j1).mul(b.at(i2, j2));
                    }
                }
            }
        }
        out
    }

    /// Tr(rho^2); asserts the imaginary part vanishes (true for Hermitian rho).
    pub fn purity_p2(&self) -> Q {
        let t = self.matmul(self).trace();
        assert!(t.im.is_zero(), "Tr(rho^2) not real");
        t.re
    }
}

// Standard single-qubit matrices (exact).
pub fn pauli_i() -> Matrix { Matrix::identity(2) }
pub fn pauli_x() -> Matrix {
    Matrix::from_real_rows(&[vec![qi(0), qi(1)], vec![qi(1), qi(0)]])
}
pub fn pauli_y() -> Matrix {
    Matrix::from_rows(vec![
        vec![QC::zero(), QC::imag(qi(-1))],
        vec![QC::imag(qi(1)), QC::zero()],
    ])
}
pub fn pauli_z() -> Matrix {
    Matrix::from_real_rows(&[vec![qi(1), qi(0)], vec![qi(0), qi(-1)]])
}
pub fn proj0() -> Matrix {
    Matrix::from_real_rows(&[vec![qi(1), qi(0)], vec![qi(0), qi(0)]])
}
pub fn proj1() -> Matrix {
    Matrix::from_real_rows(&[vec![qi(0), qi(0)], vec![qi(0), qi(1)]])
}
/// |0><1| (amplitude-damping jump operator at gamma = 1).
pub fn lower01() -> Matrix {
    Matrix::from_real_rows(&[vec![qi(0), qi(1)], vec![qi(0), qi(0)]])
}

// ---------------------------------------------------------------------------
// Terminals, annotations, report trait, universe
// ---------------------------------------------------------------------------

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Terminal {
    ReportCollision,
    LiftBudgetExhaustion,
    OverlapGluingRefusal,
    TrajectoryExhaustedNoTerminal,
}
impl Terminal {
    pub fn label(&self) -> &'static str {
        match self {
            Terminal::ReportCollision => "REPORT_COLLISION",
            Terminal::LiftBudgetExhaustion => "LIFT_BUDGET_EXHAUSTION",
            Terminal::OverlapGluingRefusal => "OVERLAP_GLUING_REFUSAL",
            Terminal::TrajectoryExhaustedNoTerminal => "TRAJECTORY_EXHAUSTED_NO_TERMINAL",
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Annotation {
    DecouplingDetected { reason: String },
    TwoSignalCollapse,
}

pub trait Report {
    type Carrier: Eq + std::hash::Hash + Clone + std::fmt::Debug;
    fn report(&self, rho: &Matrix) -> Self::Carrier;
}

pub struct QuantumRelationalUniverse {
    pub dim: usize,
    pub povm: Vec<Matrix>,
}
impl QuantumRelationalUniverse {
    pub fn new(dim: usize, povm: Vec<Matrix>) -> Self {
        let mut s = Matrix::zeros(dim, dim);
        for e in &povm {
            s = s.add(e);
        }
        assert_eq!(s, Matrix::identity(dim), "POVM effects do not sum to I");
        Self { dim, povm }
    }
    pub fn profile(&self, rho: &Matrix) -> Vec<Q> {
        self.povm
            .iter()
            .map(|e| {
                let t = rho.matmul(e).trace();
                assert!(t.im.is_zero(), "Tr(rho E) not real");
                t.re
            })
            .collect()
    }
    /// N+1 <= M+1 under the modal quantizer (Round 1 Theorem Q.1).
    pub fn report_horizon_bound(&self) -> usize {
        self.povm.len() + 1
    }
}
impl Report for QuantumRelationalUniverse {
    type Carrier = usize; // modal quantizer: first argmax
    fn report(&self, rho: &Matrix) -> usize {
        let p = self.profile(rho);
        let mx = p.iter().max().expect("empty POVM").clone();
        p.iter().position(|v| *v == mx).unwrap()
    }
}

// ---------------------------------------------------------------------------
// Channels, purity monitor, trajectory evaluators
// ---------------------------------------------------------------------------

pub struct KrausChannel {
    pub kraus: Vec<Matrix>,
    /// Fresh ancilla qubits consumed (declared cost, assumption A-LIFT).
    pub cost: u32,
}
impl KrausChannel {
    pub fn unitary(u: Matrix) -> Self {
        KrausChannel { kraus: vec![u], cost: 0 }
    }
    pub fn apply(&self, rho: &Matrix) -> Matrix {
        let mut out = Matrix::zeros(rho.n, rho.m);
        for a in &self.kraus {
            out = out.add(&a.matmul(rho).matmul(&a.dagger()));
        }
        out
    }
    fn dim(&self) -> usize {
        self.kraus[0].m
    }
    pub fn is_tp(&self) -> bool {
        let d = self.dim();
        let mut s = Matrix::zeros(d, d);
        for a in &self.kraus {
            s = s.add(&a.dagger().matmul(a));
        }
        s == Matrix::identity(d)
    }
    pub fn is_unital(&self) -> bool {
        let d = self.kraus[0].n;
        let mut s = Matrix::zeros(d, d);
        for a in &self.kraus {
            s = s.add(&a.matmul(&a.dagger()));
        }
        s == Matrix::identity(d)
    }
}

/// Round 2 Lemma Q.3 checker: P2 must be non-increasing across unital steps.
#[derive(Default)]
pub struct PurityMonitor {
    pub history: Vec<Q>,
}
impl PurityMonitor {
    pub fn observe(&mut self, rho: &Matrix, ch_unital: bool) {
        let p = rho.purity_p2();
        if let Some(last) = self