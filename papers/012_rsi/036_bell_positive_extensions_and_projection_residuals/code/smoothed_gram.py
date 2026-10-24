"""Exact complete Bell tables with unbounded CF / minimum negative mass.

No LP solver or floating-point tolerance is used.  The certificate is a local
stochastic model minus white noise; quantum realizability follows from the
unit-vector Gram representation (Tsirelson).  Bounds, not optimum claims.
"""
from fractions import Fraction as F
from itertools import product
import json


def profile(k):
    if type(k) is not int or k < 2:
        raise ValueError("k must be an integer at least two")
    n = k * k
    half = tuple(-1 + F(2 * t, k) if t < k else F(1) for t in range(2 * n))
    return half + tuple(-x for x in half)


def certificate(k):
    f = profile(k)
    n, d = k * k, len(f)
    s = sum(x*x for x in f) / d
    energy = sum((f[(t+1) % d]-f[t])**2 for t in range(d))
    assert s == 1 - F(k*k-1, 3*k**3)
    assert energy == F(8, k)
    assert all(abs(x) <= 1 for x in f)
    assert all(f[(t+2*n) % d] == -f[t] for t in range(d))
    # Autocorrelation supplies EVERY pair, including off-chain contexts.
    corr = tuple(sum(f[t]*f[(t+r) % d] for t in range(d))/(d*s) for r in range(d))
    assert corr[0] == 1 and all(abs(c) <= 1 for c in corr)
    v = corr[1]
    assert v == 1-F(1, n*k)/s
    assert corr[2*n-1] == -v
    floor, cap = 1-n*(1-v), (1-s)/s
    assert floor > 0 and cap > 0
    assert floor/cap == 3*k-4+F(3,k+1)
    return dict(k=k, settings=n, contexts=n*n, dimension=d, profile=f,
                norm_square=s, autocorrelation=corr, visibility=v,
                cf_lower=floor, negative_mass_upper=cap, ratio_lower=floor/cap)


def behavior(cert, x, y, a, b):
    n, d = cert["settings"], cert["dimension"]
    if not (type(x) is int and type(y) is int and 0 <= x < n and 0 <= y < n
            and a in (-1, 1) and b in (-1, 1)):
        raise ValueError("invalid Bell cell")
    c = cert["autocorrelation"][(2*y+1-2*x) % d]
    return (1+a*b*c)/4


def local_cell(cert, x, y, a, b):
    """Direct hidden-coordinate / shared-sign stochastic model."""
    f, d = cert["profile"], cert["dimension"]
    return sum((1+a*r*f[(t+2*x) % d])*(1+b*r*f[(t+2*y+1) % d])/4
               for t in range(d) for r in (-1, 1))/(2*d)


def signed_assignment(cert, assignment):
    """Explicit normalized global weights, evaluated only on demand."""
    f, d, n, s = (cert[key] for key in ("profile", "dimension", "settings", "norm_square"))
    if len(assignment) != 2*n or any(a not in (-1, 1) for a in assignment):
        raise ValueError("invalid global assignment")
    shifts = tuple(2*x for x in range(n)) + tuple(2*y+1 for y in range(n))
    local = F(0)
    for t in range(d):
        for r in (-1, 1):
            weight = F(1, 2*d)
            for a, shift in zip(assignment, shifts):
                weight *= (1+a*r*f[(t+shift) % d])/2
            local += weight
    return local/s - (1-s)/s * F(1, 2**(2*n))


def replay():
    rows = []
    for k in (2, 3, 4, 5, 8, 12):
        c = certificate(k)
        n, s = c["settings"], c["norm_square"]
        # Check all context correlations and all four cells; compute the direct
        # hidden-variable mixture once per cyclic difference, not per cell.
        for y in range(n):
            for a, b in product((-1, 1), repeat=2):
                assert local_cell(c, 0, y, a, b)/s-(1-s)/s/4 == behavior(c, 0, y, a, b)
        for x in range(n):
            for y in range(n):
                cells = [behavior(c, x, y, a, b) for a, b in product((-1, 1), repeat=2)]
                assert min(cells) >= 0 and sum(cells) == 1
                assert cells[0]+cells[1] == cells[0]+cells[2] == F(1, 2)
        rows.append({key: str(c[key]) for key in
                     ("k", "settings", "contexts", "cf_lower", "negative_mass_upper", "ratio_lower")})
    # Exhaustive assignment replay on the smallest complete 4x4 member.
    c = certificate(2)
    n = c["settings"]
    weights = {g: signed_assignment(c, g) for g in product((-1, 1), repeat=2*n)}
    assert sum(weights.values()) == 1
    actual_mass = sum(max(-q, 0) for q in weights.values())
    assert actual_mass <= c["negative_mass_upper"]
    for x in range(n):
        for y in range(n):
            for a, b in product((-1, 1), repeat=2):
                assert sum(q for g,q in weights.items() if g[x] == a and g[n+y] == b) == behavior(c,x,y,a,b)
    return {"schema": 1, "scope": "exact finite replay; analytic family proof in manuscript",
            "families": rows, "complete_contexts_checked": sum(int(r["contexts"]) for r in rows),
            "exhaustive_assignments": len(weights), "actual_small_signed_mass": str(actual_mass)}


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))
