//! General exact standard-form LP: min c.x with A x = b and x >= 0.
//! Two-phase Bland simplex proposes; independent primal/dual replay certifies.
//! Unlike free weighted-L1 projection, positivity constraints are retained.

use num_rational::BigRational as Q;
use num_traits::{One, Signed, Zero};
use thiserror::Error;

#[derive(Debug, Clone, PartialEq, Eq, Error)]
pub enum StandardLpError {
    #[error("LP dimensions or rational denominator are invalid")]
    InvalidInput,
    #[error("LP is infeasible")]
    Infeasible,
    #[error("LP objective is unbounded below")]
    Unbounded,
    #[error("declared simplex pivot budget exhausted")]
    BudgetExhausted,
    #[error("independent LP certificate verification failed")]
    CertificateMismatch,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct StandardLp {
    costs: Vec<Q>,
    matrix: Vec<Vec<Q>>,
    rhs: Vec<Q>,
}

/// Untrusted candidate: equality of values alone is never sufficient.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct StandardLpSolution {
    pub primal: Vec<Q>,
    pub dual: Vec<Q>,
    pub value: Q,
    pub pivots: usize,
}

fn canonical(value: Q) -> Result<Q, StandardLpError> {
    if value.denom().is_zero() {
        return Err(StandardLpError::InvalidInput);
    }
    Ok(Q::new(value.numer().clone(), value.denom().clone()))
}

fn dot(a: &[Q], b: &[Q]) -> Q {
    a.iter().zip(b).map(|(x, y)| x * y).sum()
}

fn pivot(tableau: &mut [Vec<Q>], row: usize, column: usize) {
    let scale = tableau[row][column].clone();
    for x in &mut tableau[row] {
        *x /= &scale;
    }
    let pivot_row = tableau[row].clone();
    for (i, other) in tableau.iter_mut().enumerate() {
        if i == row {
            continue;
        }
        let factor = other[column].clone();
        if !factor.is_zero() {
            for (x, y) in other.iter_mut().zip(&pivot_row) {
                *x -= &factor * y;
            }
        }
    }
}

fn simplex(
    tableau: &mut [Vec<Q>],
    basis: &mut [usize],
    eligible: usize,
    remaining: &mut usize,
) -> Result<(), StandardLpError> {
    let rhs = tableau[0].len() - 1;
    loop {
        let Some(entering) = (0..eligible).find(|&j| tableau[0][j].is_negative()) else {
            return Ok(());
        };
        let leaving = (1..tableau.len())
            .filter(|&i| tableau[i][entering].is_positive())
            .min_by_key(|&i| (&tableau[i][rhs] / &tableau[i][entering], basis[i - 1]));
        let Some(leaving) = leaving else {
            return Err(StandardLpError::Unbounded);
        };
        if *remaining == 0 {
            return Err(StandardLpError::BudgetExhausted);
        }
        *remaining -= 1;
        pivot(tableau, leaving, entering);
        basis[leaving - 1] = entering;
    }
}

impl StandardLp {
    pub fn new(costs: Vec<Q>, matrix: Vec<Vec<Q>>, rhs: Vec<Q>) -> Result<Self, StandardLpError> {
        if matrix.len() != rhs.len() || matrix.iter().any(|r| r.len() != costs.len()) {
            return Err(StandardLpError::InvalidInput);
        }
        Ok(Self {
            costs: costs.into_iter().map(canonical).collect::<Result<_, _>>()?,
            matrix: matrix
                .into_iter()
                .map(|row| row.into_iter().map(canonical).collect())
                .collect::<Result<_, _>>()?,
            rhs: rhs.into_iter().map(canonical).collect::<Result<_, _>>()?,
        })
    }

    pub fn costs(&self) -> &[Q] {
        &self.costs
    }
    pub fn matrix(&self) -> &[Vec<Q>] {
        &self.matrix
    }
    pub fn rhs(&self) -> &[Q] {
        &self.rhs
    }

    pub fn verify(&self, candidate: &StandardLpSolution) -> bool {
        let n = self.costs.len();
        let m = self.rhs.len();
        if candidate.primal.len() != n
            || candidate.dual.len() != m
            || candidate
                .primal
                .iter()
                .chain(&candidate.dual)
                .chain([&candidate.value])
                .any(|x| !x.denom().is_positive())
            || candidate.primal.iter().any(|x| x.is_negative())
        {
            return false;
        }
        self.matrix
            .iter()
            .zip(&self.rhs)
            .all(|(r, b)| dot(r, &candidate.primal) == *b)
            && (0..n).all(|j| {
                let pairing: Q = self
                    .matrix
                    .iter()
                    .zip(&candidate.dual)
                    .map(|(r, y)| &r[j] * y)
                    .sum();
                pairing <= self.costs[j]
            })
            && dot(&self.costs, &candidate.primal) == candidate.value
            && dot(&self.rhs, &candidate.dual) == candidate.value
    }

