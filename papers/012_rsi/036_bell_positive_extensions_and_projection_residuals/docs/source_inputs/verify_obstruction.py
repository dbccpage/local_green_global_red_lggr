#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_obstruction.py
=====================

Exact-arithmetic verification companion to the review notes
"Projection, Retraction, Obstruction: review and generalization of the
Bell-observer framework" (v0.1).

Every computation in this file is carried out over the exact rational
numbers (fractions.Fraction).  No floating point appears in any
computation; decimals are printed only for human readability.

Scenario: the CHSH (2,2,2) Bell scenario.
  X = Y = {0,1}, A = B = {-1,+1}  (internally: outcome indices 0,1 with
  values -1,+1).
  Omega = A^X x B^Y: the 16 deterministic response assignments
      lambda = (alpha, beta),  alpha: X -> A,  beta: Y -> B.
  T : R^16 -> R^16 is the marginalization matrix
      T[(x,y,a,b), lambda] = 1{ alpha(x)=a and beta(y)=b }.

Checks
------
  C0  simplex self-tests (including Beale's cycling example, which forces
      the anti-cycling rule to actually engage).
  C1  CHSH local bound: K(lambda) in {+2,-2} and S(vertex) in {+2,-2} for
      all 16 deterministic assignments; sanity of the T construction.
  C2  im(T) is contained in the no-signalling subspace V_NS.
  C3  Lemma L1 (NS-fiber): rank(T) = 9 = dim of the ambient no-signalling
      linear subspace V_NS (the NS functionals have ambient rank 7); the
      normalized affine slice is 8-dimensional; and T({sum q = 1}) equals
      exactly the normalized NS tables (constructive: the PR box admits an
      exact normalized signed preimage).
  C4  Positive extension: explicit q* >= 0 with sum q* = 1 and T q* = p_v
      for the isotropic boxes v = 3/8 (interior) and v = 1/2 (boundary).
  C5  Infeasibility just outside: v = 51/100 admits no positive preimage.
  C6  LP (29): R(v) = max(0, (2v-1)/4) exactly for
      v in {3/8, 5/8, 70/99, 1}   (sharpness of the 1/8 bound).
  C7  LP duality: exact dual optimum of (29) equals the primal optimum;
      the normalized CHSH witness B = s/8 attains it (|B_abxy| <= 1/8).
  C8  Negative-mass LP: primal optimum = dual optimum exactly;
      N(local box) = 0; N(5/8), N(1) reported exactly.
  C9  Signalling table: the negative-mass LP is infeasible (p not in V_NS).
  C10 Stability (Eq. 30 with the 8-epsilon bound): a rational perturbation
      of p_{5/8} with ||p~ - p||_pi = 1/400 still certifies R >= 1/16.
  C11 Observer module: minimax floor = half the fiber task-diameter with
      midpoint attainment, refinement monotonicity, report-preserving
      invariance, and the evidence-gain criterion.

