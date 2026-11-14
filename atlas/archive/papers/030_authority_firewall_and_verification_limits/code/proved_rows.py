"""Finite check for AVF-030-C11.

Calls FinitePartitionCoverage. It does not reimplement coverage or the
omitted-class counterexample.
"""

from __future__ import annotations

from mod_verification_limits_core import DiscreteResidual, FinitePartitionCoverage


def replay_proved_rows() -> dict:
    zero = DiscreteResidual.from_ints(0, 0)
    unit = (DiscreteResidual.from_ints(1, 0), DiscreteResidual.from_ints(-1, 0))
    two = (DiscreteResidual.from_ints(1, 1), DiscreteResidual.from_ints(-1, -1))
    partition = FinitePartitionCoverage(classes=((zero,), unit, two))

    def specification(residual: DiscreteResidual) -> bool:
        return residual.is_exact_zero

    def detector(residual: DiscreteResidual) -> bool:
        return residual.norm1 == 0

    complete = (zero, unit[0], two[0])
    incomplete = (zero, unit[0])
    covered, covered_error = partition.verify_coverage(specification, detector, complete)
    missed, missed_error = partition.verify_coverage(specification, detector, incomplete)
    witness, counterexample = partition.construct_omitted_class_counterexample(specification, incomplete)
    agrees = all(counterexample(item) == specification(item) for item in incomplete)
    return {
        "ok": covered is True
        and covered_error is None
        and missed is False
        and partition.is_class_constant(counterexample) is True
        and agrees is True
        and counterexample(witness) != specification(witness)
        and witness in two,
        "AVF-030-C11": {
            "carrier_size": len(partition.carrier),
            "complete_coverage": covered,
            "complete_error": covered_error,
            "omitted_coverage": missed,
            "omitted_error": missed_error,
            "counterexample_class_constant": partition.is_class_constant(counterexample),
            "counterexample_agrees_on_tested": agrees,
            "counterexample_disagrees_on_omitted": counterexample(witness) != specification(witness),
            "omitted_witness_coordinates": [str(part) for part in witness.coordinates],
        },
    }
