"""Residual honesty classification and honest refusal terminals.

Separates mathematical classification from institutional authorization:
    cochain evaluation -> checked mathematical result -> authorization decision -> issued receipt.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Optional

from models import (
    AuthorityReceiptRegistry,
    AuthorityToken,
    CoreResidualClass,
    MathematicalDefectClass,
    Proposal,
    Terminal,
    TerminalStatus,
)


def _is_zero_cochain(cochain: Any) -> bool:
    """Predicate determining if cochain coordinates are identically zero."""
    if cochain is None:
        return True
    if isinstance(cochain, (int, float)):
        return cochain == 0
    if isinstance(cochain, (list, tuple)):
        return all(_is_zero_cochain(x) for x in cochain)
    return cochain == 0


def _compute_boundary_mass(boundary_val: Any) -> float:
    """Compute coordinate-wise L1 norm for scalar or vector-valued differentials.

    Prevents signed coordinates from canceling (e.g. (1, -1) has mass 2.0, not 0.0).
    """
    if isinstance(boundary_val, (int, float)):
        val = float(abs(boundary_val))
        if math.isnan(val) or math.isinf(val):
            raise ValueError(f"Boundary value cannot be NaN or infinite: {boundary_val}")
        return val
    if isinstance(boundary_val, (list, tuple)):
        total = 0.0
        for x in boundary_val:
            if not isinstance(x, (int, float)):
                raise ValueError(f"Unsupported boundary coordinate type: {type(x)}")
            val = float(abs(x))
            if math.isnan(val) or math.isinf(val):
                raise ValueError(f"Boundary coordinate cannot be NaN or infinite: {x}")
            total += val
        return total
    raise ValueError(f"Unsupported boundary carrier type: {type(boundary_val)}")


@dataclass(frozen=True)
class CochainEvaluation:
    """Checked mathematical classification and supporting evidence for a cochain."""

    defect_mass: float
    boundary_mass: float
    is_exact: bool
    is_closed: bool
    defect_class: MathematicalDefectClass
    repair_witness: Any = None
    witness_verified: bool = False
    cochain: Any = None
    diagnostic: str = ""
    proposal_id: Optional[int] = None
    contract_id: Optional[str] = None

    def __post_init__(self) -> None:
        if math.isnan(self.defect_mass) or math.isinf(self.defect_mass) or self.defect_mass < 0.0:
            raise ValueError(f"Invalid defect_mass in evaluation: {self.defect_mass}")
        if math.isnan(self.boundary_mass) or math.isinf(self.boundary_mass) or self.boundary_mass < 0.0:
            raise ValueError(f"Invalid boundary_mass in evaluation: {self.boundary_mass}")

        # Invariant checks for mathematical defect classes:
        if self.defect_class == MathematicalDefectClass.ZERO_DEFECT:
            if self.defect_mass != 0.0:
                raise ValueError(f"ZERO_DEFECT requires defect_mass == 0.0, got {self.defect_mass}")
            if self.boundary_mass != 0.0:
                raise ValueError(f"ZERO_DEFECT requires boundary_mass == 0.0, got {self.boundary_mass}")
            if not self.is_closed:
                raise ValueError("ZERO_DEFECT requires is_closed == True")
            if not self.is_exact:
                raise ValueError("ZERO_DEFECT requires is_exact == True")
            if self.cochain is not None and not _is_zero_cochain(self.cochain):
                raise ValueError(f"ZERO_DEFECT with non-zero cochain: {self.cochain}")

        elif self.defect_class == MathematicalDefectClass.EXACT_REPAIRABLE:
            if self.defect_mass <= 0.0:
                raise ValueError(f"EXACT_REPAIRABLE requires defect_mass > 0.0, got {self.defect_mass}")
            if self.boundary_mass != 0.0:
                raise ValueError(f"EXACT_REPAIRABLE requires boundary_mass == 0.0, got {self.boundary_mass}")
            if not self.is_closed:
                raise ValueError("EXACT_REPAIRABLE requires is_closed == True")
            if not self.is_exact:
                raise ValueError("EXACT_REPAIRABLE requires is_exact == True")

        elif self.defect_class == MathematicalDefectClass.CLOSED_NON_EXACT:
            if self.defect_mass <= 0.0:
                raise ValueError(f"CLOSED_NON_EXACT requires defect_mass > 0.0, got {self.defect_mass}")
            if self.boundary_mass != 0.0:
                raise ValueError(f"CLOSED_NON_EXACT requires boundary_mass == 0.0, got {self.boundary_mass}")
            if not self.is_closed:
                raise ValueError("CLOSED_NON_EXACT requires is_closed == True")
            if self.is_exact:
                raise ValueError("CLOSED_NON_EXACT requires is_exact == False")

        elif self.defect_class == MathematicalDefectClass.OPEN_DEFECT:
            if self.boundary_mass <= 0.0:
                raise ValueError(f"OPEN_DEFECT requires boundary_mass > 0.0, got {self.boundary_mass}")
            if self.is_closed:
                raise ValueError("OPEN_DEFECT requires is_closed == False")


def evaluate_cochain_defect(
    defect_mass: float,
    boundary_mass: float | None = None,
    is_exact: bool | None = None,
    cochain: Any = None,
    d0_fn: Callable[[Any], Any] | None = None,
    d1_fn: Callable[[Any], Any] | None = None,
    is_exact_fn: Callable[[Any], bool] | None = None,
    repair_witness: Any = None,
    proposal_id: int | None = None,
    contract_id: str | None = None,
) -> CochainEvaluation:
    """Evaluate mathematical cochain predicates independently of terminal authority.

    Distinguishes:
    1. Zero defect: r = 0 (implies d1(r) = 0).
    2. Nonzero repairable defect: r != 0 and Exact(r).
    3. Closed non-exact residual: Closed(r) and not Exact(r).
    4. Open residual: not Closed(r).

    Fails closed when:
    - Zero defect is asserted with nonzero boundary or nonzero cochain.
    - Nonzero mass with zero boundary is provided without exactness data (information deficiency).
    - Malformed numerical inputs (NaN, infinite, negative) are supplied.
    """
    # 0. Validate input numerical bounds
    if math.isnan(defect_mass) or math.isinf(defect_mass) or defect_mass < 0.0:
        raise ValueError(f"Invalid defect_mass: must be a non-negative finite real number, got {defect_mass}")
    if boundary_mass is not None and (math.isnan(boundary_mass) or math.isinf(boundary_mass) or boundary_mass < 0.0):
        raise ValueError(f"Invalid boundary_mass: must be a non-negative finite real number, got {boundary_mass}")

    # 1. If explicit cochain and operators are supplied, evaluate exactness and closedness directly
    if cochain is not None:
        if d1_fn is not None:
            boundary_val = d1_fn(cochain)
            boundary_mass = _compute_boundary_mass(boundary_val)
        if is_exact_fn is not None:
            is_exact = is_exact_fn(cochain)

        is_zero_c = _is_zero_cochain(cochain)
        if is_zero_c and defect_mass > 0.0:
            raise ValueError("Inconsistent cochain evaluation: zero cochain cannot have non-zero defect mass")
        if not is_zero_c and defect_mass == 0.0:
            raise ValueError("Inconsistent cochain evaluation: non-zero cochain cannot have zero defect mass")

    if boundary_mass is None:
        boundary_mass = 0.0

    # 2. Algebraic consistency checks: In a linear complex, d(0) = 0.
    if defect_mass == 0.0 and boundary_mass > 0.0:
        raise ValueError(
            "Inconsistent cochain evaluation: zero defect cannot have non-zero boundary in a linear complex"
        )
    if defect_mass == 0.0 and is_exact is False:
        raise ValueError("Inconsistent cochain evaluation: zero defect must be exact")

    is_closed = boundary_mass == 0.0

    # 3. Classify mathematical defect class
    if defect_mass == 0.0:
        return CochainEvaluation(
            defect_mass=0.0,
            boundary_mass=0.0,
            is_exact=True,
            is_closed=True,
            defect_class=MathematicalDefectClass.ZERO_DEFECT,
            cochain=cochain,
            diagnostic="Zero defect: vanishing defect mass and boundary mass",
            proposal_id=proposal_id,
            contract_id=contract_id,
        )

    if is_closed:
        if is_exact is None:
            raise ValueError(
                "Information deficiency: coordinate mass and boundary mass alone cannot "
                "distinguish exactness from nonzero mass; cochain data or a checked "
                "exactness certificate is required"
            )
        if is_exact:
            witness_verified = False
            verified_witness = None
            if repair_witness is not None:
                # Require explicit presence of d0_fn and cochain to verify witness equation d0(w) == cochain
                if d0_fn is not None and cochain is not None:
                    if d0_fn(repair_witness) == cochain:
                        witness_verified = True
                        verified_witness = repair_witness

            return CochainEvaluation(
                defect_mass=defect_mass,
                boundary_mass=0.0,
                is_exact=True,
                is_closed=True,
                defect_class=MathematicalDefectClass.EXACT_REPAIRABLE,
                repair_witness=verified_witness,
                witness_verified=witness_verified,
                cochain=cochain,
                diagnostic=(
                    "Nonzero exact defect: in im(d0), repairable with verified witness"
                    if witness_verified
                    else "Nonzero exact defect: unverified repair witness (missing d0_fn/cochain or failed witness equation)"
                ),
                proposal_id=proposal_id,
                contract_id=contract_id,
            )
        return CochainEvaluation(
            defect_mass=defect_mass,
            boundary_mass=0.0,
            is_exact=False,
            is_closed=True,
            defect_class=MathematicalDefectClass.CLOSED_NON_EXACT,
            cochain=cochain,
            diagnostic="Closed non-exact residual: vanishing boundary with non-trivial cohomology",
            proposal_id=proposal_id,
            contract_id=contract_id,
        )

    return CochainEvaluation(
        defect_mass=defect_mass,
        boundary_mass=boundary_mass,
        is_exact=False,
        is_closed=False,
        defect_class=MathematicalDefectClass.OPEN_DEFECT,
        cochain=cochain,
        diagnostic=f"Open boundary defect: non-zero boundary mass {boundary_mass}",
        proposal_id=proposal_id,
        contract_id=contract_id,
    )


def classify_terminal_outcome(
    defect_mass: float | None = None,
    boundary_mass: float | None = None,
    max_dim_checked: int = 1,
    budget_remaining: int = 100,
    evaluation: CochainEvaluation | None = None,
    is_exact: bool | None = None,
    repair_witness: Any = None,
    proposal_id: int = 1,
    registry: AuthorityReceiptRegistry | None = None,
    proposal: Proposal | None = None,
) -> Terminal:
    """Evaluate residual honesty and return a typed terminal.

    Mathematical classification returns classification terminals (refusal or residual).
    Does NOT manufacture authority or throwaway registries from unchecked inputs.
    """
    del proposal_id, registry, proposal  # Authority issuance is separated to gate_authority_issuance

    if budget_remaining <= 0:
        return Terminal(
            status=TerminalStatus.BUDGET_UNKNOWN,
            reason="Resource budget exhausted; honest refusal ('I do not know')",
        )

    if evaluation is None:
        if defect_mass is None or boundary_mass is None:
            raise ValueError("Either evaluation or (defect_mass, boundary_mass) must be provided")
        evaluation = evaluate_cochain_defect(
            defect_mass=defect_mass,
            boundary_mass=boundary_mass,
            is_exact=is_exact,
            repair_witness=repair_witness,
        )

    if evaluation.defect_class == MathematicalDefectClass.ZERO_DEFECT:
        return Terminal(
            status=TerminalStatus.REFUSAL,
            residual_class=CoreResidualClass.RESOLVED_EXACT,
            reason="Defect mass is zero; verified exact closure (requires verification gate for authority issuance)",
        )

    if evaluation.defect_class == MathematicalDefectClass.EXACT_REPAIRABLE:
        return Terminal(
            status=TerminalStatus.REFUSAL,
            residual_class=CoreResidualClass.RESOLVED_EXACT,
            reason="Nonzero exact defect; repair witness required and authority withheld at classification stage",
        )

    if evaluation.defect_class == MathematicalDefectClass.CLOSED_NON_EXACT:
        return Terminal(
            status=TerminalStatus.RESIDUAL_CLOSED,
            residual_class=CoreResidualClass.CLOSED_RESIDUAL,
            reason="Non-zero defect with vanishing boundary; persistent closed residual",
        )

    return Terminal(
        status=TerminalStatus.RESIDUAL_OPEN,
        residual_class=CoreResidualClass.OPEN_RESIDUAL,
        reason=f"Open boundary defect (mass={evaluation.boundary_mass}) at dimension {max_dim_checked}",
    )


def gate_authority_issuance(
    proposal: Proposal,
    evaluation: CochainEvaluation,
    registry: AuthorityReceiptRegistry | None,
) -> Terminal:
    """Distinct authority gate: issues authority receipt ONLY from checked mathematical evidence.

    Separates:
        cochain evaluation -> checked mathematical result -> authorization decision -> issued receipt.
    """
    if registry is None:
        return Terminal(
            status=TerminalStatus.REFUSAL,
            residual_class=CoreResidualClass.RESOLVED_EXACT,
            reason="No receipt registry provided; authority cannot be issued without accountable verifier",
        )

    # 1. Enforce proposal binding if evaluation was bound to a specific proposal
    if evaluation.proposal_id is not None and evaluation.proposal_id != proposal.id:
        return Terminal(
            status=TerminalStatus.REFUSAL,
            residual_class=CoreResidualClass.OPEN_RESIDUAL,
            reason=f"Evidence proposal_id ({evaluation.proposal_id}) does not match proposal ({proposal.id})",
        )

    # 2. Re-verify mathematical evidence consistency before issuing authority:
    if evaluation.defect_class == MathematicalDefectClass.ZERO_DEFECT:
        if (
            evaluation.defect_mass != 0.0
            or evaluation.boundary_mass != 0.0
            or not evaluation.is_closed
            or not evaluation.is_exact
            or (evaluation.cochain is not None and not _is_zero_cochain(evaluation.cochain))
        ):
            return Terminal(
                status=TerminalStatus.REFUSAL,
                residual_class=CoreResidualClass.OPEN_RESIDUAL,
                reason="Inconsistent or contradictory evidence: ZERO_DEFECT contradicts underlying metrics",
            )
        token = registry.issue(proposal, evidence=evaluation)
        return Terminal(
            status=TerminalStatus.AUTHORITY,
            token=token,
            residual_class=CoreResidualClass.RESOLVED_EXACT,
            reason="Zero defect mathematically verified; authority token issued by registry",
        )

    if evaluation.defect_class == MathematicalDefectClass.EXACT_REPAIRABLE:
        if (
            evaluation.defect_mass <= 0.0
            or evaluation.boundary_mass != 0.0
            or not evaluation.is_closed
            or not evaluation.is_exact
            or evaluation.repair_witness is None
            or not evaluation.witness_verified
        ):
            return Terminal(
                status=TerminalStatus.REFUSAL,
                residual_class=CoreResidualClass.RESOLVED_EXACT,
                reason="Exact nonzero defect lacks verified repair witness; authority withheld",
            )
        token = registry.issue(proposal, evidence=evaluation)
        return Terminal(
            status=TerminalStatus.AUTHORITY,
            token=token,
            residual_class=CoreResidualClass.RESOLVED_EXACT,
            reason="Exact nonzero defect verified and repaired with valid witness; authority granted",
        )

    if evaluation.defect_class == MathematicalDefectClass.CLOSED_NON_EXACT:
        return Terminal(
            status=TerminalStatus.RESIDUAL_CLOSED,
            residual_class=CoreResidualClass.CLOSED_RESIDUAL,
            reason="Closed non-exact residual cannot receive authority; route to governance",
        )

    return Terminal(
        status=TerminalStatus.RESIDUAL_OPEN,
        residual_class=CoreResidualClass.OPEN_RESIDUAL,
        reason="Open boundary defect; authority withheld",
    )
