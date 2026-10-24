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


@dataclass(frozen=True)
class InfeasibilityCertificate:
    dual: tuple
    pivots: int


@dataclass(frozen=True)
class UnboundednessCertificate:
    primal: tuple
    direction: tuple
    pivots: int


class CertifiedInfeasible(Refusal):
    def __init__(self, certificate):
        self.certificate = certificate
        super().__init__("INFEASIBLE")


class CertifiedUnbounded(Refusal):
    def __init__(self, certificate):
        self.certificate = certificate
        super().__init__("UNBOUNDED")


def _certificate_inputs(costs, matrix, rhs):
    """Validate original LP data, independently of tableau transformations."""
    if any(type(v) not in (tuple, list) for v in (costs, matrix, rhs)):
        raise Refusal("SHAPE")
    if len(matrix) != len(rhs) or any(type(row) not in (tuple, list) or len(row) != len(costs)
                                      for row in matrix):
        raise Refusal("SHAPE")
    return (tuple(map(rational, costs)), tuple(tuple(map(rational, r)) for r in matrix),
            tuple(map(rational, rhs)))


def _exact_vector(v, size):
    return type(v) is tuple and len(v) == size and all(type(q) is Q for q in v)


def verify_infeasible(costs, matrix, rhs, cert):
    """Farkas witness: A^T y >= 0 and b.y < 0. No solver state is read.

    Pivot metadata is a nonnegative integer, not evidence of infeasibility.
    Exact int/Fraction problem inputs are accepted; witness entries are Fraction.
    """
    try:
        costs, matrix, rhs = _certificate_inputs(costs, matrix, rhs)
        if (type(cert) is not InfeasibilityCertificate or not _exact_vector(cert.dual, len(rhs))
                or type(cert.pivots) is not int or cert.pivots < 0):
            return False
        return (dot(rhs, cert.dual) < 0
                and all(sum((row[j] * y for row, y in zip(matrix, cert.dual)), Q(0)) >= 0
                        for j in range(len(costs))))
    except (TypeError, ValueError, AttributeError):
        return False


def verify_unbounded(costs, matrix, rhs, cert):
    """Check a feasible base point and a nonnegative nullspace descent ray."""
    try:
        costs, matrix, rhs = _certificate_inputs(costs, matrix, rhs)
        n = len(costs)
        if (type(cert) is not UnboundednessCertificate or not _exact_vector(cert.primal, n)
                or not _exact_vector(cert.direction, n)
                or type(cert.pivots) is not int or cert.pivots < 0):
            return False
        return (all(q >= 0 for q in (*cert.primal, *cert.direction))
                and all(dot(row, cert.primal) == b and dot(row, cert.direction) == 0
                        for row, b in zip(matrix, rhs))
                and dot(costs, cert.direction) < 0)
    except (TypeError, ValueError, AttributeError):
        return False


def verify_standard(costs, matrix, rhs, cert):
    """Replay feasibility and zero gap against original int/Fraction inputs.

    Witness entries are Fractions. Pivots must be a nonnegative exact integer
    as schema metadata; their value is not evidence of optimality.
    """
    try:
        costs, matrix, rhs = _certificate_inputs(costs, matrix, rhs)
        n, m = len(costs), len(rhs)
        if (type(cert) is not LPCertificate or not _exact_vector(cert.primal, n)
                or not _exact_vector(cert.dual, m) or type(cert.value) is not Q
                or type(cert.pivots) is not int or cert.pivots < 0):
            return False
        return (all(x >= 0 for x in cert.primal)
                and all(dot(row, cert.primal) == b for row, b in zip(matrix, rhs))
                and all(sum((matrix[i][j] * cert.dual[i] for i in range(m)), Q(0)) <= costs[j]
                        for j in range(n))
                and dot(costs, cert.primal) == cert.value == dot(rhs, cert.dual))
    except (TypeError, ValueError, AttributeError):
        return False


def solve_standard(costs, matrix, rhs, *, max_pivots=10000, max_entries=2000000):
    """Minimize c.x subject to Ax=b and x>=0; total pivot budget across phases.

    Returns LPCertificate at an optimum. CertifiedInfeasible and
    CertifiedUnbounded carry independently replayable mathematical witnesses;
    ordinary Refusal (including budget exhaustion) is inconclusive.
    """
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
                return entering
            leaving = min(eligible, key=lambda i: (table[i][-1] / table[i][entering], current_basis[i - 1]))
            pivot(table, leaving, entering)
            current_basis[leaving - 1] = entering

    if simplex(tab, basis) is not None:
        # Phase one's nonnegative artificial objective cannot be unbounded below.
        raise Refusal("CERTIFICATE_MISMATCH")
    if tab[0][-1] != 0:
        cert = InfeasibilityCertificate(tuple(signs[i] * (tab[0][n + i] - 1) for i in range(m)),
                                       max_pivots - remaining)
        if not verify_infeasible(costs, matrix, rhs, cert):
            raise Refusal("CERTIFICATE_MISMATCH")
        raise CertifiedInfeasible(cert)
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
    ray_entering = simplex(phase_two, basis_two)
    primal = [Q(0)] * n
    for i, variable in enumerate(basis_two):
        primal[variable] = phase_two[i + 1][-1]
    if ray_entering is not None:
        direction = [Q(int(j == ray_entering)) for j in range(n)]
        for i, variable in enumerate(basis_two):
            direction[variable] = -phase_two[i + 1][ray_entering]
        cert = UnboundednessCertificate(tuple(primal), tuple(direction), max_pivots - remaining)
        if not verify_unbounded(costs, matrix, rhs, cert):
            raise Refusal("CERTIFICATE_MISMATCH")
        raise CertifiedUnbounded(cert)
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
    """Replay a convex-hull certificate; ordinary malformed inputs return False."""
    try:
        if (type(generators) not in (tuple, list) or type(target) not in (tuple, list)
                or any(type(g) not in (tuple, list) for g in generators)):
            return False
        generators, target, costs, matrix, rhs = standard_form(generators, target, max_entries=max_entries)
        k, m = len(generators), len(target)
        if (type(cert) is not DefectCertificate or not _exact_vector(cert.coefficients, k)
                or not _exact_vector(cert.residual, m) or not _exact_vector(cert.witness, m)
                or type(cert.offset) is not Q or type(cert.defect) is not Q
                or not verify_standard(costs, matrix, rhs, cert.lp)):
            return False
        residual = tuple(sum((g[i] * c for g, c in zip(generators, cert.coefficients)), Q(0)) - target[i]
                         for i in range(m))
        return (cert.lp.primal[:k] == cert.coefficients
                and cert.lp.dual[:m] == cert.witness and cert.lp.dual[m] == cert.offset
                and cert.lp.value == cert.defect
                and residual == cert.residual
                and all(c >= 0 for c in cert.coefficients) and sum(cert.coefficients) == 1
                and all(abs(y) <= 1 for y in cert.witness)
                and all(dot(g, cert.witness) + cert.offset <= 0 for g in generators)
                and dot(target, cert.witness) + cert.offset == cert.defect == sum(map(abs, residual)))
    except (TypeError, ValueError, AttributeError):
        return False


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


