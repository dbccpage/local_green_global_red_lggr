"""Core data models for Role Non-Impersonation and Authority Preservation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, Optional


class Role(str, Enum):
    """The six conserved authority governance roles."""
    OBSTRUCTION = "obstruction"
    AUTHORITY = "authority"
    TRANSPORT = "transport"
    COMPARISON = "comparison"
    SHADOW = "shadow"
    RESIDUAL = "residual"


class FailureMode(str, Enum):
    """The six characteristic authority failure modes arising from role collapse."""
    UNDETECTED_OBSTRUCTION = "undetected_obstruction"
    PROPOSAL_BECOMES_ACTION = "proposal_becomes_action"
    SILENT_REPRESENTATION_MUTATION = "silent_representation_mutation"
    COMPARISON_BECOMES_LAUNDERING = "comparison_becomes_laundering"
    CONTINUUM_SHADOW_BECOMES_FAKE_AUTHORITY = "continuum_shadow_becomes_fake_authority"
    RESIDUAL_GETS_HIDDEN_OR_RENAMED = "residual_gets_hidden_or_renamed"


ROLE_TO_FAILURE: dict[Role, FailureMode] = {
    Role.OBSTRUCTION: FailureMode.UNDETECTED_OBSTRUCTION,
    Role.AUTHORITY: FailureMode.PROPOSAL_BECOMES_ACTION,
    Role.TRANSPORT: FailureMode.SILENT_REPRESENTATION_MUTATION,
    Role.COMPARISON: FailureMode.COMPARISON_BECOMES_LAUNDERING,
    Role.SHADOW: FailureMode.CONTINUUM_SHADOW_BECOMES_FAKE_AUTHORITY,
    Role.RESIDUAL: FailureMode.RESIDUAL_GETS_HIDDEN_OR_RENAMED,
}

FAILURE_TO_ROLE: dict[FailureMode, Role] = {
    failure: role for role, failure in ROLE_TO_FAILURE.items()
}


class TerminalStatus(str, Enum):
    """Terminal outcome status for an execution pipeline."""
    AUTHORITY = "authority"
    RESIDUAL_CLOSED = "residual_closed"
    RESIDUAL_OPEN = "residual_open"
    REFUSAL = "refusal"
    BUDGET_UNKNOWN = "budget_unknown"
    COHERENT_UP_TO = "coherent_up_to"


class CoreResidualClass(str, Enum):
    """Cohomological classification of defects."""
    RESOLVED_EXACT = "resolved_exact"
    CLOSED_RESIDUAL = "closed_residual"
    OPEN_RESIDUAL = "open_residual"


@dataclass(frozen=True)
class Proposal:
    """An unverified candidate proposal entering the pipeline."""
    id: int
    payload: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AuthorityToken:
    """A receipt reference issued by a trusted registry in this reference model."""
    proposal_id: int
    verifier: str
    replayable: bool
    receipt_digest: str
    receipt_id: str = ""
    timestamp: str = ""

    def is_well_formed_for(self, proposal: Proposal) -> bool:
        """Check only the public syntactic part of receipt validation."""
        return (
            self.proposal_id == proposal.id
            and self.replayable
            and bool(self.verifier.strip())
            and bool(self.receipt_digest.strip())
            and bool(self.receipt_id.strip())
        )


RECEIPT_ENVELOPE_KEYS: frozenset[str] = frozenset({"token", "verified_token", "receipt_envelope"})


class MathematicalDefectClass(str, Enum):
    """The four-way mathematical defect classification independent of terminal authority."""
    ZERO_DEFECT = "zero_defect"
    EXACT_REPAIRABLE = "exact_repairable"
    CLOSED_NON_EXACT = "closed_non_exact"
    OPEN_DEFECT = "open_defect"


@dataclass
class AuthorityReceiptRegistry:
    """Verifier-owned receipt registry for deterministic, local contract tests.

    This is deliberately an in-memory trust model. It prevents a caller from
    authorizing a hand-written token, but it is not a cryptographic custody or
    independently deployable authentication system.
    """

    verifier: str
    _issued: dict[str, tuple[str, str]] = field(default_factory=dict, init=False, repr=False)
    _next_sequence: int = field(default=0, init=False, repr=False)

    @staticmethod
    def _proposal_digest(proposal: Proposal) -> str:
        """Compute digest of proposal id, payload, and all action-relevant metadata.

        Separates the proposal body from the receipt/evidence envelope keys
        so that attaching an issued receipt does not invalidate its own binding.
        """
        action_metadata = {
            k: v for k, v in sorted(proposal.metadata.items())
            if k not in RECEIPT_ENVELOPE_KEYS
        }
        payload = json.dumps(
            {"id": proposal.id, "metadata": action_metadata, "payload": proposal.payload},
            default=repr,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def issue(self, proposal: Proposal, evidence: Optional[Any] = None) -> AuthorityToken:
        """Record and return a token bound to this exact proposal instance and verified evidence."""
        if not self.verifier.strip():
            raise ValueError("Receipt registry requires a non-empty verifier identity")
        self._next_sequence += 1
        proposal_digest = self._proposal_digest(proposal)
        evidence_repr = repr(evidence) if evidence is not None else "no_evidence_attached"
        evidence_digest = hashlib.sha256(evidence_repr.encode("utf-8")).hexdigest()
        receipt_id = hashlib.sha256(
            f"{self.verifier}:{proposal_digest}:{evidence_digest}:{self._next_sequence}".encode("utf-8")
        ).hexdigest()
        receipt_digest = hashlib.sha256(
            f"{receipt_id}:{proposal_digest}:{evidence_digest}:{self.verifier}".encode("utf-8")
        ).hexdigest()
        self._issued[receipt_id] = (proposal_digest, receipt_digest)
        return AuthorityToken(
            proposal_id=proposal.id,
            verifier=self.verifier,
            replayable=True,
            receipt_digest=f"sha256:{receipt_digest}",
            receipt_id=receipt_id,
        )

    def validates(self, proposal: Proposal, token: AuthorityToken) -> bool:
        """Require a registry-issued receipt and an unchanged proposal binding."""
        if not token.is_well_formed_for(proposal) or token.verifier != self.verifier:
            return False
        issued = self._issued.get(token.receipt_id)
        if issued is None:
            return False
        proposal_digest, receipt_digest = issued
        return (
            proposal_digest == self._proposal_digest(proposal)
            and token.receipt_digest == f"sha256:{receipt_digest}"
        )


@dataclass(frozen=True)
class Terminal:
    """A typed terminal outcome produced by an execution pipeline."""
    status: TerminalStatus
    token: Optional[AuthorityToken] = None
    residual_class: Optional[CoreResidualClass] = None
    reason: str = ""

    @property
    def is_authority(self) -> bool:
        return self.status == TerminalStatus.AUTHORITY and self.token is not None

    @property
    def is_residual(self) -> bool:
        return self.status in (TerminalStatus.RESIDUAL_CLOSED, TerminalStatus.RESIDUAL_OPEN)

    @property
    def is_refusal(self) -> bool:
        return self.status in (TerminalStatus.REFUSAL, TerminalStatus.BUDGET_UNKNOWN)

    @property
    def is_coherent_up_to(self) -> bool:
        return self.status == TerminalStatus.COHERENT_UP_TO


@dataclass(frozen=True)
class TypedPacket:
    """A data packet carrying an explicit governance role alongside its payload."""
    payload: Any
    role: Role
