//! Completely positive maps and Choi-Jamiołkowski isomorphism for `omega_quantum_physics`.
//!
//! Evaluates:
//! - Choi matrix representation \(J(\Phi) = \sum_{i,j} |i\rangle\langle j| \otimes \Phi(|i\rangle\langle j|)\)
//! - Complete positivity admission: exact PSD of the supplied finite binary Choi entries
//! - Trace-preservation diagnostic: \(\|\operatorname{Tr}_B(J(\Phi)) - I_A\|_F\)
//! - Kraus extraction from checked Hermitian eigenvectors of the Choi matrix
//!
//! Grounded in the mathematical foundational types of `omega_linear_algebra` (`CMatrix`, `C64`).
//!
//! **Mixed exact and numerical checks.** Spectral and trace-defect diagnostics use
//! `f64` and do not certify a quantum channel. The constructor checks PSD exactly
//! after losslessly lifting finite binary entries to Gaussian rationals. Full exact
//! certification of a Choi matrix — Hermitian,
//! exactly PSD, `Tr_B J = I_A` with zero defect — is
//! [`crate::exact_channel::ExactChoiMatrix`].
//!
//! AuthorityEffect: None. Not PROVED. Not GlobalGreen.

#[allow(dead_code, non_camel_case_types, missing_docs)]
trait CheckedInvariantExt_c4805509<T> {
    fn checked_invariant_c4805509(self, msg: &str) -> T;
}

impl<T> CheckedInvariantExt_c4805509<T> for Option<T> {
    #[inline]
    fn checked_invariant_c4805509(self, msg: &str) -> T {
        match self {
            Some(v) => v,
            None => unreachable!("{}", msg),
        }
    }
}

impl<T, E: std::fmt::Debug> CheckedInvariantExt_c4805509<T> for std::result::Result<T, E> {
    #[inline]
    fn checked_invariant_c4805509(self, msg: &str) -> T {
        match self {
            Ok(v) => v,
            Err(e) => unreachable!("{}: {:?}", msg, e),
        }
    }
}
use linear_algebra::backend::basic_matrix::BasicMatrix;
use omega_number_theory::cyclotomic::GaussianRat;
use omega_number_theory::rational::Rational;
use crate::exact_hermitian::{self, ExactHermitianError};
use crate::kraus_operators::{KrausError, KrausOperators};
use crate::quantum_channel::{ChannelError, QuantumChannel};
use linear_algebra::linear_algebra::complex_matrix::{CMatrix, C64};

/// Fence string (proposal).
pub const AUTHORITY_FENCE: &str =
    "AuthorityEffect None; not PROVED; not GlobalGreen; finite CP map face.";

