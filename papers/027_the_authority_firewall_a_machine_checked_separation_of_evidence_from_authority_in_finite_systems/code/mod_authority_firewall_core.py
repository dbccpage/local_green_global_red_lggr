"""Reference implementation for the Authority Firewall in finite verification systems.

This module formalizes:
1. The binary coproduct decomposition: Terminal = AuthEvidence + ResidualOutcome.
2. Constructor disjointness: Sum.inr != Sum.inl.
3. The pointwise separation theorem: residual terminals cannot inhabit the authority summand.
4. The seven-guard authority predicate (Definition 2.2).
5. A simulation of the negative case study: an audited solver attempting self-certification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Generic, Optional, TypeVar, Union


class FirewallViolationError(TypeError):
    """Raised when an invalid promotion of residual evidence into authority is attempted."""
    pass


@dataclass(frozen=True)
class AuthEvidence:
    """Authority certificate payload inhabiting the inl summand of Terminal."""
    packet_id: str
    terminalizer_id: str
    replayable: bool
    details: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.packet_id, str) or not self.packet_id.strip():
            raise ValueError("packet_id must be a non-empty string")
        if not isinstance(self.terminalizer_id, str) or not self.terminalizer_id.strip():
            raise ValueError("terminalizer_id must be a non-empty string")
        if not isinstance(self.replayable, bool):
            raise TypeError(f"replayable must be an exact boolean, got {type(self.replayable).__name__}")


@dataclass(frozen=True)
class ResidualClass:
    """Classified residual defect class inhabiting the inr summand."""
    class_id: str
    defect_mass: Fraction
    description: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.class_id, str) or not self.class_id.strip():
            raise ValueError("class_id must be a non-empty string")
        if not isinstance(self.defect_mass, Fraction):
            raise TypeError(f"defect_mass must be fractions.Fraction, got {type(self.defect_mass).__name__}")


@dataclass(frozen=True)
class ResidualFailure:
    """Typed closure or absorption failure inhabiting the inr summand."""
    failure_mode: str
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.failure_mode, str) or not self.failure_mode.strip():
            raise ValueError("failure_mode must be a non-empty string")
        if not isinstance(self.reason, str):
            raise TypeError(f"reason must be a string, got {type(self.reason).__name__}")


ResidualOutcome = Union[ResidualClass, ResidualFailure]

A = TypeVar("A")
R = TypeVar("R")


@dataclass(frozen=True)
class Coproduct(Generic[A, R]):
    """Strict binary coproduct A + R."""
    is_inl: bool
    _inl_val: Optional[A] = None
    _inr_val: Optional[R] = None

    def __post_init__(self) -> None:
        if not isinstance(self.is_inl, bool):
            raise TypeError(f"is_inl must be an exact boolean, got {type(self.is_inl).__name__}")
        if self.is_inl:
            if self._inl_val is None:
                raise ValueError("Coproduct in inl state requires a non-None _inl_val")
            if self._inr_val is not None:
                raise ValueError("Coproduct in inl state must have _inr_val=None")
        else:
            if self._inr_val is None:
                raise ValueError("Coproduct in inr state requires a non-None _inr_val")
            if self._inl_val is not None:
                raise ValueError("Coproduct in inr state must have _inl_val=None")

    @property
    def is_inr(self) -> bool:
        return not self.is_inl

    @classmethod
    def inl(cls, value: A) -> Coproduct[A, R]:
        if value is None:
            raise ValueError("Cannot construct inl with None payload")
        return cls(is_inl=True, _inl_val=value, _inr_val=None)

    @classmethod
    def inr(cls, value: R) -> Coproduct[A, R]:
        if value is None:
            raise ValueError("Cannot construct inr with None payload")
        return cls(is_inl=False, _inl_val=None, _inr_val=value)

    @property
    def inl_value(self) -> A:
        if not self.is_inl or self._inl_val is None:
            raise ValueError("Attempted to access inl_value on an inr summand")
        return self._inl_val

    @property
    def inr_value(self) -> R:
        if self.is_inl or self._inr_val is None:
            raise ValueError("Attempted to access inr_value on an inl summand")
        return self._inr_val

    def __repr__(self) -> str:
        if self.is_inl:
            return f"Sum.inl({self._inl_val!r})"
        return f"Sum.inr({self._inr_val!r})"


# Terminal type alias: AuthEvidence + ResidualOutcome
Terminal = Coproduct[AuthEvidence, ResidualOutcome]


def residual_terminal(r: ResidualOutcome) -> Terminal:
    """Map a residual outcome into the terminal coproduct via inr."""
    if not isinstance(r, (ResidualClass, ResidualFailure)):
        raise TypeError(f"residual must be ResidualClass or ResidualFailure, got {type(r).__name__}")
    return Coproduct.inr(r)


def auth_terminal(e: AuthEvidence) -> Terminal:
    """Map authority evidence into the terminal coproduct via inl."""
    if not isinstance(e, AuthEvidence):
        raise TypeError(f"authority evidence must be AuthEvidence, got {type(e).__name__}")
    return Coproduct.inl(e)


def is_auth(t: Terminal) -> bool:
    """Check if a terminal value lies in the authority (inl) summand."""
    if not isinstance(t, Coproduct):
        raise TypeError(f"Expected Coproduct terminal, got {type(t).__name__}")
    return t.is_inl


def residual_not_auth(r: ResidualOutcome) -> bool:
    """Pointwise Coproduct Separation Theorem (Theorem 3.1).
    
    Verifies that for any residual outcome r, residual_terminal(r) is NOT in the authority summand.
    Returns True indicating that constructor disjointness holds.
    """
    term = residual_terminal(r)
    return not is_auth(term)


@dataclass(frozen=True)
class IsAuthGuards:
    """The seven-guard authority predicate from Definition 2.2.
    
    Represents the operational conjunction of externally verified boolean checks.
    Does not internally compute cryptographic hashes or execute state-space search.
    """
    verified_replay_hash: bool
    matching_replay: bool
    terminalizer_present: bool
    exhaustive_search: bool  # kappa == 0
    zero_defect: bool        # delta == 0
    descent_witness: bool
    replay_freshness: bool

    def __post_init__(self) -> None:
        guard_fields = (
            ("verified_replay_hash", self.verified_replay_hash),
            ("matching_replay", self.matching_replay),
            ("terminalizer_present", self.terminalizer_present),
            ("exhaustive_search", self.exhaustive_search),
            ("zero_defect", self.zero_defect),
            ("descent_witness", self.descent_witness),
            ("replay_freshness", self.replay_freshness),
        )
        for name, val in guard_fields:
            if not isinstance(val, bool):
                raise TypeError(f"Guard '{name}' must be an exact boolean, got {type(val).__name__}: {val!r}")

    def all_guards_met(self) -> bool:
        """Check if all seven operational guards are strictly satisfied."""
        return bool(
            self.verified_replay_hash is True
            and self.matching_replay is True
            and self.terminalizer_present is True
            and self.exhaustive_search is True
            and self.zero_defect is True
            and self.descent_witness is True
            and self.replay_freshness is True
        )


class AuthorityFirewall:
    """Enforces structural separation between diagnostic evidence and operational authority."""

    def __init__(self, require_seven_guards: bool = True):
        self.require_seven_guards = require_seven_guards

    def route_outcome(
        self,
        residual: Optional[ResidualOutcome] = None,
        authority_evidence: Optional[AuthEvidence] = None,
        guards: Optional[IsAuthGuards] = None,
    ) -> Terminal:
        """Route an execution outcome into the terminal coproduct."""
        if residual is not None and authority_evidence is not None:
            raise ValueError("Ambiguous route: cannot provide both residual and authority_evidence")

        if authority_evidence is not None:
            if not isinstance(authority_evidence, AuthEvidence):
                raise TypeError(
                    f"authority_evidence must be an instance of AuthEvidence, got {type(authority_evidence).__name__}"
                )
            if self.require_seven_guards:
                if (
                    guards is None
                    or not isinstance(guards, IsAuthGuards)
                    or not guards.all_guards_met()
                    or not authority_evidence.replayable
                ):
                    # Authority rejected due to failed guards; route into typed residual failure
                    return Coproduct.inr(
                        ResidualFailure(
                            failure_mode="GUARD_FAILURE",
                            reason="Authority evidence provided but one or more of seven guards failed or evidence is unreplayable."
                        )
                    )
            return Coproduct.inl(authority_evidence)

        if residual is not None:
            if not isinstance(residual, (ResidualClass, ResidualFailure)):
                raise TypeError(
                    f"residual must be an instance of ResidualOutcome, got {type(residual).__name__}"
                )
            return Coproduct.inr(residual)

        return Coproduct.inr(
            ResidualFailure(
                failure_mode="NO_INPUT",
                reason="Neither authority evidence nor residual diagnostic provided."
            )
        )

    def attempt_residual_promotion(self, r: ResidualOutcome) -> None:
        """Refuse any direct type promotion of residual evidence to authority."""
        if not isinstance(r, (ResidualClass, ResidualFailure)):
            raise TypeError(f"residual must be an instance of ResidualOutcome, got {type(r).__name__}")
        raise FirewallViolationError(
            f"Firewall Refusal: Residual evidence {r} cannot inhabit the authority summand."
        )


@dataclass
class SolverAuditSimulation:
    """Models the Section 4 negative instance: an audited solver claiming certification."""
    solver_name: str = "BitwiseSolver"
    reported_accuracy: Fraction = field(default_factory=lambda: Fraction(4667, 10000))
    shipped_truth_tables: int = 25535
    pareto_complete_truth_tables: int = 25768
    shipped_has_independent_evaluator: bool = False
    shipped_search_exhaustive_flag: bool = True

    def run_adversarial_audit(self) -> dict[str, Union[bool, int, Fraction, str]]:
        """Run the CC1 adversarial audit against solver claims."""
        missing_tables = self.pareto_complete_truth_tables - self.shipped_truth_tables
        exhaustiveness_survives = (missing_tables == 0) and self.shipped_search_exhaustive_flag
        evaluator_independent = self.shipped_has_independent_evaluator

        guards = IsAuthGuards(
            verified_replay_hash=evaluator_independent,
            matching_replay=True,
            terminalizer_present=True,
            exhaustive_search=exhaustiveness_survives,
            zero_defect=(missing_tables == 0),
            descent_witness=evaluator_independent,
            replay_freshness=True,
        )

        return {
            "missing_truth_tables": missing_tables,
            "exhaustiveness_survives": exhaustiveness_survives,
            "evaluator_independent": evaluator_independent,
            "guards_passed": guards.all_guards_met(),
            "guards_object": guards,
        }

    def evaluate_with_firewall(self, firewall: AuthorityFirewall) -> Terminal:
        """Evaluate the solver under the firewall discipline."""
        audit = self.run_adversarial_audit()
        guards: IsAuthGuards = audit["guards_object"]  # type: ignore

        if guards.all_guards_met():
            return firewall.route_outcome(
                authority_evidence=AuthEvidence(
                    packet_id="PACKET-SOLVER-OK",
                    terminalizer_id="TERM-DESCENT",
                    replayable=True,
                ),
                guards=guards,
            )
        else:
            defect = ResidualClass(
                class_id="AST_SHIFT_EXPR_DEFECT",
                defect_mass=Fraction(int(audit["missing_truth_tables"]), self.pareto_complete_truth_tables),
                description=f"Omitted {audit['missing_truth_tables']} in-bound Pareto truth tables."
            )
            return firewall.route_outcome(residual=defect)
