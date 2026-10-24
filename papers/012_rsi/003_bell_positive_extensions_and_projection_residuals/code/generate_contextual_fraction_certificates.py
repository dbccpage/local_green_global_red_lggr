"""Regenerate the 78 GLM fixtures with a separate LP encoding and exact checks.

Default is read-only. --write replaces the fixture after every case verifies.
The original GLM solver and its historical checkpoint/summary bugs are not used.
"""
import argparse
import importlib.util
import json
from fractions import Fraction as F
from pathlib import Path
import sys
import numpy as np
from scipy.optimize import linprog
from contextual_fraction import incidence, require, verify_case

ROOT = Path(__file__).resolve().parents[1]


def rationals(values):
    return [str(F(float(v)).limit_denominator(10**7)) for v in values]


def generate():
    source = ROOT/"docs/source_inputs/glm_2026_10_23/verify_cf2n.py"
    spec = importlib.util.spec_from_file_location("glm_behavior_fixtures", source)
    fixtures = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixtures)
    cases = []
    for parties, battery in [(2, fixtures.chsh_battery()), (3, fixtures.ghz_battery())]:
        for name, p, _kind in battery:
            _, _, _, matrix = incidence(parties)
            A = np.array(matrix, dtype=float)
            b = np.array(p, dtype=float)
            n = A.shape[1]
            cf = linprog(-np.ones(n), A_ub=A, b_ub=b, bounds=(0,None), method="highs")
            require(cf.success, "CF candidate search failed: "+name)
            neg = linprog(np.r_[np.zeros(n), np.ones(n)], A_eq=np.c_[A,-A],
                          b_eq=b, bounds=(0,None), method="highs")
            require(neg.success, "N candidate search failed: "+name)
            gamma = rationals(cf.x)
            split = list(map(F, rationals(neg.x)))
            q = [split[j]-split[n+j] for j in range(n)]
            valcf = 1-sum(map(F, gamma))
            valn = sum(max(-v, 0) for v in q)
            case = dict(name=name, parties=parties, p=list(map(str,p)),
                        cf_primal=gamma, cf_dual=rationals(-cf.ineqlin.marginals),
                        n_primal=list(map(str,q)), n_dual=rationals(neg.eqlin.marginals),
                        cf=str(valcf), n=str(valn))
            verify_case(case)
            cases.append(case)
    return cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    cases = generate()
    counts = {r:0 for r in ("equal","less","greater")}
    for case in cases:
        cf, neg = F(case["cf"]), F(case["n"])
        counts["equal" if cf == 2*neg else "less" if cf < 2*neg else "greater"] += 1
    require(counts == {"equal":74,"less":3,"greater":1}, "unexpected comparison result")
    if args.write:
        path = ROOT/"data/contextual_fraction_certificates.json"
        path.write_text(json.dumps(dict(schema_version=1, counts=counts, cases=cases),
                                   indent=2)+"\n", encoding="utf-8")
    print("PASS regenerated 78 exactly checked CF/N certificates:", counts)


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    main()

