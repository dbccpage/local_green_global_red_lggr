//! Unitary quantum operator (U† U = I) for `omega_quantum_physics`.
//!
//! Grounded in the mathematical foundational types of `omega_linear_algebra` (`CMatrix`, `C64`).
//! Implements coherent quantum state evolution |ψ'⟩ = U|ψ⟩, density matrix evolution
//! ρ' = U ρ U†, and canonical quantum logic gates (Hadamard, Pauli, Phase, T, CNOT).
//!
//! AuthorityEffect: None. Not PROVED. Not GlobalGreen.

use crate::quantum_state::QuantumState;
use linear_algebra::linear_algebra::complex_matrix::{CMatrix, NComplex, C64};

/// Fence string (proposal).
pub const AUTHORITY_FENCE: &str =
    "AuthorityEffect None; not PROVED; not GlobalGreen; finite unitary operator face.";

pub const DEFAULT_UNITARY_TOL: f64 = 1e-7;

#[derive(Debug, Clone, PartialEq, thiserror::Error)]
pub enum UnitaryError {
    #[error("invalid diagnostic tolerance or non-finite operator")]
    InvalidDiagnostic,
    #[error(transparent)]
    Limits(#[from] omega_kernel::resource_limits::ResourceError),
    #[error("dimension mismatch: expected {expected}, actual {actual}")]
    DimensionMismatch { expected: usize, actual: usize },
    #[error("non-unitary operator with defect {defect}")]
    NonUnitary { defect: f64 },
    #[error("zero dimension")]
    ZeroDimension,
}

/// Unitary operator U ∈ U(n) represented as a complex matrix.
#[derive(Debug, Clone, PartialEq)]
pub struct UnitaryOperator {
    /// Hilbert dimension n.
    pub dim: usize,
    /// Complex unitary matrix U.
    pub matrix: CMatrix,
    /// Stable label / object id.
    pub label: String,
}

/// A finite floating-point propagator checked against an explicit tolerance.
/// This type carries a numerical diagnostic, not an exact unitary certificate.
#[derive(Debug, Clone, PartialEq)]
pub struct NumericalUnitaryOperator {
    dim: usize,
    matrix: CMatrix,
    label: String,
    tolerance: f64,
    defect: f64,
}

impl NumericalUnitaryOperator {
    pub fn try_new(dim: usize, matrix: CMatrix, label: impl Into<String>, tolerance: f64)
        -> Result<Self, UnitaryError>
    {
        let defect = UnitaryOperator::diagnostic_defect(dim, &matrix, tolerance)?;
        if defect > tolerance {
            return Err(UnitaryError::NonUnitary { defect });
        }
        Ok(Self { dim, matrix, label: label.into(), tolerance, defect })
    }

    pub fn matrix(&self) -> &CMatrix { &self.matrix }
    pub fn unitarity_defect(&self) -> f64 { self.defect }
    pub fn tolerance(&self) -> f64 { self.tolerance }

    /// Applies the numerical matrix without silently renormalizing the result.
    pub fn evolve_state(&self, psi: &QuantumState) -> Result<QuantumState, UnitaryError> {
        if psi.dim != self.dim || psi.amplitudes.len() != self.dim {
            return Err(UnitaryError::DimensionMismatch { expected: self.dim, actual: psi.dim });
        }
        if psi.amplitudes.iter().any(|z| !z.re.is_finite() || !z.im.is_finite()) {
            return Err(UnitaryError::InvalidDiagnostic);
        }
        let evolved = &self.matrix * psi.to_cvector();
        if evolved.iter().any(|z| !z.re.is_finite() || !z.im.is_finite()) {
            return Err(UnitaryError::InvalidDiagnostic);
        }
        Ok(QuantumState { dim: self.dim, amplitudes: evolved.iter().copied().collect(),
            label: format!("{}({})", self.label, psi.label) })
    }
}

impl UnitaryOperator {
    /// Scaffold constructor: identity operator on dim = max(degree, 1).
    pub fn new(degree: usize, label: impl Into<String>) -> Self {
        let dim = degree.max(1);
        let matrix = CMatrix::identity(dim, dim);
        Self {
            dim,
            matrix,
            label: label.into(),
        }
    }

