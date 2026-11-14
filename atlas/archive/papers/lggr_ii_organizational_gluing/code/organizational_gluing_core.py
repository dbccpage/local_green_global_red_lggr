"""
Finite organizational evaluator model for Local Green, Global Red II.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, FrozenSet, List, Optional, Tuple


def _require_exact_bool(value: Any, field_name: str) -> bool:
    """Validate a Python Boolean value, rejecting int, float, str, None, etc."""
    if type(value) is not bool:
        raise TypeError(
            f"{field_name} must be an exact bool, got "
            f"{type(value).__name__} ({value!r})"
        )
    return value


def _exact_bool_to_bit(value: Any, source: str) -> int:
    """Validate a Python Boolean verdict and return its integer encoding."""
    if type(value) is not bool:
        raise ValueError(
            f"{source} must return an exact bool, got "
            f"{type(value).__name__} ({value!r})"
        )
    return int(value)


class DefectSign(Enum):
    """Trichotomy of evaluator gluing defect Δ_E."""
    LOCAL_GREEN_GLOBAL_RED = -1   # E_G = 0, ∏ E_i = 1 (failure of composition)
    EVALUATOR_AGREEMENT = 0       # E_G = ∏ E_i (evaluator agreement; does NOT imply closure)
    UNEARNED_SUCCESS = 1          # E_G = 1, ∏ E_i = 0 (global pass despite local failure)


class EvidenceCeiling(Enum):
    """Evidence labels retained by the trace-record adapter."""
    BoundaryChecked = "BoundaryChecked"
    EmpiricalOracleRequired = "EmpiricalOracleRequired"
    CertifiedTerminal = "CertifiedTerminal"


@dataclass(frozen=True)
class BoundaryCut:
    """Declared composition cut b with incoming and outgoing pole tokens."""
    name: str
    incoming_token: str
    outgoing_token: str
    description: str = ""

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("BoundaryCut must have a non-empty name.")
        if not self.incoming_token.strip() or not self.outgoing_token.strip():
            raise ValueError("BoundaryCut requires non-empty incoming and outgoing pole tokens.")


@dataclass(frozen=True)
class FunctionUnit:
    """Operational function or departmental unit F_i."""
    name: str
    department: str
    description: str = ""


@dataclass(frozen=True)
class LocalValidator:
    """Local validator E_i evaluating isolated departmental performance."""
    name: str
    function_unit: FunctionUnit
    evaluator_fn: Callable[[Any], bool]

    def evaluate(self, trace: Any) -> int:
        return _exact_bool_to_bit(
            self.evaluator_fn(trace), f"LocalValidator {self.name}"
        )


@dataclass(frozen=True)
class BoundaryOwner:
    """Declared boundary owner object O = (Authority, Accountability)."""
    name: str
    role: str
    has_authority: bool      # A: standing to install boundary tests and modify E_i
    has_accountability: bool # C: grading and incentives tied directly to E_G

    def __post_init__(self):
        _require_exact_bool(self.has_authority, "BoundaryOwner.has_authority")
        _require_exact_bool(self.has_accountability, "BoundaryOwner.has_accountability")

    @property
    def is_complete(self) -> bool:
        """Authority closure G_auth requires both authority (A) and accountability (C)."""
        return self.has_authority and self.has_accountability


@dataclass(frozen=True)
class EvaluatorGluingDefect:
    """
    Evaluator gluing defect:
    Δ_E(b) = E_G(b) - ∏_i E_i(b) ∈ {-1, 0, +1}.
    """
    delta_E: int
    global_evaluator_pass: int
    local_evaluator_passes: Tuple[int, ...]
    local_product: int

    def __post_init__(self):
        try:
            passes = tuple(self.local_evaluator_passes)
        except TypeError:
            raise TypeError("local_evaluator_passes must be an iterable of binary integers (0 or 1)")
        object.__setattr__(self, "local_evaluator_passes", passes)
        if type(self.delta_E) is not int or self.delta_E not in (-1, 0, 1):
            raise ValueError(f"EvaluatorGluingDefect delta_E must be in {{-1, 0, 1}}, got {self.delta_E}")
        if type(self.global_evaluator_pass) is not int or self.global_evaluator_pass not in (0, 1):
            raise ValueError("global_evaluator_pass must be a binary integer (0 or 1)")
        for p in self.local_evaluator_passes:
            if type(p) is not int or p not in (0, 1):
                raise ValueError("local_evaluator_passes must be binary integers (0 or 1)")
        if type(self.local_product) is not int or self.local_product not in (0, 1):
            raise ValueError("local_product must be a binary integer (0 or 1)")
        expected_prod = 1 if all(p == 1 for p in self.local_evaluator_passes) else 0
        if self.local_product != expected_prod:
            raise ValueError(f"local_product mismatch: expected {expected_prod}, got {self.local_product}")
        expected_delta = self.global_evaluator_pass - self.local_product
        if self.delta_E != expected_delta:
            raise ValueError(f"delta_E mismatch: expected {expected_delta}, got {self.delta_E}")

    @property
    def is_local_green_global_red(self) -> bool:
        return self.delta_E == -1

    @property
    def is_evaluator_agreement(self) -> bool:
        """Δ_E = 0: evaluator agreement (not organizational closure)."""
        return self.delta_E == 0

    @property
    def is_unearned_success(self) -> bool:
        return self.delta_E == 1

    @property
    def defect_sign(self) -> DefectSign:
        return DefectSign(self.delta_E)


class OrganizationalEvaluatorSystem:
    """
    Organizational evaluator system:
    S_b = ({F_i}, {E_i}, E_G, O)
    """

    def __init__(
        self,
        cut: BoundaryCut,
        functions: List[FunctionUnit],
        validators: List[LocalValidator],
        global_evaluator: Callable[[Any], bool],
        boundary_owner: Optional[BoundaryOwner] = None,
    ):
        if not validators:
            raise ValueError("OrganizationalEvaluatorSystem requires at least one local validator.")
        self.cut = cut
        self.functions = list(functions)
        self.validators = list(validators)
        self.global_evaluator = global_evaluator
        self.boundary_owner = boundary_owner

    def evaluate(self, trace: Any) -> EvaluatorGluingDefect:
        """Evaluates trace and computes Δ_E(b) = E_G(b) - ∏ E_i(b)."""
        local_passes = tuple(v.evaluate(trace) for v in self.validators)
        local_prod = 1 if all(p == 1 for p in local_passes) else 0

        eg_val = _exact_bool_to_bit(self.global_evaluator(trace), "Global evaluator")

        delta = eg_val - local_prod
        return EvaluatorGluingDefect(
            delta_E=delta,
            global_evaluator_pass=eg_val,
            local_evaluator_passes=local_passes,
            local_product=local_prod,
        )


@dataclass(frozen=True)
class OrganizationalClosureConditions:
    """
    The three declared organizational boundary governance prerequisites:
    G_rep (Representational Sufficiency)
    G_auth (Authority Closure)
    G_time (Temporal Coherence)

    Note: As established by Lemma 4.4, these conditions do NOT force evaluator
    factorization (E_G = ∏ E_i). Boundary closure requires both evaluator agreement
    and governance prerequisites.
    """
    g_rep: bool
    g_auth: bool
    g_time: bool

    def __post_init__(self):
        _require_exact_bool(self.g_rep, "OrganizationalClosureConditions.g_rep")
        _require_exact_bool(self.g_auth, "OrganizationalClosureConditions.g_auth")
        _require_exact_bool(self.g_time, "OrganizationalClosureConditions.g_time")

    @property
    def governance_prerequisites_satisfied(self) -> bool:
        """Conjunction of declared governance prerequisites: G_rep ∧ G_auth ∧ G_time."""
        return self.g_rep and self.g_auth and self.g_time

    def is_checked_closure_eligible(self, defect: EvaluatorGluingDefect) -> bool:
        """
        Checked closure eligibility requires BOTH evaluator agreement (Δ_E = 0)
        AND governance prerequisites (G_rep ∧ G_auth ∧ G_time).
        Per Lemma 4.4, governance alone does NOT force evaluator factorization.
        """
        return defect.delta_E == 0 and self.governance_prerequisites_satisfied

    def audit_boundary_governance(self, defect: EvaluatorGluingDefect) -> Dict[str, Any]:
        """
        Audits evaluator defect and governance prerequisites separately.
        Per Lemma 4.4, governance prerequisites do NOT force evaluator factorization.
        """
        evaluator_agrees = (defect.delta_E == 0)
        gov_ok = self.governance_prerequisites_satisfied
        return {
            "evaluator_agrees": evaluator_agrees,
            "delta_E": defect.delta_E,
            "governance_prerequisites_satisfied": gov_ok,
            "closure_eligible": evaluator_agrees and gov_ok,
            "failed_prerequisites": [
                k for k, v in [("G_rep", self.g_rep), ("G_auth", self.g_auth), ("G_time", self.g_time)]
                if not v
            ],
        }

    def contrapositive_audit(self, defect: EvaluatorGluingDefect) -> Dict[str, Any]:
        """
        Backward-compatible audit method returning boundary governance status.
        """
        return self.audit_boundary_governance(defect)


class DefinitionalNecessityGuard:
    """
    Enforces the Organizational Boundary Closure Lemma (§5):
    L^1_declared(b) = 0 ⟹ G_auth(b)

    This is a NECESSITY GUARD only. It asserts that G_auth is required
    when declared closure eligibility is claimed. It does NOT compute
    full closure eligibility (which additionally requires Δ_E = 0).
    """

    @staticmethod
    def assert_auth_required_for_declared_closure(
        conditions: OrganizationalClosureConditions,
        declared_L1_zero: bool,
    ) -> None:
        """
        If declared_L1_zero is True, G_auth must be present by definition.
        Raises PermissionError on violation. Does not return eligibility.
        """
        _require_exact_bool(declared_L1_zero, "declared_L1_zero")
        if declared_L1_zero and not conditions.g_auth:
            raise PermissionError(
                "Violation of Closure Lemma necessity: declared closure eligibility requires G_auth."
            )

    @staticmethod
    def assert_owner_alone_is_insufficient(
        g_auth: bool, g_rep: bool, g_time: bool
    ) -> bool:
        """
        An owner object alone (G_auth=True) does not suffice if G_rep or G_time fails.
        """
        _require_exact_bool(g_auth, "g_auth")
        _require_exact_bool(g_rep, "g_rep")
        _require_exact_bool(g_time, "g_time")
        if g_auth and (not g_rep or not g_time):
            # Owner present, but boundary remains unclosed
            return True
        return False


class NonAdditivityAuditor:
    """
    Mechanizes Lemma 4.2.1: Non-Additivity of Scalar Channel Defects.
    Direct scalar sums of channel defects can leave {-1, 0, 1}.
    Provides Shapley value coalitional attribution as a non-disjoint alternative.
    """

    @staticmethod
    def direct_scalar_sum(channel_defects: List[int]) -> int:
        """Computes direct scalar sum and detects range violations."""
        total = sum(channel_defects)
        return total

    @staticmethod
    def is_range_violation(total: int) -> bool:
        return total not in (-1, 0, 1)

    @staticmethod
    def compute_shapley_attribution(
        players: List[str],
        coalitional_value_fn: Callable[[FrozenSet[str]], float],
    ) -> Dict[str, float]:
        r"""
        Computes exact Shapley attribution over non-orthogonal conditions:
        φ_i = ∑_{S ⊆ N \ {i}} (|S|!(|N|-|S|-1)! / |N|!) [v(S ∪ {i}) - v(S)]

        Rejects duplicate player identifiers and non-finite coalition values.
        """
        if len(players) != len(set(players)):
            raise ValueError("players list must contain unique identifiers.")

        n = len(players)
        shapley_values: Dict[str, float] = {p: 0.0 for p in players}

        for i, player in enumerate(players):
            other_players = [p for p in players if p != player]
            phi_i = 0.0

            for r in range(len(other_players) + 1):
                for subset in itertools.combinations(other_players, r):
                    s_set = frozenset(subset)
                    with_player = s_set | {player}
                    v_with = coalitional_value_fn(with_player)
                    v_without = coalitional_value_fn(s_set)
                    marginal_contribution = v_with - v_without
                    if not math.isfinite(marginal_contribution):
                        raise ValueError("coalitional_value_fn returned non-finite value.")
                    weight = (math.factorial(len(s_set)) * math.factorial(n - len(s_set) - 1)) / math.factorial(n)
                    phi_i += weight * marginal_contribution

            shapley_values[player] = phi_i

        return shapley_values


class WeakSufficiencyAuditor:
    """
    Mechanizes Lemma 4.4: Weak Boundary Sufficiency Does Not Force Factorization.
    Exhibits the finite Boolean counterexample where representation recovers E_G,
    G_auth and G_time hold, yet E_G ≠ E_1 * E_2.
    """

    @staticmethod
    def evaluate_counterexample() -> Dict[str, Any]:
        e1 = 1
        e2 = 1
        eg = 0
        rep = (1, 1, 0)  # rep[2] = 0 = eg (weak sufficiency holds)
        g_auth = True
        g_time = True

        weak_sufficiency = (rep[2] == eg)
        local_product = e1 * e2
        evaluator_factorization = (eg == local_product)

        return {
            "weak_sufficiency_holds": weak_sufficiency,
            "g_auth": g_auth,
            "g_time": g_time,
            "evaluator_factorization_holds": evaluator_factorization,
            "delta_E": eg - local_product,  # -1
            "refutes_factorization_implication": weak_sufficiency and g_auth and g_time and (not evaluator_factorization),
        }


class DetectorAdequacyGuard:
    """
    Distinguish a negative witness from a zero-defect observation:
    - RED (Δ_E = -1) is sound as a detection of non-factorization under the declared assignment.
    - GREEN (Δ_E = 0) is unsound as a certificate without an adequacy certificate.
    """

    @staticmethod
    def is_aligned_validator_collapsing(
        validators: List[LocalValidator],
        sample_traces: List[Any],
        global_evaluator: Callable[[Any], bool],
    ) -> bool:
        """
        Evaluate the finite collapse proxy used by M7.

        The result is true exactly when the product of all supplied local
        validators equals E_G on every supplied sample trace. A single local
        validator copying E_G is therefore insufficient when a peer validator
        makes the product disagree with E_G.
        """
        if not validators:
            raise ValueError("validators must be non-empty to evaluate detector alignment.")
        if not sample_traces:
            raise ValueError("sample_traces must be non-empty to evaluate detector alignment.")
        matches: List[bool] = []
        for trace in sample_traces:
            local_passes = tuple(v.evaluate(trace) for v in validators)
            local_product = 1 if all(value == 1 for value in local_passes) else 0
            global_value = _exact_bool_to_bit(global_evaluator(trace), "Global evaluator")
            matches.append(local_product == global_value)
        return all(matches)

    @staticmethod
    def audit_verdict(
        defect: EvaluatorGluingDefect,
        has_detector_adequacy_cert: bool = False,
    ) -> Dict[str, Any]:
        """
        Report the finite evaluator defect without promoting it to certification.

        - RED (Δ_E = -1): Sound detection of non-factorization under declared assignment.
        - GREEN (Δ_E = 0):
            * If EG = 1, prod = 1: Observed passing agreement. Caller-declared adequacy
              is reported as a diagnostic observation, but cannot certify organizational
              closure without verified boundary owner and governance audit.
            * If EG = 0, prod = 0: Joint failure agreement (EG=0, prod=0). Agreement at failure
              is NOT organizational success.
        - UNEARNED_SUCCESS (Δ_E = +1): Diagnostic anomaly.

        Note: Certified closure is never emitted by this diagnostic helper (certified=False).
        """
        _require_exact_bool(has_detector_adequacy_cert, "has_detector_adequacy_cert")
        if defect.delta_E == -1:
            return {
                "verdict": "RED",
                "soundness": "SOUND_AS_DETECTION",
                "certified": False,
                "message": "Local green, global red detected at composition boundary.",
            }
        elif defect.delta_E == 0:
            if defect.global_evaluator_pass == 0:
                return {
                    "verdict": "AGREEMENT_AT_FAILURE",
                    "soundness": "OBSERVED_JOINT_FAILURE",
                    "certified": False,
                    "message": "Evaluator agreement at failing outcome (EG=0, prod=0); agreement does not denote organizational success.",
                }
            if not has_detector_adequacy_cert:
                return {
                    "verdict": "GREEN",
                    "soundness": "UNSOUND_AS_CERTIFICATE",
                    "certified": False,
                    "message": "Observed passing evaluator agreement, but detector adequacy has not been established; diagnostic only.",
                }
            return {
                "verdict": "GREEN",
                "soundness": "OBSERVED_AGREEMENT_ADEQUACY_DECLARED",
                "certified": False,
                "message": "Observed agreement at passing outcome with caller-declared adequacy certificate; diagnostic only.",
            }
        else:
            return {
                "verdict": "UNEARNED_SUCCESS",
                "soundness": "DIAGNOSTIC_ANOMALY",
                "certified": False,
                "message": "Global pass despite local failure (Δ_E = +1).",
            }


class CaseStudyFactory:
    """
    Legacy named Boolean examples.

    The names preserve the public API of earlier releases. The returned values
    are illustrative inputs, not empirical findings.
    """

    @staticmethod
    def create_pear_therapeutics() -> Tuple[OrganizationalEvaluatorSystem, OrganizationalClosureConditions, EvaluatorGluingDefect]:
        """Return one fixed local-pass/global-fail assignment."""
        cut = BoundaryCut("Pear_Handoff", "Prescriptions_Written", "Insurance_Reimbursement", "Digital therapeutics payer cut")
        f_reg = FunctionUnit("Regulatory", "Clinical/Regulatory", "FDA clearance")
        f_sales = FunctionUnit("CommercialSales", "Sales", "Prescriptions written")

        # Illustrative Boolean model assignment
        trace = {"fda_authorized": True, "rx_written": True, "enterprise_viability_threshold_met": False}

        v_fda = LocalValidator("FDA_Clearance", f_reg, lambda t: t["fda_authorized"])
        v_rx = LocalValidator("Prescriptions", f_sales, lambda t: t["rx_written"])
        global_eval = lambda t: t["enterprise_viability_threshold_met"]

        # Boundary owner missing / unaccountable to reimbursement (model assignment)
        owner = BoundaryOwner("BrandManager", "Product Lead", has_authority=True, has_accountability=False)

        system = OrganizationalEvaluatorSystem(cut, [f_reg, f_sales], [v_fda, v_rx], global_eval, owner)
        conditions = OrganizationalClosureConditions(g_rep=False, g_auth=False, g_time=True)
        defect = system.evaluate(trace)
        return system, conditions, defect

    @staticmethod
    def create_northvolt_ett() -> Tuple[OrganizationalEvaluatorSystem, OrganizationalClosureConditions, EvaluatorGluingDefect]:
        """Return a second fixed local-pass/global-fail assignment."""
        cut = BoundaryCut("Northvolt_Handoff", "FAT_Signoff", "Volume_Production", "Battery cell scaling cut")
        f_fat = FunctionUnit("Commissioning", "FAT", "Machine-level signoff")
        f_ass = FunctionUnit("Assembly", "Manufacturing", "Cell assembly")

        trace = {"fat_passed": True, "assembly_passed": True, "volume_delivery": False}

        v_fat = LocalValidator("FAT_Validator", f_fat, lambda t: t["fat_passed"])
        v_ass = LocalValidator("Assembly_Validator", f_ass, lambda t: t["assembly_passed"])
        global_eval = lambda t: t["volume_delivery"]

        owner = BoundaryOwner("PlantLead", "Plant Manager", has_authority=False, has_accountability=True)

        system = OrganizationalEvaluatorSystem(cut, [f_fat, f_ass], [v_fat, v_ass], global_eval, owner)
        conditions = OrganizationalClosureConditions(g_rep=False, g_auth=False, g_time=True)
        defect = system.evaluate(trace)
        return system, conditions, defect

    @staticmethod
    def create_boeing_mcas() -> Tuple[OrganizationalEvaluatorSystem, OrganizationalClosureConditions, EvaluatorGluingDefect]:
        """Return a third fixed local-pass/global-fail assignment."""
        cut = BoundaryCut("Boeing_MCAS_Handoff", "Software_Flight_Control", "Pilot_Reaction_Envelope", "Safety interface cut")
        f_sw = FunctionUnit("FlightControl", "Software", "MCAS algorithm")
        f_aero = FunctionUnit("Aerodynamics", "Flight Sciences", "Simulator envelope")

        trace = {"sw_unit_test": True, "aero_envelope": True, "continuous_flight_safety": False}

        v_sw = LocalValidator("MCAS_Test", f_sw, lambda t: t["sw_unit_test"])
        v_aero = LocalValidator("Aero_Test", f_aero, lambda t: t["aero_envelope"])
        global_eval = lambda t: t["continuous_flight_safety"]

        # Fragmented authority across software, sensor assumptions, and training (model assignment)
        owner = None

        system = OrganizationalEvaluatorSystem(cut, [f_sw, f_aero], [v_sw, v_aero], global_eval, owner)
        conditions = OrganizationalClosureConditions(g_rep=False, g_auth=False, g_time=False)
        defect = system.evaluate(trace)
        return system, conditions, defect


@dataclass(frozen=True)
class ObservedPerformanceTrace:
    """Boolean trace consumed by the composition-record adapter."""
    contract_id: str
    composed_id: str
    left_id: str
    right_id: str
    local_left_pass: bool   # E1
    local_right_pass: bool  # E2
    global_pass: bool       # EG

    def __post_init__(self):
        for field_name in ("local_left_pass", "local_right_pass", "global_pass"):
            val = getattr(self, field_name)
            if not isinstance(val, bool):
                raise TypeError(
                    f"ObservedPerformanceTrace {field_name} must be a bool, got {type(val).__name__} ({val!r})"
                )


@dataclass(frozen=True)
class CompositionRecord:
    """Target composition record schema with strict invariant validation."""
    composed_id: str
    left_id: str
    right_id: str
    local_left_pass: bool
    local_right_pass: bool
    global_pass: bool
    delta_E: int
    evidence_ceiling: EvidenceCeiling = EvidenceCeiling.BoundaryChecked

    def __post_init__(self):
        for field_name in ("local_left_pass", "local_right_pass", "global_pass"):
            val = getattr(self, field_name)
            if not isinstance(val, bool):
                raise TypeError(
                    f"CompositionRecord {field_name} must be a bool, got {type(val).__name__} ({val!r})"
                )

        if type(self.delta_E) is not int or self.delta_E not in (-1, 0, 1):
            raise ValueError(f"CompositionRecord delta_E must be in {{-1, 0, 1}}, got {self.delta_E}")

        expected_delta = (1 if self.global_pass else 0) - (
            (1 if self.local_left_pass else 0) * (1 if self.local_right_pass else 0)
        )
        if self.delta_E != expected_delta:
            raise ValueError(f"CompositionRecord delta_E mismatch: expected {expected_delta}, got {self.delta_E}")

        if self.evidence_ceiling != EvidenceCeiling.BoundaryChecked:
            raise PermissionError(
                f"Prospective composition record ceiling is restricted to BoundaryChecked, got {self.evidence_ceiling}"
            )

    @classmethod
    def from_trace(
        cls,
        trace: ObservedPerformanceTrace,
        claimed_ceiling: EvidenceCeiling = EvidenceCeiling.EmpiricalOracleRequired,
    ) -> "CompositionRecord":
        """Maps observed trace to composition record, capping ceiling at BoundaryChecked."""
        left_val = 1 if trace.local_left_pass else 0
        right_val = 1 if trace.local_right_pass else 0
        global_val = 1 if trace.global_pass else 0
        delta = global_val - (left_val * right_val)

        effective_ceiling = EvidenceCeiling.BoundaryChecked

        return cls(
            composed_id=trace.composed_id,
            left_id=trace.left_id,
            right_id=trace.right_id,
            local_left_pass=trace.local_left_pass,
            local_right_pass=trace.local_right_pass,
            global_pass=trace.global_pass,
            delta_E=delta,
            evidence_ceiling=effective_ceiling,
        )


@dataclass(frozen=True)
class BooleanBoundary:
    """Finite Boolean boundary record matching the Lean `BooleanBoundary` fields."""

    e1: bool
    e2: bool
    e_g: bool
    rep: Tuple[bool, bool, bool]
    g_auth: bool
    g_time: bool

    def __post_init__(self) -> None:
        _require_exact_bool(self.e1, "BooleanBoundary.e1")
        _require_exact_bool(self.e2, "BooleanBoundary.e2")
        _require_exact_bool(self.e_g, "BooleanBoundary.e_g")
        _require_exact_bool(self.g_auth, "BooleanBoundary.g_auth")
        _require_exact_bool(self.g_time, "BooleanBoundary.g_time")
        if type(self.rep) is not tuple or len(self.rep) != 3:
            raise ValueError("BooleanBoundary.rep must be a 3-tuple of bools")
        _require_exact_bool(self.rep[0], "BooleanBoundary.rep[0]")
        _require_exact_bool(self.rep[1], "BooleanBoundary.rep[1]")
        _require_exact_bool(self.rep[2], "BooleanBoundary.rep[2]")


def weak_boundary_sufficiency(boundary: BooleanBoundary) -> bool:
    """The third representation coordinate recovers the global verdict."""
    return boundary.rep[2] == boundary.e_g


def product_sufficiency(boundary: BooleanBoundary) -> bool:
    """The recovered global coordinate equals the local product."""
    return boundary.rep[2] == (boundary.e1 and boundary.e2)


def evaluator_factorization(boundary: BooleanBoundary) -> bool:
    """The global verdict equals the local product."""
    return boundary.e_g == (boundary.e1 and boundary.e2)


@dataclass(frozen=True)
class ComposedTrace:
    """One composed trace `c = (left, right)`."""

    left: Any
    right: Any


def joint_carrier(
    pi1: Callable[[Any], Any],
    pi2: Callable[[Any], Any],
    trace: ComposedTrace,
) -> Tuple[Any, Any]:
    """Joint carrier `J(c) = (pi1(left), pi2(right))`."""
    return (pi1(trace.left), pi2(trace.right))


def carrier_local_product(
    e1: Callable[[Any], bool],
    e2: Callable[[Any], bool],
    pi1: Callable[[Any], Any],
    pi2: Callable[[Any], Any],
    trace: ComposedTrace,
) -> bool:
    """Local product of carrier-local evaluators on one trace."""
    left_pass = _require_exact_bool(e1(pi1(trace.left)), "e1")
    right_pass = _require_exact_bool(e2(pi2(trace.right)), "e2")
    return left_pass and right_pass


def org_delta(global_pass: bool, local_product: bool) -> int:
    """`Δ_E = E_G - L` on exact Booleans, encoded as integers 0 and 1."""
    global_bit = int(_require_exact_bool(global_pass, "global_pass"))
    local_bit = int(_require_exact_bool(local_product, "local_product"))
    return global_bit - local_bit


class FiniteTheoremCensus:
    """Finite checks for the Boolean equivalence and the carrier-class obstruction."""

    @staticmethod
    def product_sufficiency_iff_factorization_census() -> Dict[str, int]:
        """Evaluate every 8-bit Boolean boundary.

        Under weak recovery, product sufficiency and evaluator factorization
        are counted separately and then compared by the caller. Assignments
        that fail weak recovery are counted only when the two predicates disagree.
        """
        recovered = 0
        matched = 0
        unconditional_disagreements = 0
        for bits in itertools.product((False, True), repeat=8):
            boundary = BooleanBoundary(
                bits[0],
                bits[1],
                bits[2],
                (bits[3], bits[4], bits[5]),
                bits[6],
                bits[7],
            )
            same = product_sufficiency(boundary) == evaluator_factorization(boundary)
            if weak_boundary_sufficiency(boundary):
                recovered += 1
                matched += int(same)
            else:
                unconditional_disagreements += int(not same)
        return {
            "recovered": recovered,
            "matched": matched,
            "unconditional_disagreements": unconditional_disagreements,
        }

    @staticmethod
    def quotient_factor_table(
        traces: List[ComposedTrace],
        pi1: Callable[[Any], Any],
        pi2: Callable[[Any], Any],
        global_evaluator: Callable[[ComposedTrace], bool],
    ) -> Dict[str, Any]:
        """Build a quotient factor when each joint-carrier class has one verdict.

        A class that carries two global verdicts is returned in `blocked_classes`
        and is omitted from `factor`.
        """
        if not traces:
            raise ValueError("traces must be nonempty")
        classes: Dict[Tuple[Any, Any], set] = {}
        order: List[Tuple[Any, Any]] = []
        for trace in traces:
            key = joint_carrier(pi1, pi2, trace)
            verdict = _require_exact_bool(global_evaluator(trace), "global evaluator")
            if key not in classes:
                classes[key] = set()
                order.append(key)
            classes[key].add(verdict)
        factor: Dict[Tuple[Any, Any], bool] = {}
        blocked: List[Tuple[Any, Any]] = []
        for key in order:
            verdicts = classes[key]
            if len(verdicts) == 1:
                factor[key] = next(iter(verdicts))
            else:
                blocked.append(key)
        return {
            "factors": not blocked,
            "factor": factor,
            "blocked_classes": tuple(blocked),
        }

    @staticmethod
    def negative_defect_witness(
        trace: ComposedTrace,
        other: ComposedTrace,
        pi1: Callable[[Any], Any],
        pi2: Callable[[Any], Any],
        e1: Callable[[Any], bool],
        e2: Callable[[Any], bool],
        global_evaluator: Callable[[ComposedTrace], bool],
    ) -> Dict[str, Any]:
        """Locate a defect of -1 when mixing meets a transported local-green class.

        Local evaluators receive only the carrier coordinates, so equal joint
        carriers transport the local product. The witness is the trace whose
        global verdict is false.
        """
        same_carrier = joint_carrier(pi1, pi2, trace) == joint_carrier(pi1, pi2, other)
        if not same_carrier:
            raise ValueError("traces are not in one joint-carrier class")
        local_trace = carrier_local_product(e1, e2, pi1, pi2, trace)
        if not local_trace:
            raise ValueError("the first trace is not locally green")
        global_trace = _require_exact_bool(global_evaluator(trace), "global evaluator")
        global_other = _require_exact_bool(global_evaluator(other), "global evaluator")
        if global_trace == global_other:
            raise ValueError("global verdicts do not differ")
        local_other = carrier_local_product(e1, e2, pi1, pi2, other)
        if local_trace != local_other:
            raise ValueError("local product failed to transport under carrier-local evaluators")
        delta_trace = org_delta(global_trace, local_trace)
        delta_other = org_delta(global_other, local_other)
        if not global_trace:
            witness_is_first = True
            witness_delta = delta_trace
        else:
            witness_is_first = False
            witness_delta = delta_other
        if witness_delta != -1:
            raise ValueError(f"witness defect must be -1, got {witness_delta}")
        return {
            "same_carrier": same_carrier,
            "locally_green": local_trace,
            "local_transported": True,
            "delta_trace": delta_trace,
            "delta_other": delta_other,
            "witness_is_first": witness_is_first,
            "witness_delta": witness_delta,
        }
