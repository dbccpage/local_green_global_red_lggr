"""Finite checks for LGGR I rows I1–I7. Calls carrier_kernel_census."""

import pytest

from carrier_kernel_census import (
    Composed,
    b2i,
    carrier_verdicts_agree,
    class_factor,
    collapse_carrier,
    delta_eval,
    downstream_verdicts_agree,
    locally_green,
    negative_defect_trace,
    section_i_census,
    strict_pass_gap,
    verdict_ceiling_witness,
)


def test_section_i_finite_census():
    census = section_i_census()
    assert census["same_class"] is True
    assert census["ceiling_trace"] is False
    assert census["carrier_verdicts_agree"] is True
    assert census["local_green"] is True
    assert census["local_green_other"] is True
    assert census["products_agree"] is True
    assert census["negative_defect_is_red"] is True
    assert census["negative_defect"] == -1
    assert census["green_delta"] == 0
    assert census["red_delta"] == -1
    assert census["global_passes"] == 1
    assert census["local_passes"] == 2
    assert census["gap"] == 1
    assert census["downstream_agrees"] is True
    assert census["invariant_pair_factors"] is True
    assert census["mixed_global_factors"] is False
    assert census["mixed_delta_factors"] is False


def test_verdict_ceiling_can_miss_on_the_first_trace():
    missed = verdict_ceiling_witness(
        collapse_carrier,
        lambda _carrier: False,
        lambda bit: bit,
        True,
        False,
    )
    assert missed is True
    assert carrier_verdicts_agree(
        collapse_carrier, lambda _carrier: False, True, False
    )


def test_carrier_checks_refuse_separated_or_constant_targets():
    separate = lambda bit: bit
    with pytest.raises(ValueError, match="one carrier class"):
        verdict_ceiling_witness(separate, lambda bit: bit, lambda bit: bit, True, False)
    with pytest.raises(ValueError, match="does not vary"):
        verdict_ceiling_witness(
            collapse_carrier, lambda _carrier: True, lambda _bit: True, True, False
        )
    with pytest.raises(ValueError, match="one carrier class"):
        carrier_verdicts_agree(separate, lambda bit: True, True, False)
    with pytest.raises(ValueError, match="one carrier class"):
        downstream_verdicts_agree(
            separate, lambda bit: bit, lambda bit: bit, True, False
        )
    with pytest.raises(TypeError, match="bit"):
        b2i(1)
    with pytest.raises(TypeError, match="induced evaluator"):
        verdict_ceiling_witness(
            collapse_carrier, lambda _carrier: 1, lambda bit: bit, True, False
        )
    assert delta_eval(False, True, True) == 1
    assert delta_eval(False, False, False) == 0


def test_joint_carrier_refusals_and_green_arms():
    pi = collapse_carrier
    green = Composed(True, True)
    red = Composed(False, True)
    other_class = lambda bit: bit
    with pytest.raises(ValueError, match="joint-carrier"):
        negative_defect_trace(
            other_class, pi, lambda bit: True, lambda bit: True,
            lambda trace: trace.g1, green, red,
        )
    with pytest.raises(ValueError, match="locally green"):
        negative_defect_trace(
            pi, pi, lambda _carrier: False, lambda _carrier: True,
            lambda trace: trace.g1, green, red,
        )
    with pytest.raises(ValueError, match="locally green"):
        negative_defect_trace(
            pi, pi, lambda _carrier: True, lambda _carrier: False,
            lambda trace: trace.g1, green, red,
        )
    assert locally_green(pi, pi, lambda _carrier: True, lambda _carrier: False, green) is False
    with pytest.raises(ValueError, match="locally green"):
        strict_pass_gap(
            pi, pi, lambda _carrier: False, lambda _carrier: True,
            lambda trace: trace.g1, green, red,
        )
    with pytest.raises(ValueError, match="do not differ"):
        strict_pass_gap(
            pi, pi, lambda _carrier: True, lambda _carrier: True,
            lambda _trace: False, green, red,
        )
    with pytest.raises(ValueError, match="do not differ"):
        negative_defect_trace(
            pi, pi, lambda _carrier: True, lambda _carrier: True,
            lambda _trace: True, green, red,
        )
    with pytest.raises(ValueError, match="joint-carrier"):
        strict_pass_gap(
            other_class, pi, lambda bit: True, lambda bit: True,
            lambda trace: trace.g1, green, red,
        )
    with pytest.raises(ValueError, match="nonempty"):
        class_factor((), pi, pi, lambda trace: True)
    constant = class_factor((green,), pi, pi, lambda trace: True)
    assert constant["factors"] is True
    assert constant["factor"][((), ())] is True

    early = negative_defect_trace(
        pi, pi, lambda _carrier: True, lambda _carrier: True,
        lambda trace: not trace.g1, green, red,
    )
    assert early[0] is green
    assert early[1] == -1
