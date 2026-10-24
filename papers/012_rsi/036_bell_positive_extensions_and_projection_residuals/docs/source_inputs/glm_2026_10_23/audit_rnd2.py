#!/usr/bin/env python3
"""
audit_rnd2.py — gold-standard certification of the §18-conjecture violation at
the GHZ battery point rnd2 (mixture k=4, den=12).

The conjecture CF(p) <= 2 N(p) held with equality on the CHSH battery (62/62)
and on both isotropic lines, but GHZ rnd2 returned CF = 19/64 > 2N = 25/128
from the exact simplex with re-verified primal certificates.  Before claiming
a counterexample, this script certifies BOTH values independently:

  1. N  = 25/256: (a) primal re-run under pure Bland pivoting;
                  (b) the Proposition-4 dual LP  max p.alpha + beta
                      s.t. -1 <= alpha.l_lam + beta <= 0 over all 64 vertices,
                      with the returned (alpha, beta) re-verified as a feasible
                      dual point attaining the primal optimum (strong duality
                      in exact arithmetic).

  2. CF = 19/64: (a) primal re-run under pure Bland pivoting;
                  (b) the CF-LP dual  max p.u  s.t. D^T(u + v) = 0 (27 moment
                      orthogonality rows), v >= 0, sum_{i match lam} u_i <= -1
                      for all 64 assignments — re-verified as a feasible dual
                      point; its value certifies w_max <= 45/64, i.e.
                      CF >= 19/64.  Combined with the (re-verified) primal
                      decomposition certificate CF <= 19/64, CF is pinched.

Every number is an exact Fraction.  Exit 0 iff all certificates close.
"""

import itertools
import sys
import time
from fractions import Fraction as F

import verify_cf2n as m

FAILS = []