def _contextual_matrix(model, *, require_compatible, max_assignments=1048576, max_entries=2000000):
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
    for a, ca in enumerate(contexts if require_compatible else ()):
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


def contextual_matrix(model, *, max_assignments=1048576, max_entries=2000000):
    """Columns from declared measurements; exact overlap compatibility required."""
    return _contextual_matrix(model, require_compatible=True,
                              max_assignments=max_assignments, max_entries=max_entries)


def observed_matrix(model, *, max_assignments=1048576, max_entries=2000000):
    """Columns from declared measurements and the unchanged observed vector.

    Rows must be exact nonnegative distributions. Overlap discrepancies are
    retained, as finite sampling can produce them. This is not an empirical
    model validity check or a projection of observations to compatible data.
    """
    return _contextual_matrix(model, require_compatible=False,
                              max_assignments=max_assignments, max_entries=max_entries)


@dataclass(frozen=True)
class ContextualityResult:
    kind: str
    assignments: tuple
    certificate: DefectCertificate


def evaluate(model, *, max_pivots=10000, max_assignments=1048576, max_entries=2000000):
    """Evaluate an exact compatible empirical model; signalling tables refuse.

    For uncertain observations use evaluate_observed and a justified raw l1
    radius. A positive raw distance alone is not a claim about the true model.
    """
    assignments, columns, target = contextual_matrix(model, max_assignments=max_assignments, max_entries=max_entries)
    certificate = solve_l1(columns, target, max_pivots=max_pivots, max_entries=max_entries)
    return ContextualityResult("GlobalSection" if certificate.defect == 0 else "Obstructed", assignments, certificate)


@dataclass(frozen=True)
class ObservationBound:
    """Conditional lower bound for every true table within the supplied radius.

    This record neither establishes statistical coverage nor classifies the
    unknown true table. The certificate's optimum concerns the observed vector.
    """
    assignments: tuple
    observed: tuple
    radius: Q
    certificate: DefectCertificate
    guaranteed_margin: Q


def verify_observed(model, uncertainty_radius, result, *, max_assignments=1048576, max_entries=2000000):
    """Replay the certificate and bind the bound to the original observations/radius."""
    try:
        radius = rational(uncertainty_radius)
        assignments, columns, observed = observed_matrix(model, max_assignments=max_assignments,
                                                         max_entries=max_entries)
    except Refusal:
        return False
    if (radius < 0 or type(result) is not ObservationBound or type(result.radius) is not Q
            or type(result.guaranteed_margin) is not Q or type(result.observed) is not tuple
            or any(type(x) is not Q for x in result.observed)
            or type(result.assignments) is not tuple
            or any(type(row) is not tuple or any(type(x) is not int for x in row)
                   for row in result.assignments)
            or type(result.certificate) is not DefectCertificate):
        return False
    try:
        valid = verify_defect(columns, observed, result.certificate, max_entries=max_entries)
    except (AttributeError, TypeError, ValueError):
        return False
    if not valid:
        return False
    c = result.certificate
    return (result.assignments == assignments and result.observed == observed and result.radius == radius
            and result.guaranteed_margin == max(Q(0), dot(observed, c.witness) + c.offset - radius))


def evaluate_observed(model, uncertainty_radius, *, max_pivots=10000,
                      max_assignments=1048576, max_entries=2000000):
    """Retain possibly signalling observations and return a conditional witness bound.

    The nonnegative exact radius bounds the total raw l1 observation error,
    summed over all context/outcome entries. Justifying its coverage is the
    caller's obligation. No normalization or no-signalling fit is performed.
    The lower-level solve_l1 also accepts targets that are not distributions.
    """
    radius = rational(uncertainty_radius)
    if radius < 0:
        raise Refusal("INVALID_RADIUS")
    assignments, columns, observed = observed_matrix(model, max_assignments=max_assignments,
                                                     max_entries=max_entries)
    certificate = solve_l1(columns, observed, max_pivots=max_pivots, max_entries=max_entries)
    result = ObservationBound(assignments, observed, radius, certificate,
                              max(Q(0), dot(observed, certificate.witness) + certificate.offset - radius))
    if not verify_observed(model, radius, result, max_assignments=max_assignments, max_entries=max_entries):
        raise Refusal("CERTIFICATE_MISMATCH")
    return result
