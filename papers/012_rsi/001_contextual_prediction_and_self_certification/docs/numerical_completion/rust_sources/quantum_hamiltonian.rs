//! Hamiltonians `H = H*` and the unitary time evolution they generate.
//!
//! A Hamiltonian generates `U(t) = exp(-i H t)` (units `hbar = 1`) on pure states and
//! density operators: the Schroedinger equation `i d|psi>/dt = H|psi>` and the
//! Liouville-von Neumann equation `d rho/dt = -i [H, rho]`.
//!
//! **Exact: [`ExactHamiltonian`].** A Hermitian operator over `Q(i)`. `exp(-iHt)` is
//! transcendental in general, so the exact face offers the propagators that *are*
//! exact, each checked rather than assumed:
//!
//! - the **Cayley propagator** `U(tau) = (I + i tau H/2)^(-1) (I - i tau H/2)`, a
//!   unitary over `Q(i)` for every Hermitian `H` and rational `tau`: each eigenvalue
//!   `l` of `H` is sent to the unit complex number `(1 - i tau l/2)/(1 + i tau l/2)`.
//!   The propagator is verified exactly unitary, conserves `<H>` exactly, satisfies
//!   `U(tau)^(-1) = U(-tau)`, and agrees with the spectral form `sum_j f(l_j) P_j`. It
//!   is the implicit midpoint (Crank-Nicolson) rule, a rational approximation of
//!   `exp(-i H tau)` of order `tau^3` per step, not the exponential;
//! - the **quarter-turn propagator**: for `t = pi s` with `s` rational and
//!   `2 l_j s` an integer `k_j` for every eigenvalue, `exp(-i l_j t) = (-i)^(k_j)` and
//!   `U(t) = sum_j (-i)^(k_j) P_j` over `Q(i)` with the verified spectral projectors.
//!   For the Rabi pair `H = 3/2 Z + 2 X` (eigenvalues `+-5/2`) and `t = pi/5` this is
//!   `U = -i (3 Z + 4 X)/5` and the spin-flip probability from `|0>` is exactly
//!   `16/25`.
//!
//! **Diagnostic: [`QuantumHamiltonian`].** The `f64` Hamiltonian: its eigenpairs come
//! from `linear_algebra::hermitian_eigen` (nalgebra's symmetric eigensolver with an
//! independent residual and orthonormality check), *not* from a singular value
//! decomposition; a singular value decomposition returns `|l|`, so for a spectrum with
//! `+-l` (every traceless qubit Hamiltonian, `sigma_x` among them) its vectors are an
//! arbitrary basis of the degenerate subspace and the energies, the ground state and
//! `U(t)` are wrong. The input must be exactly Hermitian in its `f64` representation;
//! a triangle is never discarded.
//!
//! AuthorityEffect: None.

use linear_algebra::hermitian_eigen::{hermitian_eigen_checked, SpectrumError, SpectrumPolicy};
use linear_algebra::backend::basic_matrix::BasicMatrix;
use linear_algebra::linear_algebra::complex_matrix::{CMatrix, CVector, C64};
use num_traits::Zero;
use omega_number_theory::cyclotomic::GaussianRat;
use omega_number_theory::rational::{ri, Rational};

use crate::density_matrix::{ExactDensityError, ExactDensityMatrix};
use crate::exact_hermitian::{self, SpectrumError as ResolutionError};
use crate::exact_operator::{ExactOperator, OperatorError};
use crate::hilbert_space::HilbertSpace;
use crate::observable::{ExactObservable, ExactObservableError, Observable, ObservableError};
use crate::pauli::Pauli;
use crate::quantum_state::{QuantumState, QuantumStateError, RayError, RayVector};
use crate::unitary_operator::{NumericalUnitaryOperator, UnitaryError};
use linear_algebra::linear_algebra::density::NumericalDensityMatrix as LinAlgDensityMatrix;

/// Fence string (proposal).
pub const AUTHORITY_FENCE: &str =
    "AuthorityEffect None; not PROVED; not GlobalGreen; finite Hamiltonian face.";

/// Unitarity tolerance of the `f64` propagator. Not a certificate.
pub const PROPAGATOR_UNITARY_TOL: f64 = 1e-6;

