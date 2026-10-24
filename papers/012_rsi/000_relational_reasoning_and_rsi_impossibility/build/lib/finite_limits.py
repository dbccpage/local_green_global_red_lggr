"""Exact finite research models, not a model of unrestricted intelligence.

All worlds and tests are declared explicitly. Queries are deterministic and
non-destructive. Source truth and an agent's comprehension are not certified.
"""
from collections import deque
from fractions import Fraction as Q
from functools import lru_cache


def rational(value):
    if type(value) not in (int, Q):
        raise ValueError("EXACT_RATIONAL_REQUIRED")
    return Q(value)


def fiber_certificate(view, values):
    if type(view) is not tuple or type(values) is not tuple or not values or len(view) != len(values):
        raise ValueError("NONEMPTY_MATCHING_TUPLES_REQUIRED")
    values = tuple(map(rational, values))
    if any(type(v) not in (str, int) for v in view):
        raise ValueError("FINITE_VIEW_LABEL_REQUIRED")
    groups = {}
    for index, label in enumerate(view):
        groups.setdefault(label, []).append(index)
    fibers, diameter, witness = [], Q(0), None
    for label, indices in groups.items():
        low = min(indices, key=lambda i: values[i])
        high = max(indices, key=lambda i: values[i])
        width = values[high] - values[low]
        if width > diameter:
            diameter, witness = width, (low, high)
        fibers.append((label, values[low], values[high], (values[low]+values[high])/2))
    return {"diameter": diameter, "radius": diameter/2, "witness": witness, "fibers": tuple(fibers)}


def verify_fibers(view, values, certificate):
    """Independent pair-based replay; does not call the extrema generator."""
    try:
        if type(certificate) is not dict or set(certificate) != {"diameter", "radius", "witness", "fibers"}:
            return False
        if (type(view) is not tuple or type(values) is not tuple or not values or len(view) != len(values)
                or any(type(label) not in (str, int) for label in view)):
            return False
        values = tuple(map(rational, values))
        rational(certificate["diameter"])
        rational(certificate["radius"])
        gap = max(abs(values[i]-values[j]) for i in range(len(view)) for j in range(len(view)) if view[i] == view[j])
        if certificate["diameter"] != gap or certificate["radius"] != gap/2:
            return False
        expected = set(view)
        seen = set()
        for label, lo, hi, middle in certificate["fibers"]:
            if type(label) not in (str, int):
                return False
            for scalar in (lo, hi, middle):
                rational(scalar)
            if label not in expected or label in seen:
                return False
            seen.add(label)
            members = [values[i] for i in range(len(view)) if view[i] == label]
            if (lo not in members or hi not in members or any(not lo <= v <= hi for v in members)
                    or middle != (lo+hi)/2 or any(abs(v-middle) > (hi-lo)/2 for v in members)):
                return False
        if seen != expected:
            return False
        witness = certificate["witness"]
        if gap == 0:
            return witness is None
        i, j = witness
        return (type(i) is int and type(j) is int and 0 <= i < len(view) and 0 <= j < len(view)
                and view[i] == view[j] and abs(values[i]-values[j]) == gap)
    except (ValueError, TypeError, KeyError, IndexError):
        return False


def checked_extension(old_view, old_values, new_view, new_values, *, cap=Q(0)):
    """Retain the old observations and certify the complete enlarged archive."""
    cap = rational(cap)
    if cap < 0:
        raise ValueError("NONNEGATIVE_CAP_REQUIRED")
    view, values = old_view + new_view, old_values + new_values
    certificate = fiber_certificate(view, values)
    if not verify_fibers(view, values, certificate):
        raise ValueError("CERTIFICATE_MISMATCH")
    if certificate["radius"] > cap:
        raise ValueError("MEMORY_CONTRACT_BROKEN")
    return view, values, certificate


def validate_system(readout, actions):
    if type(readout) is not tuple or not readout or len(readout) > 64 or type(actions) is not tuple:
        raise ValueError("FINITE_SYSTEM_REQUIRED")
    if any(type(v) not in (str, int, Q) for v in readout):
        raise ValueError("EXACT_READOUT_REQUIRED")
    if len(actions) > 16 or any(type(a) is not tuple or len(a) != len(readout)
            or any(type(j) is not int or not 0 <= j < len(readout) for j in a) for a in actions):
        raise ValueError("TOTAL_FINITE_ACTIONS_REQUIRED")


def future_partition(readout, actions):
    validate_system(readout, actions)
    def classes(signatures):
        seen = {}
        return tuple(seen.setdefault(s, len(seen)) for s in signatures)
    labels = classes(readout)
    for _ in range(len(readout)):
        refined = classes(tuple((labels[i], *(labels[a[i]] for a in actions)) for i in range(len(readout))))
        if refined == labels:
            return labels
        labels = refined
    raise ValueError("REFINEMENT_INVARIANT_BROKEN")


