"""Refusal Monad and Kleisli pipeline execution engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar, Union

from models import AuthorityReceiptRegistry, Proposal, Terminal

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True)
class Success(Generic[T]):
    """Successful computation carrying value T."""
    value: T

    def is_success(self) -> bool:
        return True

    def is_refusal(self) -> bool:
        return False

    def bind(self, fn: Callable[[T], RefusalM[U]]) -> RefusalM[U]:
        return fn(self.value)


@dataclass(frozen=True)
class Refusal:
    """Explicit refusal computation carrying failure diagnostic."""
    reason: str

    def is_success(self) -> bool:
        return False

    def is_refusal(self) -> bool:
        return True

    def bind(self, fn: Callable[[Any], RefusalM[U]]) -> RefusalM[U]:
        # Left-zero absorption: once refused, propagation is strictly invariant
        return self


RefusalM = Union[Success[T], Refusal]


def pure(x: T) -> RefusalM[T]:
    return Success(x)


class AuthorityPipeline:
    """The 5-stage Kleisli authority verification pipeline:
    R (Obstruction) -> rho (Transport) -> D (Descent) -> V (Verification) -> tau (Terminalization).
    """

    def __init__(
        self,
        obstruction_stage: Callable[[Proposal], RefusalM[Proposal]],
        transport_stage: Callable[[Proposal], RefusalM[Proposal]],
        descent_stage: Callable[[Proposal], RefusalM[Proposal]],
        verify_stage: Callable[[Proposal], RefusalM[Proposal]],
        terminalize_stage: Callable[[Proposal], RefusalM[Terminal]],
        receipt_registry: AuthorityReceiptRegistry | None = None,
    ) -> None:
        self.obstruction = obstruction_stage
        self.transport = transport_stage
        self.descent = descent_stage
        self.verify = verify_stage
        self.terminalize = terminalize_stage
        self.receipt_registry = receipt_registry

    def execute(self, proposal: Proposal) -> RefusalM[Terminal]:
        """Execute the five-stage pipeline with strict Kleisli short-circuiting."""
        step1 = self.obstruction(proposal)
        step2 = step1.bind(self.transport)
        step3 = step2.bind(self.descent)
        step4 = step3.bind(self.verify)
        step5 = step4.bind(self.terminalize)
        return step5


def verify_authority(
    proposal: Proposal,
    terminal: Terminal,
    receipt_registry: AuthorityReceiptRegistry | None,
) -> bool:
    """Check the fundamental proposal/authority boundary:
    p in P does not imply Auth(p).
    Authority requires a terminal token recorded by the verifier-owned registry.
    """
    if not terminal.is_authority or terminal.token is None or receipt_registry is None:
        return False
    return receipt_registry.validates(proposal, terminal.token)