Run:  python3 verify_obstruction.py      (exit code 0 iff all checks pass)
"""

from fractions import Fraction as Fr
import sys

INFEASIBLE, OPTIMAL, UNBOUNDED = "infeasible", "optimal", "unbounded"


# ----------------------------------------------------------------------
# Exact linear algebra
# ----------------------------------------------------------------------

def exact_rank(A):
    """Rank of a matrix over Q (list of rows)."""
    A = [[Fr(v) for v in row] for row in A]
    if not A:
        return 0
    nrows, ncols = len(A), len(A[0])
    rank, r = 0, 0
    for c in range(ncols):
        piv = next((i for i in range(r, nrows) if A[i][c] != 0), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        pr = A[r]
        for i in range(nrows):
            if i != r and A[i][c] != 0:
                f = A[i][c] / pr[c]
                A[i] = [a - f * b for a, b in zip(A[i], pr)]
        r += 1
        rank += 1
        if r == nrows:
            break
    return rank


def exact_solve(A, b):
    """One exact solution of A x = b over Q, or None if inconsistent.
    Free variables are set to zero."""
    nrows = len(A)
    ncols = len(A[0]) if nrows else 0
    M = [list(map(Fr, row)) + [Fr(v)] for row, v in zip(A, b)]
    r, piv_cols = 0, []
    for c in range(ncols):
        piv = next((i for i in range(r, nrows) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        inv = M[r][c]
        M[r] = [v / inv for v in M[r]]
        pr = M[r]
        for i in range(nrows):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * bb for a, bb in zip(M[i], pr)]
        piv_cols.append(c)
        r += 1
        if r == nrows:
            break
    for i in range(r, nrows):
        if M[i][ncols] != 0:
            return None          # all remaining coefficients are zero here
    x = [Fr(0)] * ncols
    for idx, c in enumerate(piv_cols):
        x[c] = M[idx][ncols]
    return x


def nullspace_basis(A, ncols):
    """Basis of {x in Q^ncols : A x = 0} as a list of column vectors."""
    M = [[Fr(v) for v in row] for row in A]
    nrows = len(M)
    r, piv_cols = 0, []
    for c in range(ncols):
        piv = next((i for i in range(r, nrows) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        inv = M[r][c]
        M[r] = [v / inv for v in M[r]]
        pr = M[r]
        for i in range(nrows):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], pr)]
        piv_cols.append(c)
        r += 1
        if r == nrows:
            break
    basis = []
    for fc in (c for c in range(ncols) if c not in piv_cols):
        v = [Fr(0)] * ncols
        v[fc] = Fr(1)
        for idx, pc in enumerate(piv_cols):
            v[pc] = -M[idx][fc]
        basis.append(v)
    return basis


# ----------------------------------------------------------------------
# Two-phase primal simplex over Q, Bland's rule (anti-cycling)
# ----------------------------------------------------------------------

class SimplexError(Exception):
    pass


def _pivot(mat, zrow, basis, ri, ci):
    p = mat[ri][ci]
    mat[ri] = [v / p for v in mat[ri]]
    pr = mat[ri]
    for r in range(len(mat)):
        if r != ri and mat[r][ci] != 0:
            f = mat[r][ci]
            mat[r] = [a - f * b for a, b in zip(mat[r], pr)]
    if zrow is not None and zrow[ci] != 0:
        f = zrow[ci]
        zrow[:] = [a - f * b for a, b in zip(zrow, pr)]
    basis[ri] = ci


def _entering(zrow, ncols):
    """Bland: smallest index with negative reduced cost."""
    for j in range(ncols):
        if zrow[j] < 0:
            return j
    return -1


def _leaving(mat, basis, ci):
    """Min ratio; ties broken by smallest basic variable index (Bland)."""
    best_i, best_r = None, None
    for i in range(len(mat)):
        d = mat[i][ci]
        if d > 0:
            ratio = mat[i][-1] / d
            if best_r is None or ratio < best_r or \
               (ratio == best_r and basis[i] < basis[best_i]):
                best_i, best_r = i, ratio
    return best_i


def simplex_solve(n, obj, le=(), eq=(), maximize=False):
    """
    min obj.x  s.t.  le: a.x <= b,  eq: a.x = b,  x >= 0   (all over Q).
    Returns (status, value, x).
    """
    c = [Fr(v) for v in obj]
    if maximize:
        c = [-v for v in c]

    rows = []
    for coeffs, b in le:
        coeffs, b = [Fr(v) for v in coeffs], Fr(b)
        if b < 0:
            rows.append(('ge', [-v for v in coeffs], -b))
        else:
            rows.append(('le', coeffs, b))
    for coeffs, b in eq:
        coeffs, b = [Fr(v) for v in coeffs], Fr(b)
        if b < 0:
            coeffs, b = [-v for v in coeffs], -b
        rows.append(('eq', coeffs, b))

    m = len(rows)
    ncols = n
    slack_col = [None] * m
    for i, (t, _, _) in enumerate(rows):
        if t in ('le', 'ge'):
            slack_col[i] = ncols
            ncols += 1
    art_col = [None] * m
    for i, (t, _, _) in enumerate(rows):
        if t in ('eq', 'ge'):
            art_col[i] = ncols
            ncols += 1

    mat = []
    for i, (t, coeffs, b) in enumerate(rows):
        row = [Fr(0)] * (ncols + 1)
        for j in range(n):
            row[j] = coeffs[j]
        row[ncols] = b
        if slack_col[i] is not None:
            row[slack_col[i]] = Fr(1) if t == 'le' else Fr(-1)
        if art_col[i] is not None:
            row[art_col[i]] = Fr(1)
        mat.append(row)

    art_set = set(j for j in art_col if j is not None)
    basis = [art_col[i] if art_col[i] is not None else slack_col[i]
             for i in range(m)]

    zrow = [Fr(0)] * (ncols + 1)

    # ---- Phase 1: minimize the sum of the artificial variables ----
    if art_set:
        for j in art_set:
            zrow[j] = Fr(1)
        for i in range(m):
            if basis[i] in art_set:
                zrow[:] = [a - b for a, b in zip(zrow, mat[i])]
        while True:
            j = _entering(zrow, ncols)
            if j < 0:
                break
            ri = _leaving(mat, basis, j)
            if ri is None:
                raise SimplexError("phase-1 unbounded: implementation bug")
            _pivot(mat, zrow, basis, ri, j)
        if -zrow[-1] > 0:
            return INFEASIBLE, None, None

        # Drive basic artificials (at value zero) out of the basis.
        redundant = set()
        for i in range(m):
            if basis[i] in art_set:
                for j in range(ncols):
                    if j not in art_set and mat[i][j] != 0:
                        _pivot(mat, zrow, basis, i, j)
                        break
                else:
                    redundant.add(i)

        keep = [j for j in range(ncols) if j not in art_set]
        cmap = {old: new for new, old in enumerate(keep)}
        mat = [[row[j] for j in keep] + [row[-1]]
               for k, row in enumerate(mat) if k not in redundant]
        basis = [cmap[b] for k, b in enumerate(basis) if k not in redundant]
        ncols2 = len(keep)
    else:
        ncols2 = ncols

    # ---- Phase 2 ----
    z2 = [Fr(0)] * (ncols2 + 1)
    for j in range(n):                 # original variables carry the cost
        z2[j] = c[j]                   # keep[] starts with 0..n-1
    for i in range(len(mat)):
        f = z2[basis[i]]
        if f != 0:
            z2[:] = [a - f * b for a, b in zip(z2, mat[i])]
    while True:
        j = _entering(z2, ncols2)
        if j < 0:
            break
        ri = _leaving(mat, basis, j)
        if ri is None:
            return UNBOUNDED, None, None
        _pivot(mat, z2, basis, ri, j)

    x = [Fr(0)] * n
    for i, bi in enumerate(basis):
        if bi < n:
            x[bi] = mat[i][-1]
    value = -z2[-1]
    if maximize:
        value = -value
    return OPTIMAL, value, x


# ----------------------------------------------------------------------
# CHSH scenario utilities
# ----------------------------------------------------------------------

VAL = (Fr(-1), Fr(1))                       # outcome index -> value

ASSIGNMENTS = [(a0, a1, b0, b1)
               for a0 in (0, 1) for a1 in (0, 1)
               for b0 in (0, 1) for b1 in (0, 1)]
N_LAM = len(ASSIGNMENTS)                    # 16

CTX = [(x, y, a, b)
       for x in (0, 1) for y in (0, 1)
       for a in (0, 1) for b in (0, 1)]
CTX_IDX = {key: i for i, key in enumerate(CTX)}
N_P = len(CTX)                              # 16


def _responds(assignment, x, y, a, b):
    """1{ alpha(x) = a and beta(y) = b } for lambda = (a0,a1,b0,b1)."""
    a0, a1, b0, b1 = assignment
    av = a0 if x == 0 else a1
    bv = b0 if y == 0 else b1
    return av == a and bv == b


def T_matrix():
    T = [[Fr(0)] * N_LAM for _ in range(N_P)]
    for i, (x, y, a, b) in enumerate(CTX):
        for j, lam in enumerate(ASSIGNMENTS):
            if _responds(lam, x, y, a, b):
                T[i][j] = Fr(1)
    return T


def T_apply(q):
    out = []
    for x, y, a, b in CTX:
        s = Fr(0)
        for j, lam in enumerate(ASSIGNMENTS):
            if _responds(lam, x, y, a, b):
                s += q[j]
        out.append(s)
    return out


def sign_xy(x, y):
    return -1 if (x == 1 and y == 1) else 1


def S_of(p):
    s = Fr(0)
    for (x, y, a, b) in CTX:
        s += sign_xy(x, y) * VAL[a] * VAL[b] * p[CTX_IDX[(x, y, a, b)]]
    return s


def isotropic(v):
    """p_v = v * PR + (1 - v) * white noise,  v rational."""
    p = [None] * N_P
    for (x, y, a, b) in CTX:
        target = -1 if (x == 1 and y == 1) else 1
        pr = Fr(1, 2) if VAL[a] * VAL[b] == target else Fr(0)
        p[CTX_IDX[(x, y, a, b)]] = v * pr + (1 - v) * Fr(1, 4)
    return p


def pi_weighted_norm(p, q):
    """||p - q||_pi with the 1/2 convention: (1/2) * sum_xy pi_xy sum_ab |.|"""
    total = Fr(0)
    for x, y in ((0, 0), (0, 1), (1, 0), (1, 1)):
        for a, b in ((0, 0), (0, 1), (1, 0), (1, 1)):
            d = p[CTX_IDX[(x, y, a, b)]] - q[CTX_IDX[(x, y, a, b)]]
            total += abs(d)
    return total * Fr(1, 8)                # (1/2)*(1/4)*L1


def vertex_behavior(j):
    col = [Fr(0)] * N_P
    for i, (x, y, a, b) in enumerate(CTX):
        if _responds(ASSIGNMENTS[j], x, y, a, b):
            col[i] = Fr(1)
    return col


# ----------------------------------------------------------------------
# LP instances
# ----------------------------------------------------------------------

def lp_repair_distance(p):
    """LP (29): min (1/8) sum u  s.t.  -u <= p - Tq <= u,  q >= 0, sum q = 1."""
    T = T_matrix()
    n = 32
    c = [Fr(0)] * 16 + [Fr(1, 8)] * 16
    le = []
    for i in range(N_P):
        row = [-T[i][j] for j in range(16)] + [Fr(0)] * 16
        row[16 + i] = Fr(-1)
        le.append((row, -p[i]))            # p - Tq - u <= 0
    for i in range(N_P):
        row = [T[i][j] for j in range(16)] + [Fr(0)] * 16
        row[16 + i] = Fr(-1)
        le.append((row, p[i]))             # Tq - p - u <= 0
    eq = [([Fr(1)] * 16 + [Fr(0)] * 16, Fr(1))]
    return simplex_solve(n, c, le=le, eq=eq)


def lp_dual_repair(p):
    """Dual of (29): max B.p - beta  s.t.  B.l_lambda - beta <= 0 for all
    vertices lambda,  |B_i| <= 1/8  (uniform pi = 1/4)."""
    T = T_matrix()
    cols = [[T[i][j] for i in range(N_P)] for j in range(N_LAM)]
    n = 34                                 # Bp(16), Bm(16), betap, betam
    c = [-p[j] for j in range(16)] + [p[j] for j in range(16)] + \
        [Fr(1), Fr(-1)]                    # min -(B.p - beta)
    le = []
    for lam in range(N_LAM):
        row = [Fr(0)] * n
        for i in range(N_P):
            row[i] = cols[lam][i]
            row[16 + i] = -cols[lam][i]
        row[32], row[33] = Fr(-1), Fr(1)
        le.append((row, Fr(0)))            # B.l - beta <= 0
    for j in range(16):
        row = [Fr(0)] * n
        row[j], row[16 + j] = Fr(1), Fr(-1)
        le.append((row, Fr(1, 8)))         # Bp - Bm <= 1/8
        row2 = [Fr(0)] * n
        row2[j], row2[16 + j] = Fr(-1), Fr(1)
        le.append((row2, Fr(1, 8)))        # -(Bp - Bm) <= 1/8
    status, val, x = simplex_solve(n, c, le=le)
    if status != OPTIMAL:
        return status, None, None
    B = [x[j] - x[16 + j] for j in range(16)]
    beta = x[32] - x[33]
    return status, -val, (B, beta)


def lp_negative_mass(p):
    """min sum q-  s.t.  T(q+ - q-) = p,  sum(q+ - q-) = 1,  q+, q- >= 0."""
    T = T_matrix()
    n = 32
    c = [Fr(0)] * 16 + [Fr(1)] * 16
    eq = []
    for i in range(N_P):
        eq.append((list(T[i]) + [-v for v in T[i]], p[i]))
    eq.append(([Fr(1)] * 16 + [Fr(-1)] * 16, Fr(1)))
    return simplex_solve(n, c, eq=eq)


def lp_dual_negative_mass(p):
    """Dual: max alpha.p + beta  s.t.  -1 <= alpha.l_lambda + beta <= 0."""
    T = T_matrix()
    cols = [[T[i][j] for i in range(N_P)] for j in range(N_LAM)]
    n = 34                                 # ap(16), am(16), bp, bm
    c = [-p[j] for j in range(16)] + [p[j] for j in range(16)] + \
        [Fr(-1), Fr(1)]                    # min -(alpha.p + beta)
    le = []
    for lam in range(N_LAM):
        row = [Fr(0)] * n
        for i in range(N_P):
            row[i] = cols[lam][i]
            row[16 + i] = -cols[lam][i]
        row[32], row[33] = Fr(1), Fr(-1)
        le.append((row, Fr(0)))            # alpha.l + beta <= 0
        row2 = [Fr(0)] * n
        for i in range(N_P):
            row2[i] = -cols[lam][i]
            row2[16 + i] = cols[lam][i]
        row2[32], row2[33] = Fr(-1), Fr(1)
        le.append((row2, Fr(1)))           # -(alpha.l + beta) <= 1
    status, val, x = simplex_solve(n, c, le=le)
    if status != OPTIMAL:
        return status, None, None
    alpha = [x[j] - x[16 + j] for j in range(16)]
    beta = x[32] - x[33]
    return status, -val, (alpha, beta)


# ----------------------------------------------------------------------
#pretty printing
# ----------------------------------------------------------------------

def fnum(x):
    return f"{x}  (= {float(x):.6f})"


RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond)))
    tag = "PASS" if cond else "FAIL"
    print(f"  [{tag}] {name}" + (f"   {detail}" if detail else ""))
    return cond


def header(t):
    print(f"\n{'=' * 72}\n{t}\n{'=' * 72}")


# ----------------------------------------------------------------------
# Checks
# ----------------------------------------------------------------------

def c0_selftest():
    header("C0  simplex self-tests")
    st, v, _ = simplex_solve(2, [1, 1], eq=[([1, -1], 0)], le=[([-1, 0], -2)])
    check("selftest eq+ge", st == OPTIMAL and v == 4, f"value = {v}")

    st, v, _ = simplex_solve(1, [-1], le=[([1], 3)])
    check("selftest min -x, x<=3", st == OPTIMAL and v == -3, f"value = {v}")

    st, v, _ = simplex_solve(1, [1], le=[([1], 1), ([-1], -2)])
    check("selftest infeasible", st == INFEASIBLE)

    st, v, _ = simplex_solve(1, [-1])
    check("selftest unbounded", st == UNBOUNDED)

    st, v, _ = simplex_solve(1, [1], le=[([1], 5)], maximize=True)
    check("selftest maximize", st == OPTIMAL and v == 5, f"value = {v}")

    # Beale's cycling example (Dantzig's rule cycles; Bland's must not).
    st, v, _ = simplex_solve(
        4, [Fr(-3, 4), 150, Fr(-1, 50), 6],
        le=[([Fr(1, 4), -60, Fr(-1, 25), 9], 0),
            ([Fr(1, 2), -90, Fr(-1, 50), 3], 0),
            ([0, 0, 1, 0], 1)])
    check("selftest Beale (anti-cycling)", st == OPTIMAL and v == Fr(-1, 20),
          f"value = {v}")


def c1_local_bound():
    header("C1  CHSH local bound at the deterministic vertices")
    ok = True
    ks = []
    for j, (a0, a1, b0, b1) in enumerate(ASSIGNMENTS):
        va0, va1, vb0, vb1 = VAL[a0], VAL[a1], VAL[b0], VAL[b1]
        K = va0 * (vb0 + vb1) + va1 * (vb0 - vb1)
        ks.append(K)
        lv = vertex_behavior(j)
        if S_of(lv) != K:
            ok = False
        if K not in (Fr(2), Fr(-2)):
            ok = False
    check("K(lambda) in {+2,-2} and S(vertex) = K(lambda) for all 16",
          ok, f"values: {sorted(set(ks))}")

    # sanity of T: column sums are 4, T(1/16) = uniform behavior
    T = T_matrix()
    colsums = {sum(T[i][j] for i in range(N_P)) for j in range(N_LAM)}
    uni = T_apply([Fr(1, 16)] * 16)
    check("column sums = 4 and T(uniform) = uniform behavior",
          colsums == {Fr(4)} and all(u == Fr(1, 4) for u in uni))


def ns_constraint_matrix():
    rows = []
    for a in (0, 1):
        for x in (0, 1):
            row = [Fr(0)] * N_P
            for b in (0, 1):
                row[CTX_IDX[(x, 0, a, b)]] += Fr(1)
                row[CTX_IDX[(x, 1, a, b)]] -= Fr(1)
            rows.append(row)
    for b in (0, 1):
        for y in (0, 1):
            row = [Fr(0)] * N_P
            for a in (0, 1):
                row[CTX_IDX[(0, y, a, b)]] += Fr(1)
                row[CTX_IDX[(1, y, a, b)]] -= Fr(1)
            rows.append(row)
    return rows


def c2_image_is_ns():
    header("C2  im(T) is contained in the no-signalling subspace")
    N = ns_constraint_matrix()
    T = T_matrix()
    ok = True
    for j in range(N_LAM):
        col = [T[i][j] for i in range(N_P)]
        for row in N:
            if sum(r * c for r, c in zip(row, col)) != 0:
                ok = False
    check("N @ (T e_lambda) = 0 for all 16 vertices", ok)


def c3_ns_fiber_lemma():
    header("C3  Lemma L1: T({q : sum q = 1}) = normalized NS tables")
    N = ns_constraint_matrix()
    T = T_matrix()
    rank_T = exact_rank(T)
    rank_N = exact_rank(N)
    check("rank(T) = 9 (linear span of the 16 vertices)", rank_T == 9,
          f"rank = {rank_T}")
    check("ambient rank of the NS functionals = 7", rank_N == 7,
          f"rank = {rank_N}")

    ns_basis = nullspace_basis(N, N_P)
    check("dim V_NS = 9 (constructive basis)", len(ns_basis) == 9,
          f"dim = {len(ns_basis)}")

    # On V_NS all four context-sum functionals coincide, so the normalized
    # slice {p in V_NS : context sums = 1} is an affine hyperplane of V_NS.
    ok = True
    for e in ns_basis:
        sums = [sum(e[CTX_IDX[(x, y, a, b)]] for a in (0, 1) for b in (0, 1))
                for x in (0, 1) for y in (0, 1)]
        if len(set(sums)) != 1:
            ok = False
    check("context sums coincide across contexts on V_NS", ok)

    # P = I - J/16 projects onto ker(sum); T(ker sum) = direction space of aff(L)
    P = [[(Fr(1) if i == j else Fr(0)) - Fr(1, 16) for j in range(16)]
         for i in range(16)]
    TP = [[sum(T[i][k] * P[k][j] for k in range(16)) for j in range(16)]
          for i in range(N_P)]
    check("dim aff(L) = rank(T restricted to {sum q = 0}) = 8",
          exact_rank(TP) == 8, f"rank = {exact_rank(TP)}")

    # constructive: the PR box (normalized, NS) has an exact signed preimage
    p_pr = isotropic(Fr(1))
    A = [list(T[i]) for i in range(N_P)] + [[Fr(1)] * 16]
    b = list(p_pr) + [Fr(1)]
    q = exact_solve(A, b)
    check("PR box admits an exact normalized signed preimage",
          q is not None and T_apply(q) == p_pr and sum(q) == 1)


def c4_positive_extension():
    header("C4  Positive extension at v = 3/8 (interior) and v = 1/2 (boundary)")
    for v in (Fr(3, 8), Fr(1, 2)):
        p = isotropic(v)
        T = T_matrix()
        eq = [([Fr(1)] * 16, Fr(1))]
        for i in range(N_P):
            eq.append((list(T[i]), p[i]))
        st, val, q = simplex_solve(16, [Fr(0)] * 16, eq=eq)
        ok = (st == OPTIMAL and val == 0 and q is not None
              and all(x >= 0 for x in q)
              and T_apply(q) == p and sum(q) == 1)
        check(f"explicit positive extension for v = {v}",
              ok, f"T q* = p_v exactly, sum q* = 1")


def c5_infeasible_outside():
    header("C5  No positive extension at v = 51/100")
    p = isotropic(Fr(51, 100))
    T = T_matrix()
    eq = [([Fr(1)] * 16, Fr(1))]
    for i in range(N_P):
        eq.append((list(T[i]), p[i]))
    st, val, q = simplex_solve(16, [Fr(0)] * 16, eq=eq)
    check("LP detects infeasibility exactly", st == INFEASIBLE,
          f"(v = 51/100 > 1/2: outside the local polytope)")


def c6_sharpness():
    header("C6  LP (29): R(v) = max(0, (2v-1)/4) on the isotropic line")
    for v in (Fr(3, 8), Fr(5, 8), Fr(70, 99), Fr(1)):
        expected = max(Fr(0), (2 * v - 1) / 4)
        st, val, _ = lp_repair_distance(isotropic(v))
        check(f"R({v}) = {expected}", st == OPTIMAL and val == expected,
              f"LP value = {val}  (={float(val):.6f})")


def c7_duality():
    header("C7  Exact LP duality for (29) + CHSH witness attainment")
    for v in (Fr(3, 8), Fr(5, 8), Fr(70, 99), Fr(1)):
        p = isotropic(v)
        stp, valp, _ = lp_repair_distance(p)
        std, vald, sol = lp_dual_repair(p)
        ok = (stp == OPTIMAL and std == OPTIMAL and valp == vald)
        detail = f"primal = {valp}, dual = {vald}"
        if sol is not None:
            B, beta = sol
            ok = ok and all(abs(b) <= Fr(1, 8) for b in B)
            # the fixed witness s/8 is dual-feasible: it lower-bounds R and
            # attains the optimum exactly when R > 0 (nonlocal boxes)
            Bw = [sign_xy(x, y) * VAL[a] * VAL[b] * Fr(1, 8)
                  for (x, y, a, b) in CTX]
            wit_val = sum(b * pp for b, pp in zip(Bw, p)) \
                - max(sum(b * l for b, l in zip(Bw, vertex_behavior(lam)))
                      for lam in range(N_LAM))
            ok = ok and (wit_val <= valp) and \
                (valp == 0 or wit_val == valp)
            detail += f", ||B*||_inf <= 1/8, witness s/8 gives {wit_val}"
        check(f"strong duality at v = {v}", ok, detail)


def c8_negative_mass():
    header("C8  Negative-mass LP: primal = dual exactly")
    p = isotropic(Fr(3, 8))
    st, val, _ = lp_negative_mass(p)
    check("N(local box v = 3/8) = 0", st == OPTIMAL and val == 0,
          f"value = {val}")

    for v in (Fr(5, 8), Fr(1)):
        p = isotropic(v)
        stp, valp, _ = lp_negative_mass(p)
        std, vald, _ = lp_dual_negative_mass(p)
        ok = stp == OPTIMAL and std == OPTIMAL and valp == vald
        detail = f"N = {valp}" if valp is not None else f"primal status {stp}"
        check(f"N(v = {v}): primal = dual", ok, detail)


def c9_signalling():
    header("C9  Signalling table has no normalized signed preimage")
    p = [Fr(1, 4)] * N_P
    p[CTX_IDX[(0, 0, 1, 1)]] = Fr(3, 8)   # ++
    p[CTX_IDX[(0, 0, 0, 0)]] = Fr(3, 8)   # --
    p[CTX_IDX[(0, 0, 1, 0)]] = Fr(1, 8)   # +-
    p[CTX_IDX[(0, 0, 0, 1)]] = Fr(1, 8)   # -+
    p[CTX_IDX[(0, 1, 1, 1)]] = Fr(3, 8)   # A-marginal now depends on y
    p[CTX_IDX[(0, 1, 1, 0)]] = Fr(3, 8)
    p[CTX_IDX[(0, 1, 0, 1)]] = Fr(1, 8)
    p[CTX_IDX[(0, 1, 0, 0)]] = Fr(1, 8)
    # normalization per context holds; signalling in A at x = 0
    st, val, _ = lp_negative_mass(p)
    Nmat = ns_constraint_matrix()
    ns_defect = max(sum(r * c for r, c in zip(row, p)) for row in Nmat)
    check("negative-mass LP infeasible for signalling p", st == INFEASIBLE,
          f"(max NS residual = {ns_defect} != 0, consistent with Lemma L1)")


def c10_stability():
    header("C10  Stability: the 8-epsilon bound at a perturbed isotropic box")
    v = Fr(5, 8)
    p = isotropic(v)
    delta = Fr(1, 100)
    pt = list(p)
    pt[CTX_IDX[(0, 0, 1, 1)]] += delta
    pt[CTX_IDX[(0, 0, 1, 0)]] -= delta
    eps = pi_weighted_norm(p, pt)
    Sp = S_of(pt)
    bound = (Sp - 2 - 8 * eps) / 8
    st, val, _ = lp_repair_distance(pt)
    check("||p~ - p||_pi = 1/400", eps == Fr(1, 400), f"eps = {eps}")
    check("R(p~) >= (|S(p~)| - 2 - 8 eps)/8 = 1/16 exactly",
          st == OPTIMAL and val is not None and val >= bound
          and bound == Fr(1, 16),
          f"bound = {bound}, R(p~) = {val}")


def c11_observer():
    header("C11  Observer module: fiber determinacy theorems")
    # histories h1..h4; reports: y0 = {h1,h2}, y1 = {h3}; tasks 0,1,7
    H = ["h1", "h2", "h3"]
    O = {"h1": "y0", "h2": "y0", "h3": "y1"}
    f = {"h1": Fr(0), "h2": Fr(1), "h3": Fr(7)}

    def floor_of(histories, obs, task):
        return max(
            (max(task[h] for h in histories if obs[h] == y)
             - min(task[h] for h in histories if obs[h] == y)) / 2
            for y in set(obs.values()))

    fl = floor_of(H, O, f)
    check("minimax floor = half the fiber task-diameter", fl == Fr(1, 2),
          f"floor = {fl}")

    # midpoint attainment: g(y0) = 1/2, g(y1) = 7 achieves the floor
    g = {"y0": Fr(1, 2), "y1": Fr(7)}
    err = max(abs(f[h] - g[O[h]]) for h in H)
    check("midpoint predictor attains the floor", err == fl, f"error = {err}")

    # no predictor beats it: on the fiber {0,1} the best worst-case error is
    # exactly half the diameter (brute force over a fine rational grid)
    grid = [Fr(k, 40) for k in range(-20, 60)]
    best_y0 = min(max(abs(Fr(0) - c), abs(Fr(1) - c)) for c in grid)
    check("no predictor beats the floor on the nontrivial fiber",
          best_y0 == fl, f"grid optimum on fiber {{0,1}} = {best_y0}")

    # refinement: O' splits {h1, h2}
    O2 = {"h1": "z0", "h2": "z1", "h3": "y1"}
    check("refinement monotonicity: floor(O') <= floor(O)",
          floor_of(H, O2, f) <= fl, f"floor' = {floor_of(H, O2, f)}")

    # report-preserving update: internal state i added, report unchanged
    H2 = [("h1", 0), ("h1", 1), ("h2", 0), ("h2", 1), ("h3", 0), ("h3", 1)]
    O3 = {hp: O[hp[0]] for hp in H2}
    f3 = {hp: f[hp[0]] for hp in H2}
    check("report-preserving update leaves the floor unchanged",
          floor_of(H2, O3, f3) == fl, f"floor = {floor_of(H2, O3, f3)}")

    # evidence gain: new observation z separates h1 from h2
    z = {"h1": 0, "h2": 1, "h3": 0}
    O4 = {h: (O[h], z[h]) for h in H}
    gain = fl - floor_of(H, O4, f)
    check("evidence-gain criterion: z separates the extremal pair",
          floor_of(H, O4, f) == 0 and gain == fl,
          f"gain = {gain}")
    zc = {"h1": 0, "h2": 0, "h3": 0}
    O5 = {h: (O[h], zc[h]) for h in H}
    check("constant z carries no evidence: gain = 0",
          floor_of(H, O5, f) == fl)


def main():
    print("Exact-arithmetic verification: obstruction calculus for the")
    print("CHSH scenario and the observer module (fractions only).")
    c0_selftest()
    c1_local_bound()
    c2_image_is_ns()
    c3_ns_fiber_lemma()
    c4_positive_extension()
    c5_infeasible_outside()
    c6_sharpness()
    c7_duality()
    c8_negative_mass()
    c9_signalling()
    c10_stability()
    c11_observer()

    header("SUMMARY")
    npass = sum(1 for _, ok in RESULTS if ok)
    print(f"{npass}/{len(RESULTS)} checks passed.")
    if npass != len(RESULTS):
        for name, ok in RESULTS:
            if not ok:
                print(f"  FAILED: {name}")
    print("\nExact certificates for the notes (printed, not asserted):")
    v = Fr(5, 8)
    p = isotropic(v)
    st, val, x = lp_repair_distance(p)
    T = T_matrix()
    ell = T_apply(x[:16])
    print(f"  v = 5/8: R = {val}; primal optimizer q* (16 weights):")
    print(f"    {x[:16]}")
    print(f"  v = 5/8: nearest local behavior ell* = T q*:")
    print(f"    {ell}")
    std, vald, sol = lp_dual_repair(p)
    if sol:
        B, beta = sol
        print(f"  v = 5/8: dual optimizer B* = {B}")
        print(f"           beta* = {beta}  (max_lambda B*.l_lambda)")
    p1 = isotropic(Fr(1))
    std1, vald1, sol1 = lp_dual_repair(p1)
    if sol1:
        print(f"  v = 1  : dual optimizer B* = {sol1[0]}")
    stn, valn, qn = lp_negative_mass(isotropic(Fr(1)))
    if qn is not None:
        qplus, qminus = qn[:16], qn[16:]
        print(f"  v = 1  : N(PR) = {valn}; sum q+ = {sum(qplus)}, "
              f"sum q- = {sum(qminus)}")
    sys.exit(0 if npass == len(RESULTS) else 1)


if __name__ == "__main__":
    main()