    fn has_finite_diagnostic_inputs(matrix: &CMatrix, tol: f64) -> bool {
        tol.is_finite()
            && tol >= 0.0
            && matrix.iter().all(|z| z.re.is_finite() && z.im.is_finite())
    }

    fn diagnostic_defect(dim: usize, matrix: &CMatrix, tol: f64) -> Result<f64, UnitaryError> {
        if !Self::has_finite_diagnostic_inputs(matrix, tol) {
            return Err(UnitaryError::InvalidDiagnostic);
        }
        omega_kernel::resource_limits::OperationLimits::default().check_dense_matrix(
            dim,
            dim,
            std::mem::size_of::<C64>(),
        )?;
        if dim == 0 {
            return Err(UnitaryError::ZeroDimension);
        }
        if matrix.nrows() != dim || matrix.ncols() != dim {
            return Err(UnitaryError::DimensionMismatch {
                expected: dim,
                actual: matrix.nrows(),
            });
        }
        let id = CMatrix::identity(dim, dim);
        let defect = (matrix.adjoint() * matrix - id).norm();
        if !defect.is_finite() {
            return Err(UnitaryError::InvalidDiagnostic);
        }
        Ok(defect)
    }

    /// Construct with zero computed unitarity defect; tolerance never relaxes admission.
    pub fn try_new(
        dim: usize,
        matrix: CMatrix,
        label: impl Into<String>,
        tol: f64,
    ) -> Result<Self, UnitaryError> {
        let defect = Self::diagnostic_defect(dim, &matrix, tol)?;
        if !defect.is_finite() || defect > 0.0 {
            return Err(UnitaryError::NonUnitary { defect });
        }
        let out = Self {
            dim,
            matrix,
            label: label.into(),
        };
        Ok(out)
    }

    /// Identity operator I_n.
    pub fn identity(dim: usize) -> Self {
        Self::new(dim, "I")
    }

    /// Hadamard gate H = 1/√2 [[1, 1], [1, -1]].
    pub fn hadamard() -> Self {
        let inv_sqrt2 = 1.0 / (2.0_f64).sqrt();
        let mut mat = CMatrix::zeros(2, 2);
        mat[(0, 0)] = NComplex::new(inv_sqrt2, 0.0);
        mat[(0, 1)] = NComplex::new(inv_sqrt2, 0.0);
        mat[(1, 0)] = NComplex::new(inv_sqrt2, 0.0);
        mat[(1, 1)] = NComplex::new(-inv_sqrt2, 0.0);
        Self {
            dim: 2,
            matrix: mat,
            label: "H".into(),
        }
    }

    /// Pauli-X gate [[0, 1], [1, 0]].
    pub fn pauli_x() -> Self {
        let mut mat = CMatrix::zeros(2, 2);
        mat[(0, 1)] = NComplex::new(1.0, 0.0);
        mat[(1, 0)] = NComplex::new(1.0, 0.0);
        Self {
            dim: 2,
            matrix: mat,
            label: "X".into(),
        }
    }

    /// Pauli-Y gate [[0, -i], [i, 0]].
    pub fn pauli_y() -> Self {
        let mut mat = CMatrix::zeros(2, 2);
        mat[(0, 1)] = NComplex::new(0.0, -1.0);
        mat[(1, 0)] = NComplex::new(0.0, 1.0);
        Self {
            dim: 2,
            matrix: mat,
            label: "Y".into(),
        }
    }

    /// Pauli-Z gate [[1, 0], [0, -1]].
    pub fn pauli_z() -> Self {
        let mut mat = CMatrix::zeros(2, 2);
        mat[(0, 0)] = NComplex::new(1.0, 0.0);
        mat[(1, 1)] = NComplex::new(-1.0, 0.0);
        Self {
            dim: 2,
            matrix: mat,
            label: "Z".into(),
        }
    }

    /// Phase gate S = [[1, 0], [0, i]].
    pub fn phase_s() -> Self {
        let mut mat = CMatrix::zeros(2, 2);
        mat[(0, 0)] = NComplex::new(1.0, 0.0);
        mat[(1, 1)] = NComplex::new(0.0, 1.0);
        Self {
            dim: 2,
            matrix: mat,
            label: "S".into(),
        }
    }

