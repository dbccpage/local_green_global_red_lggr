"""Exact replay of contextual-fraction and signed-mass certificates.

The solver is not trusted: model enumeration, all feasibility inequalities,
normalization, no-signalling, and equality of objectives are checked here.
Assignments are lexicographic tuples (a0,a1,b0,b1[,c0,c1]); cells are
lexicographic (setting tuple, outcome tuple).
"""
import itertools
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ("p", "cf_primal", "cf_dual", "n_primal", "n_dual")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def vector(case, key, size):
    value = case[key]
    require(type(value) is list and len(value) == size, key + " dimension")
    require(all(type(x) is str for x in value), key + " rational strings required")
    return [Fraction(x) for x in value]


def dot(a, b):
    require(len(a) == len(b), "dot dimensions")
    return sum(x*y for x, y in zip(a, b))


def incidence(parties):
    require(type(parties) is int and parties in (2, 3), "unsupported scenario")
    contexts = list(itertools.product(range(2), repeat=parties))
    outcomes = list(itertools.product(range(2), repeat=parties))
    assignments = list(itertools.product(range(2), repeat=2*parties))
    cells = list(itertools.product(contexts, outcomes))
    matrix = [[int(all(g[2*k+ctx[k]] == out[k] for k in range(parties)))
               for g in assignments] for ctx, out in cells]
    return contexts, outcomes, cells, matrix


def verify_case(case):
    parties = case["parties"]
    contexts, outcomes, cells, matrix = incidence(parties)
    size = len(cells)
    p, gamma, y, q, z = [vector(case, key, size) for key in FIELDS]
    require(all(x >= 0 for x in p), "negative behavior")
    lookup = dict(zip(cells, p))
    require(all(sum(lookup[c, o] for o in outcomes) == 1 for c in contexts),
            "behavior normalization")
    for length in range(1, parties):
        for kept in itertools.combinations(range(parties), length):
            seen = {}
            for ctx in contexts:
                for out in itertools.product(range(2), repeat=length):
                    key = tuple(ctx[k] for k in kept), out
                    mass = sum(lookup[ctx, o] for o in outcomes
                               if tuple(o[k] for k in kept) == out)
                    require(key not in seen or seen[key] == mass, "signalling behavior")
                    seen[key] = mass
    require(all(x >= 0 for x in gamma), "negative local subweight")
    require(all(dot(row, gamma) <= value for row, value in zip(matrix, p)),
            "CF primal domination")
    require(all(x >= 0 for x in y), "CF dual nonnegativity")
    require(all(dot(col, y) >= 1 for col in zip(*matrix)), "CF dual coverage")
    require(sum(gamma) == dot(p, y), "CF duality gap")
    cf = 1-sum(gamma)
    require(sum(q) == 1, "signed extension normalization")
    require(all(dot(row, q) == value for row, value in zip(matrix, p)),
            "signed extension projection")
    require(all(-1 <= dot(col, z) <= 0 for col in zip(*matrix)), "N dual spread")
    negative = sum(max(-x, 0) for x in q)
    require(negative == dot(p, z), "N duality gap")
    require(type(case["cf"]) is str and Fraction(case["cf"]) == cf, "CF objective")
    require(type(case["n"]) is str and Fraction(case["n"]) == negative, "N objective")
    return cf, negative


def replay(path=None):
    path = path or ROOT/"data/contextual_fraction_certificates.json"
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    counterexample = next(c for c in data["cases"] if c["name"] == "GHZ rnd2 (k=4, den=12)")
    _, _, cells, _ = incidence(3)
    documented = []
    for ctx, out in cells:
        parity = sum(out) % 2
        w = Fraction(int(parity == 0), 4)
        local = int(out == (1, 1, 1))
        g = Fraction(int(parity == int(ctx == (0, 0, 0))), 4)
        chi = -1 if sum(ctx) == 0 else 1 if sum(ctx) == 2 else 0
        q = (1 + Fraction(5, 8)*chi*(-1)**parity)/8
        documented.append(w/6 + Fraction(local, 3) + 5*g/12 + q/12)
    require(documented == list(map(Fraction, counterexample["p"])), "manuscript counterexample mixture")
    counts = {"equal": 0, "less": 0, "greater": 0}
    for case in data["cases"]:
        cf, neg = verify_case(case)
        relation = "equal" if cf == 2*neg else "less" if cf < 2*neg else "greater"
        counts[relation] += 1
    require(len(data["cases"]) == 78, "fixture inventory")
    require(counts == {"equal": 74, "less": 3, "greater": 1}, "comparison tally")
    print("PASS 78 exact CF/N certificate cases:", counts)
    return counts


if __name__ == "__main__":
    replay()

