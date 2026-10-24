"""Finite executable memory experiment matching MemoryImplementation.lean.

These are pure finite models. No persistence or live-agent integration is claimed.
"""


def _pair(value):
    if type(value) is not tuple or len(value) != 2 or any(type(x) is not bool for x in value):
        raise ValueError("BOOLEAN_PAIR_REQUIRED")
    return value


def _rows(rows):
    if type(rows) is not tuple:
        raise ValueError("IMMUTABLE_ROWS_REQUIRED")
    for row in rows:
        _pair(row)
    return rows


def compatible(rows):
    rows = _rows(rows)
    return all(p[0] != q[0] or p[1] == q[1] for p in rows for q in rows)


def append_checked(old, fresh):
    proposed = _rows(old) + _rows(fresh)
    return proposed if compatible(proposed) else None


def recall_checked(rows, label, candidate):
    _pair((label, candidate))
    rows = _rows(rows)
    if (label, candidate) in rows and all(p[0] != label or p[1] == candidate for p in rows):
        return candidate
    return None


def encode(state):
    first, second = _pair(state)
    return second, first


def swap(state, action):
    _pair(state)
    if type(action) is not bool:
        raise ValueError("BOOLEAN_ACTION_REQUIRED")
    return encode(state) if action else state


def gated_overwrite(state, candidate):
    _pair(state)
    _pair(candidate)
    return candidate if candidate != (True, True) else state