def distinguishing_word(readout, actions, left, right):
    """Independent product-state search for a future readout difference."""
    validate_system(readout, actions)
    if any(type(i) is not int or not 0 <= i < len(readout) for i in (left, right)):
        raise ValueError("STATE_OUT_OF_RANGE")
    queue, seen = deque([(left, right, ())]), set()
    while queue:
        x, y, word = queue.popleft()
        if (x, y) in seen:
            continue
        seen.add((x, y))
        if readout[x] != readout[y]:
            return word
        for index, action in enumerate(actions):
            queue.append((action[x], action[y], word+(index,)))
    return None


def memory_capacity(readout, actions):
    count = len(set(future_partition(readout, actions)))
    return {"classes": count, "fixed_length_bits": (count-1).bit_length()}


def optimal_queries(values, queries, *, tolerance=Q(0)):
    """Minimize worst-case query count; None means the declared panel cannot solve it.

    At most twelve worlds and sixteen tests: this is a small exact solver.
    A tree leaf supplies the midpoint decoder that is actually needed for use.
    """
    if (type(values) is not tuple or not 1 <= len(values) <= 12 or type(queries) is not tuple
            or len(queries) > 16 or any(type(q) is not tuple or len(q) != len(values)
            or any(type(v) is not int for v in q) for q in queries)):
        raise ValueError("BOUNDED_QUERY_MODEL_REQUIRED")
    values = tuple(map(rational, values))
    tolerance = rational(tolerance)
    if tolerance < 0:
        raise ValueError("NONNEGATIVE_TOLERANCE_REQUIRED")

    @lru_cache(None)
    def solve(states):
        low, high = min(values[i] for i in states), max(values[i] for i in states)
        if high-low <= 2*tolerance:
            return 0, {"value": str((low+high)/2)}
        best = None
        for index, query in enumerate(queries):
            parts = tuple((outcome, tuple(i for i in states if query[i] == outcome))
                          for outcome in sorted({query[i] for i in states}))
            if len(parts) == 1:
                continue
            children = [(o, solve(s)) for o, s in parts]
            if any(child is None for _, child in children):
                continue
            depth = 1+max(child[0] for _, child in children)
            candidate = depth, {"query": index, "children": {str(o): child[1] for o, child in children}}
            if best is None or depth < best[0]:
                best = candidate
        return best
    return solve(tuple(range(len(values))))


def verify_query_tree(values, queries, result, *, tolerance=Q(0)):
    """Replay every branch, then independently test whether a shallower strategy exists."""
    try:
        values, tolerance = tuple(map(rational, values)), rational(tolerance)
        if tolerance < 0 or not values or len(values) > 12:
            return False
        if type(queries) is not tuple or len(queries) > 16 or any(type(q) is not tuple or len(q) != len(values) or any(type(v) is not int for v in q) for q in queries):
            return False
        def fits(states):
            return max(values[i] for i in states)-min(values[i] for i in states) <= 2*tolerance
        @lru_cache(None)
        def possible(states, budget):
            if fits(states):
                return True
            if budget == 0:
                return False
            for q in queries:
                parts = tuple(tuple(i for i in states if q[i] == o) for o in sorted({q[i] for i in states}))
                if len(parts) > 1 and all(possible(part, budget-1) for part in parts):
                    return True
            return False
        states = tuple(range(len(values)))
        if result is None:
            return not possible(states, len(values)-1)
        depth, tree = result
        if type(depth) is not int or not 0 <= depth < len(values):
            return False
        def visit(states, node):
            if type(node) is not dict:
                raise ValueError("INVALID_TREE")
            if set(node) == {"value"}:
                value = Q(node["value"])
                if str(value) != node["value"] or any(abs(values[i]-value) > tolerance for i in states):
                    raise ValueError("INVALID_LEAF")
                return 0
            if set(node) != {"query", "children"} or type(node["query"]) is not int or not 0 <= node["query"] < len(queries):
                raise ValueError("INVALID_TREE")
            query = queries[node["query"]]
            outcomes = sorted({query[i] for i in states})
            if len(outcomes) < 2 or set(node["children"]) != {str(o) for o in outcomes}:
                raise ValueError("INVALID_BRANCHES")
            return 1+max(visit(tuple(i for i in states if query[i] == o), node["children"][str(o)]) for o in outcomes)
        return visit(states, tree) == depth and (depth == 0 or not possible(states, depth-1))
    except (ValueError, TypeError, KeyError, IndexError, ZeroDivisionError, RecursionError):
        return False