def ck(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


def main():
    # ---- rebuild the point deterministically from the battery ----
    pts = {name: (p, kind) for name, p, kind in m.ghz_battery()}
    name = "GHZ rnd2 (k=4, den=12)"
    p, kind = pts[name]
    ok_norm = all(
        sum(p[m.ghz_entry_index(x, y, z, a, b, c)]
            for a, b, c in itertools.product((0, 1), repeat=3)) == 1
        for x, y, z in itertools.product((0, 1), repeat=3))
    ok_ns = m.ghz_is_ns(p)
    ck(f"{name}: rebuilt from the seeded battery; normalized = {ok_norm},"
       f" fully no-signalling = {ok_ns}", ok_norm and ok_ns)

    # ---- N: primal under Bland-only pivoting ----
    saved = m.BLAND_ONLY[0]
    m.BLAND_ONLY[0] = True
    t0 = time.time()
    st, val, x = m.lp_min_negmass(m.T_GHZ, p)
    q = [x[j] - x[64 + j] for j in range(64)]
    ck(f"N primal (Bland-only): status={st}, N = {val}  [{time.time()-t0:.1f}s]",
       st == 'optimal' and val == F(25, 256)
       and m.apply_T(m.T_GHZ, q) == [F(v) for v in p] and sum(q) == 1
       and sum(-v for v in q if v < 0) == val)
    m.BLAND_ONLY[0] = saved

    # ---- N: Proposition-4 dual LP over the 64 vertices ----
    na = 64
    n = 2 * na + 2 + 2 * na          # alpha+/-, beta+/-, s1, s2
    A_rows, rhs = [], []
    for j in range(na):
        row = [F(0)] * n
        for cell in range(na):
            if m.T_GHZ[cell][j]:
                row[cell] += F(1)
                row[na + cell] -= F(1)
        row[2 * na] += F(1)
        row[2 * na + 1] -= F(1)
        row[2 * na + 2 + j] = F(1)               # s1: value + beta <= 0
        A_rows.append(row)
        rhs.append(F(0))
        row2 = [F(0)] * n
        for cell in range(na):
            if m.T_GHZ[cell][j]:
                row2[cell] += F(1)
                row2[na + cell] -= F(1)
        row2[2 * na] += F(1)
        row2[2 * na + 1] -= F(1)
        row2[2 * na + 2 + na + j] = F(-1)        # s2: value + beta >= -1
        A_rows.append(row2)
        rhs.append(F(-1))
    c = ([F(-p[k]) for k in range(na)] + [F(p[k]) for k in range(na)]
         + [F(-1), F(1)] + [F(0)] * (2 * na))
    t0 = time.time()
    st2, val2, x2 = m.simplex(A_rows, rhs, c)
    alpha = [x2[k] - x2[na + k] for k in range(na)]
    beta = x2[2 * na] - x2[2 * na + 1]
    vv = [sum(alpha[cell] * m.T_GHZ[cell][j] for cell in range(na)) for j in range(na)]
    dual_ok = (st2 == 'optimal'
               and max(vv) - min(vv) <= 1
               and beta == -max(vv)
               and m.dot(alpha, p) + beta == -val2)
    ck(f"N dual (Prop 4): status={st2}, value = {-val2}  [{time.time()-t0:.1f}s];"
       f" certificate: spread(alpha.l) = {max(vv)-min(vv)} <= 1,"
       f" beta = -max = {-max(vv)}, alpha.p + beta = {m.dot(alpha, p) + beta}",
       dual_ok)
    ck("STRONG DUALITY for N at rnd2: dual == primal == 25/256",
       dual_ok and st == 'optimal' and -val2 == val == F(25, 256))

    # ---- CF: primal under Bland-only pivoting ----
    m.BLAND_ONLY[0] = True
    t0 = time.time()
    st3, w, gamma, moments = m.lp_cf_ghz_moment(p)
    delta = m.ghz_delta_from_moments(moments)
    gpart = m.apply_T(m.T_GHZ, gamma)
    kappa_ctx = sum(delta[m.ghz_entry_index(0, 0, 0, a, b, c)]
                    for a, b, c in itertools.product((0, 1), repeat=3))
    ck(f"CF primal (Bland-only): status={st3}, w_max = {w}  [{time.time()-t0:.1f}s]",
       st3 == 'optimal' and w == F(45, 64)
       and all(g >= 0 for g in gamma)
       and [gpart[i] + delta[i] for i in range(64)] == [F(v) for v in p]
       and all(d >= 0 for d in delta)
       and m.ghz_delta_marginals_ok(delta)
       and sum(gamma) + kappa_ctx == 1)
    m.BLAND_ONLY[0] = saved

    # ---- CF: dual LP  max p.u  s.t. D^T(u+v) = 0, v >= 0, match-sums <= -1 ----
    idx, _ = m.ghz_moment_index()
    moments27 = [('kappa', None)] + [(nm, k) for nm in ('U', 'W', 'T') for k in (0, 1)] \
        + [(nm, k) for nm in ('Pxy', 'Pxz', 'Pyz') for k in itertools.product((0, 1), repeat=2)] \
        + [('XYZ', k) for k in itertools.product((0, 1), repeat=3)]
    # D[cell][k] coefficients (the m+ column entries)
    D = []
    for cell in range(64):
        expr = m.ghz_delta_expr(idx, cell)
        D.append([expr.get(idx[nm][k] if nm != 'kappa' else idx['kappa'], F(0))
                  for nm, k in moments27])
    nvar = 2 * 64 + 64 + 64            # u+/u-, v >= 0, slacks
    A_rows, rhs = [], []
    for k in range(27):
        row = [F(0)] * nvar
        for cell in range(64):
            d = D[cell][k]
            if d:
                row[cell] += d
                row[64 + cell] -= d
                row[128 + cell] += d
        A_rows.append(row)
        rhs.append(F(0))
    for lam in range(64):
        row = [F(0)] * nvar
        for cell in range(64):
            if m.T_GHZ[cell][lam]:
                row[cell] += F(1)
                row[64 + cell] -= F(1)
        row[192 + lam] = F(1)
        A_rows.append(row)
        rhs.append(F(-1))
    c = ([F(-p[k]) for k in range(64)] + [F(p[k]) for k in range(64)]
         + [F(0)] * 128)
    t0 = time.time()
    st4, val4, x4 = m.simplex(A_rows, rhs, c)
    u = [x4[k] - x4[64 + k] for k in range(64)]
    v = x4[128:192]
    # re-verify the dual certificate
    okD = all(sum(D[cell][k] * (u[cell] + v[cell]) for cell in range(64)) == 0
              for k in range(27))
    okM = all(sum(u[cell] for cell in range(64) if m.T_GHZ[cell][lam]) <= -1
              for lam in range(64))
    okV = all(vv >= 0 for vv in v)
    obj = m.dot(p, u)
    ck(f"CF dual: status={st4}, value = {obj}  [{time.time()-t0:.1f}s];"
       f" certificate: D^T(u+v)=0 {okD}, v >= 0 {okV}, match-sums <= -1 {okM}",
       st4 == 'optimal' and okD and okM and okV and obj == -val4)
    ck("STRONG DUALITY for CF at rnd2: dual == primal optimum (CF = 19/64)",
       st4 == 'optimal' and obj == F(19, 64) - 1 and st3 == 'optimal' and w == F(45, 64))

    # ---- verdict ----
    cf = F(19, 64)
    two_n = 2 * F(25, 256)
    print(f"\nVIOLATION VERDICT at {name}:")
    print(f"  CF  = {cf}  (pinched: primal decomposition CF <= {cf};"
          f" dual certificate CF >= {cf})")
    print(f"  2N  = {two_n}  (pinched: signed-extension primal N <= {two_n}/2;"
          f" Prop-4 dual N >= {two_n}/2)")
    print(f"  CF - 2N = {cf - two_n} > 0")
    ck("CERTIFIED COUNTEREXAMPLE: CF > 2N with both values certificate-pinned",
       cf > two_n)
    if FAILS:
        print("\nFAILURES:", *FAILS, sep="\n  ")
        sys.exit(1)
    print("\nAll certificates close. The §18 conjecture CF <= 2N is REFUTED on"
          " the (3,2,2) GHZ scenario by this behavior.")
    sys.exit(0)


if __name__ == '__main__':
    main()