// ---------------------------------------------------------------------------
// Exact Hamiltonians
// ---------------------------------------------------------------------------

/// Refusals of the exact Hamiltonian face.
#[derive(Debug, Clone, PartialEq, Eq, thiserror::Error)]
pub enum ExactHamiltonianError {
    #[error("observable: {0}")]
    Observable(ExactObservableError),
    #[error("operator: {0}")]
    Operator(OperatorError),
    #[error("ray: {0}")]
    Ray(RayError),
    #[error("state: {0}")]
    State(ExactDensityError),
    #[error("declared spectrum refused: {0:?}")]
    Resolution(ResolutionError),
    /// The Cayley propagator failed its own exact unitarity check (an internal
    /// inconsistency; it cannot happen for a Hermitian `H`).
    #[error("the Cayley propagator is not unitary")]
    CayleyNotUnitary,
    /// The spectrum is not rational, so there are no projectors over `Q(i)`.
    #[error("the spectrum is irrational; the spectral propagators need rational eigenvalues")]
    IrrationalSpectrum,
    /// `2 l s` is not an integer for the eigenvalue `l`: the phase `exp(-i pi l s)` is
    /// not a power of `-i`.
    #[error("eigenvalue {eigenvalue} at s = {s} is not a quarter turn: 2 l s = {turns}")]
    NotAQuarterTurn {
        eigenvalue: Rational,
        s: Rational,
        turns: Rational,
    },
    #[error("a qubit Hamiltonian acts on C^2, got dimension {0}")]
    NotAQubit(usize),
}

impl From<OperatorError> for ExactHamiltonianError {
    fn from(e: OperatorError) -> Self {
        ExactHamiltonianError::Operator(e)
    }
}

impl From<ExactObservableError> for ExactHamiltonianError {
    fn from(e: ExactObservableError) -> Self {
        ExactHamiltonianError::Observable(e)
    }
}

/// A Hermitian operator over `Q(i)` read as a Hamiltonian.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ExactHamiltonian {
    observable: ExactObservable,
}

/// `i^(-k)` for an integer `k`: `exp(-i pi k / 2)`.
fn power_of_minus_i(k: i64) -> GaussianRat {
    match k.rem_euclid(4) {
        0 => GaussianRat::one(),
        1 => GaussianRat::from_ints(0, -1),
        2 => GaussianRat::from_ints(-1, 0),
        _ => GaussianRat::from_ints(0, 1),
    }
}

impl ExactHamiltonian {
    /// A Hamiltonian from a Hermitian operator.
    pub fn try_new(op: ExactOperator) -> Result<Self, ExactHamiltonianError> {
        Ok(Self {
            observable: ExactObservable::try_new(op)?,
        })
    }

    /// The qubit Hamiltonian `cx X + cy Y + cz Z` with rational coefficients; the Rabi
    /// Hamiltonian `(Delta/2) Z + (Omega/2) X` is `qubit(Omega/2, 0, Delta/2)`.
    pub fn qubit(
        cx: &Rational,
        cy: &Rational,
        cz: &Rational,
    ) -> Result<Self, ExactHamiltonianError> {
        let term = |c: &Rational, p: Pauli| p.to_operator().scale_rat(c);
        let sum = term(cx, Pauli::X)?
            .add(&term(cy, Pauli::Y)?)?
            .add(&term(cz, Pauli::Z)?)?;
        Self::try_new(sum)
    }

    /// The Hamiltonian as an observable.
    pub fn as_observable(&self) -> &ExactObservable {
        &self.observable
    }

    /// Dimension `n`.
    pub fn dim(&self) -> usize {
        self.observable.dim()
    }

    /// `(I + i tau H/2)^(-1) (I - i tau H/2)`, verified exactly unitary.
    pub fn cayley_propagator(
        &self,
        tau: &Rational,
    ) -> Result<ExactOperator, ExactHamiltonianError> {
        let n = self.dim();
        let identity = ExactOperator::identity(n)?;
        let half_i_tau = GaussianRat {
            re: Rational::zero(),
            im: tau * ri(2).recip(),
        };
        let shift = self.observable.as_operator().scale(&half_i_tau)?;
        let numerator = identity.sub(&shift)?;
        let denominator = identity.add(&shift)?;
        let propagator = denominator.inverse()?.mul(&numerator)?;
        if !propagator.is_unitary() {
            return Err(ExactHamiltonianError::CayleyNotUnitary);
        }
        Ok(propagator)
    }