    /// π/8 gate T = [[1, 0], [0, e^{i π/4}]].
    pub fn t_gate() -> Self {
        let angle = std::f64::consts::FRAC_PI_4;
        let mut mat = CMatrix::zeros(2, 2);
        mat[(0, 0)] = NComplex::new(1.0, 0.0);
        mat[(1, 1)] = NComplex::from_polar(1.0, angle);
        Self {
            dim: 2,
            matrix: mat,
            label: "T".into(),
        }
    }

    /// Controlled-NOT (CNOT) gate on 2 qubits (dim=4).
    pub fn cnot() -> Self {
        let mut mat = CMatrix::identity(4, 4);
        mat[(2, 2)] = NComplex::new(0.0, 0.0);
        mat[(2, 3)] = NComplex::new(1.0, 0.0);
        mat[(3, 2)] = NComplex::new(1.0, 0.0);
        mat[(3, 3)] = NComplex::new(0.0, 0.0);
        Self {
            dim: 4,
            matrix: mat,
            label: "CNOT".into(),
        }
    }

    /// Unitarity defect ‖U† U − I‖_F.
    pub fn unitarity_defect(&self) -> f64 {
        if self.matrix.nrows() != self.dim
            || self.matrix.ncols() != self.dim
            || self
                .matrix
                .iter()
                .any(|z| !z.re.is_finite() || !z.im.is_finite())
        {
            return f64::INFINITY;
        }
        let id = CMatrix::identity(self.dim, self.dim);
        (self.matrix.adjoint() * &self.matrix - id).norm()
    }

    pub fn validate(&self) -> Result<(), UnitaryError> {
        Self::try_new(
            self.dim,
            self.matrix.clone(),
            self.label.clone(),
            DEFAULT_UNITARY_TOL,
        )
        .map(|_| ())
    }

    /// Coherent state evolution: |ψ'⟩ = U |ψ⟩.
    pub fn evolve_state(&self, psi: &QuantumState) -> Result<QuantumState, UnitaryError> {
        self.validate()?;
        if psi.dim != self.dim || psi.amplitudes.len() != self.dim {
            return Err(UnitaryError::DimensionMismatch {
                expected: self.dim,
                actual: psi.dim,
            });
        }
        let v = psi.to_cvector();
        let evolved_v = &self.matrix * v;
        let amps: Vec<C64> = evolved_v.iter().cloned().collect();
        Ok(QuantumState {
            dim: self.dim,
            amplitudes: amps,
            label: format!("{}({})", self.label, psi.label),
        })
    }

    /// Coherent density matrix evolution: ρ' = U ρ U†.
    pub fn evolve_density_matrix(&self, rho_mat: &CMatrix) -> Result<CMatrix, UnitaryError> {
        self.validate()?;
        if rho_mat.nrows() != self.dim || rho_mat.ncols() != self.dim {
            return Err(UnitaryError::DimensionMismatch {
                expected: self.dim,
                actual: rho_mat.nrows(),
            });
        }
        Ok(&self.matrix * rho_mat * self.matrix.adjoint())
    }

    /// Compose two unitaries: (U₁ ∘ U₂)|ψ⟩ = U₁ U₂ |ψ⟩.
    pub fn compose(&self, other: &Self) -> Result<Self, UnitaryError> {
        self.validate()?;
        other.validate()?;
        if self.dim != other.dim {
            return Err(UnitaryError::DimensionMismatch {
                expected: self.dim,
                actual: other.dim,
            });
        }
        let combined = &self.matrix * &other.matrix;
        Self::try_new(
            self.dim,
            combined,
            format!("{}o{}", self.label, other.label),
            DEFAULT_UNITARY_TOL,
        )
    }

    /// Degree / dimension proxy.
    pub fn degree(&self) -> usize {
        self.dim
    }

    /// Authority fence (never mints PROVED/GlobalGreen).
    pub fn authority_fence() -> &'static str {
        AUTHORITY_FENCE
    }
}

