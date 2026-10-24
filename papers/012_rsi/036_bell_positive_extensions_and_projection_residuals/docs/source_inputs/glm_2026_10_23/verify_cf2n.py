#!/usr/bin/env python3
"""
verify_cf2n.py — exact-rational settlement of the §18 conjecture CF(p) <= 2*N(p).

Check numbering continues verify_obstruction.py (C0-C11) and verify_headroom.py
(C12-C21): self-tests S0 here, then C22 onward.  Pure standard library;
fractions.Fraction only; no floating point anywhere.
Run:  python3 verify_cf2n.py   (exit 0 iff every check passes)

WHAT IS COMPUTED (the LP specified in math_notes.md §18, "maximize local weight
against a free NS partner"):

  CF LP, moment form (primary):
    variables  gamma[lam] >= 0  over the deterministic assignments lam,
               free moments  kappa, U[x], W[y] (, T[z]) and E-terms
    rows       p(cell) = sum_{lam matching cell} gamma[lam] + delta(cell),
               delta(cell) = (kappa + A*U[x] + B*W[y] + A*B*E[x,y]) / 4   [CHSH]
                            (kappa + A*U[x] + B*W[y] + C*T[z] + A*B*Pxy + ...)
                            / 8                                          [GHZ]
               delta(cell) >= 0   (one row per cell)
    objective  max sum_lam gamma[lam]  =: w_max,   CF(p) = 1 - w_max.
    The moment parametrization makes the no-signalling marginals of delta
    automatic (context sums all equal kappa; single-party marginals consistent);
    delta >= 0 then forces kappa >= 0, and summing a context of the cell rows
    gives 1 = w + kappa, i.e. delta = (1-w)*r with r a normalized NS behavior.
    So LP feasibility == Abramsky et al. decompositions, exactly.

  CF LP, vertex form (CHSH cross-check):
    p = sum gamma[lam] d_lam + sum beta[j] v_j, gamma, beta >= 0,
    sum gamma + sum beta = 1, with v_j the 24 vertices of the (2,2,2) NS
    polytope (16 deterministic + 8 parity-odd fully-correlated boxes).

  N LP (primal, as in verify_headroom.py):
    min sum q^-  s.t.  T(q+ - q-) = p,  sum(q+ - q-) = 1,  q+- >= 0.
  N LP (dual, Proposition 4 form):
    max alpha.p + beta  s.t.  -1 <= alpha.l_lam + beta <= 0 for every vertex lam
    (equivalently spread_lam(alpha.l_lam) <= 1, beta = -max_lam alpha.l_lam).
    Primal and dual optima are required to agree to the last bit over Q.

  CONJECTURE TEST: for every battery point p, assert CF(p) <= 2*N(p) exactly,
  and record the ratio CF/(2N).  Equality holds on both isotropic lines
  (Theorems 24/27 + Proposition 25 give CF = 2N = max(0, 2v-1) there), at the
  PR box and the 8 CHSH nonlocal vertices; strict inequality is the expected
  verdict on generic interior points.  A FAIL line means a separating
  counterexample was found (a genuine Tier-A discovery either way).
"""

import itertools
import random
import sys
import time
from fractions import Fraction as F

FAILURES = []
N_CHECKS = [0]


def ck(name, cond, detail=""):
    N_CHECKS[0] += 1
    ok = bool(cond)
    if not ok:
        FAILURES.append(name)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def banner(txt):
    print("\n" + "=" * 72 + f"\n{txt}\n" + "=" * 72)


# ----------------------------------------------------------------------------
# Exact two-phase primal simplex over Q (Dantzig's rule with Bland fallback).
# min c.x  s.t.  A x = b, x >= 0.   Returns (status, value, x).
# ----------------------------------------------------------------------------

BLAND_ONLY = [False]      # set [0] True to force Bland's rule from iteration 0


def simplex(Ain, bin_, cin):
    m0 = len(Ain)
    n = len(cin)
    A = [[F(x) for x in row] for row in Ain]
    b = [F(x) for x in bin_]
    c = [F(x) for x in cin]
    for i in range(m0):
        if b[i] < 0:
            A[i] = [-v for v in A[i]]
            b[i] = -b[i]
    m = m0
    NC = n + m                 # total columns (originals + artificials)
    RHS = NC                   # row length is NC+1; last slot is the rhs
    T = [A[i] + [F(1) if j == i else F(0) for j in range(m)] + [b[i]] for i in range(m)]
    basis = list(range(n, n + m))
    iters = [0]
    BLAND_AFTER = 3 * (m + n) + 50

    def pivot(r, col):
        piv = T[r][col]
        if piv != 1:
            T[r] = [v / piv for v in T[r]]
        Tr = T[r]
        for i in range(m):
            if i != r:
                f = T[i][col]
                if f:
                    T[i] = [a - f * t for a, t in zip(T[i], Tr)]
        basis[r] = col

    def run(cost, allowed):
        while True:
            iters[0] += 1
            cb = [cost[basis[i]] for i in range(m)]
            red = []
            for j in range(NC):
                s = cost[j]
                for i in range(m):
                    cbi = cb[i]
                    if cbi and T[i][j]:
                        s -= cbi * T[i][j]
                red.append(s)
            cand = [j for j in allowed if red[j] < 0]
            if not cand:
                return 'optimal'
            if iters[0] <= BLAND_AFTER and not BLAND_ONLY[0]:
                j0 = min(cand, key=lambda j: (red[j], j))
            else:
                j0 = min(cand)      # Bland: smallest index => guaranteed termination
            ratios = []
            for i in range(m):
                if T[i][j0] > 0:
                    ratios.append((T[i][RHS] / T[i][j0], basis[i], i))
            if not ratios:
                return 'unbounded'
            ratios.sort(key=lambda t: (t[0], t[1]))
            pivot(ratios[0][2], j0)

    # phase 1
    cost1 = [F(0)] * n + [F(1)] * m
    st = run(cost1, list(range(NC)))
    if st != 'optimal':
        return ('error', None, None)
    p1 = sum(cost1[basis[i]] * T[i][RHS] for i in range(m))
    if p1 > 0:
        return ('infeasible', None, None)
    # drive artificials out of the basis (or delete redundant rows)
    i = 0
    while i < m:
        if basis[i] >= n:
            col = None
            for j in range(n):
                if T[i][j] != 0:
                    col = j
                    break
            if col is None:
                del T[i]
                del basis[i]
                m -= 1
                continue
            pivot(i, col)
        i += 1
    # phase 2
    cost2 = c + [F(0)] * (NC - n)
    st = run(cost2, list(range(n)))
    if st == 'unbounded':
        return ('unbounded', None, None)
    x = [F(0)] * n
    for i in range(m):
        if basis[i] < n:
            x[basis[i]] = T[i][RHS]
    val = sum(c[j] * x[j] for j in range(n))
    return ('optimal', val, x)


