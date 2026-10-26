"""Tests for query-relative finite shadows and continuum tethering."""

import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models import TerminalStatus
from shadow import (
    FiniteShadow,
    TransportCertificate,
    evaluate_query_relative_authority,
)


def test_continuum_without_shadows_refuses():
    """Continuum object alone cannot authorize without finite shadows."""
    result = evaluate_query_relative_authority(
        continuum_object="infinite_model_R",
        query="eval(0.5)",
        shadows=[],
        certificates=[],
        verifiers={},
    )
    assert result.is_refusal()
    assert "cannot self-authorize" in result.reason


def test_successful_query_relative_authorization():
    """Valid cofinal shadows with verified transport confer query authority."""
    shadow1 = FiniteShadow(index="s1", projection_data={"val": 0.5}, covered_queries=frozenset({"measure_point_A"}), coherent_through=4, is_valid=True)
    shadow2 = FiniteShadow(index="s2", projection_data={"val": 0.5}, covered_queries=frozenset({"measure_point_A"}), coherent_through=6, is_valid=True)
    cert = TransportCertificate(
        source_index="s1", target_index="s2", query="measure_point_A", loss_bound=Fraction(1, 100), is_certified=True
    )

    verifiers = {
        "s1": lambda data, q: data["val"] == 0.5,
        "s2": lambda data, q: data["val"] == 0.5,
    }

    result = evaluate_query_relative_authority(
        continuum_object="continuous_field_psi",
        query="measure_point_A",
        shadows=[shadow1, shadow2],
        certificates=[cert],
        verifiers=verifiers,
    )
    assert result.is_success()
    terminal = result.value
    assert terminal.status == TerminalStatus.COHERENT_UP_TO
    assert terminal.token is None
    assert terminal.is_coherent_up_to


def test_unverified_shadow_or_excessive_transport_loss_refuses():
    """Excessive transport loss between shadows blocks authority preservation."""
    shadow1 = FiniteShadow(index="s1", projection_data={"val": 0.5}, covered_queries=frozenset({"query_x"}), coherent_through=1, is_valid=True)
    shadow2 = FiniteShadow(index="s2", projection_data={"val": 0.5}, covered_queries=frozenset({"query_x"}), coherent_through=1, is_valid=True)
    high_loss_cert = TransportCertificate(
        source_index="s1", target_index="s2", query="query_x", loss_bound=Fraction(1, 4), is_certified=False
    )

    verifiers = {
        "s1": lambda data, q: True,
        "s2": lambda data, q: True,
    }

    result = evaluate_query_relative_authority(
        continuum_object="continuous_field_psi",
        query="query_x",
        shadows=[shadow1, shadow2],
        certificates=[high_loss_cert],
        verifiers=verifiers,
    )
    assert result.is_refusal()
    assert "transport contract" in result.reason


def test_missing_coverage_or_transport_certificate_refuses():
    shadow1 = FiniteShadow(index="s1", projection_data={}, covered_queries=frozenset({"q"}), coherent_through=2, is_valid=True)
    shadow2 = FiniteShadow(index="s2", projection_data={}, covered_queries=frozenset(), coherent_through=2, is_valid=True)
    verifiers = {"s1": lambda data, query: True, "s2": lambda data, query: True}

    result = evaluate_query_relative_authority("X", "q", [shadow1, shadow2], [], verifiers)
    assert result.is_refusal()
    assert "lacks declared coverage" in result.reason
