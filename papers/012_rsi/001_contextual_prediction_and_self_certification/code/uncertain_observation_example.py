"""Exact review counterexample: sampling error alone creates a raw LP defect."""
from dataclasses import asdict, replace
from fractions import Fraction as Q
from itertools import product
import json

import contextuality_lp as lp
import epistemic_kernel as k


def example():
    truth_table = k.classical_mixture()
    truth = lp.Scenario((2, 2, 2, 2), ((0, 2), (0, 3), (1, 2), (1, 3)),
                        tuple(tuple(truth_table[c].get(o, Q(0)) for o in product((0, 1), repeat=2))
                              for c in k.CONTEXTS))
    rows = [list(row) for row in truth.tables]
    rows[0][0] -= Q(1, 100)
    rows[0][2] += Q(1, 100)
    observed = replace(truth, tables=rows)
    try:
        lp.evaluate(observed)
    except lp.Refusal as exc:
        public_result = exc.kind
    else:
        raise AssertionError("exact-table evaluator must reject this signalling table")
    radius = Q(1, 50)
    result = lp.evaluate_observed(observed, radius)
    _, _, true_vector = lp.contextual_matrix(truth)
    actual_error = sum(abs(a-b) for a, b in zip(true_vector, result.observed))
    assert actual_error == radius == result.certificate.defect and result.guaranteed_margin == 0
    assert lp.verify_observed(observed, radius, result)
    return {"scope": "exact fixture with known truth; not a statistical coverage calculation",
            "exact_evaluator": public_result, "truth": [str(x) for x in true_vector],
            "observed": [str(x) for x in result.observed],
            "actual_raw_l1_error": str(actual_error), "bound": asdict(result)}


if __name__ == "__main__":
    print(json.dumps(example(), indent=2, default=lambda x: str(x) if type(x) is Q else x))