    pub fn solve(&self, max_pivots: usize) -> Result<StandardLpSolution, StandardLpError> {
        let (m, n) = (self.rhs.len(), self.costs.len());
        let signs: Vec<Q> = self
            .rhs
            .iter()
            .map(|b| if b.is_negative() { -Q::one() } else { Q::one() })
            .collect();
        let mut tableau = vec![vec![Q::zero(); n + m + 1]; m + 1];
        for i in 0..m {
            for j in 0..n {
                tableau[i + 1][j] = &signs[i] * &self.matrix[i][j];
            }
            tableau[i + 1][n + i] = Q::one();
            tableau[i + 1][n + m] = &signs[i] * &self.rhs[i];
        }
        for j in 0..n {
            tableau[0][j] = -(1..=m).map(|i| tableau[i][j].clone()).sum::<Q>();
        }
        tableau[0][n + m] = -(1..=m).map(|i| tableau[i][n + m].clone()).sum::<Q>();
        let mut basis: Vec<usize> = (n..n + m).collect();
        let mut remaining = max_pivots;
        simplex(&mut tableau, &mut basis, n, &mut remaining)?;
        if !tableau[0][n + m].is_zero() {
            return Err(StandardLpError::Infeasible);
        }
        for i in 1..=m {
            if basis[i - 1] >= n {
                if let Some(j) = (0..n).find(|&j| !tableau[i][j].is_zero()) {
                    if remaining == 0 {
                        return Err(StandardLpError::BudgetExhausted);
                    }
                    remaining -= 1;
                    pivot(&mut tableau, i, j);
                    basis[i - 1] = j;
                }
            }
        }
        let mut phase_two = vec![self.costs.clone()];
        phase_two[0].extend(vec![Q::zero(); m + 1]);
        let mut basis_two = Vec::new();
        for i in 1..=m {
            if basis[i - 1] < n {
                phase_two.push(tableau[i].clone());
                basis_two.push(basis[i - 1]);
            }
        }
        for (i, &variable) in basis_two.iter().enumerate() {
            let cost = phase_two[0][variable].clone();
            let row = phase_two[i + 1].clone();
            for (x, y) in phase_two[0].iter_mut().zip(row) {
                *x -= &cost * y;
            }
        }
        simplex(&mut phase_two, &mut basis_two, n, &mut remaining)?;
        let mut primal = vec![Q::zero(); n];
        for (i, &variable) in basis_two.iter().enumerate() {
            primal[variable] = phase_two[i + 1][n + m].clone();
        }
        let dual = (0..m).map(|i| -&signs[i] * &phase_two[0][n + i]).collect();
        let candidate = StandardLpSolution {
            primal,
            dual,
            value: -phase_two[0][n + m].clone(),
            pivots: max_pivots - remaining,
        };
        if !self.verify(&candidate) {
            return Err(StandardLpError::CertificateMismatch);
        }
        Ok(candidate)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn q(n: i64) -> Q {
        Q::from_integer(n.into())
    }
    #[test]
    fn exact_certificate_and_forged_dual() {
        let lp = StandardLp::new(vec![q(1), q(2)], vec![vec![q(1), q(1)]], vec![q(1)]).unwrap();
        let solution = lp.solve(100).unwrap();
        assert_eq!(solution.value, q(1));
        assert!(lp.verify(&solution));
        let mut forged = solution;
        forged.dual[0] = q(2);
        assert!(!lp.verify(&forged));
        forged.dual[0] = q(1);
        forged.value = Q::new_raw((-1).into(), (-1).into());
        assert!(!lp.verify(&forged));
    }
    #[test]
    fn infeasible_unbounded_and_budget_are_distinct() {
        let lp = StandardLp::new(vec![q(1)], vec![vec![q(1)]], vec![q(-1)]).unwrap();
        assert_eq!(lp.solve(10), Err(StandardLpError::Infeasible));
        let lp = StandardLp::new(vec![q(-1)], vec![], vec![]).unwrap();
        assert_eq!(lp.solve(10), Err(StandardLpError::Unbounded));
        let lp = StandardLp::new(vec![q(1)], vec![vec![q(1)]], vec![q(1)]).unwrap();
        assert_eq!(lp.solve(0), Err(StandardLpError::BudgetExhausted));
    }
    #[test]
    fn redundant_negative_rows_and_empty_program() {
        let lp = StandardLp::new(
            vec![q(3)],
            vec![vec![q(-1)], vec![q(2)], vec![q(0)]],
            vec![q(-2), q(4), q(0)],
        )
        .unwrap();
        let solution = lp.solve(100).unwrap();
        assert_eq!(solution.primal, vec![q(2)]);
        assert_eq!(solution.value, q(6));
        assert!(lp.verify(&solution));
        assert_eq!(
            StandardLp::new(vec![], vec![], vec![])
                .unwrap()
                .solve(0)
                .unwrap()
                .value,
            q(0)
        );
    }
}
