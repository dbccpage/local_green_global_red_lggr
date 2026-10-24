//! Exact L1 distance from a point to the convex hull of rational generators.

use num_traits::{One, Signed, Zero};
use omega_solvers::solver_lp_standard_form::{StandardLp, StandardLpError, StandardLpSolution};

use super::{EmpiricalError, MAX_LP_ENTRIES, Q};

/// Receipt of `min ||G p - t||_1` over the probability simplex: the L1
/// distance of `t` from the convex hull of the columns of `G`.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct L1DefectReceipt {
    pub defect: Q,
    pub coefficients: Vec<Q>,
    pub residual: Vec<Q>,
    /// `phi*` with `G^T phi* + y0 <= 0` coordinatewise, sup-norm at most one,
    /// and `t . phi* + y0` equal to the defect: zero duality gap.
    pub dual_witness: Vec<Q>,
    pub dual_offset: Q,
    /// The standard-form solution over `(p, u, v)`. Replay rebuilds the LP,
    /// verifies `primal`, `dual` and `value` and binds `p` to `coefficients`
    /// and the dual to `(dual_witness, dual_offset)`. `lp.pivots` is a trace
    /// and is not bound by replay.
    pub lp: StandardLpSolution,
}

pub(super) fn dot(a: &[Q], b: &[Q]) -> Q {
    a.iter().zip(b).map(|(x, y)| x * y).sum()
}

pub(super) fn too_large() -> EmpiricalError {
    EmpiricalError::LpSizeLimit {
        limit: MAX_LP_ENTRIES,
    }
}

/// Refuse a dense rational matrix of more than [`MAX_LP_ENTRIES`] entries
/// before it is allocated; the product itself is checked, never wrapped.
pub(super) fn bound_dense(rows: usize, columns: usize) -> Result<(), EmpiricalError> {
    match rows.checked_mul(columns) {
        Some(entries) if entries <= MAX_LP_ENTRIES => Ok(()),
        _ => Err(too_large()),
    }
}

/// Variables `(p, u, v)`, rows `G p - u + v = t` and `sum p = 1`, cost `sum u + sum v`.
fn standard_form_l1(generators: &[Vec<Q>], target: &[Q]) -> Result<StandardLp, EmpiricalError> {
    let (k, m) = (generators.len(), target.len());
    let width = m
        .checked_mul(2)
        .and_then(|twice| twice.checked_add(k))
        .ok_or_else(too_large)?;
    bound_dense(m.checked_add(1).ok_or_else(too_large)?, width)?;
    let mut rows = Vec::with_capacity(m + 1);
    for i in 0..m {
        let mut row = vec![Q::zero(); width];
        for (j, column) in generators.iter().enumerate() {
            row[j] = column[i].clone();
        }
        row[k + i] = -Q::one();
        row[k + m + i] = Q::one();
        rows.push(row);
    }
    let mut rhs = target.to_vec();
    let mut row = vec![Q::zero(); width];
    for slot in row.iter_mut().take(k) {
        *slot = Q::one();
    }
    rows.push(row);
    rhs.push(Q::one());
    let costs = (0..width)
        .map(|j| if j >= k { Q::one() } else { Q::zero() })
        .collect();
    Ok(StandardLp::new(costs, rows, rhs)?)
}

/// Exact `min_p ||G p - t||_1` over the probability simplex, returning the
/// primal minimiser and the dual witness with zero duality gap. This is the
/// L1 distance from a convex hull, not the cochain quotient `Phi_1`, which
/// [`EmpiricalModel::cech_quotient_defect`] delegates to its owner.
pub fn l1_distance_to_convex_hull(
    generators: &[Vec<Q>],
    target: &[Q],
    pivots: usize,
) -> Result<L1DefectReceipt, EmpiricalError> {
    let (k, m) = (generators.len(), target.len());
    if k == 0 || generators.iter().any(|g| g.len() != m) {
        return Err(EmpiricalError::Shape);
    }
    let lp = standard_form_l1(generators, target)?;
    let solution = lp.solve(pivots)?;
    if !lp.verify(&solution) {
        return Err(EmpiricalError::Lp(StandardLpError::CertificateMismatch));
    }
    let coefficients: Vec<Q> = solution.primal[..k].to_vec();
    let residual: Vec<Q> = (0..m)
        .map(|i| {
            generators
                .iter()
                .zip(&coefficients)
                .map(|(g, c)| &g[i] * c)
                .sum::<Q>()
                - &target[i]
        })
        .collect();
    let receipt = L1DefectReceipt {
        defect: solution.value.clone(),
        coefficients,
        residual,
        dual_witness: solution.dual[..m].to_vec(),
        dual_offset: solution.dual[m].clone(),
        lp: solution,
    };
    if verify_l1_defect_receipt(generators, target, &receipt) {
        Ok(receipt)
    } else {
        Err(EmpiricalError::Lp(StandardLpError::CertificateMismatch))
    }
}

/// Independent replay: the LP certificate, the residual, the sup-norm bound,
/// the kernel (or offset) condition and the zero duality gap are all re-checked.
pub fn verify_l1_defect_receipt(
    generators: &[Vec<Q>],
    target: &[Q],
    receipt: &L1DefectReceipt,
) -> bool {
    let (k, m) = (generators.len(), target.len());
    if receipt.coefficients.len() != k
        || receipt.residual.len() != m
        || receipt.dual_witness.len() != m
        || generators.iter().any(|g| g.len() != m)
    {
        return false;
    }
    let Ok(lp) = standard_form_l1(generators, target) else {
        return false;
    };
    if !lp.verify(&receipt.lp) || receipt.lp.value != receipt.defect {
        return false;
    }
    let subrecord_bound = receipt.lp.primal.len() == k + 2 * m
        && receipt.lp.dual.len() == m + 1
        && receipt.lp.primal[..k] == receipt.coefficients[..]
        && receipt.lp.dual[..m] == receipt.dual_witness[..]
        && receipt.lp.dual[m] == receipt.dual_offset;
    if !subrecord_bound {
        return false;
    }
    let residual_ok = (0..m).all(|i| {
        let combination: Q = generators
            .iter()
            .zip(&receipt.coefficients)
            .map(|(g, c)| &g[i] * c)
            .sum();
        combination - &target[i] == receipt.residual[i]
    });
    let coefficients_ok = receipt.coefficients.iter().all(|c| !c.is_negative())
        && receipt.coefficients.iter().sum::<Q>() == Q::one();
    let sup_norm_ok = receipt.dual_witness.iter().all(|y| y.abs() <= Q::one());
    let adjoint_ok = generators
        .iter()
        .all(|g| dot(g, &receipt.dual_witness) + &receipt.dual_offset <= Q::zero());
    let gap_zero = dot(target, &receipt.dual_witness) + &receipt.dual_offset == receipt.defect
        && omega_functional::Phi1Functional::unweighted_l1_rational(&receipt.residual).as_ref()
            == Some(&receipt.defect);
    residual_ok && coefficients_ok && sup_norm_ok && adjoint_ok && gap_zero
}
