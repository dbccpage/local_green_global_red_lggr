"""Tests for the deterministic adversarial fixture suite."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from adversarial_benchmark import (
    AttackCategory,
    build_benchmark_suite,
    create_defense_pipeline,
    evaluate_pipeline_benchmark,
    evaluate_unfenced_baseline,
)
from models import Proposal
from pipeline import verify_authority


def test_unfenced_baseline_failure():
    """The baseline is a fixed always-allow classifier, not an LLM result."""
    suite = build_benchmark_suite()
    metrics = evaluate_unfenced_baseline(suite)

    assert metrics.total_cases == 20
    assert metrics.attack_cases == 16
    assert metrics.benign_cases == 4
    assert metrics.attacks_blocked == 0
    assert metrics.attacks_succeeded == 16
    assert metrics.attack_detection_rate == 0.0
    assert metrics.benign_preservation_rate == 1.0
    assert metrics.accuracy == 0.20


def test_defense_pipeline_intercepts_all_attacks():
    """Verify the deterministic fixture classifications for the five-stage pipeline."""
    pipeline = create_defense_pipeline()
    suite = build_benchmark_suite()
    metrics = evaluate_pipeline_benchmark(pipeline, suite)

    assert metrics.total_cases == 20
    assert metrics.attack_cases == 16
    assert metrics.benign_cases == 4
    assert metrics.attacks_blocked == 16
    assert metrics.attacks_succeeded == 0
    assert metrics.benign_passed == 4
    assert metrics.benign_false_refusals == 0
    assert metrics.attack_detection_rate == 1.0
    assert metrics.benign_preservation_rate == 1.0
    assert metrics.accuracy == 1.0


def test_defense_pipeline_stage_attribution():
    """Verify that each attack category is refused at its exact designated architectural stage."""
    pipeline = create_defense_pipeline()
    suite = build_benchmark_suite()
    metrics = evaluate_pipeline_benchmark(pipeline, suite)

    # Obstruction catches: 3 direct prompt injections + 2 indirect prompt injections + 2 role tampering = 7
    assert metrics.stage_breakdown["obstruction"] == 7

    # Transport catches: 2 payload mutation / checksum smuggling attacks = 2
    assert metrics.stage_breakdown["transport"] == 2

    # Descent catches: 4 unauthorized tool hijacking attacks = 4
    assert metrics.stage_breakdown["descent"] == 4

    # Verify catches: 2 confidence spoofing + 1 replay attack = 3
    assert metrics.stage_breakdown["verify"] == 3


def test_benign_proposals_receive_registry_issued_receipts():
    """Legitimate fixtures receive receipts that replay only through the owned registry."""
    pipeline = create_defense_pipeline()
    suite = build_benchmark_suite()
    benign_cases = [c for c in suite if c.category == AttackCategory.BENIGN_WORKFLOW]

    for case in benign_cases:
        proposal = Proposal(id=case.id, payload=case.payload, metadata=case.metadata)
        outcome = pipeline.execute(proposal)

        assert outcome.is_success()
        terminal = outcome.value
        assert terminal.is_authority
        assert terminal.token is not None
        assert terminal.token.proposal_id == case.id
        assert terminal.token.replayable is True
        assert verify_authority(proposal, terminal, pipeline.receipt_registry) is True


def test_caller_metadata_cannot_bypass_confidence_spoofing_fixture_114():
    """Regression: Asserting verified_token in caller metadata must NOT bypass verification."""
    pipeline = create_defense_pipeline()
    suite = build_benchmark_suite()
    case_114 = next(c for c in suite if c.id == 114)

    # 1. Caller asserts verified_token=True
    meta_spoofed_bool = dict(case_114.metadata)
    meta_spoofed_bool["verified_token"] = True
    proposal_bool = Proposal(id=case_114.id, payload=case_114.payload, metadata=meta_spoofed_bool)
    outcome_bool = pipeline.execute(proposal_bool)

    assert outcome_bool.is_refusal()
    assert "Verify:" in outcome_bool.reason
    assert "heuristic confidence" in outcome_bool.reason

    # 2. Caller asserts verified_token string
    meta_spoofed_str = dict(case_114.metadata)
    meta_spoofed_str["verified_token"] = "valid_signature_token"
    proposal_str = Proposal(id=case_114.id, payload=case_114.payload, metadata=meta_spoofed_str)
    outcome_str = pipeline.execute(proposal_str)

    assert outcome_str.is_refusal()
    assert "Verify:" in outcome_str.reason

    # 3. Caller asserts hand-crafted AuthorityToken not issued by the registry
    from models import AuthorityToken
    meta_spoofed_token = dict(case_114.metadata)
    meta_spoofed_token["verified_token"] = AuthorityToken(
        proposal_id=114,
        verifier="untrusted_external_actor",
        replayable=True,
        receipt_digest="sha256:fake_digest",
        receipt_id="unregistered_receipt",
    )
    proposal_token = Proposal(id=case_114.id, payload=case_114.payload, metadata=meta_spoofed_token)
    outcome_token = pipeline.execute(proposal_token)

    assert outcome_token.is_refusal()
    assert "Verify:" in outcome_token.reason


def test_positive_receipt_validation_and_tamper_detection():
    """Regression test for Review Finding 5:
    Ensure legitimate issuance-then-presentation flow validates:
    1. Token issued for proposal validates against the proposal.
    2. Attaching the token to proposal.metadata['token'] (or passing directly)
       validates without invalidating its own binding.
    3. Changing payload invalidates validation.
    4. Changing action-relevant metadata (e.g. target_tool, author) invalidates validation.
    """
    from adversarial_benchmark import verify_defense_stage
    from models import AuthorityReceiptRegistry

    registry = AuthorityReceiptRegistry("benchmark_verifier")
    base_proposal = Proposal(
        id=301,
        payload="Fetch documentation for verified research.",
        metadata={"target_tool": "read_doc", "author": "alice"},
    )

    # 1. Issue legitimate token
    token = registry.issue(base_proposal, evidence="checked_proposal_301")
    assert registry.validates(base_proposal, token) is True

    # 2. Attach token to proposal metadata envelope - binding remains valid!
    meta_with_token = dict(base_proposal.metadata)
    meta_with_token["token"] = token
    proposal_with_token = Proposal(
        id=base_proposal.id,
        payload=base_proposal.payload,
        metadata=meta_with_token,
    )
    assert registry.validates(proposal_with_token, token) is True

    # 3. Passing to verify_defense_stage succeeds with legitimate token
    res = verify_defense_stage(proposal_with_token, registry=registry)
    assert res.is_success()

    # Also works when passing token as explicit argument
    res_arg = verify_defense_stage(base_proposal, registry=registry, token=token)
    assert res_arg.is_success()

    # 4. Tampering with payload breaks validation
    tampered_payload_proposal = Proposal(
        id=base_proposal.id,
        payload="Fetch documentation and execute privilege escalation.",
        metadata=meta_with_token,
    )
    assert registry.validates(tampered_payload_proposal, token) is False

    # 5. Tampering with action-relevant metadata breaks validation
    tampered_tool_meta = dict(meta_with_token)
    tampered_tool_meta["target_tool"] = "execute_transfer"
    tampered_tool_proposal = Proposal(
        id=base_proposal.id,
        payload=base_proposal.payload,
        metadata=tampered_tool_meta,
    )
    assert registry.validates(tampered_tool_proposal, token) is False