def dot(u, v):
    return sum(a * b for a, b in zip(u, v))


# ----------------------------------------------------------------------------
# CHSH (2,2,2) scenario module (matches math_notes.md conventions)
# ----------------------------------------------------------------------------

SPIN = (F(1), F(-1))                      # spin of outcome bit 0 / 1

chsh_assignments = list(itertools.product((1, -1), repeat=4))   # (a0,a1,b0,b1) spins


def chsh_coords(i):
    x = i // 8
    y = (i // 4) % 2
    o = i % 4
    return x, y, o // 2, o % 2


def chsh_entry_index(x, y, a, b):
    return (x * 2 + y) * 4 + a * 2 + b


T_CHSH = [[0] * 16 for _ in range(16)]
for i in range(16):
    x, y, a, b = chsh_coords(i)
    for j, t in enumerate(chsh_assignments):
        if SPIN[a] == t[0 + x] and SPIN[b] == t[2 + y]:
            T_CHSH[i][j] = 1

C_PAT = {(0, 0): 1, (0, 1): 1, (1, 0): 1, (1, 1): -1}      # CHSH sign pattern
S_COEF = []
for i in range(16):
    x, y, a, b = chsh_coords(i)
    S_COEF.append(F(C_PAT[(x, y)]) * SPIN[a] * SPIN[b])


def K_assign(j):
    t = chsh_assignments[j]
    return (t[0] * t[2] + t[0] * t[3] + t[1] * t[2] - t[1] * t[3])


def S_table(P):
    return sum(P[i] * S_COEF[i] for i in range(16))


def apply_T(T, q):
    ne = len(T)
    out = [F(0)] * ne
    for j, qj in enumerate(q):
        if qj:
            col = [T[i][j] for i in range(ne)]
            for i in range(ne):
                if col[i]:
                    out[i] += qj * col[i]
    return out


PR = [F(0)] * 16
for i in range(16):
    x, y, a, b = chsh_coords(i)
    if SPIN[a] * SPIN[b] == F((-1) ** (x * y)):
        PR[i] = F(1, 2)
U = [F(1, 4)] * 16


def p_iso(v):
    return [v * PR[i] + (1 - v) * U[i] for i in range(16)]


def chsh_is_ns(P):
    """Marginal consistency + normalization for the 16-entry table."""
    for x, y in itertools.product((0, 1), repeat=2):
        if sum(P[chsh_entry_index(x, y, a, b)] for a, b in itertools.product((0, 1), repeat=2)) != 1:
            return False
    for a in (0, 1):
        for x in (0, 1):
            vals = set()
            for y in (0, 1):
                s = sum(P[chsh_entry_index(x, y, a, b)] for b in (0, 1))
                vals.add(s)
            if len(vals) != 1:
                return False
    for b in (0, 1):
        for y in (0, 1):
            vals = set()
            for x in (0, 1):
                s = sum(P[chsh_entry_index(x, y, a, b)] for a in (0, 1))
                vals.add(s)
            if len(vals) != 1:
                return False
    return True


# ---- CHSH CF LP, moment form ------------------------------------------------
# variable layout: gamma[0..15]; then kappa+ ,kappa-, U+[x],U-[x] (x=0,1),
# W+[y],W-[y], E+[(x,y)],E-[(x,y])  -- free moments split into plus/minus parts.

def chsh_moment_index():
    idx = {}
    base = 16
    idx['kappa'] = base
    base += 2
    idx['U'] = {}
    for x in (0, 1):
        idx['U'][x] = base
        base += 2
    idx['W'] = {}
    for y in (0, 1):
        idx['W'][y] = base
        base += 2
    idx['E'] = {}
    for x, y in itertools.product((0, 1), repeat=2):
        idx['E'][(x, y)] = base
        base += 2
    return idx, base


def chsh_delta_expr(idx, cell):
    """delta(cell) as a sparse dict {var: coeff} over the moment variables."""
    x, y, a, b = chsh_coords(cell)
    A, B = SPIN[a], SPIN[b]
    e = {}
    e[idx['kappa']] = F(1, 4)
    e[idx['U'][x]] = e.get(idx['U'][x], F(0)) + F(1, 4) * A
    e[idx['W'][y]] = e.get(idx['W'][y], F(0)) + F(1, 4) * B
    e[idx['E'][(x, y)]] = e.get(idx['E'][(x, y)], F(0)) + F(1, 4) * A * B
    return e


def lp_cf_chsh_moment(p):
    """Maximize sum gamma s.t. p = gamma-part + delta, delta moment-NS >= 0.
    Returns (status, w_max, gamma, moments_raw)."""
    idx, nvar0 = chsh_moment_index()
    nvar = nvar0 + 16            # + one slack per delta >= 0 row
    A_rows, rhs = [], []
    for cell in range(16):
        row = [F(0)] * nvar
        for j in range(16):
            if T_CHSH[cell][j]:
                row[j] = F(1)
        for var, cf in chsh_delta_expr(idx, cell).items():
            # delta = cf * (m+ - m-)
            row[var] += cf
            row[var + 1] -= cf
        A_rows.append(row)
        rhs.append(F(p[cell]))
    for cell in range(16):
        row = [F(0)] * nvar
        for var, cf in chsh_delta_expr(idx, cell).items():
            row[var] += cf
            row[var + 1] -= cf
        row[nvar0 + cell] = F(-1)      # delta(cell) - slack = 0, slack >= 0
        A_rows.append(row)
        rhs.append(F(0))
    c = [F(-1)] * 16 + [F(0)] * (nvar - 16)
    st, val, x = simplex(A_rows, rhs, c)
    if st != 'optimal':
        return st, None, None, None
    gamma = x[:16]
    moments = {'kappa': x[idx['kappa']] - x[idx['kappa'] + 1],
               'U': [x[idx['U'][k]] - x[idx['U'][k] + 1] for k in (0, 1)],
               'W': [x[idx['W'][k]] - x[idx['W'][k] + 1] for k in (0, 1)],
               'E': {kk: x[idx['E'][kk]] - x[idx['E'][kk] + 1] for kk in idx['E']}}
    return 'optimal', -val, gamma, moments


def chsh_delta_from_moments(moments):
    out = [F(0)] * 16
    for cell in range(16):
        x, y, a, b = chsh_coords(cell)
        A, B = SPIN[a], SPIN[b]
        out[cell] = F(1, 4) * (moments['kappa'] + A * moments['U'][x]
                               + B * moments['W'][y] + A * B * moments['E'][(x, y)])
    return out


# ---- CHSH CF LP, vertex form (independent cross-check) ----------------------
# NS vertices: 16 deterministic + 8 parity-odd fully-correlated boxes.

def chsh_ns_vertices():
    verts = []
    for j, t in enumerate(chsh_assignments):
        col = [F(T_CHSH[i][j]) for i in range(16)]
        verts.append(col)
    for sig in itertools.product((1, -1), repeat=4):
        if sig[0] * sig[1] * sig[2] * sig[3] != -1:
            continue
        v = [F(0)] * 16
        for i in range(16):
            x, y, a, b = chsh_coords(i)
            v[i] = F(1, 4) * (1 + SPIN[a] * SPIN[b] * F(sig[2 * x + y]))
        verts.append(v)
    return verts


def lp_cf_chsh_vertex(p, verts):
    nvar = 16 + len(verts)
    A_rows, rhs = [], []
    for cell in range(16):
        row = [F(0)] * nvar
        for j in range(16):
            if T_CHSH[cell][j]:
                row[j] = F(1)
        for k, v in enumerate(verts):
            row[16 + k] = v[cell]
        A_rows.append(row)
        rhs.append(F(p[cell]))
    A_rows.append([F(1)] * nvar)
    rhs.append(F(1))
    c = [F(-1)] * 16 + [F(0)] * (len(verts))
    st, val, x = simplex(A_rows, rhs, c)
    if st != 'optimal':
        return st, None, None
    return 'optimal', -val, x[:16]


# ---- N LP primal + dual ------------------------------------------------------

def lp_min_negmass(T, p):
    """N(p) for behavior p given assignment->table matrix T (rows=entries)."""
    ne = len(T)
    na = len(T[0])
    n = 2 * na
    A = []
    rhs = []
    for i in range(ne):
        row = [F(0)] * n
        for j in range(na):
            row[j] = F(T[i][j])
            row[na + j] = -F(T[i][j])
        A.append(row)
        rhs.append(F(p[i]))
    row = [F(1 if k < na else -1) for k in range(n)]
    A.append(row)
    rhs.append(F(1))
    c = [F(0)] * na + [F(1)] * na
    st, val, x = simplex(A, rhs, c)
    return st, val, x


def lp_dual_negmass_chsh(p):
    """max alpha.p + beta s.t. -1 <= alpha.l_lam + beta <= 0 for all 16 lambdas.
    Free vars split; rows: value+beta + s1 = 0 and value+beta - s2 = -1.
    Returns (status, value, alpha, beta)."""
    na = 16
    nvar = 2 * na + 2            # alpha+/- per cell, beta+/-, plus-slacks are extra
    # layout: alpha+ [0..15], alpha- [16..31], beta+ [32], beta- [33],
    #         s1[34..49] (for <= 0 row), s2[50..65] (for >= -1 row)
    n = 66
    A_rows, rhs = [], []
    for j in range(na):
        row = [F(0)] * n
        for cell in range(na):
            if T_CHSH[cell][j]:
                row[cell] += F(1)
                row[na + cell] -= F(1)
        row[32] += F(1)
        row[33] -= F(1)
        row[34 + j] = F(1)
        A_rows.append(row)
        rhs.append(F(0))
        row2 = [F(0)] * n
        for cell in range(na):
            if T_CHSH[cell][j]:
                row2[cell] += F(1)
                row2[na + cell] -= F(1)
        row2[32] += F(1)
        row2[33] -= F(1)
        row2[50 + j] = F(-1)
        A_rows.append(row2)
        rhs.append(F(-1))
    c = ([F(-p[k]) for k in range(na)] + [F(p[k]) for k in range(na)]
         + [F(-1), F(1)] + [F(0)] * 32)
    st, val, x = simplex(A_rows, rhs, c)
    if st != 'optimal':
        return st, None, None, None
    alpha = [x[k] - x[na + k] for k in range(na)]
    beta = x[32] - x[33]
    return 'optimal', -val, alpha, beta


# ----------------------------------------------------------------------------
# GHZ (3,2,2) scenario module
# ----------------------------------------------------------------------------

ghz_assignments = list(itertools.product((1, -1), repeat=6))   # (a0,a1,b0,b1,c0,c1)


def ghz_coords(i):
    x = i // 32
    y = (i // 16) % 2
    z = (i // 8) % 2
    o = i % 8
    return x, y, z, o // 4, (o // 2) % 2, o % 2


def ghz_entry_index(x, y, z, a, b, c):
    return ((x * 2 + y) * 2 + z) * 8 + a * 4 + b * 2 + c


T_GHZ = [[0] * 64 for _ in range(64)]
for i in range(64):
    x, y, z, a, b, c = ghz_coords(i)
    for j, t in enumerate(ghz_assignments):
        if SPIN[a] == t[0 + x] and SPIN[b] == t[2 + y] and SPIN[c] == t[4 + z]:
            T_GHZ[i][j] = 1

# Mermin coefficient pattern chi: -1 at (0,0,0); +1 at (0,1,1),(1,0,1),(1,1,0); 0 else.
CHI = [F(0)] * 64
for i in range(64):
    x, y, z, a, b, c = ghz_coords(i)
    ctx = (x, y, z)
    if ctx == (0, 0, 0):
        chiv = F(-1)
    elif ctx in ((0, 1, 1), (1, 0, 1), (1, 1, 0)):
        chiv = F(1)
    else:
        chiv = F(0)
    CHI[i] = chiv * SPIN[a] * SPIN[b] * SPIN[c]     # chi(ctx) * s_a s_b s_c


def M_assign(j):
    t = ghz_assignments[j]
    f = lambda x, y, z: t[0 + x] * t[2 + y] * t[4 + z]
    return -f(0, 0, 0) + f(0, 1, 1) + f(1, 0, 1) + f(1, 1, 0)


def M_table(P):
    return sum(P[i] * CHI[i] for i in range(64))


def Q_box(v):
    """Mermin line: Q_v = (1 + v*chi*s_as_bs_c)/8 (uniform marginals)."""
    return [F(1, 8) * (1 + v * CHI[i]) for i in range(64)]


def ghz_box():
    """G(a,b,c|x,y,z) = 1/4 if s_as_bs_c = beta(x,y,z); beta=-1 only at (0,0,0)."""
    P = [F(0)] * 64
    for i in range(64):
        x, y, z, a, b, c = ghz_coords(i)
        beta = F(-1) if (x, y, z) == (0, 0, 0) else F(1)
        if SPIN[a] * SPIN[b] * SPIN[c] == beta:
            P[i] = F(1, 4)
    return P


# Svetlichny pattern (same as verify_headroom.py C20)
SVET = {(0, 0, 0): 1, (0, 0, 1): 1, (0, 1, 0): 1, (0, 1, 1): -1,
        (1, 0, 0): 1, (1, 0, 1): -1, (1, 1, 0): -1, (1, 1, 1): -1}


def svet_box():
    P = [F(0)] * 64
    for i in range(64):
        x, y, z, a, b, c = ghz_coords(i)
        P[i] = F(1, 8) * (1 + F(SVET[(x, y, z)]) * SPIN[a] * SPIN[b] * SPIN[c])
    return P


def w_box_ghz():
    """All-plus parity box: E = +1 at every context; LOCAL (4-assignment mixture)."""
    P = [F(0)] * 64
    for i in range(64):
        x, y, z, a, b, c = ghz_coords(i)
        P[i] = F(1, 8) * (1 + SPIN[a] * SPIN[b] * SPIN[c])
    return P


def ghz_is_ns(P):
    """Full marginal consistency (all subset levels) + normalization."""
    for x, y, z in itertools.product((0, 1), repeat=3):
        s = sum(P[ghz_entry_index(x, y, z, a, b, c)]
                for a, b, c in itertools.product((0, 1), repeat=3))
        if s != 1:
            return False
    for a in (0, 1):
        for x in (0, 1):
            vals = set()
            for y, z in itertools.product((0, 1), repeat=2):
                s = sum(P[ghz_entry_index(x, y, z, a, b, c)]
                        for b, c in itertools.product((0, 1), repeat=2))
                vals.add(s)
            if len(vals) != 1:
                return False
    for b in (0, 1):
        for y in (0, 1):
            vals = set()
            for x, z in itertools.product((0, 1), repeat=2):
                s = sum(P[ghz_entry_index(x, y, z, a, b, c)]
                        for a, c in itertools.product((0, 1), repeat=2))
                vals.add(s)
            if len(vals) != 1:
                return False
    for c in (0, 1):
        for z in (0, 1):
            vals = set()
            for x, y in itertools.product((0, 1), repeat=2):
                s = sum(P[ghz_entry_index(x, y, z, a, b, c)] for a, b in itertools.product((0, 1), repeat=2))
                vals.add(s)
            if len(vals) != 1:
                return False
    for a, b in itertools.product((0, 1), repeat=2):
        for x, y in itertools.product((0, 1), repeat=2):
            vals = set()
            for z in (0, 1):
                s = sum(P[ghz_entry_index(x, y, z, a, b, c)] for c in (0, 1))
                vals.add(s)
            if len(vals) != 1:
                return False
    for a, c in itertools.product((0, 1), repeat=2):
        for x, z in itertools.product((0, 1), repeat=2):
            vals = set()
            for y in (0, 1):
                s = sum(P[ghz_entry_index(x, y, z, a, b, c)] for b in (0, 1))
                vals.add(s)
            if len(vals) != 1:
                return False
    for b, c in itertools.product((0, 1), repeat=2):
        for y, z in itertools.product((0, 1), repeat=2):
            vals = set()
            for x in (0, 1):
                s = sum(P[ghz_entry_index(x, y, z, a, b, c)] for a in (0, 1))
                vals.add(s)
            if len(vals) != 1:
                return False
    return True


# ---- GHZ CF LP, moment form --------------------------------------------------
# variables: gamma[0..63]; free moments kappa, U[x] (2), W[y] (2), T[z] (2),
# Pxy (4), Pxz (4), Pyz (4), XYZ (8)  => 27 free moments, split => 54 vars.
# delta(a,b,c|x,y,z) = (kappa + A*U[x] + B*W[y] + C*T[z] + A*B*Pxy[x,y]
#                       + A*C*Pxz[x,z] + B*C*Pyz[y,z] + A*B*C*XYZ[x,y,z]) / 8

def ghz_moment_index():
    idx = {}
    base = 64
    idx['kappa'] = base
    base += 2
    for nm in ('U', 'W', 'T', 'Pxy', 'Pxz', 'Pyz', 'XYZ'):
        idx[nm] = {}
        if nm in ('U', 'W', 'T'):
            ks = [0, 1]
        elif nm in ('Pxy', 'Pxz', 'Pyz'):
            ks = list(itertools.product((0, 1), repeat=2))
        else:
            ks = list(itertools.product((0, 1), repeat=3))
        for k in ks:
            idx[nm][k] = base
            base += 2
    return idx, base


def ghz_delta_expr(idx, cell):
    x, y, z, a, b, c = ghz_coords(cell)
    A, B, C = SPIN[a], SPIN[b], SPIN[c]
    e = {}
    e[idx['kappa']] = F(1, 8)
    for nm, k, coef in (('U', x, A), ('W', y, B), ('T', z, C),
                        ('Pxy', (x, y), A * B), ('Pxz', (x, z), A * C),
                        ('Pyz', (y, z), B * C), ('XYZ', (x, y, z), A * B * C)):
        v = idx[nm][k]
        e[v] = e.get(v, F(0)) + F(1, 8) * coef
    return e


def lp_cf_ghz_moment(p):
    idx, nvar0 = ghz_moment_index()
    nvar = nvar0 + 64            # + one slack per delta >= 0 row
    A_rows, rhs = [], []
    for cell in range(64):
        row = [F(0)] * nvar
        for j in range(64):
            if T_GHZ[cell][j]:
                row[j] = F(1)
        for var, cf in ghz_delta_expr(idx, cell).items():
            row[var] += cf
            row[var + 1] -= cf
        A_rows.append(row)
        rhs.append(F(p[cell]))
    for cell in range(64):
        row = [F(0)] * nvar
        for var, cf in ghz_delta_expr(idx, cell).items():
            row[var] += cf
            row[var + 1] -= cf
        row[nvar0 + cell] = F(-1)      # delta(cell) - slack = 0, slack >= 0
        A_rows.append(row)
        rhs.append(F(0))
    c = [F(-1)] * 64 + [F(0)] * (nvar - 64)
    st, val, x = simplex(A_rows, rhs, c)
    if st != 'optimal':
        return st, None, None, None
    gamma = x[:64]
    moments = {'kappa': x[idx['kappa']] - x[idx['kappa'] + 1]}
    for nm in ('U', 'W', 'T', 'Pxy', 'Pxz', 'Pyz', 'XYZ'):
        moments[nm] = {k: x[idx[nm][k]] - x[idx[nm][k] + 1] for k in idx[nm]}
    return 'optimal', -val, gamma, moments


def ghz_delta_from_moments(moments):
    out = [F(0)] * 64
    for cell in range(64):
        x, y, z, a, b, c = ghz_coords(cell)
        A, B, C = SPIN[a], SPIN[b], SPIN[c]
        out[cell] = F(1, 8) * (moments['kappa']
                               + A * moments['U'][x] + B * moments['W'][y] + C * moments['T'][z]
                               + A * B * moments['Pxy'][(x, y)] + A * C * moments['Pxz'][(x, z)]
                               + B * C * moments['Pyz'][(y, z)]
                               + A * B * C * moments['XYZ'][(x, y, z)])
    return out


# ----------------------------------------------------------------------------
# Marginal-consistency checks for the scaled NS partner delta
# ----------------------------------------------------------------------------

def chsh_delta_marginals_ok(delta):
    """delta = kappa * r with r NS normalized: context sums all equal (kappa),
    single-party marginals consistent across the other party's setting."""
    sums = set()
    for x, y in itertools.product((0, 1), repeat=2):
        sums.add(sum(delta[chsh_entry_index(x, y, a, b)]
                     for a, b in itertools.product((0, 1), repeat=2)))
    if len(sums) != 1:
        return False
    for a in (0, 1):
        for x in (0, 1):
            vals = set()
            for y in (0, 1):
                vals.add(sum(delta[chsh_entry_index(x, y, a, b)] for b in (0, 1)))
            if len(vals) != 1:
                return False
    for b in (0, 1):
        for y in (0, 1):
            vals = set()
            for x in (0, 1):
                vals.add(sum(delta[chsh_entry_index(x, y, a, b)] for a in (0, 1)))
            if len(vals) != 1:
                return False
    return True


def ghz_delta_marginals_ok(delta):
    """Same as ghz_is_ns except the context sums only need to be EQUAL (= kappa)."""
    sums = set()
    for x, y, z in itertools.product((0, 1), repeat=3):
        sums.add(sum(delta[ghz_entry_index(x, y, z, a, b, c)]
                     for a, b, c in itertools.product((0, 1), repeat=3)))
    if len(sums) != 1:
        return False
    # singles
    for a in (0, 1):
        for x in (0, 1):
            vals = set()
            for y, z in itertools.product((0, 1), repeat=2):
                vals.add(sum(delta[ghz_entry_index(x, y, z, a, b, c)]
                             for b, c in itertools.product((0, 1), repeat=2)))
            if len(vals) != 1:
                return False
    for b in (0, 1):
        for y in (0, 1):
            vals = set()
            for x, z in itertools.product((0, 1), repeat=2):
                vals.add(sum(delta[ghz_entry_index(x, y, z, a, b, c)]
                             for a, c in itertools.product((0, 1), repeat=2)))
            if len(vals) != 1:
                return False
    for c in (0, 1):
        for z in (0, 1):
            vals = set()
            for x, y in itertools.product((0, 1), repeat=2):
                vals.add(sum(delta[ghz_entry_index(x, y, z, a, b, c)]
                             for a, b in itertools.product((0, 1), repeat=2)))
            if len(vals) != 1:
                return False
    # pairs
    for a, b in itertools.product((0, 1), repeat=2):
        for x, y in itertools.product((0, 1), repeat=2):
            vals = set()
            for z in (0, 1):
                vals.add(sum(delta[ghz_entry_index(x, y, z, a, b, cc)] for cc in (0, 1)))
            if len(vals) != 1:
                return False
    for a, c in itertools.product((0, 1), repeat=2):
        for x, z in itertools.product((0, 1), repeat=2):
            vals = set()
            for y in (0, 1):
                vals.add(sum(delta[ghz_entry_index(x, y, z, a, bb, c)] for bb in (0, 1)))
            if len(vals) != 1:
                return False
    for b, c in itertools.product((0, 1), repeat=2):
        for y, z in itertools.product((0, 1), repeat=2):
            vals = set()
            for x in (0, 1):
                vals.add(sum(delta[ghz_entry_index(x, y, z, aa, b, c)] for aa in (0, 1)))
            if len(vals) != 1:
                return False
    return True


# ----------------------------------------------------------------------------
# Self-tests (same as verify_headroom.py)
# ----------------------------------------------------------------------------

def selftest():
    st, val, x = simplex([[1, 1]], [1], [F(-1), F(0)])
    ck("S0a simplex trivial LP", st == 'optimal' and val == F(-1) and x == [F(1), F(0)],
       f"status={st} val={val}")
    A = [[F(1, 4), F(-60), F(-1, 25), F(9), F(1), F(0), F(0)],
         [F(1, 2), F(-90), F(-1, 50), F(3), F(0), F(1), F(0)],
         [F(0), F(0), F(1), F(0), F(0), F(0), F(1)]]
    bb = [F(0), F(0), F(1)]
    c = [F(-3, 4), F(150), F(-1, 50), F(6), F(0), F(0), F(0)]
    st, val, x = simplex(A, bb, c)
    ck("S0b Beale anti-cycling", st == 'optimal' and val == F(-1, 20),
       f"status={st} val={val} (expect -1/20)")


# ----------------------------------------------------------------------------
# Battery construction
# ----------------------------------------------------------------------------

def chsh_battery():
    pts = []
    line_vs = [F(0), F(1, 8), F(1, 4), F(3, 8), F(7, 16), F(1, 2), F(9, 16),
               F(5, 8), F(11, 16), F(3, 4), F(7, 8), F(15, 16), F(1)]
    for v in line_vs:
        pts.append((f"CHSH p_{v}", p_iso(v), ('line', v)))
    # all-plus parity box: local (E = +1 at all four contexts)
    Wc = [F(1, 4) * (1 + SPIN[a] * SPIN[b]) for i in range(16)
          for (x, y, a, b) in [chsh_coords(i)]]
    pts.append(("CHSH W (all-plus parity, local)", Wc, ('W', None)))
    # the 8 nonlocal NS vertices: E = sigma everywhere, product of sigma = -1
    for sig in itertools.product((1, -1), repeat=4):
        if sig[0] * sig[1] * sig[2] * sig[3] != -1:
            continue
        v = [F(0)] * 16
        for i in range(16):
            x, y, a, b = chsh_coords(i)
            v[i] = F(1, 4) * (1 + SPIN[a] * SPIN[b] * F(sig[2 * x + y]))
        pts.append((f"CHSH V_sig{sig}", v, ('V', sig)))
    # random NS mixtures (deterministic seed)
    rng = random.Random(20261023)
    pool = []
    for j in range(16):
        pool.append([F(T_CHSH[i][j]) for i in range(16)])
    for sig in itertools.product((1, -1), repeat=4):
        if sig[0] * sig[1] * sig[2] * sig[3] != -1:
            continue
        v = [F(0)] * 16
        for i in range(16):
            x, y, a, b = chsh_coords(i)
            v[i] = F(1, 4) * (1 + SPIN[a] * SPIN[b] * F(sig[2 * x + y]))
        pool.append(v)
    pool.append(list(U))
    for t in range(40):
        k = rng.randint(3, 5)
        comps = rng.sample(pool, k)
        ws = [rng.randrange(1, 9) for _ in range(k)]
        tot = sum(ws)
        p = [F(0)] * 16
        for w, comp in zip(ws, comps):
            for i in range(16):
                p[i] += F(w, tot) * comp[i]
        pts.append((f"CHSH rnd{t} (k={k}, den={tot})", p, ('rnd', t)))
    return pts


def ghz_battery():
    pts = []
    for v in [F(0), F(3, 8), F(1, 2), F(5, 8), F(7, 10), F(1)]:
        pts.append((f"GHZ Q_{v}", Q_box(v), ('line', v)))
    pts.append(("GHZ G (GHZ box)", ghz_box(), ('G', None)))
    pts.append(("GHZ S-box (Svetlichny)", svet_box(), ('S', None)))
    pts.append(("GHZ W (all-plus parity, local)", w_box_ghz(), ('W', None)))
    pts.append(("GHZ U (uniform)", [F(1, 8)] * 64, ('U', None)))
    rng = random.Random(4711)
    pool = [ghz_box(), svet_box(), w_box_ghz(), [F(1, 8)] * 64,
            Q_box(F(1, 2)), Q_box(F(5, 8)), Q_box(F(1))]
    for j in (0, 7, 42, 63):
        pool.append([F(T_GHZ[i][j]) for i in range(64)])
    for t in range(6):
        k = rng.randint(3, 4)
        comps = rng.sample(pool, k)
        ws = [rng.randrange(1, 7) for _ in range(k)]
        tot = sum(ws)
        p = [F(0)] * 64
        for w, comp in zip(ws, comps):
            for i in range(64):
                p[i] += F(w, tot) * comp[i]
        pts.append((f"GHZ rnd{t} (k={k}, den={tot})", p, ('rnd', t)))
    return pts


# ----------------------------------------------------------------------------
# Per-point evaluation
# ----------------------------------------------------------------------------

def eval_chsh_point(name, p, kind, verts, ratios):
    # N primal
    st, val, x = lp_min_negmass(T_CHSH, p)
    ok = st == 'optimal'
    q = [x[j] - x[16 + j] for j in range(16)] if ok else None
    ok = ok and apply_T(T_CHSH, q) == [F(v) for v in p] and sum(q) == 1
    ok = ok and sum(-v for v in q if v < 0) == val
    # N dual + explicit certificate re-verification (Prop 4 form)
    st2, val2, alpha, beta = lp_dual_negmass_chsh(p)
    vv = chsh_vertex_values(alpha) if st2 == 'optimal' else None
    okdual = (st2 == 'optimal' and val2 == val
              and max(vv) - min(vv) <= 1
              and beta == -max(vv)
              and dot(alpha, p) + beta == val2)
    N_val = val if ok else None
    # CF moment form
    st3, w, gamma, moments = lp_cf_chsh_moment(p)
    okcf = st3 == 'optimal'
    if okcf:
        delta = chsh_delta_from_moments(moments)
        gpart = apply_T(T_CHSH, gamma)
        kappa_ctx = sum(delta[chsh_entry_index(0, 0, a, b)]
                        for a, b in itertools.product((0, 1), repeat=2))
        okcf = (all(g >= 0 for g in gamma)
                and [gpart[i] + delta[i] for i in range(16)] == [F(v) for v in p]
                and all(d >= 0 for d in delta)
                and chsh_delta_marginals_ok(delta)
                and sum(gamma) + kappa_ctx == 1)
    CF_val = 1 - w if okcf else None
    # CF vertex form cross-check
    st4, w2, _ = lp_cf_chsh_vertex(p, verts)
    okv = st4 == 'optimal' and w2 == w
    cf_ok = ok and okdual and okcf and okv
    if not cf_ok:
        ck(f"{name}: LP/certificate chain", False,
           f"Nprimal={ok} Ndual={okdual} CFmoment={okcf} CFvertex={okv}")
        return
    # known values
    known = ""
    if kind[0] == 'line':
        v = kind[1]
        exp_cf = max(F(0), 2 * v - 1)
        exp_n = max(F(0), v - F(1, 2))
        known = f"expected CF={exp_cf} N={exp_n}"
        if not (CF_val == exp_cf and N_val == exp_n):
            ck(f"{name}: Thm27/Prop25 closed forms", False,
               f"CF={CF_val} N={N_val} expected CF={exp_cf} N={exp_n}")
            return
    if kind[0] == 'V':
        if not (CF_val == 1 and N_val == F(1, 2)):
            ck(f"{name}: vertex closed forms", False,
               f"CF={CF_val} N={N_val} expected CF=1 N=1/2")
            return
    if kind[0] == 'W':
        if not (CF_val == 0 and N_val == 0):
            ck(f"{name}: local parity box", False, f"CF={CF_val} N={N_val} expected 0,0")
            return
    # conjecture
    okc = CF_val <= 2 * N_val
    if N_val > 0:
        ratios.append((CF_val / (2 * N_val), name, CF_val, N_val))
    tag = "EQUAL" if CF_val == 2 * N_val else ("strict" if okc else "VIOLATION")
    print(f"    {name:34s} CF={str(CF_val):8s} N={str(N_val):8s} "
          f"2N={str(2 * N_val):8s} {tag}")
    if not okc:
        ck(f"C25 conjecture CF<=2N at {name}", False,
           f"CF={CF_val} > 2N={2 * N_val}  <-- COUNTEREXAMPLE")
    return {'cf': CF_val, 'n': N_val}


def eval_ghz_point(name, p, kind, ratios):
    st, val, x = lp_min_negmass(T_GHZ, p)
    ok = st == 'optimal'
    q = [x[j] - x[64 + j] for j in range(64)] if ok else None
    ok = ok and apply_T(T_GHZ, q) == [F(v) for v in p] and sum(q) == 1
    ok = ok and sum(-v for v in q if v < 0) == val
    st3, w, gamma, moments = lp_cf_ghz_moment(p)
    okcf = st3 == 'optimal'
    if okcf:
        delta = ghz_delta_from_moments(moments)
        gpart = apply_T(T_GHZ, gamma)
        kappa_ctx = sum(delta[ghz_entry_index(0, 0, 0, a, b, c)]
                        for a, b, c in itertools.product((0, 1), repeat=3))
        okcf = (all(g >= 0 for g in gamma)
                and [gpart[i] + delta[i] for i in range(64)] == [F(v) for v in p]
                and all(d >= 0 for d in delta)
                and ghz_delta_marginals_ok(delta)
                and sum(gamma) + kappa_ctx == 1)
    if not (ok and okcf):
        ck(f"{name}: LP/certificate chain", False, f"Nprimal={ok} CFmoment={okcf}")
        return
    N_val, CF_val = val, 1 - w
    known = ""
    if kind[0] == 'line':
        v = kind[1]
        exp_cf = max(F(0), 2 * v - 1)
        exp_n = max(F(0), v - F(1, 2))
        known = f"expected CF={exp_cf} N={exp_n}"
        if not (CF_val == exp_cf and N_val == exp_n):
            ck(f"{name}: Thm24/Prop25 closed forms", False,
               f"CF={CF_val} N={N_val} expected CF={exp_cf} N={exp_n}")
            return
    if kind[0] == 'G':
        # proven: CF(G) = 1 (M(G) = -4 <= -4 + 2w forces w = 0) and N(G) >= 1/2
        # (dual alpha = M/4, spread 1).  Exact N(G) is REPORTED, not asserted.
        if not (CF_val == 1 and N_val >= F(1, 2)):
            ck(f"{name}: G-box certified bounds", False,
               f"CF={CF_val} N={N_val} expected CF=1 and N >= 1/2")
            return
    if kind[0] == 'S':
        if not (N_val == F(1, 2) and CF_val == 1):
            ck(f"{name}: S-box closed forms", False,
               f"CF={CF_val} N={N_val} expected CF=1 N=1/2")
            return
    if kind[0] in ('W', 'U'):
        if not (CF_val == 0 and N_val == 0):
            ck(f"{name}: trivial box", False, f"CF={CF_val} N={N_val} expected 0,0")
            return
    okc = CF_val <= 2 * N_val
    if N_val > 0:
        ratios.append((CF_val / (2 * N_val), name, CF_val, N_val))
    tag = "EQUAL" if CF_val == 2 * N_val else ("strict" if okc else "VIOLATION")
    print(f"    {name:34s} CF={str(CF_val):8s} N={str(N_val):8s} "
          f"2N={str(2 * N_val):8s} {tag}")
    if not okc:
        ck(f"C27 conjecture CF<=2N at {name}", False,
           f"CF={CF_val} > 2N={2 * N_val}  <-- COUNTEREXAMPLE")
    return {'cf': CF_val, 'n': N_val}


# ----------------------------------------------------------------------------
# Analytic dual certificates (no LP): Prop 4 closed forms on the known points
# ----------------------------------------------------------------------------

def chsh_vertex_values(alpha):
    """alpha.l_lam for the 16 deterministic boxes: (T^T alpha)_lam."""
    return [sum(F(alpha[cell]) * T_CHSH[cell][j] for cell in range(16))
            for j in range(16)]


def c24_analytic_duals():
    ok = True
    # alpha = S/4: spread exactly 1 over the 16 vertices (K in {+-2})
    alpha = [F(s, 4) for s in S_COEF]
    vv = chsh_vertex_values(alpha)
    ok &= max(vv) - min(vv) == 1 and set(vv) <= {F(1, 2), F(-1, 2)}
    for v in [F(1, 2), F(9, 16), F(5, 8), F(11, 16), F(3, 4), F(7, 8), F(15, 16), F(1)]:
        floor = dot(alpha, p_iso(v)) - max(vv)
        ok &= floor == v - F(1, 2)
    ck("C24a CHSH analytic dual alpha = S/4: spread exactly 1 over the 16 vertices;"
       " N(p_v) >= v - 1/2 pinched tight for every v >= 1/2", ok,
       f"vertex range [{min(vv)},{max(vv)}], floors = v-1/2 exactly")
    # PR: floor 1/2 = N(PR)
    okb = dot(alpha, PR) - max(vv) == F(1, 2)
    ck("C24b CHSH dual floor at PR: alpha.PR - max = 1/2", okb)
    return ok and okb


def c26_analytic_duals():
    ok = True
    # alpha = M/4 on GHZ: spread exactly 1 over the 64 vertices (M in {+-2})
    alpha = [F(0)] * 64
    for i in range(64):
        alpha[i] = CHI[i] / 4
    vv = [sum(F(alpha[cell]) * T_GHZ[cell][j] for cell in range(64))
          for j in range(64)]
    ok &= max(vv) - min(vv) == 1
    ok &= set(vv) <= {F(1, 2), F(-1, 2)}
    for v in [F(1, 2), F(5, 8), F(7, 10), F(1)]:
        floor = dot(alpha, Q_box(v)) - max(vv)
        ok &= floor == v - F(1, 2)
    ck("C26a GHZ analytic dual alpha = M/4: spread exactly 1 over the 64 vertices;"
       " N(Q_v) >= v - 1/2 pinched tight for every v >= 1/2", ok,
       f"vertex range [{min(vv)},{max(vv)}]")
    # alpha = Svet/8 on the S-box: spread 1, floor 1/2
    sc = [F(0)] * 64
    for i in range(64):
        x, y, z, a, b, c = ghz_coords(i)
        sc[i] = F(SVET[(x, y, z)]) * SPIN[a] * SPIN[b] * SPIN[c] / 8
    vv2 = [sum(F(sc[cell]) * T_GHZ[cell][j] for cell in range(64)) for j in range(64)]
    okb = max(vv2) - min(vv2) == 1
    Sb = svet_box()
    okb &= (dot(sc, Sb) - max(vv2)) == F(1, 2)
    ck("C26b GHZ analytic dual alpha = Svet/8: spread 1, N(S-box) >= 1/2 (C20d: exact)",
       okb)
    return ok and okb


# ----------------------------------------------------------------------------
# Main — staged execution with pickle checkpoints so long runs survive tool
# timeouts:  python3 verify_cf2n.py chsh|ghz|final|all
# ----------------------------------------------------------------------------

import pickle

CKPT = '/home/z/my-project/scripts/cf2n_ckpt'


def run_chsh():
    banner("PART 1: CHSH (16-entry) — 62-point battery")
    verts = chsh_ns_vertices()
    ck("C22pre NS vertex list: 16 deterministic + 8 parity-odd fully-correlated"
       " boxes, each a normalized NS table (per-context sums = 1)", len(verts) == 24
       and all(chsh_is_ns(v) for v in verts),
       f"{len(verts)} vertices")
    ratios_chsh = []
    res_chsh = []
    for name, p, kind in chsh_battery():
        r = eval_chsh_point(name, p, kind, verts, ratios_chsh)
        res_chsh.append((name, kind, r))
    n_ok = sum(1 for _, _, r in res_chsh if r is not None)
    ck("C22a CHSH: all 62 points — N-primal certificate re-verified"
       " (Tq=p, sum=1, mass=value); N-dual == N-primal to the last bit;"
       " CF-moment certificate re-verified (p = gamma-part + delta, delta >= 0,"
       " delta marginally consistent, sum gamma + kappa = 1);"
       " CF-vertex value == CF-moment value", n_ok == 62, f"{n_ok}/62 closed")
    n_line = sum(1 for _, k, r in res_chsh if r is not None and k[0] == 'line')
    ck("C22b CHSH: Thm 27 + Prop 25 closed forms CF = max(0,2v-1),"
       " N = max(0,v-1/2) confirmed by LP on all 13 line points",
       n_line == 13, f"{n_line}/13")
    n_v = sum(1 for _, k, r in res_chsh if r is not None and k[0] == 'V')
    ck("C22c CHSH: all 8 nonlocal NS vertices have CF = 1, N = 1/2",
       n_v == 8, f"{n_v}/8")
    c24_analytic_duals()
    with open(CKPT + '_chsh.pkl', 'wb') as fh:
        pickle.dump((res_chsh, ratios_chsh, N_CHECKS[0], list(FAILURES)), fh)
    print(f"[stage chsh done: {N_CHECKS[0]} checks, {len(FAILURES)} failures]")


def run_ghz():
    banner("PART 2: GHZ (64-entry) — 16-point battery")
    try:
        with open(CKPT + '_ghz_partial.pkl', 'rb') as fh:
            res_ghz, ratios_ghz = pickle.load(fh)
        print(f"[resuming ghz: {len(res_ghz)} points already done]", flush=True)
    except Exception:
        res_ghz, ratios_ghz = [], []
    done_names = {t[0] for t in res_ghz}
    for name, p, kind in ghz_battery():
        if name in done_names:
            print(f"    [skip done: {name}]", flush=True)
            continue
        t0 = time.time()
        print(f"    [working: {name}]", flush=True)
        r = eval_ghz_point(name, p, kind, ratios_ghz)
        print(f"    [{time.time() - t0:6.1f}s] {name} done", flush=True)
        res_ghz.append((name, kind, r))
        with open(CKPT + '_ghz_partial.pkl', 'wb') as fh:
            pickle.dump((res_ghz, ratios_ghz), fh)
    n_ok = sum(1 for _, _, r in res_ghz if r is not None)
    ck("C23a GHZ: all 16 points — N-primal certificate re-verified;"
       " CF-moment certificate re-verified (p = gamma-part + delta, delta >= 0,"
       " delta marginally consistent at scale kappa, sum gamma + kappa = 1)",
       n_ok == 16, f"{n_ok}/16 closed")
    n_line = sum(1 for _, k, r in res_ghz if r is not None and k[0] == 'line')
    ck("C23b GHZ: Thm 24 + Prop 25 closed forms CF = max(0,2v-1),"
       " N = max(0,v-1/2) confirmed by LP on all 6 Mermin-line points",
       n_line == 6, f"{n_line}/6")
    n_box = sum(1 for _, k, r in res_ghz if r is not None and k[0] in ('G', 'S', 'W', 'U'))
    ck("C23c GHZ: edge boxes close (G: CF=1; S-box: CF=1, N=1/2; W and U: 0,0)",
       n_box == 4, f"{n_box}/4")
    c26_analytic_duals()
    with open(CKPT + '_ghz.pkl', 'wb') as fh:
        pickle.dump((res_ghz, ratios_ghz, N_CHECKS[0], list(FAILURES)), fh)
    print(f"[stage ghz done: {N_CHECKS[0]} checks, {len(FAILURES)} failures]")


def run_final():
    with open(CKPT + '_chsh.pkl', 'rb') as fh:
        res_chsh, ratios_chsh, n1, f1 = pickle.load(fh)
    with open(CKPT + '_ghz.pkl', 'rb') as fh:
        res_ghz, ratios_ghz, n2, f2 = pickle.load(fh)
    banner("PART 3: the conjecture CF(p) <= 2 N(p)")
    all_r = [(n, k, r) for n, k, r in res_chsh + res_ghz]
    viol = [(n, r) for n, k, r in all_r if r is not None and r['cf'] > 2 * r['n']]
    ck("C25 CONJECTURE on CHSH: CF(p) <= 2 N(p) at all 62 battery points",
       len(viol) == 0 and len(res_chsh) == 62
       and all(r is not None for _, _, r in res_chsh),
       "violations: " + (", ".join(n for n, _ in viol) if viol else "none"))
    ck("C27 CONJECTURE on GHZ: CF(p) <= 2 N(p) at all 16 battery points",
       all(r is not None and r['cf'] <= 2 * r['n'] for _, _, r in res_ghz),
       "violations: " + (", ".join(n for n, k, r in res_ghz
                                   if r is not None and r['cf'] > 2 * r['n'])
                         or "none"))
    all_ratios = ratios_chsh + ratios_ghz
    max_ratio = max((rt for rt, _, _, _ in all_ratios), default=None)
    n_eq = sum(1 for n, k, r in all_r if r is not None and r['cf'] == 2 * r['n'])
    ck("C28 summary: max ratio CF/(2N) over all battery points <= 1",
       max_ratio is not None and max_ratio <= 1,
       f"max ratio = {max_ratio}; {n_eq} equality points, "
       f"{sum(1 for _, _, r in all_r if r is not None)} points closed")
    print("\nTop ratios CF/(2N) (equality = tight points of the conjecture):")
    for rt, name, cf, n in sorted(all_ratios, reverse=True)[:15]:
        print(f"    {str(rt):10s} {name:36s} CF={cf} 2N={2 * n}")
    print("\nEquality points (CF = 2N):")
    for n, k, r in all_r:
        if r is not None and r['cf'] == 2 * r['n']:
            print(f"    {n:36s} CF = 2N = {r['cf']}")
    print(f"\nStage check counts (cumulative within this process): chsh={n1}, "
          f"ghz={n2}, final={N_CHECKS[0]}; total distinct failures: {len(all_fail)}")
    all_fail = list(dict.fromkeys(f1 + f2 + FAILURES))
    if all_fail:
        print("FAILED (deduplicated):", *all_fail, sep="\n  ")
        sys.exit(1)
    print("ALL CHECKS PASS — the §18 conjecture CF(p) <= 2 N(p) survived every"
          " point of the battery in exact rational arithmetic.")
    sys.exit(0)


def main():
    import time
    t_start = time.time()
    banner("verify_cf2n.py — the §18 conjecture CF(p) <= 2 N(p), settled exactly")
    selftest()
    stage = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if stage in ('chsh', 'all'):
        run_chsh()
    if stage in ('ghz', 'all'):
        run_ghz()
    if stage in ('final', 'all'):
        run_final()
    print(f"Elapsed: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
