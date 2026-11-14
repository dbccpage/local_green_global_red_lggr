#!/usr/bin/env python3
"""Check finite primal/dual certificates with exact rational arithmetic.

These two cycle examples witness the stated linear repair definitions; they
are not certificates for every manuscript claim or an empirical system.
"""
from fractions import Fraction as Q
from pathlib import Path
import json

def check(case, boundary):
    delta, alpha, y = ([Q(x) for x in case[k]] for k in ("delta", "primal", "dual"))
    m, n = len(boundary), len(boundary[0])
    if len(delta) != m or len(y) != m or len(alpha) != n:
        raise ValueError("Certificate dimension mismatch")
    residual = [delta[i] - sum(Q(boundary[i][j])*alpha[j] for j in range(n)) for i in range(m)]
    if any(sum(Q(boundary[i][j])*y[i] for i in range(m)) for j in range(n)):
        raise ValueError("Dual does not annihilate repairs")
    if max(map(abs,y), default=Q(0)) > 1:
        raise ValueError("Dual norm exceeds one")
    upper = sum(map(abs,residual)); lower = sum(a*b for a,b in zip(delta,y,strict=True))
    if lower != upper or upper != Q(case["optimum"]):
        raise ValueError("Primal and dual bounds do not meet")
    return {"case":case["name"], "residual":list(map(str,residual)), "lower":str(lower), "upper":str(upper), "status":"PASS"}

if __name__ == "__main__":
    data=json.loads((Path(__file__).resolve().parents[1]/"docs/witnesses/cycle_certificates.json").read_text())
    print(json.dumps([check(c,data["d0"]) for c in data["cases"]],sort_keys=True))