    /// One Cayley step applied to a ray.
    pub fn cayley_step(
        &self,
        ray: &RayVector,
        tau: &Rational,
    ) -> Result<RayVector, ExactHamiltonianError> {
        ray.apply_ray(&self.cayley_propagator(tau)?)
            .map_err(ExactHamiltonianError::Ray)
    }

    /// One Cayley step applied to a state.
    pub fn cayley_step_state(
        &self,
        rho: &ExactDensityMatrix,
        tau: &Rational,
    ) -> Result<ExactDensityMatrix, ExactHamiltonianError> {
        rho.conjugate(&self.cayley_propagator(tau)?)
            .map_err(ExactHamiltonianError::State)
    }

    fn quarter_turn_term(
        l: &Rational,
        s: &Rational,
        projector: &BasicMatrix<GaussianRat>,
    ) -> Result<ExactOperator, ExactHamiltonianError> {
        let turns = ri(2) * l * s;
        if !turns.is_integer() {
            return Err(ExactHamiltonianError::NotAQuarterTurn {
                eigenvalue: l.clone(),
                s: s.clone(),
                turns,
            });
        }
        let k = num_traits::ToPrimitive::to_i64(&turns.to_integer()).ok_or(
            ExactHamiltonianError::NotAQuarterTurn {
                eigenvalue: l.clone(),
                s: s.clone(),
                turns: turns.clone(),
            },
        )?;
        Ok(ExactOperator::try_new(projector.clone())?.scale(&power_of_minus_i(k))?)
    }

    /// `U(pi s) = sum_j (-i)^(2 l_j s) P_j`, exact when `2 l_j s` is an integer for
    /// every eigenvalue `l_j`; the eigenvalues are found exactly
    /// ([`ExactObservable::spectrum`]) and must be rational, and the projectors are the
    /// verified Lagrange projectors of [`crate::exact_hermitian::spectral_resolution`].
    pub fn quarter_turn_propagator(
        &self,
        s: &Rational,
    ) -> Result<ExactOperator, ExactHamiltonianError> {
        let spectrum = self.observable.spectrum()?;
        let eigenvalues = spectrum
            .rational_eigenvalues()
            .ok_or(ExactHamiltonianError::IrrationalSpectrum)?;
        let declared: Vec<Rational> = eigenvalues.iter().map(|(l, _)| l.clone()).collect();
        let resolution = exact_hermitian::spectral_resolution(
            self.observable.as_operator().as_matrix(),
            &declared,
        )
        .map_err(ExactHamiltonianError::Resolution)?;
        let n = self.dim();
        let mut acc = ExactOperator::zeros(n, n)?;
        for (l, projector) in resolution.eigenvalues().iter().zip(resolution.projectors()) {
            let term = Self::quarter_turn_term(l, s, projector)?;
            acc = acc.add(&term)?;
        }
        if !acc.is_unitary() {
            return Err(ExactHamiltonianError::CayleyNotUnitary);
        }
        Ok(acc)
    }

    /// `<psi|H|psi> / <psi|psi>` in a ray.
    pub fn energy(&self, ray: &RayVector) -> Result<Rational, ExactHamiltonianError> {
        Ok(self.observable.expectation_ray(ray)?)
    }
}

// ---------------------------------------------------------------------------
// f64 diagnostic face
// ---------------------------------------------------------------------------

