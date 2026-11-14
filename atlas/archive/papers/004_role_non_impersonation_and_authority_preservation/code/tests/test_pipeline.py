"""Tests for Refusal Monad laws, left-zero absorption, and the 5-stage pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from models import AuthorityReceiptRegistry, AuthorityToken, Proposal, Terminal, TerminalStatus
from pipeline import (
    AuthorityPipeline,
    Refusal,
    Success,
    pure,
    verify_authority,
)


def test_monad_laws():
    """Verify Monad identity and associativity laws."""
    # Left identity: pure(x).bind(f) == f(x)
    def f(x: int) -> Success[int]:
        return Success(x * 2)

    assert pure(10).bind(f) == f(10)

    # Right identity: m.bind(pure) == m
    m = Success(42)
    assert m.bind(pure) == m

    # Associativity: m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))
    def g(y: int) -> Success[str]:
        return Success(f"val: {y}")

    def f_bind_g(x: int) -> Success[str]:
        return f(x).bind(g)

    left = m.bind(f).bind(g)
    right = m.bind(f_bind_g)
    assert left == right


def test_refusal_left_zero_absorption():
    """Verify that refusal cannot be overridden or bypassed by any subsequent function."""
    ref = Refusal("initial_check_failed")
    called = []

    def should_not_run(x):
        called.append(True)
        return Success("unreachable")

    result = ref.bind(should_not_run)
    assert result == ref
    assert len(called) == 0, "Subsequent stage was improperly executed after refusal"


def test_five_stage_pipeline_full_success():
    """Verify that a compliant proposal successfully passes all 5 stages."""
    proposal = Proposal(id=101, payload="safe_operation")

    registry = AuthorityReceiptRegistry("independent_verifier_alpha")
    pipeline = AuthorityPipeline(
        obstruction_stage=lambda p: Success(p),
        transport_stage=lambda p: Success(p),
        descent_stage=lambda p: Success(p),
        verify_stage=lambda p: Success(p),
        terminalize_stage=lambda p: Success(Terminal(status=TerminalStatus.AUTHORITY, token=registry.issue(p))),
        receipt_registry=registry,
    )

    res = pipeline.execute(proposal)
    assert res.is_success()
    terminal = res.value
    assert terminal.is_authority
    assert verify_authority(proposal, terminal, pipeline.receipt_registry) is True


def test_five_stage_pipeline_short_circuits_at_each_stage():
    """Verify that failure at any stage short-circuits execution."""
    proposal = Proposal(id=102, payload="faulty_operation")

    # Failure at Stage 1 (Obstruction)
    p1 = AuthorityPipeline(
        obstruction_stage=lambda p: Refusal("Obstruction detected"),
        transport_stage=lambda p: pytest.fail("Stage 2 should not run"),
        descent_stage=lambda p: pytest.fail("Stage 3 should not run"),
        verify_stage=lambda p: pytest.fail("Stage 4 should not run"),
        terminalize_stage=lambda p: pytest.fail("Stage 5 should not run"),
    )
    r1 = p1.execute(proposal)
    assert r1.is_refusal()
    assert r1.reason == "Obstruction detected"

    # Failure at Stage 3 (Descent)
    p3 = AuthorityPipeline(
        obstruction_stage=lambda p: Success(p),
        transport_stage=lambda p: Success(p),
        descent_stage=lambda p: Refusal("Descent failed"),
        verify_stage=lambda p: pytest.fail("Stage 4 should not run"),
        terminalize_stage=lambda p: pytest.fail("Stage 5 should not run"),
    )
    r3 = p3.execute(proposal)
    assert r3.is_refusal()
    assert r3.reason == "Descent failed"


def test_proposal_is_not_authority_boundary():
    """Verify that a proposal alone does not confer authority."""
    proposal = Proposal(id=103, payload="sudo rm -rf")

    # 1. Bare proposal has no authority
    registry = AuthorityReceiptRegistry("verifier_alpha")
    terminal_none = Terminal(status=TerminalStatus.REFUSAL, reason="No pipeline run")
    assert verify_authority(proposal, terminal_none, registry) is False

    # 2. Token with wrong proposal id is refused
    bad_id_token = AuthorityToken(
        proposal_id=999,  # Mismatched ID!
        verifier="verifier_alpha",
        replayable=True,
        receipt_digest="hash123",
    )
    terminal_bad_id = Terminal(status=TerminalStatus.AUTHORITY, token=bad_id_token)
    assert verify_authority(proposal, terminal_bad_id, registry) is False

    # 3. Unreplayable token is refused
    unreplayed_token = AuthorityToken(
        proposal_id=proposal.id,
        verifier="verifier_alpha",
        replayable=False,  # Cannot replay!
        receipt_digest="hash123",
    )
    terminal_unreplayed = Terminal(status=TerminalStatus.AUTHORITY, token=unreplayed_token)
    assert verify_authority(proposal, terminal_unreplayed, registry) is False

    # A caller can choose plausible strings, but cannot invent a registry receipt.
    forged = AuthorityToken(
        proposal_id=proposal.id,
        verifier="verifier_alpha",
        replayable=True,
        receipt_digest="sha256:made-up",
        receipt_id="made-up",
    )
    assert verify_authority(proposal, Terminal(status=TerminalStatus.AUTHORITY, token=forged), registry) is False
