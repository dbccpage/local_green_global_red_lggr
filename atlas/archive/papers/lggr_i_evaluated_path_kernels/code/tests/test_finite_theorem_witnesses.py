"""Finite witnesses for LGGR I ledger rows whose checks call shipped code."""

import pytest

from carrier_kernel_census import carrier_verdicts_agree
from epk_core import DefectKind, EPKMetrics, EvaluatorVerdictTriple


def _report(triples: list[EvaluatorVerdictTriple]):
    report = EPKMetrics.compute(triples)
    EPKMetrics.verify_identities(report)
    return report


def test_e3_same_local_count_different_global() -> None:
    green = _report([EvaluatorVerdictTriple(1, 1, 1)])
    red = _report([EvaluatorVerdictTriple(1, 1, 0)])
    assert green.sample_size == red.sample_size
    assert green.local_pass_count == red.local_pass_count == 1
    assert green.global_pass_count != red.global_pass_count
    assert green.ngd_count != red.ngd_count
    assert green.delta_sum != red.delta_sum


def test_e4_same_local_product_different_global() -> None:
    left = EvaluatorVerdictTriple(0, 1, 1)
    right = EvaluatorVerdictTriple(0, 1, 0)
    assert left.local_product == right.local_product == 0
    assert left.eg != right.eg
    assert left.delta_eval != right.delta_eval


def test_e5_defect_kind_matches_boolean_classes() -> None:
    ngd = EvaluatorVerdictTriple(1, 1, 0)
    pgd = EvaluatorVerdictTriple(0, 1, 1)
    zdr = EvaluatorVerdictTriple(1, 1, 1)
    assert ngd.is_ngd and ngd.defect_kind == DefectKind.NGD
    assert pgd.is_pgd and pgd.defect_kind == DefectKind.PGD
    assert zdr.is_zdr and zdr.defect_kind == DefectKind.ZDR


def test_e9_same_pass_counts_different_partition() -> None:
    clean = _report(
        [EvaluatorVerdictTriple(1, 1, 1), EvaluatorVerdictTriple(0, 0, 0)]
    )
    cancelling = _report(
        [EvaluatorVerdictTriple(1, 1, 0), EvaluatorVerdictTriple(0, 0, 1)]
    )
    assert clean.local_pass_count == cancelling.local_pass_count
    assert clean.global_pass_count == cancelling.global_pass_count
    assert clean.delta_sum == cancelling.delta_sum
    assert clean.egd != cancelling.egd
    assert clean.ngd_count != cancelling.ngd_count
    assert clean.pgd_count != cancelling.pgd_count
    assert clean.zdr_count != cancelling.zdr_count


def test_e11_ngd_count_is_bounded_by_local_passes() -> None:
    report = _report(
        [
            EvaluatorVerdictTriple(1, 1, 0),
            EvaluatorVerdictTriple(1, 1, 1),
            EvaluatorVerdictTriple(0, 1, 1),
        ]
    )
    assert report.ngd_count <= report.local_pass_count
    assert report.ngd_count == 1
    assert report.local_pass_count == 2


def test_e12_same_dashboard_same_defect() -> None:
    left = EvaluatorVerdictTriple(0, 1, 1)
    right = EvaluatorVerdictTriple(1, 0, 1)
    assert left.local_product == right.local_product
    assert left.eg == right.eg
    assert left.delta_eval == right.delta_eval


def test_e13_same_defect_different_verdicts() -> None:
    green = EvaluatorVerdictTriple(1, 1, 1)
    red = EvaluatorVerdictTriple(0, 0, 0)
    assert green.delta_eval == red.delta_eval == 0
    assert green.local_product != red.local_product
    assert green.eg != red.eg


def test_e14_defect_plus_local_determines_global() -> None:
    for triple in (
        EvaluatorVerdictTriple(1, 1, 0),
        EvaluatorVerdictTriple(0, 1, 1),
        EvaluatorVerdictTriple(1, 0, 0),
    ):
        assert triple.eg == triple.local_product + triple.delta_eval


def test_e15_defect_kind_agrees_with_defect_value() -> None:
    samples = [
        EvaluatorVerdictTriple(1, 1, 0),
        EvaluatorVerdictTriple(0, 1, 1),
        EvaluatorVerdictTriple(0, 0, 0),
    ]
    for left in samples:
        for right in samples:
            assert (left.defect_kind == right.defect_kind) == (
                left.delta_eval == right.delta_eval
            )


def test_e16_one_boolean_key_collides() -> None:
    ngd = EvaluatorVerdictTriple(1, 1, 0)
    pgd = EvaluatorVerdictTriple(0, 1, 1)
    zdr = EvaluatorVerdictTriple(1, 1, 1)
    lrgr = EvaluatorVerdictTriple(0, 0, 0)
    assert len({ngd.defect_kind, pgd.defect_kind, zdr.defect_kind}) == 3
    assert ngd.local_product == zdr.local_product
    assert ngd.defect_kind != zdr.defect_kind
    assert ngd.eg == lrgr.eg
    assert ngd.defect_kind != lrgr.defect_kind


def test_e17_carrier_collision_agrees() -> None:
    assert carrier_verdicts_agree(lambda bit: 0, lambda _bit: True, True, False)


def test_e18_h2_failure_partition() -> None:
    sample = [
        EvaluatorVerdictTriple(1, 1, 0),
        EvaluatorVerdictTriple(0, 0, 0),
        EvaluatorVerdictTriple(1, 1, 1),
        EvaluatorVerdictTriple(0, 1, 1),
    ]
    assert EPKMetrics.failure_partition_holds(sample)
    failure, ngd, lrgr = EPKMetrics.failure_partition(sample)
    assert (failure, ngd, lrgr) == (2, 1, 1)
    assert EPKMetrics.ngd_below_failure_given_both_witnesses(sample) is True
    with pytest.raises(ValueError, match="empty"):
        EPKMetrics.failure_partition([])
    with pytest.raises(ValueError, match="witnesses"):
        EPKMetrics.ngd_below_failure_given_both_witnesses(
            [EvaluatorVerdictTriple(1, 1, 0)]
        )
