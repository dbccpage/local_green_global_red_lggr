"""Reference implementation for The Authority Firewall and Verification Limits.

Formalizes:
1. Detector Calibration vs. Adequacy:
   D(x) = pass != Adequate(D, C, P) != Operational Authority.
   The four calibration examples (positive, negative, collision, metamorphic) constitute
   a necessary Minimum Calibration Record to falsify trivial collapsing/constant detectors.
   Full adequacy over a claim class requires an additional coverage theorem, exhaustive
   finite domain enumeration, or an explicitly bounded claim scope.
2. Capability-Protected Non-Authority Firewall:
   Under an object-capability model with untrusted runtime access, no sequence of
   operations in the untrusted interface can instantiate or forge an AuthorityCapability.
3. Sovereign Witness Validation and Descent Verification:
   Authority certification requires a cryptographically bound descent witness issued by
   an authorized sovereign verifier. Fabricated, unbound, or unverified witnesses fail-closed.
4. Six-Axis Evidence Lattice:
   Mathematical, Mechanization, Implementation, Empirical, Security, Authority.
   Green status on one axis never implies green on another.
5. Halting vs. Structural Authority:
   Fluent halting or syntactic task completion does not confer operational authority.
6. Exact Rational Arithmetic:
   All discrete obstruction computations and calibration norms are computed using
   exact rational arithmetic (fractions.Fraction).
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Callable, Optional


class TerminalVerdict(str, Enum):
    AUTHORITY_CERTIFIED = "AuthorityCertified"
    DETECTOR_INADEQUATE = "DetectorInadequate"
    REFUSAL_DEFECT = "RefusalDefect"
    FLUENT_HALT_NON_AUTHORITY = "FluentHaltNonAuthority"


class CapabilityViolationError(TypeError):
    """Raised when an unauthorized capability construction from runtime results is attempted."""
    pass


@dataclass(frozen=True)
class DiscreteResidual:
    """Discrete obstruction residual represented in exact rational coordinates."""
    coordinates: tuple[Fraction, ...]

    @classmethod
    def from_ints(cls, *coords: int) -> DiscreteResidual:
        return cls(tuple(Fraction(c, 1) for c in coords))

    @classmethod
    def from_fractions(cls, *coords: tuple[int, int]) -> DiscreteResidual:
        return cls(tuple(Fraction(num, den) for num, den in coords))

    @property
    def norm1(self) -> Fraction:
        """Exact L1 norm of the residual."""
        return sum(abs(c) for c in self.coordinates) if self.coordinates else Fraction(0, 1)

    @property
    def is_exact_zero(self) -> bool:
        """Exact zero defect check."""
        return self.norm1 == Fraction(0, 1)


@dataclass(frozen=True)
class CalibrationCase:
    """Individual calibration case binding input data and expected ground-truth outcome."""
    case_id: str
    residual: DiscreteResidual
    expected_pass: bool
    description: str = ""


@dataclass(frozen=True)
class CollisionPair:
    """Two distinct protected states that must not be collapsed by the detector."""
    pair_id: str
    residual_a: DiscreteResidual
    residual_b: DiscreteResidual
    description: str = ""

    def are_distinct(self) -> bool:
        return self.residual_a.coordinates != self.residual_b.coordinates


@dataclass(frozen=True)
class MetamorphicPair:
    """Invariant-preserving rewrite of a state where detector verdict must remain invariant."""
    pair_id: str
    original: DiscreteResidual
    transformed: DiscreteResidual
    description: str = ""

    def preserves_norm(self) -> bool:
        return self.original.norm1 == self.transformed.norm1


@dataclass(frozen=True)
class CalibrationEvaluationResult:
    """Evaluation result of running a detector against a calibration record."""
    passed: bool
    failures: tuple[str, ...] = ()
    evaluated_cases: int = 0


@dataclass(frozen=True)
class MinimumCalibrationRecord:
    """The four required calibration artifacts for detector sanity verification.
    
    NOTE ON ADEQUACY:
    Passing this four-case calibration record is a necessary minimum filter against
    collapsing detectors (e.g. constant terminalizers). However, four examples CANNOT
    establish detector adequacy over an unbounded or general claim class C. Full adequacy
    requires an exhaustive finite domain enumeration, an explicit coverage theorem,
    or a declared bounded claim domain.
    """
    positive_case: CalibrationCase
    negative_case: CalibrationCase
    collision_pair: CollisionPair
    metamorphic_pair: MetamorphicPair

    def execute_calibration(
        self,
        detector: Callable[[DiscreteResidual], bool],
    ) -> CalibrationEvaluationResult:
        """Executes the detector against each calibration case and verifies adherence."""
        failures: list[str] = []
        evaluated = 0

        # 1. Positive case (valid input that must pass)
        evaluated += 1
        pos_res = detector(self.positive_case.residual)
        if pos_res != self.positive_case.expected_pass:
            failures.append(
                f"Positive case {self.positive_case.case_id} failed: "
                f"expected {self.positive_case.expected_pass}, got {pos_res}"
            )

        # 2. Negative case (defective input that must refuse)
        evaluated += 1
        neg_res = detector(self.negative_case.residual)
        if neg_res != self.negative_case.expected_pass:
            failures.append(
                f"Negative case {self.negative_case.case_id} failed: "
                f"expected {self.negative_case.expected_pass}, got {neg_res}"
            )

        # 3. Collision case (distinct protected states must not collapse)
        evaluated += 1
        res_a = detector(self.collision_pair.residual_a)
        res_b = detector(self.collision_pair.residual_b)
        # If both are non-zero defect states, a collapsing detector passes both
        if not self.collision_pair.residual_a.is_exact_zero and not self.collision_pair.residual_b.is_exact_zero:
            if res_a and res_b:
                failures.append(
                    f"Collision pair {self.collision_pair.pair_id} collapsed: "
                    f"both distinct non-zero defects were falsely passed"
                )

        # 4. Metamorphic case (invariant-preserving transform must preserve verdict)
        evaluated += 1
        orig_res = detector(self.metamorphic_pair.original)
        trans_res = detector(self.metamorphic_pair.transformed)
        if orig_res != trans_res:
            failures.append(
                f"Metamorphic pair {self.metamorphic_pair.pair_id} failed: "
                f"verdict flipped under invariant-preserving transform ({orig_res} != {trans_res})"
            )

        return CalibrationEvaluationResult(
            passed=(len(failures) == 0),
            failures=tuple(failures),
            evaluated_cases=evaluated,
        )


def create_canonical_calibration_record() -> MinimumCalibrationRecord:
    """Creates a standard exact rational calibration record."""
    return MinimumCalibrationRecord(
        positive_case=CalibrationCase(
            case_id="POS_ZERO_DEFECT",
            residual=DiscreteResidual.from_ints(0, 0, 0),
            expected_pass=True,
            description="Trivially closed boundary with zero obstruction",
        ),
        negative_case=CalibrationCase(
            case_id="NEG_RATIONAL_DEFECT",
            residual=DiscreteResidual.from_fractions((1, 2), (-1, 3), (0, 1)),
            expected_pass=False,
            description="Non-zero rational boundary residual requiring refusal",
        ),
        collision_pair=CollisionPair(
            pair_id="COL_DISTINCT_DEFECTS",
            residual_a=DiscreteResidual.from_fractions((1, 2), (0, 1), (0, 1)),
            residual_b=DiscreteResidual.from_fractions((0, 1), (1, 2), (0, 1)),
            description="Orthogonal defects with identical L1 norm but distinct supports",
        ),
        metamorphic_pair=MetamorphicPair(
            pair_id="META_COORDINATE_PERM",
            original=DiscreteResidual.from_fractions((1, 4), (-3, 4), (0, 1)),
            transformed=DiscreteResidual.from_fractions((-3, 4), (1, 4), (0, 1)),
            description="Permutation of coordinate indices preserving defect norm",
        ),
    )


class _CapabilityToken:
    """Internal private token preventing direct instantiation of AuthorityCapability."""
    pass


_SOVEREIGN_TOKEN = _CapabilityToken()


@dataclass(frozen=True)
class AuthorityCapability:
    """Protected authority capability object.
    
    Cannot be constructed directly by untrusted code or runtime execution results.
    Only SovereignDescentVerifier holds the unforgeable sovereign token required to mint.
    """
    grantee: str
    scope: str
    verifier_id: str
    _token: _CapabilityToken = field(repr=False)

    def __post_init__(self) -> None:
        if self._token is not _SOVEREIGN_TOKEN:
            raise CapabilityViolationError(
                "AuthorityCapability cannot be instantiated directly by untrusted code. "
                "Only an authorized SovereignDescentVerifier can issue authority capabilities."
            )


@dataclass(frozen=True)
class RuntimeResult:
    """Standard runtime result carrying execution logs and metrics."""
    result_id: str
    output_data: str
    residual: Optional[DiscreteResidual] = None
    is_halted: bool = True
    detector_passed: bool = False

    def compute_hash(self) -> str:
        """Computes cryptographic digest of the result payload."""
        h = hashlib.sha256()
        h.update(self.result_id.encode("utf-8"))
        h.update(b":")
        h.update(self.output_data.encode("utf-8"))
        if self.residual is not None:
            h.update(b":")
            coords_str = ",".join(f"{c.numerator}/{c.denominator}" for c in self.residual.coordinates)
            h.update(coords_str.encode("utf-8"))
        return h.hexdigest()

    def to_authority_capability(self) -> None:
        """Firewall rule: RuntimeResult cannot construct AuthorityCapability."""
        raise CapabilityViolationError(
            f"Capability Firewall: RuntimeResult {self.result_id} cannot construct "
            f"an AuthorityCapability."
        )


@dataclass(frozen=True)
class AuthorityWitness:
    """Sealed authority token constructible only by sovereign descent verifier.
    
    Binds the verifier, specific result_id, content hash, cryptographic signature,
    and internal unforgeable sovereign capability token.
    """
    verifier_id: str
    result_id: str
    content_hash: str
    signature: str
    _token: _CapabilityToken = field(repr=False)

    def __post_init__(self) -> None:
        if self._token is not _SOVEREIGN_TOKEN:
            raise CapabilityViolationError(
                "AuthorityWitness cannot be instantiated directly by untrusted code. "
                "Only an authorized SovereignDescentVerifier can issue authority witnesses."
            )

    def is_valid_signature(self, verifier_secret: str) -> bool:
        """Validates HMAC signature against known verifier secret."""
        if not verifier_secret or not self.verifier_id or not self.result_id or not self.content_hash or not self.signature:
            return False
        expected = hmac.new(
            verifier_secret.encode("utf-8"),
            f"{self.verifier_id}:{self.result_id}:{self.content_hash}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, self.signature)


class SovereignDescentVerifier:
    """Sovereign descent authority verifier holding cryptographic verification credentials."""

    def __init__(self, verifier_id: str, secret_key: str):
        self.verifier_id = verifier_id
        self.secret_key = secret_key

    def verify_and_issue_witness(
        self,
        result: RuntimeResult,
    ) -> AuthorityWitness:
        """Validates descent over discrete residual and issues a bound authority witness."""
        if result.residual is None or not result.residual.is_exact_zero:
            raise ValueError(
                f"SovereignDescentVerifier {self.verifier_id}: cannot issue witness for "
                f"unresolved residual norm {result.residual.norm1 if result.residual else 'None'}."
            )
        content_hash = result.compute_hash()
        sig = hmac.new(
            self.secret_key.encode("utf-8"),
            f"{self.verifier_id}:{result.result_id}:{content_hash}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return AuthorityWitness(
            verifier_id=self.verifier_id,
            result_id=result.result_id,
            content_hash=content_hash,
            signature=sig,
            _token=_SOVEREIGN_TOKEN,
        )

    def mint_capability(self, witness: AuthorityWitness, scope: str = "EXECUTE") -> AuthorityCapability:
        """Mints an AuthorityCapability using the internal sovereign token."""
        if not witness.is_valid_signature(self.secret_key):
            raise CapabilityViolationError("Invalid witness signature: capability minting refused.")
        return AuthorityCapability(
            grantee=witness.result_id,
            scope=scope,
            verifier_id=self.verifier_id,
            _token=_SOVEREIGN_TOKEN,
        )


@dataclass(frozen=True)
class SixAxisEvidenceLattice:
    """The six independent verification axes."""
    mathematical: bool = False
    mechanization: bool = False
    implementation: bool = False
    empirical: bool = False
    security: bool = False
    authority: bool = False

    def can_auto_promote(self, source_axis: str, target_axis: str) -> bool:
        """Rule: Green on one axis NEVER promotes or greens another axis."""
        return False

    def is_fully_verified(self) -> bool:
        """Deployment requires all six independent axes to be true."""
        return (
            self.mathematical
            and self.mechanization
            and self.implementation
            and self.empirical
            and self.security
            and self.authority
        )


class StructuralVerificationGate:
    """Evaluates runtime outputs under detector adequacy and structural descent discipline."""

    def __init__(self, authorized_verifiers: Optional[dict[str, str]] = None):
        """Initializes gate with trusted verifier ID -> secret key registry."""
        self.authorized_verifiers = dict(authorized_verifiers or {})

    def register_verifier(self, verifier_id: str, secret_key: str) -> None:
        self.authorized_verifiers[verifier_id] = secret_key

    def evaluate_result(
        self,
        result: RuntimeResult,
        calibration_record: Optional[MinimumCalibrationRecord],
        detector: Optional[Callable[[DiscreteResidual], bool]] = None,
        authority_witness: Optional[AuthorityWitness] = None,
    ) -> TerminalVerdict:
        """Route runtime result into a terminal verdict under fail-closed discipline."""
        # 1. Syntactic halt check
        if not result.is_halted:
            return TerminalVerdict.FLUENT_HALT_NON_AUTHORITY

        # 2. Primary detector pass check
        if not result.detector_passed:
            return TerminalVerdict.REFUSAL_DEFECT

        # 3. Minimum calibration record check (fail-closed if absent)
        if calibration_record is None:
            return TerminalVerdict.DETECTOR_INADEQUATE

        # 4. If detector is provided, execute calibration cases
        if detector is not None:
            cal_result = calibration_record.execute_calibration(detector)
            if not cal_result.passed:
                return TerminalVerdict.DETECTOR_INADEQUATE

        # 5. Authority witness validation
        if authority_witness is not None:
            # Type and sealed capability check
            if not isinstance(authority_witness, AuthorityWitness):
                return TerminalVerdict.REFUSAL_DEFECT

            if getattr(authority_witness, "_token", None) is not _SOVEREIGN_TOKEN:
                return TerminalVerdict.REFUSAL_DEFECT

            # Non-empty field validation
            if (
                not authority_witness.verifier_id
                or not authority_witness.result_id
                or not authority_witness.content_hash
                or not authority_witness.signature
            ):
                return TerminalVerdict.REFUSAL_DEFECT

            # Check authorized verifier registration
            secret = self.authorized_verifiers.get(authority_witness.verifier_id)
            if not secret:
                return TerminalVerdict.REFUSAL_DEFECT

            # Check that witness is strictly bound to this exact result
            if authority_witness.result_id != result.result_id:
                return TerminalVerdict.REFUSAL_DEFECT

            if authority_witness.content_hash != result.compute_hash():
                return TerminalVerdict.REFUSAL_DEFECT

            # Check cryptographic signature authenticity
            if not authority_witness.is_valid_signature(secret):
                return TerminalVerdict.REFUSAL_DEFECT

            # Check underlying residual is exact zero (authority only on zero obstruction)
            if result.residual is None or not result.residual.is_exact_zero:
                return TerminalVerdict.REFUSAL_DEFECT

            # All structural and provenance descent checks passed
            return TerminalVerdict.AUTHORITY_CERTIFIED

        # Fluent completion with passed detector but no authority witness
        return TerminalVerdict.FLUENT_HALT_NON_AUTHORITY


@dataclass(frozen=True)
class FinitePartitionCoverage:
    """Finite calibration completeness engine with sharp partition coverage bounds.
    
    Mathematical Model:
    - Finite carrier X decomposed into disjoint equivalence classes under invariant rewrites.
    - Specification A: X -> {0,1}, Detector D: X -> {0,1}.
    - Condition: A and D are class-constant on each partition class.
    - Theorem: D = A on X <=> forall r in R, D(r) = A(r), where R contains a representative of each class.
    - Sharpness: omitting any class admits a class-constant counterexample detector.
    """
    classes: tuple[tuple[DiscreteResidual, ...], ...]

    @property
    def carrier(self) -> tuple[DiscreteResidual, ...]:
        return tuple(elem for eq_class in self.classes for elem in eq_class)

    def is_class_constant(self, predicate: Callable[[DiscreteResidual], bool]) -> bool:
        """Verifies predicate evaluates identically on all elements within each equivalence class."""
        for eq_class in self.classes:
            if not eq_class:
                continue
            first_val = predicate(eq_class[0])
            for elem in eq_class[1:]:
                if predicate(elem) != first_val:
                    return False
        return True

    def verify_coverage(
        self,
        spec: Callable[[DiscreteResidual], bool],
        detector: Callable[[DiscreteResidual], bool],
        representatives: tuple[DiscreteResidual, ...],
    ) -> tuple[bool, Optional[str]]:
        """Verifies if representative set R proves D = A on carrier X."""
        if not self.is_class_constant(spec):
            return False, "Specification A is not class-constant over declared partition"
        if not self.is_class_constant(detector):
            return False, "Detector D is not class-constant over declared partition"

        # Check coverage: does R cover every equivalence class?
        covered_classes: set[int] = set()
        for r in representatives:
            found = False
            for idx, eq_class in enumerate(self.classes):
                if r in eq_class:
                    covered_classes.add(idx)
                    found = True
                    break
            if not found:
                return False, f"Representative {r} does not belong to carrier X"

        if len(covered_classes) < len(self.classes):
            omitted = set(range(len(self.classes))) - covered_classes
            return False, f"Coverage incomplete: omitted equivalence classes {sorted(omitted)}"

        # Evaluate D(r) == A(r) on representatives
        for r in representatives:
            if detector(r) != spec(r):
                return False, f"Detector disagreement on representative {r}: D({r})={detector(r)} != A({r})={spec(r)}"

        return True, None

    def construct_omitted_class_counterexample(
        self,
        spec: Callable[[DiscreteResidual], bool],
        representatives: tuple[DiscreteResidual, ...],
    ) -> tuple[DiscreteResidual, Callable[[DiscreteResidual], bool]]:
        """Sharpness witness: given incomplete representatives R, constructs a class-constant detector
        that agrees with spec on all tested classes but disagrees on the first omitted class.
        """
        covered_classes: set[int] = set()
        for r in representatives:
            for idx, eq_class in enumerate(self.classes):
                if r in eq_class:
                    covered_classes.add(idx)
                    break

        omitted = sorted(set(range(len(self.classes))) - covered_classes)
        if not omitted:
            raise ValueError("Cannot construct counterexample: representative coverage is complete.")

        target_omitted_idx = omitted[0]
        omitted_witness = self.classes[target_omitted_idx][0]

        def counterexample_detector(r: DiscreteResidual) -> bool:
            for idx, eq_class in enumerate(self.classes):
                if r in eq_class:
                    if idx == target_omitted_idx:
                        return not spec(r)
                    else:
                        return spec(r)
            return False

        return omitted_witness, counterexample_detector


@dataclass(frozen=True)
class MasterDemoScenarioResult:
    scenario_id: str
    name: str
    description: str
    expected_verdict: TerminalVerdict
    actual_verdict: TerminalVerdict
    passed: bool


def run_master_demo_scenarios() -> list[MasterDemoScenarioResult]:
    """Executes the canonical seven-scenario benchmark demonstrating the Authority Firewall.
    
    Demonstrates:
    - C1: Fluent compliance audit without structural verification -> FluentHaltNonAuthority
    - O1: Missing descent packet -> DetectorInadequate
    - O2: Shape-only pass with open residual -> RefusalDefect
    - O3: Budget exhaustion -> RefusalDefect
    - O4: Continuum claim without finite shadow -> DetectorInadequate
    - O5: Re-encoded claim without certified transport chi_F -> RefusalDefect
    - O6: Multi-LLM consensus without support sieve -> RefusalDefect
    - O7: Authentic sovereign descent witness over exact zero residual -> AuthorityCertified
    """
    secret = "master_demo_secret_2026"
    verifier = SovereignDescentVerifier(verifier_id="SOV_MASTER", secret_key=secret)
    gate = StructuralVerificationGate()
    gate.register_verifier("SOV_MASTER", secret)
    cal_record = create_canonical_calibration_record()

    def sound_det(r: DiscreteResidual) -> bool:
        return r.is_exact_zero

    scenarios = [
        # Scenario C1: Classical fluent compliance audit
        (
            "C1",
            "Classical Fluent Halting",
            "Model emits fluent SOC2 compliance paragraph without structural descent witness.",
            RuntimeResult(
                result_id="SCENARIO_C1",
                output_data="Fully compliant with SOC2 Type II. Residual risk is negligible.",
                residual=DiscreteResidual.from_ints(0, 0, 0),
                is_halted=True,
                detector_passed=True,
            ),
            cal_record,
            sound_det,
            None,
            TerminalVerdict.FLUENT_HALT_NON_AUTHORITY,
        ),
        # Scenario O1: Same claim, no finite descent calibration
        (
            "O1",
            "Missing Descent Packet",
            "Claim submitted without calibration record or descent packet.",
            RuntimeResult(
                result_id="SCENARIO_O1",
                output_data="Compliance claim without descent packet",
                residual=DiscreteResidual.from_ints(0, 0, 0),
                is_halted=True,
                detector_passed=True,
            ),
            None,  # Missing calibration record
            sound_det,
            None,
            TerminalVerdict.DETECTOR_INADEQUATE,
        ),
        # Scenario O2: Shape-only pass, residual open
        (
            "O2",
            "Open Residual Conflict",
            "Partial residual declared open with non-zero L1 norm.",
            RuntimeResult(
                result_id="SCENARIO_O2",
                output_data="Partial match with non-zero boundary defect",
                residual=DiscreteResidual.from_fractions((1, 2), (-1, 2)),
                is_halted=True,
                detector_passed=False,
            ),
            cal_record,
            sound_det,
            None,
            TerminalVerdict.REFUSAL_DEFECT,
        ),
        # Scenario O3: Resource budget exhaustion
        (
            "O3",
            "Budget Exhaustion",
            "Evaluation steps exceed allocated budget (honest refusal).",
            RuntimeResult(
                result_id="SCENARIO_O3",
                output_data="Budget limit reached before closure",
                residual=DiscreteResidual.from_ints(1, 0, 0),
                is_halted=True,
                detector_passed=False,
            ),
            cal_record,
            sound_det,
            None,
            TerminalVerdict.REFUSAL_DEFECT,
        ),
        # Scenario O4: Continuum claim without finite shadow query
        (
            "O4",
            "Continuum Claim Debt",
            "Infinite-dimensional continuum assertion lacking finite query projection.",
            RuntimeResult(
                result_id="SCENARIO_O4",
                output_data="Continuum assertion without finite shadow coverage",
                residual=DiscreteResidual.from_ints(0, 0, 0),
                is_halted=True,
                detector_passed=True,
            ),
            None,  # No finite shadow calibration
            sound_det,
            None,
            TerminalVerdict.DETECTOR_INADEQUATE,
        ),
        # Scenario O5: Re-encoded claim without certified transport chi_F
        (
            "O5",
            "Uncertified Transport",
            "Representation shift without certified transport loss accounting.",
            RuntimeResult(
                result_id="SCENARIO_O5",
                output_data="Re-encoded representation with untracked loss",
                residual=DiscreteResidual.from_ints(2, 0, 0),
                is_halted=True,
                detector_passed=False,
            ),
            cal_record,
            sound_det,
            None,
            TerminalVerdict.REFUSAL_DEFECT,
        ),
        # Scenario O6: Multi-LLM consensus without support sieve
        (
            "O6",
            "Consensus Laundering",
            "Majority vote across models lacking independent component descent.",
            RuntimeResult(
                result_id="SCENARIO_O6",
                output_data="Consensus agreement without independent verification",
                residual=DiscreteResidual.from_ints(0, 1, 0),
                is_halted=True,
                detector_passed=False,
            ),
            cal_record,
            sound_det,
            None,
            TerminalVerdict.REFUSAL_DEFECT,
        ),
        # Scenario O7: Authentic sovereign descent witness over exact zero residual
        (
            "O7",
            "Authentic Sovereign Certification",
            "Verified zero obstruction with cryptographic sovereign descent witness.",
            RuntimeResult(
                result_id="SCENARIO_O7",
                output_data="Exact zero boundary defect with sovereign proof",
                residual=DiscreteResidual.from_ints(0, 0, 0),
                is_halted=True,
                detector_passed=True,
            ),
            cal_record,
            sound_det,
            verifier.verify_and_issue_witness(
                RuntimeResult(
                    result_id="SCENARIO_O7",
                    output_data="Exact zero boundary defect with sovereign proof",
                    residual=DiscreteResidual.from_ints(0, 0, 0),
                    is_halted=True,
                    detector_passed=True,
                )
            ),
            TerminalVerdict.AUTHORITY_CERTIFIED,
        ),
    ]

    results: list[MasterDemoScenarioResult] = []
    for sc_id, name, desc, res, rec, det, wit, expected in scenarios:
        actual = gate.evaluate_result(res, calibration_record=rec, detector=det, authority_witness=wit)
        results.append(
            MasterDemoScenarioResult(
                scenario_id=sc_id,
                name=name,
                description=desc,
                expected_verdict=expected,
                actual_verdict=actual,
                passed=(actual == expected),
            )
        )
    return results
