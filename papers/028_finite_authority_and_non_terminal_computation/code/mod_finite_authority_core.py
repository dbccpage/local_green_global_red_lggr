"""Reference implementation for Finite Authority and Non-Terminal Computation.

Formalizes:
1. Proposal traces vs terminal authority: model probability P_theta does not imply Authority.
2. Evaluated Path Kernel (EPK): continuous exponential kernel and exact-rational Pade surrogate.
3. The C1–C8 gate stack matching Section 6 with strict boolean type checking and typed refusal reasons.
4. Terminal authority vs scoped checklist certificate: checklist conjunction != evidence-bearing authority.
5. Counterfeit descent detection: surface signs with non-zero residual defect or unverified gates.
6. The Primitive-Difference Local Green != Global Red (LGGR) quotient obstruction theorem on declared finite carriers.
7. Constructive minimal verdict-preserving quotient refinement (X / ~_*).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
import math
from typing import Callable, Optional, TypeVar


class TerminalStatus(str, Enum):
    AUTHORITY = "AUTHORITY"
    CHECKLIST_CERTIFIED = "CHECKLIST_CERTIFIED"
    REFUSAL = "REFUSAL"
    NON_AUTHORITY_HALT = "NON_AUTHORITY_HALT"
    PROPOSAL_ONLY = "PROPOSAL_ONLY"


class RefusalReason(str, Enum):
    PROPOSAL_FAILURE = "ProposalFailure"
    EXTRACTION_FAILURE = "ExtractionFailure"
    PARSER_INSUFFICIENT = "ParserInsufficient"
    CANONICALIZER_FAILURE = "CanonicalizerFailure"
    CANONICALIZER_AMBIGUITY = "CanonicalizerAmbiguity"
    VERIFIER_REJECTED = "VerifierRejected"
    VERIFIER_FAILURE = "VerifierFailure"
    AMBIGUOUS_ANSWER_FIBER = "AmbiguousAnswerFiber"
    NO_ACCEPTED = "NoAccepted"
    REPLAY_HASH_MISMATCH = "ReplayHashMismatch"
    ENVIRONMENT_MISMATCH = "EnvironmentMismatch"
    LEAKAGE_DETECTED = "LeakageDetected"
    PROVENANCE_UNKNOWN = "ProvenanceUnknown"
    BOUNDARY_INSUFFICIENT = "BoundaryInsufficient"
    TERMINAL_MISMATCH = "TerminalMismatch"
    COUNTERFEIT_PACKET = "CounterfeitPacket"
    NON_AUTHORITY_TERMINAL = "NonAuthorityTerminal"
    BUDGET_UNKNOWN = "BudgetUnknown"
    LIFT_REQUIRED = "LiftRequired"


@dataclass(frozen=True)
class TerminalWitness:
    """Constructs terminal object t and evidence-bearing IsAuth witness required by §0 and §6."""
    terminal_id: str
    is_auth_proof: str
    verified_answer: str

    def __post_init__(self) -> None:
        if not self.terminal_id or not self.terminal_id.strip():
            raise ValueError("terminal_id must be non-empty.")
        if not self.is_auth_proof or not self.is_auth_proof.strip():
            raise ValueError("is_auth_proof must be non-empty.")


@dataclass(frozen=True)
class ProposalTrace:
    """Trace emitted by a proposal system (LLM, Turing machine, or search algorithm)."""
    trace_id: str
    input_claim: str
    extracted_answer: str
    proposal_probability: Fraction
    cost: Fraction = Fraction(1)
    residual_risk: Fraction = Fraction(0)
    is_halted: bool = True
    surface_signs: dict[str, bool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.proposal_probability, bool) or not isinstance(self.proposal_probability, (int, Fraction)):
            raise TypeError(f"proposal_probability must be exact rational, got {type(self.proposal_probability).__name__}")
        if self.proposal_probability < 0 or self.proposal_probability > 1:
            raise ValueError(f"proposal_probability must be in [0, 1], got {self.proposal_probability}")

        if isinstance(self.cost, bool) or not isinstance(self.cost, (int, Fraction)):
            raise TypeError(f"cost must be exact rational, got {type(self.cost).__name__}")
        if self.cost < 0:
            raise ValueError(f"cost must be non-negative, got {self.cost}")

        if isinstance(self.residual_risk, bool) or not isinstance(self.residual_risk, (int, Fraction)):
            raise TypeError(f"residual_risk must be exact rational, got {type(self.residual_risk).__name__}")
        if self.residual_risk < 0:
            raise ValueError(f"residual_risk must be non-negative, got {self.residual_risk}")


@dataclass(frozen=True)
class EvaluatedPathKernel:
    """Computes accepted proposal mass under a declared evaluator (Section 4).

    Implements:
    - compute_exponential_kernel: canonical continuous-discount kernel e^{-lambda C - mu R}
    - compute_rational_kernel: exact rational Pade surrogate 1 / (1 + lambda C + mu R) in Q
    """
    cost_sensitivity: Fraction = Fraction(1)
    risk_sensitivity: Fraction = Fraction(1)

    def __post_init__(self) -> None:
        if isinstance(self.cost_sensitivity, bool) or not isinstance(self.cost_sensitivity, (int, Fraction)):
            raise TypeError(f"cost_sensitivity must be exact rational, got {type(self.cost_sensitivity).__name__}")
        if self.cost_sensitivity < 0:
            raise ValueError(f"cost_sensitivity must be non-negative, got {self.cost_sensitivity}")

        if isinstance(self.risk_sensitivity, bool) or not isinstance(self.risk_sensitivity, (int, Fraction)):
            raise TypeError(f"risk_sensitivity must be exact rational, got {type(self.risk_sensitivity).__name__}")
        if self.risk_sensitivity < 0:
            raise ValueError(f"risk_sensitivity must be non-negative, got {self.risk_sensitivity}")

    def compute_exponential_kernel(
        self,
        traces: list[ProposalTrace],
        evaluator: Callable[[ProposalTrace], bool],
    ) -> float:
        """Calculate canonical EPK: Z_theta = sum_{gamma, E(gamma)=1} P_theta(gamma) * exp(-lambda C[gamma] - mu R[gamma])."""
        total_mass = 0.0
        for trace in traces:
            if evaluator(trace):
                exponent = float(self.cost_sensitivity * trace.cost + self.risk_sensitivity * trace.residual_risk)
                discount = math.exp(-exponent)
                total_mass += float(trace.proposal_probability) * discount
        return total_mass

    def compute_rational_kernel(
        self,
        traces: list[ProposalTrace],
        evaluator: Callable[[ProposalTrace], bool],
    ) -> Fraction:
        """Calculate rational surrogate EPK: Z_theta = sum_{gamma, E(gamma)=1} P_theta(gamma) / (1 + lambda C + mu R)."""
        total_mass = Fraction(0)
        for trace in traces:
            if evaluator(trace):
                denom = Fraction(1, 1) + self.cost_sensitivity * trace.cost + self.risk_sensitivity * trace.residual_risk
                discount = Fraction(1, denom)
                total_mass += trace.proposal_probability * discount
        return total_mass

    def compute_kernel(
        self,
        traces: list[ProposalTrace],
        evaluator: Callable[[ProposalTrace], bool],
    ) -> Fraction:
        """Default exact-rational kernel computation (Pade surrogate in Q)."""
        return self.compute_rational_kernel(traces, evaluator)


@dataclass(frozen=True)
class GateStack:
    """The C1–C8 gate stack from Section 6 of the monograph.

    Enforces strict boolean typing on all fields, rejecting string truthiness like GateStack(*['False']*8).
    Schema matches Section 6 Table:
    - C1: proposal generated
    - C2: parseable output
    - C3: canonicalization succeeds
    - C4: verifier accepts
    - C5: unique answer fiber
    - C6: replay confirms
    - C7: leakage/provenance boundary clean
    - C8: terminal gate accepts
    """
    c1_proposal_generated: bool
    c2_parseable_output: bool
    c3_canonicalization_succeeds: bool
    c4_verifier_accepts: bool
    c5_unique_answer_fiber: bool
    c6_replay_confirms: bool
    c7_leakage_provenance_clean: bool
    c8_terminal_gate_accepts: bool

    def __post_init__(self) -> None:
        for f_name in [
            "c1_proposal_generated",
            "c2_parseable_output",
            "c3_canonicalization_succeeds",
            "c4_verifier_accepts",
            "c5_unique_answer_fiber",
            "c6_replay_confirms",
            "c7_leakage_provenance_clean",
            "c8_terminal_gate_accepts",
        ]:
            val = getattr(self, f_name)
            if not isinstance(val, bool):
                raise TypeError(f"Gate {f_name} must be an explicit boolean, got {type(val).__name__} ({val!r})")

    def evaluate(self) -> tuple[bool, Optional[RefusalReason]]:
        """Evaluate conjunction of all eight gates; return failure reason on first defect."""
        if not self.c1_proposal_generated:
            return False, RefusalReason.PROPOSAL_FAILURE
        if not self.c2_parseable_output:
            return False, RefusalReason.PARSER_INSUFFICIENT
        if not self.c3_canonicalization_succeeds:
            return False, RefusalReason.CANONICALIZER_FAILURE
        if not self.c4_verifier_accepts:
            return False, RefusalReason.VERIFIER_REJECTED
        if not self.c5_unique_answer_fiber:
            return False, RefusalReason.AMBIGUOUS_ANSWER_FIBER
        if not self.c6_replay_confirms:
            return False, RefusalReason.REPLAY_HASH_MISMATCH
        if not self.c7_leakage_provenance_clean:
            return False, RefusalReason.LEAKAGE_DETECTED
        if not self.c8_terminal_gate_accepts:
            return False, RefusalReason.NON_AUTHORITY_TERMINAL
        return True, None


@dataclass(frozen=True)
class TerminalOutcome:
    status: TerminalStatus
    refusal_reason: Optional[RefusalReason] = None
    details: str = ""


def evaluate_halted_trace(
    trace: ProposalTrace,
    gates: Optional[GateStack] = None,
    terminal_witness: Optional[TerminalWitness] = None,
) -> TerminalOutcome:
    """Demonstrates Theorem T6: Halting is not evidence (§2.2, §6).

    Syntactic halting without external descent verification yields NON_AUTHORITY_HALT.
    A conjunction of eight passing gates yields CHECKLIST_CERTIFIED.
    Full operational AUTHORITY is refused unless accompanied by a constructed terminal
    object and verified IsAuth witness (§6).
    """
    if not trace.is_halted:
        return TerminalOutcome(
            status=TerminalStatus.PROPOSAL_ONLY,
            details="Trace has not reached a syntactic halt state."
        )

    if gates is None:
        return TerminalOutcome(
            status=TerminalStatus.NON_AUTHORITY_HALT,
            refusal_reason=RefusalReason.NON_AUTHORITY_TERMINAL,
            details="Computation halted, but no finite descent packet or gate stack was provided."
        )

    passed, reason = gates.evaluate()
    if not passed:
        return TerminalOutcome(
            status=TerminalStatus.REFUSAL,
            refusal_reason=reason,
            details=f"Descent failed gate check: {reason.value if reason else 'unknown'}"
        )

    if terminal_witness is None:
        return TerminalOutcome(
            status=TerminalStatus.CHECKLIST_CERTIFIED,
            details="Trace passed C1–C8 gate checklist; sufficiency to operational authority is refused without terminal IsAuth witness (§6)."
        )

    if terminal_witness.verified_answer != trace.extracted_answer:
        return TerminalOutcome(
            status=TerminalStatus.REFUSAL,
            refusal_reason=RefusalReason.TERMINAL_MISMATCH,
            details=f"Terminal witness verified_answer ({terminal_witness.verified_answer!r}) does not match trace extracted_answer ({trace.extracted_answer!r})."
        )

    return TerminalOutcome(
        status=TerminalStatus.AUTHORITY,
        details="Trace successfully descended through C1–C8 gate stack with verified terminal IsAuth witness."
    )


def detect_counterfeit_descent(
    trace: ProposalTrace,
    residual_defect_mass: Fraction,
    gates: Optional[GateStack] = None,
    terminal_witness: Optional[TerminalWitness] = None,
) -> tuple[bool, TerminalOutcome]:
    """Detect counterfeit descent: surface signs imitating authority with non-zero obstruction.

    Returns (is_counterfeit, outcome).

    Enforces:
    1. Unhalted traces cannot produce authority.
    2. Non-zero residual defect mass is an unconditional refusal (COUNTERFEIT_PACKET if surface signs present, else VERIFIER_REJECTED).
    3. Zero residual defect mass alone without gates yields NON_AUTHORITY_HALT.
    4. Passing gate stack without terminal witness yields CHECKLIST_CERTIFIED.
    5. Only passing gate stack with valid terminal witness produces AUTHORITY.
    """
    if not trace.is_halted:
        return False, TerminalOutcome(
            status=TerminalStatus.PROPOSAL_ONLY,
            details="Trace has not halted; unhalted trace cannot bear authority."
        )

    if isinstance(residual_defect_mass, bool) or not isinstance(residual_defect_mass, (int, Fraction)):
        raise TypeError(
            "residual_defect_mass must be an exact rational (Fraction or int), "
            f"got {type(residual_defect_mass).__name__}"
        )
    if residual_defect_mass < 0:
        raise ValueError(f"residual_defect_mass must be non-negative, got {residual_defect_mass}")

    has_surface_signs = (
        trace.surface_signs.get("has_citations", False)
        or trace.surface_signs.get("has_json_tags", False)
        or trace.surface_signs.get("claims_confidence", False)
    )

    if residual_defect_mass > 0:
        if has_surface_signs:
            return True, TerminalOutcome(
                status=TerminalStatus.REFUSAL,
                refusal_reason=RefusalReason.COUNTERFEIT_PACKET,
                details=f"Surface signs present but residual defect mass is non-zero: {residual_defect_mass}"
            )
        return False, TerminalOutcome(
            status=TerminalStatus.REFUSAL,
            refusal_reason=RefusalReason.VERIFIER_REJECTED,
            details=f"Residual defect mass is non-zero: {residual_defect_mass}; an open obstruction is never authority."
        )

    # residual_defect_mass == 0
    if gates is None:
        return False, TerminalOutcome(
            status=TerminalStatus.NON_AUTHORITY_HALT,
            refusal_reason=RefusalReason.NON_AUTHORITY_TERMINAL,
            details="Zero residual defect alone without verified gate stack does not confer authority."
        )

    passed, reason = gates.evaluate()
    if not passed:
        return True if has_surface_signs else False, TerminalOutcome(
            status=TerminalStatus.REFUSAL,
            refusal_reason=RefusalReason.COUNTERFEIT_PACKET if has_surface_signs else reason,
            details="Failed gate stack."
        )

    if terminal_witness is None:
        return False, TerminalOutcome(
            status=TerminalStatus.CHECKLIST_CERTIFIED,
            details="Zero residual defect and valid C1–C8 gate checklist; operational authority requires terminal IsAuth witness (§6)."
        )

    if terminal_witness.verified_answer != trace.extracted_answer:
        return True, TerminalOutcome(
            status=TerminalStatus.REFUSAL,
            refusal_reason=RefusalReason.TERMINAL_MISMATCH,
            details="Terminal witness does not match extracted answer."
        )

    return False, TerminalOutcome(
        status=TerminalStatus.AUTHORITY,
        details="Valid descent with verified terminal IsAuth witness."
    )


class LGGRObstruction:
    """Models the Primitive-Difference Local Green != Global Red Theorem (Section 4.3).

    Checks whether:
    1. Local dashboard L factors through the zero-difference quotient (L is constant on each equivalence class).
    2. Global verdict G fails to factor through the quotient (G differs on at least one pair of equivalent states).

    Requires exhaustive evaluation over a declared finite carrier X.
    """

    def __init__(
        self,
        zero_relation: Callable[[str, str], bool],
        local_dashboard: Callable[[str], str],
        global_verdict: Callable[[str], str],
        carrier: Optional[list[str]] = None,
    ):
        self.zero_rel = zero_relation
        self.local = local_dashboard
        self.global_v = global_verdict
        self.carrier = list(carrier) if carrier is not None else []

    def compute_equivalence_classes(self, carrier: Optional[list[str]] = None) -> list[list[str]]:
        """Compute connected components of the zero relation on declared carrier."""
        states = list(carrier) if carrier is not None else self.carrier
        classes: list[list[str]] = []
        visited: set[str] = set()

        for s in states:
            if s in visited:
                continue
            comp: list[str] = []
            queue = [s]
            visited.add(s)
            while queue:
                curr = queue.pop(0)
                comp.append(curr)
                for other in states:
                    if other not in visited and (self.zero_rel(curr, other) or self.zero_rel(other, curr)):
                        visited.add(other)
                        queue.append(other)
            classes.append(comp)
        return classes

    def check_local_factorization(self, pairs_or_carrier: Optional[list] = None) -> bool:
        """Check if local dashboard L is constant on every zero-difference equivalence class."""
        if pairs_or_carrier is None:
            pairs_or_carrier = self.carrier

        if pairs_or_carrier and isinstance(pairs_or_carrier[0], tuple):
            for x, y in pairs_or_carrier:
                if self.zero_rel(x, y):
                    if self.local(x) != self.local(y):
                        return False
            return True

        classes = self.compute_equivalence_classes(pairs_or_carrier)
        for comp in classes:
            if len(comp) > 1:
                val0 = self.local(comp[0])
                for other in comp[1:]:
                    if self.local(other) != val0:
                        return False
        return True

    def check_joint_factorization(self, pairs_or_carrier: Optional[list] = None) -> bool:
        """Check if paired dashboard (L, G) factors through zero-difference quotient."""
        if pairs_or_carrier is None:
            pairs_or_carrier = self.carrier

        if pairs_or_carrier and isinstance(pairs_or_carrier[0], tuple):
            for x, y in pairs_or_carrier:
                if self.zero_rel(x, y):
                    if self.local(x) != self.local(y) or self.global_v(x) != self.global_v(y):
                        return False
            return True

        classes = self.compute_equivalence_classes(pairs_or_carrier)
        for comp in classes:
            if len(comp) > 1:
                l0 = self.local(comp[0])
                g0 = self.global_v(comp[0])
                for other in comp[1:]:
                    if self.local(other) != l0 or self.global_v(other) != g0:
                        return False
        return True

    def verify_lggr_obstruction(self, pairs_or_carrier: Optional[list] = None) -> bool:
        """Returns True if Local Green (L factors through quotient) AND Global Red (Joint fails to factor)."""
        local_ok = self.check_local_factorization(pairs_or_carrier)
        joint_ok = self.check_joint_factorization(pairs_or_carrier)
        return local_ok and not joint_ok


@dataclass(frozen=True)
class RefinementSplitWitness:
    """Witness for a necessary boundary refinement split under verdict map G."""
    quotient_class: str
    state_a: str
    state_b: str
    verdict_a: str
    verdict_b: str


@dataclass(frozen=True)
class RefinementResult:
    """Result of minimal verdict-preserving quotient refinement X / ~_*."""
    carrier_size: int
    original_quotient_size: int
    refined_quotient_size: int
    class_increase: int
    splits: list[RefinementSplitWitness]
    refined_classes: list[list[str]]


def compute_minimal_verdict_refinement(
    carrier: list[str],
    quotient_map: Callable[[str], str],
    verdict_map: Callable[[str], str],
) -> RefinementResult:
    """Computes the minimal verdict-preserving refinement X / ~_*.

    Given carrier X, quotient map q: X -> Q, and verdict G: X -> Y:
    x ~_* y <=> q(x) == q(y) and G(x) == G(y).

    Proved properties:
    1. X / ~_* is the coarsest refinement preserving the existing quotient through which G descends.
    2. Exact increase in classes is: |X / ~_*| - |Q| = sum_{u in Q} (|G(q^{-1}(u))| - 1).
    3. Every split has an explicit witness (state_a, state_b) with q(a)==q(b) but G(a)!=G(b).
    """
    fibers: dict[str, list[str]] = {}
    for x in carrier:
        u = quotient_map(x)
        fibers.setdefault(u, []).append(x)

    original_q_size = len(fibers)
    refined_classes: list[list[str]] = []
    splits: list[RefinementSplitWitness] = []
    total_class_increase = 0

    for u, fiber in fibers.items():
        by_verdict: dict[str, list[str]] = {}
        for x in fiber:
            v = verdict_map(x)
            by_verdict.setdefault(v, []).append(x)

        num_subclasses = len(by_verdict)
        increase_for_u = num_subclasses - 1
        total_class_increase += increase_for_u

        if num_subclasses > 1:
            verdicts = list(by_verdict.keys())
            v_a = verdicts[0]
            v_b = verdicts[1]
            state_a = by_verdict[v_a][0]
            state_b = by_verdict[v_b][0]
            splits.append(
                RefinementSplitWitness(
                    quotient_class=u,
                    state_a=state_a,
                    state_b=state_b,
                    verdict_a=v_a,
                    verdict_b=v_b,
                )
            )

        for sub_class in by_verdict.values():
            refined_classes.append(sub_class)

    return RefinementResult(
        carrier_size=len(carrier),
        original_quotient_size=original_q_size,
        refined_quotient_size=len(refined_classes),
        class_increase=total_class_increase,
        splits=splits,
        refined_classes=refined_classes,
    )
