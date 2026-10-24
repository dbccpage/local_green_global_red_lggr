"""Finite checks for LGGR I carrier-kernel rows I1–I7.

The functions evaluate the Boolean instances named by the Lean development.
They do not replay an arbitrary carrier.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Tuple


def _exact_bool(value: Any, name: str) -> bool:
    if type(value) is not bool:
        raise TypeError(f"{name} must be an exact bool, got {type(value).__name__}")
    return value


def b2i(bit: bool) -> int:
    return 1 if _exact_bool(bit, "bit") else 0


def local_product(left: bool, right: bool) -> int:
    return b2i(left) * b2i(right)


def delta_eval(left: bool, right: bool, global_pass: bool) -> int:
    return b2i(global_pass) - local_product(left, right)


def induced_verdict(
    carrier: Callable[[Any], Any],
    evaluator: Callable[[Any], bool],
    trace: Any,
) -> bool:
    return _exact_bool(evaluator(carrier(trace)), "induced evaluator")


def verdict_ceiling_witness(
    carrier: Callable[[Any], Any],
    evaluator: Callable[[Any], bool],
    target: Callable[[Any], bool],
    trace: Any,
    other: Any,
) -> Any:
    """Return a trace where the carrier-bounded evaluator misses `target`."""
    if carrier(trace) != carrier(other):
        raise ValueError("traces are not in one carrier class")
    target_trace = _exact_bool(target(trace), "target")
    target_other = _exact_bool(target(other), "target")
    if target_trace == target_other:
        raise ValueError("target does not vary on the class")
    if induced_verdict(carrier, evaluator, trace) != target_trace:
        return trace
    return other


def carrier_verdicts_agree(
    carrier: Callable[[Any], Any],
    evaluator: Callable[[Any], bool],
    trace: Any,
    other: Any,
) -> bool:
    if carrier(trace) != carrier(other):
        raise ValueError("traces are not in one carrier class")
    return induced_verdict(carrier, evaluator, trace) == induced_verdict(
        carrier, evaluator, other
    )


def downstream_verdicts_agree(
    carrier: Callable[[Any], Any],
    chain: Callable[[Any], Any],
    judge: Callable[[Any], bool],
    trace: Any,
    other: Any,
) -> bool:
    if carrier(trace) != carrier(other):
        raise ValueError("traces are not in one carrier class")
    left = _exact_bool(judge(chain(carrier(trace))), "downstream judge")
    right = _exact_bool(judge(chain(carrier(other))), "downstream judge")
    return left == right


class Composed:
    """Declared two-stage trace `(g1, g2)`."""

    def __init__(self, g1: Any, g2: Any) -> None:
        self.g1 = g1
        self.g2 = g2


def joint_carrier(
    pi1: Callable[[Any], Any],
    pi2: Callable[[Any], Any],
    trace: Composed,
) -> Tuple[Any, Any]:
    return (pi1(trace.g1), pi2(trace.g2))


def composed_bits(
    pi1: Callable[[Any], Any],
    pi2: Callable[[Any], Any],
    e1: Callable[[Any], bool],
    e2: Callable[[Any], bool],
    trace: Composed,
) -> Tuple[bool, bool]:
    left = _exact_bool(e1(pi1(trace.g1)), "e1")
    right = _exact_bool(e2(pi2(trace.g2)), "e2")
    return left, right


def composed_local_product(
    pi1: Callable[[Any], Any],
    pi2: Callable[[Any], Any],
    e1: Callable[[Any], bool],
    e2: Callable[[Any], bool],
    trace: Composed,
) -> int:
    left, right = composed_bits(pi1, pi2, e1, e2, trace)
    return local_product(left, right)


def composed_delta(
    pi1: Callable[[Any], Any],
    pi2: Callable[[Any], Any],
    e1: Callable[[Any], bool],
    e2: Callable[[Any], bool],
    global_evaluator: Callable[[Composed], bool],
    trace: Composed,
) -> int:
    left, right = composed_bits(pi1, pi2, e1, e2, trace)
    return delta_eval(left, right, global_evaluator(trace))


def locally_green(
    pi1: Callable[[Any], Any],
    pi2: Callable[[Any], Any],
    e1: Callable[[Any], bool],
    e2: Callable[[Any], bool],
    trace: Composed,
) -> bool:
    left, right = composed_bits(pi1, pi2, e1, e2, trace)
    return left and right


def class_factor(
    traces: Tuple[Composed, ...],
    pi1: Callable[[Any], Any],
    pi2: Callable[[Any], Any],
    value,
) -> Dict[str, Any]:
    """Factor `value` through joint-carrier classes when each class is constant."""
    if not traces:
        raise ValueError("traces must be nonempty")
    classes: Dict[Tuple[Any, Any], set] = {}
    for trace in traces:
        key = joint_carrier(pi1, pi2, trace)
        classes.setdefault(key, set()).add(value(trace))
    blocked = tuple(key for key, vals in classes.items() if len(vals) != 1)
    factor = {
        key: next(iter(vals))
        for key, vals in classes.items()
        if len(vals) == 1
    }
    return {"factors": not blocked, "blocked": blocked, "factor": factor}


def negative_defect_trace(
    pi1: Callable[[Any], Any],
    pi2: Callable[[Any], Any],
    e1: Callable[[Any], bool],
    e2: Callable[[Any], bool],
    global_evaluator: Callable[[Composed], bool],
    trace: Composed,
    other: Composed,
) -> Tuple[Composed, int]:
    if joint_carrier(pi1, pi2, trace) != joint_carrier(pi1, pi2, other):
        raise ValueError("traces are not in one joint-carrier class")
    if not locally_green(pi1, pi2, e1, e2, trace):
        raise ValueError("the first trace is not locally green")
    global_trace = _exact_bool(global_evaluator(trace), "global evaluator")
    global_other = _exact_bool(global_evaluator(other), "global evaluator")
    if global_trace == global_other:
        raise ValueError("global verdicts do not differ")
    delta_trace = composed_delta(pi1, pi2, e1, e2, global_evaluator, trace)
    delta_other = composed_delta(pi1, pi2, e1, e2, global_evaluator, other)
    if not global_trace:
        return trace, delta_trace
    return other, delta_other


def strict_pass_gap(
    pi1: Callable[[Any], Any],
    pi2: Callable[[Any], Any],
    e1: Callable[[Any], bool],
    e2: Callable[[Any], bool],
    global_evaluator: Callable[[Composed], bool],
    trace: Composed,
    other: Composed,
) -> Dict[str, int]:
    if joint_carrier(pi1, pi2, trace) != joint_carrier(pi1, pi2, other):
        raise ValueError("traces are not in one joint-carrier class")
    if not locally_green(pi1, pi2, e1, e2, trace):
        raise ValueError("the first trace is not locally green")
    global_trace = _exact_bool(global_evaluator(trace), "global evaluator")
    global_other = _exact_bool(global_evaluator(other), "global evaluator")
    if global_trace == global_other:
        raise ValueError("global verdicts do not differ")
    global_passes = b2i(global_trace) + b2i(global_other)
    local_passes = composed_local_product(pi1, pi2, e1, e2, trace) + composed_local_product(
        pi1, pi2, e1, e2, other
    )
    return {
        "global_passes": global_passes,
        "local_passes": local_passes,
        "gap": local_passes - global_passes,
    }


def collapse_carrier(_trace: bool) -> Tuple[()]:
    return ()


def demo_traces() -> Tuple[Composed, Composed]:
    """The Lean demo: both stages collapse, and the global bit is the erased `g1`."""
    return Composed(True, True), Composed(False, True)


def section_i_census() -> Dict[str, Any]:
    """Evaluate rows I1–I7 on the collapsing-carrier demo."""
    green, red = demo_traces()
    pi = collapse_carrier
    local_green_eval = lambda _carrier: True
    global_eval = lambda trace: trace.g1
    ceiling = verdict_ceiling_witness(
        pi, lambda _carrier: True, lambda bit: bit, True, False
    )
    same_class = joint_carrier(pi, pi, green) == joint_carrier(pi, pi, red)
    local_green_trace = locally_green(pi, pi, local_green_eval, local_green_eval, green)
    local_green_other = locally_green(pi, pi, local_green_eval, local_green_eval, red)
    products_agree = composed_local_product(
        pi, pi, local_green_eval, local_green_eval, green
    ) == composed_local_product(pi, pi, local_green_eval, local_green_eval, red)
    witness, defect = negative_defect_trace(
        pi, pi, local_green_eval, local_green_eval, global_eval, green, red
    )
    gap = strict_pass_gap(
        pi, pi, local_green_eval, local_green_eval, global_eval, green, red
    )
    downstream = downstream_verdicts_agree(
        pi, lambda _carrier: "post", lambda token: token == "post", True, False
    )
    constant_global = lambda _trace: True
    pair_value = lambda trace: (
        composed_local_product(pi, pi, local_green_eval, local_green_eval, trace),
        constant_global(trace),
    )
    invariant_pair = class_factor((green, red), pi, pi, pair_value)
    mixed_global = class_factor((green, red), pi, pi, global_eval)
    mixed_delta = class_factor(
        (green, red),
        pi,
        pi,
        lambda trace: composed_delta(
            pi, pi, local_green_eval, local_green_eval, global_eval, trace
        ),
    )
    return {
        "same_class": same_class,
        "ceiling_trace": ceiling,
        "carrier_verdicts_agree": carrier_verdicts_agree(
            pi, lambda _carrier: True, True, False
        ),
        "local_green": local_green_trace,
        "local_green_other": local_green_other,
        "products_agree": products_agree,
        "negative_defect_is_red": witness is red,
        "negative_defect": defect,
        "global_passes": gap["global_passes"],
        "local_passes": gap["local_passes"],
        "gap": gap["gap"],
        "downstream_agrees": downstream,
        "invariant_pair_factors": invariant_pair["factors"],
        "mixed_global_factors": mixed_global["factors"],
        "mixed_delta_factors": mixed_delta["factors"],
        "green_delta": composed_delta(
            pi, pi, local_green_eval, local_green_eval, global_eval, green
        ),
        "red_delta": composed_delta(
            pi, pi, local_green_eval, local_green_eval, global_eval, red
        ),
    }
