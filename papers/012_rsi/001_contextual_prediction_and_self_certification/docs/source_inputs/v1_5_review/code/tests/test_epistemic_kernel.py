"""Exact finite checks behind Results I to IV of the epistemic no-go monograph."""

import sys
from fractions import Fraction
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import epistemic_kernel as k  # noqa: E402


def test_tables_are_distributions():
    for table in (k.pr_box(), k.classical_mixture(), k.near_tsirelson()):
        assert k.is_distribution(table)


def test_pr_box_has_no_supported_global_assignment():
    assert k.supported_global_assignments(k.pr_box()) == []


def test_pr_box_support_is_the_xor_rule_in_every_context():
    for (x, y), row in k.pr_box().items():
        assert {a ^ b for (a, b), w in row.items() if w > 0} == {x & y}


def test_no_positive_joint_marginalises_to_pr_box():
    # Any joint on assignments restricts to the PR support only if all its mass
    # sits on supported assignments; there are none, so only the zero joint passes.
    table = k.pr_box()
    for g in k.ALL_ASSIGNMENTS:
        assert not k.marginalises({g: Fraction(1)}, table)
    assert not k.marginalises({g: Fraction(1, 16) for g in k.ALL_ASSIGNMENTS}, table)


def test_classical_mixture_has_global_section_with_exact_marginals():
    table = k.classical_mixture()
    supp = k.supported_global_assignments(table)
    assert len(supp) == 2
    joint = {g: Fraction(1, 2) for g in supp}
    assert k.marginalises(joint, table)


def test_chsh_values_and_classical_bound():
    assert k.classical_chsh_bound() == 2
    assert k.chsh_value(k.pr_box()) == 4
    assert k.chsh_value(k.classical_mixture()) == 2
    assert k.chsh_value(k.near_tsirelson()) == Fraction(14, 5)
    assert k.chsh_value(k.near_tsirelson()) > k.classical_chsh_bound()


def test_near_tsirelson_is_not_in_the_classical_polytope_by_chsh():
    # A value above the classical bound certifies a positive defect without any solver.
    table = k.near_tsirelson()
    assert k.chsh_value(table) > 2
    assert not any(k.marginalises({g: Fraction(1)}, table) for g in k.ALL_ASSIGNMENTS)


def test_exact_boundary_value_is_not_glued_by_tolerance():
    # CHSH value 2 + 4e-8 as an exact rational exceeds the classical bound of 2.
    assert Fraction(2) + Fraction(4, 10**8) > k.classical_chsh_bound()


def test_fiber_lemma_exhaustive_on_f2_squared():
    for q in (lambda s: s[1], lambda s: s[0] ^ s[1], lambda s: s):
        assert k.fiber_lemma_holds(k.proj, q, k.K2)
    assert k.fiber_lemma_holds(lambda s: 0, lambda s: s[0], k.K2)


def test_private_fiber_blocks_prediction_of_the_state():
    assert k.no_function_recovers_state_from_report()


def test_swap_dynamics_witness():
    assert all(k.proj(k.swap(s)) == s[1] for s in k.K2)
    assert k.swap_not_intertwined()


LEDGER = ["entry-1", "entry-2", "entry-3"]


def test_truncated_ledger_still_verifies():
    entries = k.build_ledger("genesis", LEDGER)
    assert k.verify_ledger("genesis", entries)
    assert k.verify_ledger("genesis", entries[:2])
    assert k.verify_ledger("genesis", [])


def test_pinned_tip_separates_complete_from_truncated():
    entries = k.build_ledger("genesis", LEDGER)
    pin = k.tip("genesis", entries)
    assert k.complete_against("genesis", entries, pin)
    assert not k.complete_against("genesis", entries[:2], pin)


def test_tampered_payload_is_detected():
    entries = k.build_ledger("genesis", LEDGER)
    entries[1] = ("entry-X", entries[1][1])
    assert not k.verify_ledger("genesis", entries)


def test_invariant_verdict_is_blind_and_noninvariant_verdict_separates():
    for K in ([0], [0, 1, 2], [5, 1]):
        assert k.invariant_verdict(K) == k.invariant_verdict(k.relabel_carrier(K))
    assert k.first_is_zero([0]) != k.first_is_zero(k.relabel_carrier([0]))


ROOTS = ["root:R"]


def gate(p="P", e="E", a="A", root="root:R", basis="certificate", attempt="att-1"):
    return k.verify_three_role(attempt, p, e, a, root, basis, ROOTS)


def test_distinct_roles_with_admitted_root_pass_with_no_authority():
    receipt = gate()
    assert receipt["authority_effect"] == "None"
    assert receipt["root"] == "root:R"


@pytest.mark.parametrize(
    "kwargs,kind",
    [
        ({"a": "P"}, "SELF_AUTHORIZATION_PROPOSER"),
        ({"a": "E"}, "SELF_AUTHORIZATION_EVALUATOR"),
        ({"e": "P"}, "SELF_EVALUATION"),
        ({"basis": "prose"}, "PROSE_AUTHORITY"),
        ({"root": None}, "NO_EXTERNAL_ROOT"),
        ({"root": "root:other"}, "NO_EXTERNAL_ROOT"),
        ({"p": " "}, "MALFORMED"),
        ({"attempt": ""}, "MALFORMED"),
    ],
)
def test_gate_refusals(kwargs, kind):
    with pytest.raises(k.Refusal) as info:
        gate(**kwargs)
    assert info.value.kind == kind


def test_a_refused_link_poisons_the_composition():
    good = dict(attempt_id="a", proposer="P", evaluator="E", authorizer="A",
                authorizer_root="root:R", basis="certificate", admitted_roots=ROOTS)
    bad = dict(good, authorizer="P")
    assert k.compose_attempts([good]) is not None
    with pytest.raises(k.Refusal):
        k.compose_attempts([good, bad])


def test_distinct_identifiers_naming_one_agent_pass():
    # Identity binding is out of scope: the gate compares identifiers only.
    assert gate(p="agent-7", a="agent-7-alias")["authority_effect"] == "None"