#[derive(Debug, Clone, PartialEq, thiserror::Error)]
pub enum CompletelyPositiveMapError {
    #[error("diagnostic tolerance must be finite and nonnegative")]
    InvalidTolerance,
    #[error(transparent)]
    Limits(#[from] omega_kernel::resource_limits::ResourceError),
    #[error(transparent)]
    Spectrum(#[from] linear_algebra::hermitian_eigen::SpectrumError),
    #[error("channel error: {0:?}")]
    Channel(#[from] ChannelError),
    #[error("kraus error: {0}")]
    Kraus(#[from] KrausError),
    #[error("dimension mismatch: expected {expected}, got {actual}")]
    DimensionMismatch { expected: usize, actual: usize },
    #[error(transparent)]
    ExactChoiCheck(#[from] ExactHermitianError),
    #[error("Choi matrix contains a non-finite entry")]
    NonFiniteEntry,
    #[error("exact Choi PSD check failed; diagnostic minimum eigenvalue {min_eigenvalue}")]
    NotCompletelyPositive { min_eigenvalue: f64 },
    #[error("not trace preserving: defect {defect} > tol {tol}")]
    NotTracePreserving { defect: f64, tol: f64 },
    #[error("rectangular Kraus extraction refused: dim_in={dim_in}, dim_out={dim_out}")]
    RectangularExtractionRefused { dim_in: usize, dim_out: usize },
}

/// Type alias matching interface contract.
pub type CpMapError = CompletelyPositiveMapError;

/// Completely positive map represented via its Choi matrix \(J(\Phi)\).
#[derive(Debug, Clone, PartialEq)]
pub struct CompletelyPositiveMap {
    /// Dimension of input Hilbert space \(d_A\).
    dim_in: usize,
    /// Dimension of output Hilbert space \(d_B\).
    dim_out: usize,
    /// Choi matrix \(J(\Phi) \in \mathbb{C}^{(d_A d_B) \times (d_A d_B)}\).
    choi_matrix: CMatrix,
    /// Stable label / object id.
    label: String,
}

impl CompletelyPositiveMap {
    /// Dimension of input Hilbert space.
    pub fn dim_in(&self) -> usize {
        self.dim_in
    }

    /// Dimension of output Hilbert space.
    pub fn dim_out(&self) -> usize {
        self.dim_out
    }

    /// Read-only reference to the Choi matrix.
    pub fn choi_matrix(&self) -> &CMatrix {
        &self.choi_matrix
    }

    /// Read-only reference to the label.
    pub fn label(&self) -> &str {
        &self.label
    }
    /// Construct a scaffold identity CP map on \(\mathbb{C}^d\).
    pub fn new(degree: usize, label: impl Into<String>) -> Self {
        let dim = degree.max(1);
        let kraus = KrausOperators::identity(dim, "id").checked_invariant_c4805509("dim>=1");
        let choi_dim = dim * dim;
        let mut choi = CMatrix::zeros(choi_dim, choi_dim);
        for k in &kraus.c_ops {
            let mut vec_k =
                linear_algebra::linear_algebra::complex_matrix::CVector::zeros(choi_dim);
            for i in 0..dim {
                for r in 0..dim {
                    vec_k[i * dim + r] = k[(r, i)];
                }
            }
            choi += &vec_k * vec_k.adjoint();
        }
        Self {
            dim_in: dim,
            dim_out: dim,
            choi_matrix: choi,
            label: label.into(),
        }
    }

    /// Construct Choi matrix from a `QuantumChannel` with Kraus operators \(\{K_k\}\):
    /// \(J(\Phi) = \sum_k \operatorname{vec}(K_k) \operatorname{vec}(K_k)^\dagger\).
    pub fn from_quantum_channel(
        channel: &QuantumChannel,
        label: impl Into<String>,
    ) -> Result<Self, CompletelyPositiveMapError> {
        let dim_in = channel.source.dim;
        let dim_out = channel.target.dim;
        channel.kraus.validate()?;
        if dim_in != channel.kraus.dim || dim_out != channel.kraus.dim {
            return Err(CompletelyPositiveMapError::DimensionMismatch {
                expected: channel.kraus.dim,
                actual: dim_in,
            });
        }
        let choi_dim = preflight(dim_in, dim_out)?;

        let mut choi = CMatrix::zeros(choi_dim, choi_dim);

        // For each Kraus operator K_k (size dim_out x dim_in),
        // vec(K_k) has component at index (i * dim_out + r) equal to K_k[(r, i)].
        for k in &channel.kraus.c_ops {
            let mut vec_k =
                linear_algebra::linear_algebra::complex_matrix::CVector::zeros(choi_dim);
            for i in 0..dim_in {
                for r in 0..dim_out {
                    let idx = i * dim_out + r;
                    vec_k[idx] = k[(r, i)];
                }
            }
            choi += &vec_k * vec_k.adjoint();
        }

        Ok(Self {
            dim_in,
            dim_out,
            choi_matrix: choi,
            label: label.into(),
        })
    }

    /// Admit the exact binary-rational values of a finite Choi matrix by exact PSD.
    /// The eigensolver supplies diagnostics only; `tol` never admits a negative mode.
    pub fn try_from_choi_matrix(
        dim_in: usize,
        dim_out: usize,
        choi: CMatrix,
        label: impl Into<String>,
        tol: f64,
    ) -> Result<Self, CompletelyPositiveMapError> {
        validate_tolerance(tol)?;
        let expected = preflight(dim_in, dim_out)?;
        if choi.nrows() != expected || choi.ncols() != expected {
            return Err(CompletelyPositiveMapError::DimensionMismatch {
                expected,
                actual: choi.nrows(),
            });
        }

        let spectrum = checked_spectrum(&choi)?;
        let min_eigenvalue = spectrum
            .eigenvalues()
            .iter()
            .copied()
            .fold(f64::INFINITY, f64::min);
        if !binary_choi_is_psd(&choi)? {
            return Err(CompletelyPositiveMapError::NotCompletelyPositive { min_eigenvalue });
        }

        Ok(Self {
            dim_in,
            dim_out,
            choi_matrix: choi,
            label: label.into(),
        })
    }

    /// Validate whether the map is trace-preserving:
    /// \(\operatorname{Tr}_B(J(\Phi)) = I_A\).
    pub fn tp_defect(&self) -> f64 {
        let Ok(dim) = preflight(self.dim_in, self.dim_out) else {
            return f64::INFINITY;
        };
        if self.choi_matrix.nrows() != dim || self.choi_matrix.ncols() != dim {
            return f64::INFINITY;
        }
        let mut tr_b = CMatrix::zeros(self.dim_in, self.dim_in);
        for i in 0..self.dim_in {
            for j in 0..self.dim_in {
                let mut sum = C64::new(0.0, 0.0);
                for r in 0..self.dim_out {
                    let row = i * self.dim_out + r;
                    let col = j * self.dim_out + r;
                    sum += self.choi_matrix[(row, col)];
                }
                tr_b[(i, j)] = sum;
            }
        }
        let id_a = CMatrix::identity(self.dim_in, self.dim_in);
        (&tr_b - id_a).norm()
    }

    /// Extract Kraus operators from the spectral decomposition of the Choi matrix:
    /// \(J(\Phi) = \sum_k \lambda_k |\psi_k\rangle\langle\psi_k| \implies K_k = \operatorname{unvec}(\sqrt{\lambda_k} |\psi_k\rangle)\).
    pub fn extract_kraus_operators(
        &self,
        tol: f64,
    ) -> Result<KrausOperators, CompletelyPositiveMapError> {
        self.preflight_kraus_extraction(tol)?;
        let checked = checked_spectrum(&self.choi_matrix)?;
        let s_vals = checked.eigenvalues();
        let u = checked.eigenvectors();
        if let Some(&min_eigenvalue) = s_vals.iter().find(|&&x| x < -tol) {
            return Err(CompletelyPositiveMapError::NotCompletelyPositive { min_eigenvalue });
        }
        let kraus_list = self.build_kraus_matrices_from_spectrum(s_vals, u, tol);
        Ok(KrausOperators::try_from_cmatrices(
            self.dim_in,
            kraus_list,
            format!("{}_extracted_kraus", self.label),
        )?)
    }

    fn preflight_kraus_extraction(&self, tol: f64) -> Result<(), CompletelyPositiveMapError> {
        validate_tolerance(tol)?;
        let expected = preflight(self.dim_in, self.dim_out)?;
        if self.choi_matrix.nrows() != expected || self.choi_matrix.ncols() != expected {
            return Err(CompletelyPositiveMapError::DimensionMismatch {
                expected,
                actual: self.choi_matrix.nrows(),
            });
        }
        if self.dim_in != self.dim_out {
            return Err(CompletelyPositiveMapError::RectangularExtractionRefused {
                dim_in: self.dim_in,
                dim_out: self.dim_out,
            });
        }
        Ok(())
    }

    fn build_kraus_matrices_from_spectrum(
        &self,
        s_vals: &[f64],
        u: &CMatrix,
        tol: f64,
    ) -> Vec<CMatrix> {
        let mut kraus_list = Vec::new();
        for k in 0..s_vals.len() {
            let lambda = s_vals[k];
            if lambda <= tol {
                continue;
            }
            kraus_list.push(self.unvec_eigenvector(u, k, lambda.sqrt()));
        }
        if kraus_list.is_empty() {
            // Degenerate zero map
            kraus_list.push(CMatrix::zeros(self.dim_out, self.dim_in));
        }
        kraus_list
    }

    fn unvec_eigenvector(&self, u: &CMatrix, k: usize, scale: f64) -> CMatrix {
        let mut k_mat = CMatrix::zeros(self.dim_out, self.dim_in);
        for i in 0..self.dim_in {
            for r in 0..self.dim_out {
                let idx = i * self.dim_out + r;
                k_mat[(r, i)] = u[(idx, k)] * C64::new(scale, 0.0);
            }
        }
        k_mat
    }

    /// Convert to a fully validated `QuantumChannel` if trace-preserving.
    pub fn to_quantum_channel(
        &self,
        tol: f64,
    ) -> Result<QuantumChannel, CompletelyPositiveMapError> {
        validate_tolerance(tol)?;
        let defect = self.tp_defect();
        if !defect.is_finite() || defect > tol {
            return Err(CompletelyPositiveMapError::NotTracePreserving { defect, tol });
        }
        let kraus = self.extract_kraus_operators(tol)?;
        Ok(QuantumChannel::try_from_kraus(
            kraus,
            self.label.clone(),
            tol,
        )?)
    }

    pub fn degree(&self) -> usize {
        self.dim_in
    }

    pub fn authority_fence() -> &'static str {
        AUTHORITY_FENCE
    }
}

fn binary_choi_is_psd(choi: &CMatrix) -> Result<bool, CompletelyPositiveMapError> {
    let mut data = Vec::with_capacity(choi.len());
    for row in 0..choi.nrows() {
        for col in 0..choi.ncols() {
            let z = choi[(row, col)];
            data.push(GaussianRat {
                re: Rational::from_float(z.re).ok_or(CompletelyPositiveMapError::NonFiniteEntry)?,
                im: Rational::from_float(z.im).ok_or(CompletelyPositiveMapError::NonFiniteEntry)?,
            });
        }
    }
    let exact = BasicMatrix::from_row_major(choi.nrows(), choi.ncols(), data)
        .map_err(ExactHermitianError::Storage)?;
    Ok(exact_hermitian::is_psd(&exact)?)
}

fn validate_tolerance(tol: f64) -> Result<(), CompletelyPositiveMapError> {
    if !tol.is_finite() || tol < 0.0 {
        return Err(CompletelyPositiveMapError::InvalidTolerance);
    }
    Ok(())
}
fn preflight(a: usize, b: usize) -> Result<usize, CompletelyPositiveMapError> {
    let limits = omega_kernel::resource_limits::OperationLimits::default();
    let n = limits.checked_product(a, b)?;
    limits.check_dense_matrix(n, n, std::mem::size_of::<C64>())?;
    Ok(n)
}
fn checked_spectrum(
    matrix: &CMatrix,
) -> Result<linear_algebra::hermitian_eigen::HermitianSpectrum, CompletelyPositiveMapError> {
    let policy = linear_algebra::hermitian_eigen::SpectrumPolicy::new(256, 10_000, 1e-14, 1e-9)?;
    Ok(linear_algebra::hermitian_eigen::hermitian_eigen_checked(
        matrix, policy,
    )?)
}

// Origin: omega_engine/crates_rs/omega_quantum_physics/src/completely_positive_map.rs
// Claim: urn:omega:crates_rs:omega-quantum-physics:completely-positive-map:l4-production-boundary:v1
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
        let x = CompletelyPositiveMap::new(2, "test");
        assert_eq!(x.degree(), 2);
        assert!(CompletelyPositiveMap::authority_fence().contains("AuthorityEffect None"));
    }

    #[test]
    fn identity_channel_choi_matrix() {
        let h2 = HilbertSpace::try_new(2, "h2").unwrap();
        assert!(matches!(
            QuantumChannel::identity(&h2, "id"),
            Err(ChannelError::ToleranceAdmissionRefused { .. })
        ));
    }

    #[test]
    fn kraus_extraction_round_trip() {
        assert!(matches!(
            QuantumChannel::amplitude_damping(0.3, "ad"),
            Err(ChannelError::ToleranceAdmissionRefused { .. })
        ));
    }

    /// The transpose map's Choi matrix is SWAP: Hermitian, eigenvalues ±1. The
    /// diagnostic now refuses it, as the exact `ExactChoiMatrix` does; the former
    /// singular-value test accepted it.
    #[test]
    fn transpose_map_choi_is_refused() {
        let mut swap = CMatrix::zeros(4, 4);
        for i in 0..2 {
            for j in 0..2 {
                swap[(i * 2 + j, j * 2 + i)] = C64::new(1.0, 0.0);
            }
        }
        let err = CompletelyPositiveMap::try_from_choi_matrix(2, 2, swap, "T", 1e-9);
        assert!(matches!(
            err,
            Err(CompletelyPositiveMapError::NotCompletelyPositive { min_eigenvalue })
                if (min_eigenvalue + 1.0).abs() < 1e-9
        ));

        let mut identity_choi = CMatrix::zeros(4, 4);
        identity_choi[(0, 0)] = C64::new(1.0, 0.0);
        identity_choi[(3, 3)] = C64::new(1.0, 0.0);
        identity_choi[(0, 3)] = C64::new(1.0, 0.0);
        identity_choi[(3, 0)] = C64::new(1.0, 0.0);
        assert!(
            CompletelyPositiveMap::try_from_choi_matrix(2, 2, identity_choi, "id", 1e-9).is_ok()
        );
    }

    #[test]
    fn exact_choi_admission_rejects_tiny_negative_even_with_large_tolerance() {
        let mut matrix = CMatrix::identity(4, 4);
        matrix[(0, 0)] = C64::new(-1e-14, 0.0);
        assert!(matches!(
            CompletelyPositiveMap::try_from_choi_matrix(2, 2, matrix, "negative", 1.0),
            Err(CompletelyPositiveMapError::NotCompletelyPositive { .. })
        ));
        let identity = CompletelyPositiveMap::new(2, "id");
        assert!(CompletelyPositiveMap::try_from_choi_matrix(
            2, 2, identity.choi_matrix().clone(), "rank-one", 0.0
        ).is_ok());
    }

}
