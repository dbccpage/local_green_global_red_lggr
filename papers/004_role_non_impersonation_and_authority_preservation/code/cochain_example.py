"""A stated F_2 cochain complex used by the residual-closure fixture."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from models import (
    AuthorityReceiptRegistry,
    AuthorityToken,
    CoreResidualClass,
    FailureMode,
    Proposal,
    Terminal,
    TerminalStatus,
)

VectorF2 = Tuple[int, int, int]


def d0(value: int) -> VectorF2:
    """The declared differential d0: F_2 -> F_2^3, a |-> (a, 0, 0)."""
    return (value % 2, 0, 0)


def d1(value: VectorF2) -> int:
    """The declared differential d1: F_2^3 -> F_2, (x,y,z) |-> z."""
    return value[2] % 2


def is_exact(value: VectorF2) -> bool:
    """Membership in im(d0), for the explicitly declared small complex."""
    return value in (d0(0), d0(1))


@dataclass(frozen=True)
class CochainConflictState:
    """A configuration difference represented in the stated F_2 cochain complex."""

    source_a: VectorF2
    source_b: VectorF2

    def __post_init__(self) -> None:
        if len(self.source_a) != 3 or len(self.source_b) != 3:
            raise ValueError(
                f"Configuration vectors must have exactly 3 coordinates in F_2^3, got "
                f"len(source_a)={len(self.source_a)}, len(source_b)={len(self.source_b)}"
            )
        for name, vec in (("source_a", self.source_a), ("source_b", self.source_b)):
            for idx, val in enumerate(vec):
                if val not in (0, 1):
                    raise ValueError(
                        f"{name}[{idx}] must be in F_2 (0 or 1), got {val}"
                    )

    @property
    def difference_cochain(self) -> VectorF2:
        return tuple((a ^ b) % 2 for a, b in zip(self.source_a, self.source_b))  # type: ignore[return-value]

    def is_exact_zero(self) -> bool:
        return self.difference_cochain == (0, 0, 0)

    def boundary_d1(self) -> int:
        return d1(self.difference_cochain)


def evaluate_cochain(state: CochainConflictState) -> CoreResidualClass:
    """Classify zero, closed non-exact, and non-closed cochains consistently."""
    residual = state.difference_cochain
    if residual == (0, 0, 0):
        return CoreResidualClass.RESOLVED_EXACT
    if d1(residual) == 0:
        if is_exact(residual):
            return CoreResidualClass.RESOLVED_EXACT
        return CoreResidualClass.CLOSED_RESIDUAL
    return CoreResidualClass.OPEN_RESIDUAL


def run_full_stack_merge(
    state: CochainConflictState,
    registry: Optional[AuthorityReceiptRegistry] = None,
    proposal: Optional[Proposal] = None,
) -> Terminal:
    """Route each evaluated residual class to its corresponding typed terminal."""
    classification = evaluate_cochain(state)
    if classification == CoreResidualClass.RESOLVED_EXACT:
        if state.is_exact_zero():
            if registry is None:
                return Terminal(
                    status=TerminalStatus.REFUSAL,
                    residual_class=classification,
                    reason="Configurations have zero difference, but no receipt registry was provided; authority withheld",
                )
            active_proposal = (
                proposal
                if proposal is not None
                else Proposal(id=0, payload=f"merge:{state.source_a}:{state.source_b}")
            )
            token = registry.issue(active_proposal, evidence="zero_cochain_difference")
            return Terminal(
                status=TerminalStatus.AUTHORITY,
                token=token,
                residual_class=classification,
                reason="Configurations have zero difference; clean resolution with registry receipt",
            )
        return Terminal(
            status=TerminalStatus.REFUSAL,
            residual_class=classification,
            reason="Exact nonzero residual; a repair witness is required and no authority is issued",
        )
    if classification == CoreResidualClass.CLOSED_RESIDUAL:
        return Terminal(
            status=TerminalStatus.RESIDUAL_CLOSED,
            residual_class=classification,
            reason="Closed non-exact conflict; route to governance",
        )
    return Terminal(
        status=TerminalStatus.RESIDUAL_OPEN,
        residual_class=classification,
        reason="Open boundary conflict; request further evidence",
    )


def run_collapsed_merge_without_residual_role(state: CochainConflictState) -> Terminal:
    """Deliberately invalid fixture showing counterfeit resolution."""
    return Terminal(
        status=TerminalStatus.AUTHORITY,
        residual_class=CoreResidualClass.RESOLVED_EXACT,
        reason="Forced resolution (residual role omitted)",
    )


def audit_merge_execution(
    state: CochainConflictState,
    claimed_terminal: Terminal,
    repair_witness: Optional[int] = None,
) -> Optional[FailureMode]:
    """Require a repair witness alpha with d0(alpha) equal to the residual."""
    residual = state.difference_cochain
    has_valid_repair = repair_witness is not None and d0(repair_witness) == residual
    if claimed_terminal.status == TerminalStatus.AUTHORITY and residual != (0, 0, 0) and not has_valid_repair:
        return FailureMode.RESIDUAL_GETS_HIDDEN_OR_RENAMED
    return None
