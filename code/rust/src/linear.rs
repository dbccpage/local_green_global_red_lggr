//! Exact rational linear algebra, weighted-l1 repair certificates and 1-cochain classification.

use crate::{q, q_from_json, Q};
use num_traits::{Signed, Zero};
use serde_json::Value;

pub type Vector = Vec<Q>;
pub type Matrix = Vec<Vec<Q>>;

pub fn vector_from_json(v: &Value) -> Result<Vector, String> {
    v.as_array().ok_or("expected array")?.iter().map(q_from_json).collect()
}

/// A matrix from JSON. An empty array is allowed and returns zero rows.
pub fn matrix_from_json(v: &Value) -> Result<Matrix, String> {
    let rows: Matrix = v.as_array().ok_or("expected array")?.iter().map(vector_from_json).collect::<Result<_, _>>()?;
    if let Some(w) = rows.first().map(|r| r.len()) {
        if w == 0 || rows.iter().any(|r| r.len() != w) {
            return Err("matrix must be rectangular with at least one column".into());
        }
    }
    Ok(rows)
}

pub fn cols(a: &Matrix) -> usize {
    a.first().map(|r| r.len()).unwrap_or(0)
}

pub fn matvec(a: &Matrix, x: &[Q]) -> Vector {
    a.iter().map(|row| row.iter().zip(x).map(|(c, v)| c * v).sum()).collect()
}

pub fn transpose(a: &Matrix) -> Matrix {
    (0..cols(a)).map(|j| a.iter().map(|r| r[j].clone()).collect()).collect()
}

pub fn matmul(a: &Matrix, b: &Matrix) -> Matrix {
    let bt = transpose(b);
    a.iter().map(|r| bt.iter().map(|c| r.iter().zip(c).map(|(x, y)| x * y).sum()).collect()).collect()
}

pub fn identity(n: usize) -> Matrix {
    (0..n).map(|i| (0..n).map(|j| if i == j { q(1) } else { q(0) }).collect()).collect()
}

pub fn sub(a: &Matrix, b: &Matrix) -> Matrix {
    a.iter().zip(b).map(|(r, s)| r.iter().zip(s).map(|(x, y)| x - y).collect()).collect()
}

pub fn is_zero(a: &Matrix) -> bool {
    a.iter().all(|r| r.iter().all(|v| v.is_zero()))
}

/// Rational Gaussian elimination; free variables set to zero. `None` means the
/// system is inconsistent over Q.
pub fn solve_exact(a: &Matrix, b: &[Q]) -> Option<Vector> {
    let m = a.len();
    let n = cols(a);
    let mut w: Vec<Vec<Q>> = a.iter().zip(b).map(|(r, v)| r.iter().cloned().chain([v.clone()]).collect()).collect();
    let mut pivots = Vec::new();
    let mut pr = 0;
    for c in 0..n {
        if pr == m {
            break;
        }
        let Some(ch) = (pr..m).find(|&r| !w[r][c].is_zero()) else { continue };
        w.swap(pr, ch);
        let p = w[pr][c].clone();
        for v in w[pr].iter_mut() {
            *v = &*v / &p;
        }
        for r in 0..m {
            if r != pr && !w[r][c].is_zero() {
                let f = w[r][c].clone();
                for k in 0..=n {
                    let t = &f * &w[pr][k];
                    w[r][k] = &w[r][k] - t;
                }
            }
        }
        pivots.push(c);
        pr += 1;
    }
    if w.iter().any(|r| r[..n].iter().all(|v| v.is_zero()) && !r[n].is_zero()) {
        return None;
    }
    let mut x = vec![q(0); n];
    for (r, c) in pivots.iter().enumerate() {
        x[*c] = w[r][n].clone();
    }
    Some(x)
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum L1Status {
    OptimalityVerified,
    LowerBoundVerified,
    InvalidCertificate,
}

#[derive(Debug, Clone)]
pub struct L1Check {
    pub status: L1Status,
    pub lower: Option<Q>,
    pub upper: Q,
    pub repair_impossible: bool,
}

/// Check supplied primal/dual evidence for min_x sum_e w_e |h_e - (D x)_e|.
/// Dual z with D^T z = 0 and |z_e| <= w_e gives the lower bound z.h (weak duality);
/// equality with the primal residual certifies the optimum.
pub fn verify_l1(d: &Matrix, h: &[Q], w: &[Q], x: &[Q], z: &[Q]) -> Result<L1Check, String> {
    if w.iter().any(|v| !v.is_positive()) {
        return Err("weights must be strictly positive".into());
    }
    if h.len() != d.len() || w.len() != d.len() || z.len() != d.len() || x.len() != cols(d) {
        return Err("dimension mismatch".into());
    }
    let dx = matvec(d, x);
    let upper: Q = h.iter().zip(&dx).zip(w).map(|((a, b), wt)| wt * (a - b).abs()).sum();
    let annihilates = matvec(&transpose(d), z).iter().all(|v| v.is_zero());
    let bounded = z.iter().zip(w).all(|(a, b)| a.abs() <= *b);
    let valid = annihilates && bounded;
    let lower: Q = z.iter().zip(h).map(|(a, b)| a * b).sum();
    let status = if valid && lower == upper {
        L1Status::OptimalityVerified
    } else if valid {
        L1Status::LowerBoundVerified
    } else {
        L1Status::InvalidCertificate
    };
    Ok(L1Check {
        repair_impossible: valid && lower.is_positive(),
        lower: valid.then_some(lower),
        upper,
        status,
    })
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CochainStatus {
    /// h = D0 x for some x.
    Exact,
    /// D1 h != 0: h is not even closed.
    ClosureFailure,
    /// D1 h = 0 and h is not in im D0: a nonzero class in H^1.
    ClosedNonexact,
    /// D1 D0 != 0: the supplied maps are not a complex.
    InvalidComplex,
}

/// Classify h in C^1 against C^0 --D0--> C^1 --D1--> C^2. An empty D1 declares C^2 = 0.
pub fn classify_cochain(d0: &Matrix, h: &[Q], d1: &Matrix) -> (CochainStatus, Option<Vector>) {
    let sol = solve_exact(d0, h);
    if !d1.is_empty() {
        if !is_zero(&matmul(d1, d0)) {
            return (CochainStatus::InvalidComplex, sol);
        }
        if matvec(d1, h).iter().any(|v| !v.is_zero()) {
            return (CochainStatus::ClosureFailure, sol);
        }
    }
    let st = if sol.is_some() { CochainStatus::Exact } else { CochainStatus::ClosedNonexact };
    (st, sol)
}
