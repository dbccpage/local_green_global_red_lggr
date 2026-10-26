"""Tests for role-to-failure bijection, injectivity, and collapse detection."""

import sys
from pathlib import Path

# Add code directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models import (
    FAILURE_TO_ROLE,
    ROLE_TO_FAILURE,
    FailureMode,
    Role,
    TypedPacket,
)


def test_role_failure_bijection_completeness():
    """Verify that every role has a distinct, defined failure mode."""
    assert len(Role) == 6
    assert len(FailureMode) == 6
    assert len(ROLE_TO_FAILURE) == 6
    assert len(FAILURE_TO_ROLE) == 6


def test_role_to_failure_injectivity():
    """Verify injectivity: r1 != r2 implies f(r1) != f(r2)."""
    seen_failures = set()
    for role in Role:
        failure = ROLE_TO_FAILURE[role]
        assert failure not in seen_failures, f"Duplicate failure mode: {failure}"
        seen_failures.add(failure)
    assert len(seen_failures) == 6


def test_failure_to_role_invertibility():
    """Verify left and right inverse identities: f_inv(f(r)) == r and f(f_inv(m)) == m."""
    for role in Role:
        failure = ROLE_TO_FAILURE[role]
        assert FAILURE_TO_ROLE[failure] == role

    for failure in FailureMode:
        role = FAILURE_TO_ROLE[failure]
        assert ROLE_TO_FAILURE[role] == failure


def test_simulated_role_collapse_detection():
    """Simulate collapsing an individual role and assert the specific failure is flagged."""
    test_cases = [
        (Role.OBSTRUCTION, FailureMode.UNDETECTED_OBSTRUCTION),
        (Role.AUTHORITY, FailureMode.PROPOSAL_BECOMES_ACTION),
        (Role.TRANSPORT, FailureMode.SILENT_REPRESENTATION_MUTATION),
        (Role.COMPARISON, FailureMode.COMPARISON_BECOMES_LAUNDERING),
        (Role.SHADOW, FailureMode.CONTINUUM_SHADOW_BECOMES_FAKE_AUTHORITY),
        (Role.RESIDUAL, FailureMode.RESIDUAL_GETS_HIDDEN_OR_RENAMED),
    ]
    for removed_role, expected_failure in test_cases:
        actual_failure = ROLE_TO_FAILURE[removed_role]
        assert actual_failure == expected_failure


def test_role_erasure_quotient_boundary():
    """Verify that erasing role information conflates distinct failure modes."""
    p1 = TypedPacket(payload="same_data", role=Role.OBSTRUCTION)
    p2 = TypedPacket(payload="same_data", role=Role.AUTHORITY)

    # Identical payload
    assert p1.payload == p2.payload

    # Distinct failure modes
    assert ROLE_TO_FAILURE[p1.role] != ROLE_TO_FAILURE[p2.role]
    assert ROLE_TO_FAILURE[p1.role] == FailureMode.UNDETECTED_OBSTRUCTION
    assert ROLE_TO_FAILURE[p2.role] == FailureMode.PROPOSAL_BECOMES_ACTION