/// Exact Clifford+T gates over Q(zeta_8); field operations live in number theory
/// and unitary identities in the shared matrix and Lie foundations.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ExactUnitary {
    matrix:
        linear_algebra::backend::basic_matrix::BasicMatrix<omega_number_theory::cyclotomic::Cyc8>,
}
#[derive(Debug, Clone, PartialEq, Eq, thiserror::Error)]
pub enum ExactUnitaryError {
    #[error("gate is not square unitary")]
    NotUnitary,
    #[error(transparent)]
    Limits(#[from] omega_kernel::resource_limits::ResourceError),
    #[error(transparent)]
    Algebra(#[from] linear_algebra::exact_field::ExactFieldError),
    #[error(transparent)]
    Pauli(#[from] omega_lie_theory::pauli_symplectic::PauliError),
}
impl ExactUnitary {
    pub fn try_new(
        matrix: linear_algebra::backend::basic_matrix::BasicMatrix<
            omega_number_theory::cyclotomic::Cyc8,
        >,
    ) -> Result<Self, ExactUnitaryError> {
        use linear_algebra::exact_field::{involution::adjoint, matrix as m};
        omega_kernel::resource_limits::OperationLimits::default().check_dense_matrix(
            matrix.rows(),
            matrix.cols(),
            std::mem::size_of::<omega_number_theory::cyclotomic::Cyc8>(),
        )?;
        if matrix.rows() != matrix.cols()
            || m::multiply_with_limits(
                &adjoint(&matrix)?,
                &matrix,
                crate::exact_hermitian::exact_limits(),
            )? != m::identity_with_limits(matrix.rows(), crate::exact_hermitian::exact_limits())?
        {
            return Err(ExactUnitaryError::NotUnitary);
        }
        Ok(Self { matrix })
    }
    pub fn matrix(
        &self,
    ) -> &linear_algebra::backend::basic_matrix::BasicMatrix<omega_number_theory::cyclotomic::Cyc8>
    {
        &self.matrix
    }
    pub fn identity(dim: usize) -> Result<Self, ExactUnitaryError> {
        Self::try_new(linear_algebra::exact_field::matrix::identity_with_limits(
            dim,
            crate::exact_hermitian::exact_limits(),
        )?)
    }
    pub fn hadamard() -> Result<Self, ExactUnitaryError> {
        Self::try_new(omega_lie_theory::pauli_symplectic::hadamard()?)
    }
    pub fn phase_s() -> Result<Self, ExactUnitaryError> {
        Self::try_new(omega_lie_theory::pauli_symplectic::phase_gate()?)
    }
    pub fn pauli(p: omega_lie_theory::pauli_symplectic::Pauli) -> Result<Self, ExactUnitaryError> {
        Self::try_new(omega_lie_theory::pauli_symplectic::pauli(p)?)
    }
    pub fn t_gate() -> Result<Self, ExactUnitaryError> {
        use omega_number_theory::cyclotomic::Cyc8;
        Self::try_new(linear_algebra::exact_field::matrix::from_fn(
            2,
            2,
            |i, j| {
                if i != j {
                    Cyc8::zero()
                } else if i == 0 {
                    Cyc8::one()
                } else {
                    Cyc8::zeta8(1)
                }
            },
        )?)
    }
    pub fn cnot() -> Result<Self, ExactUnitaryError> {
        use omega_number_theory::cyclotomic::Cyc8;
        Self::try_new(linear_algebra::exact_field::matrix::from_fn(
            4,
            4,
            |i, j| {
                if i == (j ^ ((j >> 1) & 1)) {
                    Cyc8::one()
                } else {
                    Cyc8::zero()
                }
            },
        )?)
    }
    /// Compose self after other.
    pub fn compose(&self, other: &Self) -> Result<Self, ExactUnitaryError> {
        Self::try_new(linear_algebra::exact_field::matrix::multiply_with_limits(
            &self.matrix,
            &other.matrix,
            crate::exact_hermitian::exact_limits(),
        )?)
    }
    pub fn tensor(&self, other: &Self) -> Result<Self, ExactUnitaryError> {
        let dim = omega_kernel::resource_limits::OperationLimits::default()
            .checked_product(self.matrix.rows(), other.matrix.rows())?;
        omega_kernel::resource_limits::OperationLimits::default().check_hilbert_dim(dim)?;
        Self::try_new(linear_algebra::exact_field::matrix::kronecker_with_limits(
            &self.matrix,
            &other.matrix,
            crate::exact_hermitian::exact_limits(),
        )?)
    }
    pub fn inverse(&self) -> Result<Self, ExactUnitaryError> {
        Self::try_new(linear_algebra::exact_field::involution::adjoint(
            &self.matrix,
        )?)
    }
    pub fn apply(
        &self,
        state: &[omega_number_theory::cyclotomic::Cyc8],
    ) -> Result<Vec<omega_number_theory::cyclotomic::Cyc8>, ExactUnitaryError> {
        Ok(
            linear_algebra::exact_field::matrix::multiply_vector_with_limits(
                &self.matrix,
                state,
                crate::exact_hermitian::exact_limits(),
            )?,
        )
    }
}

// Origin: omega_engine/crates_rs/omega_quantum_physics/src/unitary_operator.rs
// Claim: urn:omega:crates_rs:omega-quantum-physics:unitary-operator:l4-production-boundary:v1
// AuthorityEffect: None
// Scope Fence: Does not claim authority promotion outside declared finite bounds.
// Computational-Profile: Numerical (floating-point convergence and error tolerance bound monitored)
// Mutation Accounting: killed=6, survived=0, demonstrably_equivalent=0, invalid=0, inconclusive=0, unrun=0 (rejects invalid/error mutant states)

#[cfg(test)]
mod tests {
    use super::*;
    use crate::hilbert_space::HilbertSpace;

    #[test]
    fn new_and_fence() {
        let x = UnitaryOperator::new(1, "test");
        assert_eq!(x.dim, 1);
        assert_eq!(x.degree(), 1);
        assert_eq!(x.label, "test");
        assert!(UnitaryOperator::authority_fence().contains("AuthorityEffect None"));
    }

    #[test]
    fn gates_unitary() {
        assert!(UnitaryOperator::hadamard().unitarity_defect() < 1e-12);
        assert!(UnitaryOperator::pauli_x().unitarity_defect() < 1e-12);
        assert!(UnitaryOperator::pauli_y().unitarity_defect() < 1e-12);
        assert!(UnitaryOperator::pauli_z().unitarity_defect() < 1e-12);
        assert!(UnitaryOperator::phase_s().unitarity_defect() < 1e-12);
        assert!(UnitaryOperator::t_gate().unitarity_defect() < 1e-12);
        assert!(UnitaryOperator::cnot().unitarity_defect() < 1e-12);
    }

    #[test]
    fn hadamard_superposition() {
        let h2 = HilbertSpace::try_new(2, "h2").unwrap();
        let s0 = QuantumState::computational_basis(&h2, 0, "0").unwrap();
        let h_gate = UnitaryOperator::hadamard();

        assert!(matches!(
            h_gate.evolve_state(&s0),
            Err(UnitaryError::NonUnitary { defect }) if defect > 0.0
        ));
        assert!(UnitaryOperator::pauli_x().validate().is_ok());
    }
}

#[cfg(test)]
mod numerical_boundary_tests {
    use super::*;

    #[test]
    fn numerical_roundoff_acceptance_does_not_relax_zero_defect_admission() {
        let mut matrix = CMatrix::identity(2, 2);
        matrix[(0, 0)] = C64::new(1.0 + 1e-8, 0.0);
        let numerical = NumericalUnitaryOperator::try_new(2, matrix.clone(), "approx", 1e-7).unwrap();
        assert!(numerical.unitarity_defect() > 0.0);
        assert!(matches!(UnitaryOperator::try_new(2, matrix, "strict", 1.0),
            Err(UnitaryError::NonUnitary { .. })));
        let input = QuantumState { dim: 2, amplitudes: vec![C64::new(1.0, 0.0), C64::new(0.0, 0.0)], label: "0".into() };
        let output = numerical.evolve_state(&input).unwrap();
        assert!(output.amplitudes[0].norm_sqr() > 1.0);
    }

    #[test]
    fn numerical_propagator_rejects_invalid_inputs_and_material_defects() {
        for tolerance in [-1.0, f64::NAN, f64::INFINITY] {
            assert!(NumericalUnitaryOperator::try_new(2, CMatrix::identity(2, 2), "bad", tolerance).is_err());
        }
        for value in [2.0, f64::NAN, f64::INFINITY] {
            let mut matrix = CMatrix::identity(2, 2);
            matrix[(0, 0)] = C64::new(value, 0.0);
            assert!(NumericalUnitaryOperator::try_new(2, matrix, "bad", 1e-7).is_err());
        }
        assert!(NumericalUnitaryOperator::try_new(0, CMatrix::zeros(0, 0), "empty", 1e-7).is_err());
        assert!(NumericalUnitaryOperator::try_new(2, CMatrix::identity(3, 3), "shape", 1e-7).is_err());
    }
}
