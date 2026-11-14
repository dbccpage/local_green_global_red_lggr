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

/// (rows, cols) of a nonempty rectangular matrix; Err for ragged or empty input.
pub fn shape(a: &Matrix) -> Result<(usize, usize), String> {
    let n = cols(a);
    if a.is_empty() || n == 0 || a.iter().any(|r| r.len() != n) {
        return Err("matrix must be nonempty and rectangular".into());
    }
    Ok((a.len(), n))
}

/// Require exactly `rows` x `cols`.
pub fn expect_shape(a: &Matrix, rows: usize, cols_: usize, name: &str) -> Result<(), String> {
    let s = shape(a).map_err(|e| format!("{name}: {e}"))?;
    if s != (rows, cols_) {
        return Err(format!("{name} must be {rows}x{cols_}, got {}x{}", s.0, s.1));
    }
    Ok(())
}

/// A x. Errors unless A is rectangular and len(x) = cols(A); nothing is truncated.
pub fn matvec(a: &Matrix, x: &[Q]) -> Result<Vector, String> {
    let (_, n) = shape(a)?;
    if x.len() != n {
        return Err(format!("matvec: {n} columns but vector of length {}", x.len()));
    }
    Ok(a.iter().map(|row| row.iter().zip(x).map(|(c, v)| c * v).sum()).collect())
}

pub fn transpose(a: &Matrix) -> Matrix {
    (0..cols(a)).map(|j| a.iter().map(|r| r[j].clone()).collect()).collect()
}

/// A B. Errors unless cols(A) = rows(B).
pub fn matmul(a: &Matrix, b: &Matrix) -> Result<Matrix, String> {
    let (_, n) = shape(a)?;
    let (m, _) = shape(b)?;
    if n != m {
        return Err(format!("matmul: {n} columns times {m} rows"));
    }
    let bt = transpose(b);
    Ok(a.iter().map(|r| bt.iter().map(|c| r.iter().zip(c).map(|(x, y)| x * y).sum()).collect()).collect())
}

pub fn identity(n: usize) -> Matrix {
    (0..n).map(|i| (0..n).map(|j| if i == j { q(1) } else { q(0) }).collect()).collect()
}

/// A - B. Errors unless the shapes are equal.
pub fn sub(a: &Matrix, b: &Matrix) -> Result<Matrix, String> {
    if shape(a)? != shape(b)? {
        return Err("sub: shapes differ".into());
    }
    Ok(a.iter().zip(b).map(|(r, s)| r.iter().zip(s).map(|(x, y)| x - y).collect()).collect())
}

pub fn is_zero(a: &Matrix) -> bool {
    a.iter().all(|r| r.iter().all(|v| v.is_zero()))
}

/// Rank over Q by exact elimination.
pub fn rank(a: &Matrix) -> Result<usize, String> {
    let (m, n) = shape(a)?;
    let mut w = a.clone();
    let mut r = 0;
    for c in 0..n {
        let Some(p) = (r..m).find(|&i| !w[i][c].is_zero()) else { continue };
        w.swap(r, p);
        for i in (r + 1)..m {
            if !w[i][c].is_zero() {
                let f = &w[i][c] / &w[r][c];
                for k in c..n {
                    let t = &f * &w[r][k];
                    w[i][k] = &w[i][k] - t;
                }
            }
        }
        r += 1;
        if r == m {
            break;
        }
    }
    Ok(r)
}

/// Rational Gaussian elimination; free variables set to zero. `None` means the
/// system is inconsistent over Q.
///
/// Errors unless A is rectangular and len(b) = rows(A).
pub fn solve_exact(a: &Matrix, b: &[Q]) -> Result<Option<Vector>, String> {
    let (m, n) = shape(a)?;
    if b.len() != m {
        return Err(format!("solve_exact: {m} rows but right-hand side of length {}", b.len()));
    }
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
        return Ok(None);
    }
    let mut x = vec![q(0); n];
    for (r, c) in pivots.iter().enumerate() {
        x[*c] = w[r][n].clone();
    }
    Ok(Some(x))
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
    let (m, n) = shape(d)?;
    if h.len() != m || w.len() != m || z.len() != m || x.len() != n {
        return Err("dimension mismatch".into());
    }
    let dx = matvec(d, x)?;
    let upper: Q = h.iter().zip(&dx).zip(w).map(|((a, b), wt)| wt * (a - b).abs()).sum();
    let annihilates = matvec(&transpose(d), z)?.iter().all(|v| v.is_zero());
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
///
/// Errors (malformed input, never a verdict) unless D0 is rectangular, len(h) = dim C^1 = rows(D0)
/// and, when D1 is nonempty, cols(D1) = dim C^1.
pub fn classify_cochain(d0: &Matrix, h: &[Q], d1: &Matrix) -> Result<(CochainStatus, Option<Vector>), String> {
    let (c1, _) = shape(d0)?;
    if h.len() != c1 {
        return Err(format!("h has length {} but C^1 has dimension {c1}", h.len()));
    }
    if !d1.is_empty() {
        let (_, k) = shape(d1)?;
        if k != c1 {
            return Err(format!("D1 has {k} columns but C^1 has dimension {c1}"));
        }
    }
    let sol = solve_exact(d0, h)?;
    if !d1.is_empty() {
        if !is_zero(&matmul(d1, d0)?) {
            return Ok((CochainStatus::InvalidComplex, sol));
        }
        if matvec(d1, h)?.iter().any(|v| !v.is_zero()) {
            return Ok((CochainStatus::ClosureFailure, sol));
        }
    }
    let st = if sol.is_some() { CochainStatus::Exact } else { CochainStatus::ClosedNonexact };
    Ok((st, sol))
}
