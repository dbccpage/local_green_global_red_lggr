"""Exact contextuality LP with independently replayed rational certificates.

Two-phase Bland simplex adapted from omega_solvers/solver_lp_standard_form.rs;
the convex-hull reduction follows omega_sheaf_theory/empirical_presheaf/lp.rs.
Only integers and fractions.Fraction are accepted. No floating approximation,
SciPy, external executable, or monorepo import is used.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import product
from math import prod


class Refusal(ValueError):
    """A refusal, including budget exhaustion, is never a contextuality verdict."""
    def __init__(self, kind):
        self.kind = kind
        super().__init__(kind)


def rational(value):
    if type(value) not in (int, Q):
        raise Refusal("NONEXACT_INPUT")
    return Q(value)


def dot(a, b):
    if len(a) != len(b):
        raise Refusal("SHAPE")
    return sum((x * y for x, y in zip(a, b)), Q(0))


@dataclass(frozen=True)
class LPCertificate:
    primal: tuple
    dual: tuple
    value: Q
    pivots: int


def verify_standard(costs, matrix, rhs, cert):
    """Replay feasibility and the zero gap; no simplex internals are trusted."""
    n, m = len(costs), len(rhs)
    if len(matrix) != m or any(len(row) != n for row in matrix):
        return False
    if len(cert.primal) != n or len(cert.dual) != m:
        return False
    values = (*costs, *rhs, *(v for row in matrix for v in row),
              *cert.primal, *cert.dual, cert.value)
    if any(type(v) is not Q for v in values) or any(x < 0 for x in cert.primal):
        return False
    return (all(dot(row, cert.primal) == b for row, b in zip(matrix, rhs))
            and all(sum((matrix[i][j] * cert.dual[i] for i in range(m)), Q(0)) <= costs[j]
                    for j in range(n))
            and dot(costs, cert.primal) == cert.value == dot(rhs, cert.dual))


def solve_standard(costs, matrix, rhs, *, max_pivots=10000, max_entries=2000000):
    """Minimize c.x subject to Ax=b and x>=0; total pivot budget across phases."""
    if type(max_pivots) is not int or max_pivots < 0:
        raise Refusal("INVALID_BUDGET")
    n, m = len(costs), len(rhs)
    if len(matrix) != m or any(len(row) != n for row in matrix):
        raise Refusal("SHAPE")
    if type(max_entries) is not int or max_entries < 0 or (m + 1) * (n + m + 1) > max_entries:
        raise Refusal("SIZE_LIMIT")
    costs = tuple(map(rational, costs))
    rhs = tuple(map(rational, rhs))
    matrix = tuple(tuple(map(rational, row)) for row in matrix)
    signs = [Q(-1) if b < 0 else Q(1) for b in rhs]
    tab = [[Q(0) for _ in range(n + m + 1)] for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            tab[i + 1][j] = signs[i] * matrix[i][j]
        tab[i + 1][n + i] = Q(1)
        tab[i + 1][-1] = signs[i] * rhs[i]
    for j in range(n):
        tab[0][j] = -sum((tab[i][j] for i in range(1, m + 1)), Q(0))
    tab[0][-1] = -sum((tab[i][-1] for i in range(1, m + 1)), Q(0))
    basis = list(range(n, n + m))
    remaining = max_pivots

    def pivot(table, row, col):
        nonlocal remaining
        if remaining == 0:
            raise Refusal("BUDGET_EXHAUSTED")
        remaining -= 1
        divisor = table[row][col]
        table[row] = [x / divisor for x in table[row]]
        for i in range(len(table)):
            if i != row:
                factor = table[i][col]
                if factor:
                    table[i] = [x - factor * y for x, y in zip(table[i], table[row])]

    def simplex(table, current_basis):
        while True:
            entering = next((j for j in range(n) if table[0][j] < 0), None)
            if entering is None:
                return
            eligible = [i for i in range(1, len(table)) if table[i][entering] > 0]
            if not eligible:
                raise Refusal("UNBOUNDED")
            leaving = min(eligible, key=lambda i: (table[i][-1] / table[i][entering], current_basis[i - 1]))
            pivot(table, leaving, entering)
            current_basis[leaving - 1] = entering

    simplex(tab, basis)
    if tab[0][-1] != 0:
        raise Refusal("INFEASIBLE")
    for i in range(1, m + 1):
        if basis[i - 1] >= n:
            entering = next((j for j in range(n) if tab[i][j] != 0), None)
            if entering is not None:
                pivot(tab, i, entering)
                basis[i - 1] = entering
    phase_two = [list(costs) + [Q(0)] * (m + 1)]
    basis_two = []
    for i in range(1, m + 1):
        if basis[i - 1] < n:
            phase_two.append(tab[i][:])
            basis_two.append(basis[i - 1])
    for i, variable in enumerate(basis_two):
        cost = phase_two[0][variable]
        phase_two[0] = [x - cost * y for x, y in zip(phase_two[0], phase_two[i + 1])]
    simplex(phase_two, basis_two)
    primal = [Q(0)] * n
    for i, variable in enumerate(basis_two):
        primal[variable] = phase_two[i + 1][-1]
    cert = LPCertificate(tuple(primal), tuple(-signs[i] * phase_two[0][n + i] for i in range(m)),
                         -phase_two[0][-1], max_pivots - remaining)
    if not verify_standard(costs, matrix, rhs, cert):
        raise Refusal("CERTIFICATE_MISMATCH")
    return cert


@dataclass(frozen=True)
class DefectCertificate:
    coefficients: tuple
    residual: tuple
    witness: tuple
    offset: Q
    defect: Q
    lp: LPCertificate


def standard_form(generators, target, *, max_entries=2000000):
    k, m = len(generators), len(target)
    width = k + 2 * m
    if k == 0 or any(len(g) != m for g in generators):
        raise Refusal("SHAPE")
    if type(max_entries) is not int or max_entries < 0 or (m + 2) * (width + m + 2) > max_entries:
        raise Refusal("SIZE_LIMIT")
    generators = tuple(tuple(map(rational, g)) for g in generators)
    target = tuple(map(rational, target))
    costs = (Q(0),) * k + (Q(1),) * (2 * m)
    matrix = []
    for i in range(m):
        row = [g[i] for g in generators] + [Q(0)] * (2 * m)
        row[k + i], row[k + m + i] = Q(-1), Q(1)
        matrix.append(tuple(row))
    matrix.append((Q(1),) * k + (Q(0),) * (2 * m))
    return generators, target, costs, tuple(matrix), target + (Q(1),)


def verify_defect(generators, target, cert, *, max_entries=2000000):
    try:
        generators, target, costs, matrix, rhs = standard_form(generators, target, max_entries=max_entries)
    except Refusal:
        return False
    k, m = len(generators), len(target)
    if (len(cert.coefficients) != k or len(cert.residual) != m or len(cert.witness) != m
            or any(type(v) is not Q for v in (*cert.coefficients, *cert.residual, *cert.witness, cert.offset, cert.defect))):
        return False
    residual = tuple(sum((g[i] * c for g, c in zip(generators, cert.coefficients)), Q(0)) - target[i]
                     for i in range(m))
    return (verify_standard(costs, matrix, rhs, cert.lp)
            and cert.lp.primal[:k] == cert.coefficients
            and cert.lp.dual[:m] == cert.witness and cert.lp.dual[m] == cert.offset
            and cert.lp.value == cert.defect
            and residual == cert.residual
            and all(c >= 0 for c in cert.coefficients) and sum(cert.coefficients) == 1
            and all(abs(y) <= 1 for y in cert.witness)
            and all(dot(g, cert.witness) + cert.offset <= 0 for g in generators)
            and dot(target, cert.witness) + cert.offset == cert.defect == sum(map(abs, residual)))


def solve_l1(generators, target, *, max_pivots=10000, max_entries=2000000):
    generators, target, costs, matrix, rhs = standard_form(generators, target, max_entries=max_entries)
    lp = solve_standard(costs, matrix, rhs, max_pivots=max_pivots, max_entries=max_entries)
    k, m = len(generators), len(target)
    coeff = lp.primal[:k]
    residual = tuple(sum((g[i] * c for g, c in zip(generators, coeff)), Q(0)) - target[i] for i in range(m))
    cert = DefectCertificate(coeff, residual, lp.dual[:m], lp.dual[m], lp.value, lp)
    if not verify_defect(generators, target, cert, max_entries=max_entries):
        raise Refusal("CERTIFICATE_MISMATCH")
    return cert


@dataclass(frozen=True)
class Scenario:
    outcome_sizes: tuple
    contexts: tuple
    tables: tuple


def contextual_matrix(model, *, max_assignments=1048576, max_entries=2000000):
    # Validate ordinary containers and indices before sorting or hashing.
    if not isinstance(model, Scenario):
        raise Refusal("SHAPE")
    sizes, contexts, tables = model.outcome_sizes, model.contexts, model.tables
    if (any(type(v) not in (tuple, list) for v in (sizes, contexts, tables))
            or not sizes or any(type(n) is not int or n <= 0 for n in sizes)
            or not contexts or len(contexts) != len(tables)
            or any(type(c) not in (tuple, list) for c in contexts)
            or any(type(row) not in (tuple, list) for row in tables)):
        raise Refusal("SHAPE")
    if any(any(type(i) is not int or i < 0 or i >= len(sizes) for i in c) for c in contexts):
        raise Refusal("SHAPE")
    contexts = tuple(tuple(c) for c in contexts)
    if (any(tuple(sorted(set(c))) != c for c in contexts)
            or len(set(contexts)) != len(contexts)):
        raise Refusal("SHAPE")
    if set().union(*map(set, contexts)) != set(range(len(sizes))):
        raise Refusal("UNCOVERED_MEASUREMENT")
    count = prod(sizes)
    if type(max_assignments) is not int or max_assignments < 1 or count > max_assignments:
        raise Refusal("ENUMERATION_LIMIT")
    row_count = sum(prod(sizes[i] for i in c) for c in contexts)
    if type(max_entries) is not int or (row_count + 2) * (count + 3 * row_count + 2) > max_entries:
        raise Refusal("SIZE_LIMIT")
    local = tuple(tuple(product(*(range(sizes[i]) for i in c))) for c in contexts)
    exact = []
    for row, outcomes in zip(tables, local):
        if len(row) != len(outcomes):
            raise Refusal("SHAPE")
        row = tuple(map(rational, row))
        if any(q < 0 for q in row) or sum(row) != 1:
            raise Refusal("NOT_A_DISTRIBUTION")
        exact.append(row)
    for a, ca in enumerate(contexts):
        for b, cb in enumerate(contexts[:a]):
            overlap = tuple(sorted(set(ca) & set(cb)))
            def marginal(c, outcomes, row):
                result = {}
                for outcome, weight in zip(outcomes, row):
                    key = tuple(outcome[c.index(i)] for i in overlap)
                    result[key] = result.get(key, Q(0)) + weight
                return result
            if marginal(ca, local[a], exact[a]) != marginal(cb, local[b], exact[b]):
                raise Refusal("SIGNALLING")
    assignments = tuple(product(*(range(n) for n in sizes)))
    columns = tuple(tuple(Q(tuple(g[i] for i in c) == o) for c, outcomes in zip(contexts, local) for o in outcomes)
                    for g in assignments)
    return assignments, columns, tuple(q for row in exact for q in row)


@dataclass(frozen=True)
class ContextualityResult:
    kind: str
    assignments: tuple
    certificate: DefectCertificate


def evaluate(model, *, max_pivots=10000, max_assignments=1048576, max_entries=2000000):
    assignments, columns, target = contextual_matrix(model, max_assignments=max_assignments, max_entries=max_entries)
    certificate = solve_l1(columns, target, max_pivots=max_pivots, max_entries=max_entries)
    return ContextualityResult("GlobalSection" if certificate.defect == 0 else "Obstructed", assignments, certificate)