#[derive(Debug, Clone, PartialEq, thiserror::Error)]
pub enum HamiltonianError {
    #[error("observable error: {0}")]
    Observable(#[from] ObservableError),
    #[error("unitary error: {0}")]
    Unitary(#[from] UnitaryError),
    #[error("state error: {0}")]
    State(#[from] QuantumStateError),
    #[error("dimension mismatch: expected {expected}, actual {actual}")]
    DimensionMismatch { expected: usize, actual: usize },
    /// The checked eigensolver refused (not exactly Hermitian, residual or
    /// orthonormality beyond its policy, ...).
    #[error("spectral decomposition failed: {0}")]
    Spectrum(#[from] SpectrumError),
}

/// Finite quantum Hamiltonian `H = H*` with its checked eigenpairs (`Diagnostic`).
#[derive(Debug, Clone, PartialEq)]
pub struct QuantumHamiltonian {
    observable: Observable,
    energies: Vec<f64>,
    eigenvectors: CMatrix,
}

fn spectrum_policy() -> Result<SpectrumPolicy, SpectrumError> {
    SpectrumPolicy::new(256, 10_000, 1e-14, 1e-9)
}

impl QuantumHamiltonian {
    /// Construct from an `Observable`. The matrix must be Hermitian *exactly* in its
    /// `f64` entries (`H[i][j] = conj(H[j][i])`); the eigenpairs are then computed by the
    /// checked symmetric eigensolver and sorted by energy, ascending.
    pub fn from_observable(obs: Observable) -> Result<Self, HamiltonianError> {
        let spectrum = hermitian_eigen_checked(&obs.matrix, spectrum_policy()?)?;
        Ok(Self {
            energies: spectrum.eigenvalues().to_vec(),
            eigenvectors: spectrum.eigenvectors().clone(),
            observable: obs,
        })
    }

    /// Construct from a general Hermitian `CMatrix` (Hermitian within `tol`, then
    /// required to be exactly Hermitian by the eigensolver).
    pub fn from_cmatrix(
        matrix: &CMatrix,
        label: impl Into<String>,
        tol: f64,
    ) -> Result<Self, HamiltonianError> {
        let dim = matrix.nrows();
        let obs = Observable::try_new(dim, matrix.clone(), label, tol)?;
        Self::from_observable(obs)
    }

    /// Single qubit Zeeman Hamiltonian: \(H = \frac{\hbar \omega}{2} \sigma_z\).
    pub fn zeeman(omega: f64, label: impl Into<String>) -> Result<Self, HamiltonianError> {
        let mat = Pauli::Z.to_cmatrix() * C64::new(0.5 * omega, 0.0);
        Self::from_cmatrix(&mat, label, 1e-12)
    }

    /// Driven two-level system (Rabi Hamiltonian):
    /// \(H = \frac{\omega}{2} \sigma_z + \frac{\Omega}{2} \sigma_x\).
    pub fn rabi(
        omega: f64,
        omega_rabi: f64,
        label: impl Into<String>,
    ) -> Result<Self, HamiltonianError> {
        let mat = Pauli::Z.to_cmatrix() * C64::new(0.5 * omega, 0.0)
            + Pauli::X.to_cmatrix() * C64::new(0.5 * omega_rabi, 0.0);
        Self::from_cmatrix(&mat, label, 1e-12)
    }

    /// The Hamiltonian as an observable.
    pub fn observable(&self) -> &Observable {
        &self.observable
    }

    /// The energy levels `E_0 <= E_1 <= ... <= E_(d-1)`.
    pub fn energies(&self) -> &[f64] {
        &self.energies
    }

    /// The eigenvectors, columns of the modal matrix `V` in the order of `energies()`.
    pub fn eigenvectors(&self) -> &CMatrix {
        &self.eigenvectors
    }

    /// Dimension of the Hilbert space.
    pub fn dim(&self) -> usize {
        self.observable.dim
    }

    /// Ground state energy \(E_0 = \min_n E_n\).
    pub fn ground_state_energy(&self) -> f64 {
        self.energies[0]
    }

    /// Ground state vector \(|\psi_0\rangle\).
    pub fn ground_state(&self, space: &HilbertSpace) -> Result<QuantumState, HamiltonianError> {
        let dim = self.dim();
        if space.dim() != dim {
            return Err(HamiltonianError::DimensionMismatch {
                expected: dim,
                actual: space.dim(),
            });
        }
        let amps: Vec<C64> = (0..dim).map(|i| self.eigenvectors[(i, 0)]).collect();
        Ok(QuantumState::try_normalized(
            space,
            amps,
            format!("{}_ground", self.observable.label),
        )?)
    }

    /// Energy expectation value \(\langle E \rangle = \operatorname{Tr}(H \rho)\).
    pub fn expectation_density(&self, rho: &LinAlgDensityMatrix) -> Result<f64, HamiltonianError> {
        Ok(self.observable.expectation_value_density(rho)?)
    }

    /// Energy expectation value \(\langle E \rangle = \langle\psi|H|\psi\rangle\).
    pub fn expectation_state(&self, psi: &QuantumState) -> Result<f64, HamiltonianError> {
        Ok(self.observable.expectation_value_state(psi)?)
    }

    /// Numerical time evolution operator \(U(t) = \exp(-i H t)\) (natural units \(\hbar = 1\)):
    /// \(U(t) = V \operatorname{diag}(e^{-i E_0 t}, \dots, e^{-i E_{d-1} t}) V^\dagger\).
    /// Returns a numerical diagnostic with its unitarity defect; no exact admission.
    pub fn time_evolution_operator(
        &self,
        t: f64,
        label: impl Into<String>,
    ) -> Result<NumericalUnitaryOperator, HamiltonianError> {
        let dim = self.dim();
        let mut exp_d = CMatrix::zeros(dim, dim);
        for k in 0..dim {
            let phase = -self.energies[k] * t;
            exp_d[(k, k)] = C64::new(phase.cos(), phase.sin());
        }
        let u_mat = &self.eigenvectors * &exp_d * self.eigenvectors.adjoint();
        Ok(NumericalUnitaryOperator::try_new(
            dim,
            u_mat,
            label,
            PROPAGATOR_UNITARY_TOL,
        )?)
    }

    /// Evolve a pure state: \(|\psi(t)\rangle = U(t)|\psi(0)\rangle\).
    pub fn evolve_state(
        &self,
        psi: &QuantumState,
        t: f64,
    ) -> Result<QuantumState, HamiltonianError> {
        let u = self.time_evolution_operator(t, "U_t")?;
        Ok(u.evolve_state(psi)?)
    }

    /// Commutator \([H, \rho] = H \rho - \rho H\) for the Liouville-von Neumann equation:
    /// \(\frac{d\rho}{dt} = -i [H, \rho]\).
    pub fn commutator_with_matrix(&self, rho: &CMatrix) -> Result<CMatrix, HamiltonianError> {
        let dim = self.dim();
        if rho.nrows() != dim || rho.ncols() != dim {
            return Err(HamiltonianError::DimensionMismatch {
                expected: dim,
                actual: rho.nrows(),
            });
        }
        let h = &self.observable.matrix;
        Ok((h * rho) - (rho * h))
    }

    /// The eigenvector of energy index `k` as a `CVector`.
    pub fn eigenvector(&self, k: usize) -> Option<CVector> {
        (k < self.dim()).then(|| self.eigenvectors.column(k).into_owned())
    }

    pub fn authority_fence() -> &'static str {
        AUTHORITY_FENCE
    }
}

// Origin: omega_engine/crates_rs/omega_quantum_physics/src/quantum_hamiltonian.rs
// Claim: urn:omega:crates_rs:omega-quantum-physics:quantum-hamiltonian:l4-production-boundary:v1
// AuthorityEffect: None
// Scope Fence: Does not claim authority promotion outside declared finite bounds.
// Computational-Profile: Numerical (floating-point convergence and error tolerance bound monitored)
// Mutation Accounting: killed=6, survived=0, demonstrably_equivalent=0, invalid=0, inconclusive=0, unrun=0 (rejects invalid/error mutant states)

#[cfg(test)]
mod tests {
    use super::*;
    use linear_algebra::backend::basic_matrix::BasicMatrix;
    use omega_number_theory::rational::rq;

    fn cplus(x: f64) -> C64 {
        C64::new(x, 0.0)
    }

    #[test]
    fn zeeman_hamiltonian_evolution() {
        let h2 = HilbertSpace::try_new(2, "h2").unwrap();
        let omega = 2.0 * std::f64::consts::PI; // period T = 1.0 for full 2pi rotation
        let ham = QuantumHamiltonian::zeeman(omega, "zeeman").unwrap();

        assert_eq!(ham.dim(), 2);
        assert!((ham.energies()[0] - (-std::f64::consts::PI)).abs() < 1e-10);
        assert!((ham.energies()[1] - std::f64::consts::PI).abs() < 1e-10);

        let inv_sqrt2 = (0.5_f64).sqrt();
        let plus =
            QuantumState::try_normalized(&h2, vec![cplus(inv_sqrt2), cplus(inv_sqrt2)], "plus")
                .unwrap();
        let evolved = ham.evolve_state(&plus, 0.5).unwrap();
        assert!(evolved.transition_probability(&plus).unwrap() < 1e-6);
        let evolved_full = ham.evolve_state(&plus, 1.0).unwrap();
        assert!((evolved_full.transition_probability(&plus).unwrap() - 1.0).abs() < 1e-6);
    }

    /// `sigma_x` has the eigenvalue pair `+-1`: a singular value decomposition returns the
    /// degenerate singular value `1` twice and an arbitrary basis of the plane, so the
    /// previous implementation reported the energies `(0, 0)` and propagated wrongly.
    /// `U(t) = exp(-i sigma_x t) = cos t I - i sin t sigma_x`.
    #[test]
    fn a_hamiltonian_with_plus_minus_eigenvalues_has_the_right_spectrum_and_propagator() {
        let ham = QuantumHamiltonian::from_observable(Observable::pauli_x()).unwrap();
        assert!((ham.energies()[0] + 1.0).abs() < 1e-12);
        assert!((ham.energies()[1] - 1.0).abs() < 1e-12);
        let t = 0.7_f64;
        let u = ham.time_evolution_operator(t, "U").unwrap();
        let (c, s) = (t.cos(), t.sin());
        let expect = [[cplus(c), C64::new(0.0, -s)], [C64::new(0.0, -s), cplus(c)]];
        for r in 0..2 {
            for col in 0..2 {
                assert!(
                    (u.matrix()[(r, col)] - expect[r][col]).norm() < 1e-12,
                    "({r}, {col})"
                );
            }
        }
        // The ground state is |-> = (1, -1)/sqrt 2 up to a phase.
        let h2 = HilbertSpace::try_new(2, "h2").unwrap();
        let g = ham.ground_state(&h2).unwrap();
        let minus = QuantumState::try_normalized(&h2, vec![cplus(1.0), cplus(-1.0)], "-").unwrap();
        assert!((g.transition_probability(&minus).unwrap() - 1.0).abs() < 1e-12);
    }

    /// Rabi with the Pythagorean pair: `H = 3/2 Z + 2 X` has energies `+-5/2`, and the flip
    /// probability from `|0>` is `(16/25) sin^2(5 t / 2)` at every time.
    #[test]
    fn rabi_oscillation_follows_the_closed_form() {
        let ham = QuantumHamiltonian::rabi(3.0, 4.0, "rabi").unwrap();
        assert!((ham.energies()[0] + 2.5).abs() < 1e-12 && (ham.energies()[1] - 2.5).abs() < 1e-12);
        let h2 = HilbertSpace::try_new(2, "h2").unwrap();
        let zero = QuantumState::computational_basis(&h2, 0, "0").unwrap();
        let one = QuantumState::computational_basis(&h2, 1, "1").unwrap();
        for &t in &[0.0, 0.3, 0.63, 1.1, 2.9] {
            let flipped = ham.evolve_state(&zero, t).unwrap();
            let p = flipped.transition_probability(&one).unwrap();
            let closed = 16.0 / 25.0 * (2.5 * t / 1.0_f64).sin().powi(2);
            assert!((p - closed).abs() < 1e-12, "t = {t}: {p} vs {closed}");
        }
    }

    #[test]
    fn the_solver_keeps_degenerate_subspaces_and_reports_checked_residuals() {
        // sigma_x (x) I on C^4: eigenvalues -1, -1, +1, +1.
        let x = Pauli::X.to_cmatrix();
        let id = CMatrix::identity(2, 2);
        let mut h = CMatrix::zeros(4, 4);
        for a in 0..2 {
            for b in 0..2 {
                for c in 0..2 {
                    for d in 0..2 {
                        h[(a * 2 + c, b * 2 + d)] = x[(a, b)] * id[(c, d)];
                    }
                }
            }
        }
        let ham = QuantumHamiltonian::from_cmatrix(&h, "xi", 1e-12).unwrap();
        for (k, expected) in [-1.0, -1.0, 1.0, 1.0].iter().enumerate() {
            assert!((ham.energies()[k] - expected).abs() < 1e-12);
            // H v = E v for every returned eigenvector.
            let v = ham.eigenvector(k).unwrap();
            let residual = (&h * &v - &v * cplus(ham.energies()[k])).norm();
            assert!(residual < 1e-12, "k = {k}: residual {residual}");
        }
        assert!(ham.eigenvector(4).is_none());
    }

    #[test]
    fn a_matrix_that_is_only_nearly_hermitian_is_refused_by_the_eigensolver() {
        let mut m = Pauli::Z.to_cmatrix();
        m[(0, 1)] = C64::new(1e-13, 0.0); // within the 1e-12 observable tolerance, not exactly Hermitian
        let err = QuantumHamiltonian::from_cmatrix(&m, "almost", 1e-12);
        assert!(matches!(
            err,
            Err(HamiltonianError::Spectrum(
                SpectrumError::NotHermitian { .. }
            ))
        ));
    }

    /// `d rho/dt = -i [H, rho]` for `H = sigma_x` and `rho = |0><0|`: `[X, |0><0|] =
    /// |1><0| - |0><1|`; and the energy is conserved: `Tr(H [H, rho]) = 0`.
    #[test]
    fn the_liouville_commutator_is_the_right_one_and_conserves_energy() {
        let ham = QuantumHamiltonian::from_observable(Observable::pauli_x()).unwrap();
        let mut rho = CMatrix::zeros(2, 2);
        rho[(0, 0)] = cplus(1.0);
        let c = ham.commutator_with_matrix(&rho).unwrap();
        assert_eq!(c[(0, 1)], cplus(-1.0));
        assert_eq!(c[(1, 0)], cplus(1.0));
        assert_eq!(c[(0, 0)], cplus(0.0));
        let h = &ham.observable().matrix;
        assert!((h * &c).trace().norm() < 1e-15);
        assert!(matches!(
            ham.commutator_with_matrix(&CMatrix::zeros(3, 3)),
            Err(HamiltonianError::DimensionMismatch { .. })
        ));
    }

    // ----- exact ---------------------------------------------------------------

    fn rabi_exact() -> ExactHamiltonian {
        // H = 3/2 Z + 2 X
        ExactHamiltonian::qubit(&ri(2), &ri(0), &rq(3, 2)).unwrap()
    }

    #[test]
    fn the_cayley_propagator_is_exactly_unitary_and_conserves_energy_and_inverts_by_negation() {
        let h = rabi_exact();
        let tau = rq(3, 7);
        let u = h.cayley_propagator(&tau).unwrap();
        assert!(u.is_unitary());
        // U(-tau) is the inverse.
        let back = h.cayley_propagator(&(-tau.clone())).unwrap();
        assert_eq!(u.mul(&back).unwrap(), ExactOperator::identity(2).unwrap());
        // <H> is conserved exactly under the step, for a generic ray.
        let psi = RayVector::from_ints(&[(1, 2), (3, -1)]).unwrap();
        let stepped = h.cayley_step(&psi, &tau).unwrap();
        assert_eq!(h.energy(&psi).unwrap(), h.energy(&stepped).unwrap());
        assert_eq!(psi.norm_sq(), stepped.norm_sq());
        // On states: the same conjugation keeps a density operator a density operator.
        let rho = ExactDensityMatrix::pure(&psi).unwrap();
        let rho_next = h.cayley_step_state(&rho, &tau).unwrap();
        assert_eq!(rho_next, ExactDensityMatrix::pure(&stepped).unwrap());
    }

    /// Two independent exact routes to the same unitary: inverse-based Cayley, and
    /// the spectral form `sum_j (1 - i tau l_j/2)/(1 + i tau l_j/2) P_j`.
    #[test]
    fn the_cayley_propagator_agrees_with_its_spectral_form() {
        let h = rabi_exact();
        let tau = rq(2, 5);
        let direct = h.cayley_propagator(&tau).unwrap();
        let spectrum = h
            .as_observable()
            .spectrum()
            .unwrap()
            .rational_eigenvalues()
            .unwrap();
        let declared: Vec<Rational> = spectrum.iter().map(|(l, _)| l.clone()).collect();
        let resolution = exact_hermitian::spectral_resolution(
            h.as_observable().as_operator().as_matrix(),
            &declared,
        )
        .unwrap();
        let mut acc = ExactOperator::zeros(2, 2).unwrap();
        for (l, p) in resolution.eigenvalues().iter().zip(resolution.projectors()) {
            let a = GaussianRat {
                re: Rational::zero(),
                im: &tau * l * rq(1, 2),
            };
            let f = GaussianRat::one()
                .sub(&a)
                .mul(&GaussianRat::one().add(&a).inv());
            acc = acc
                .add(
                    &ExactOperator::try_new(p.clone())
                        .unwrap()
                        .scale(&f)
                        .unwrap(),
                )
                .unwrap();
        }
        assert_eq!(direct, acc);
    }

    /// `t = pi/5`: `2 (5/2)(1/5) = 1`, so `U = -i P_+ + i P_- = -i (3 Z + 4 X)/5`, and the
    /// spin-flip probability from `|0>` is exactly `(4/5)^2 = 16/25`.
    #[test]
    fn the_rabi_quarter_turn_propagator_is_exact() {
        let h = rabi_exact();
        let u = h.quarter_turn_propagator(&rq(1, 5)).unwrap();
        let expect = ExactOperator::try_new(
            BasicMatrix::<GaussianRat>::from_row_major(
                2,
                2,
                vec![
                    GaussianRat {
                        re: Rational::zero(),
                        im: rq(-3, 5),
                    },
                    GaussianRat {
                        re: Rational::zero(),
                        im: rq(-4, 5),
                    },
                    GaussianRat {
                        re: Rational::zero(),
                        im: rq(-4, 5),
                    },
                    GaussianRat {
                        re: Rational::zero(),
                        im: rq(3, 5),
                    },
                ],
            )
            .unwrap(),
        )
        .unwrap();
        assert_eq!(u, expect);
        let zero = RayVector::basis(2, 0).unwrap();
        let one = RayVector::basis(2, 1).unwrap();
        let evolved = zero.apply_ray(&u).unwrap();
        assert_eq!(evolved.transition_probability(&one).unwrap(), rq(16, 25));
        // Other times that are quarter turns: s = 2/5 gives k = 2, U = -I; s = 4/5: U = I.
        assert_eq!(
            h.quarter_turn_propagator(&rq(2, 5)).unwrap(),
            ExactOperator::identity(2)
                .unwrap()
                .scale(&GaussianRat::from_ints(-1, 0))
                .unwrap()
        );
        assert_eq!(
            h.quarter_turn_propagator(&rq(4, 5)).unwrap(),
            ExactOperator::identity(2).unwrap()
        );
        // A time that is not a quarter turn for these energies is refused.
        assert!(matches!(
            h.quarter_turn_propagator(&rq(1, 3)),
            Err(ExactHamiltonianError::NotAQuarterTurn { .. })
        ));
    }

    #[test]
    fn an_irrational_spectrum_has_no_exact_spectral_propagator() {
        // [[1,1],[1,0]] has eigenvalues (1 +- sqrt 5)/2.
        let golden = ExactOperator::from_rows(vec![
            vec![GaussianRat::one(), GaussianRat::one()],
            vec![GaussianRat::one(), GaussianRat::zero()],
        ])
        .unwrap();
        let h = ExactHamiltonian::try_new(golden).unwrap();
        assert_eq!(
            h.quarter_turn_propagator(&rq(1, 2)),
            Err(ExactHamiltonianError::IrrationalSpectrum)
        );
        // The Cayley route needs no spectrum and still gives an exact unitary.
        assert!(h.cayley_propagator(&rq(1, 3)).unwrap().is_unitary());
    }

    #[test]
    fn non_hermitian_operators_are_not_hamiltonians() {
        let n = ExactOperator::from_rows(vec![
            vec![GaussianRat::zero(), GaussianRat::one()],
            vec![GaussianRat::zero(), GaussianRat::zero()],
        ])
        .unwrap();
        assert!(matches!(
            ExactHamiltonian::try_new(n),
            Err(ExactHamiltonianError::Observable(_))
        ));
    }

    #[test]
    fn authority_fence_is_none() {
        assert!(QuantumHamiltonian::authority_fence().contains("AuthorityEffect None"));
    }
}
