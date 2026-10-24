"""Exact Q(sqrt(3)) certificates for a full 3x3 quantum Bell counterexample.

The model is enumerated independently of Lean and the earlier binary-settings
helpers. SciPy is only an optional numerical comparison, not the certificate.
"""
from dataclasses import dataclass
from fractions import Fraction as F
import itertools
import json
from math import sqrt


@dataclass(frozen=True)
class Q3:
    a: F = F(0)
    b: F = F(0)

    def __post_init__(self):
        object.__setattr__(self, "a", F(self.a))
        object.__setattr__(self, "b", F(self.b))

    @staticmethod
    def of(x):
        return x if isinstance(x, Q3) else Q3(x)

    def __add__(self, other):
        o = self.of(other)
        return Q3(self.a+o.a, self.b+o.b)

    __radd__ = __add__

    def __neg__(self):
        return Q3(-self.a, -self.b)

    def __sub__(self, other):
        return self + -self.of(other)

    def __rsub__(self, other):
        return self.of(other) + -self

    def __mul__(self, other):
        o = self.of(other)
        return Q3(self.a*o.a+3*self.b*o.b, self.a*o.b+self.b*o.a)

    __rmul__ = __mul__

    def __truediv__(self, other):
        o = self.of(other)
        d = o.a*o.a-3*o.b*o.b
        if d == 0:
            raise ZeroDivisionError("zero quadratic-field denominator")
        return self*Q3(o.a/d, -o.b/d)

    def sign(self):
        s = lambda x: (x > 0)-(x < 0)
        if not self.a:
            return s(self.b)
        if not self.b or s(self.a) == s(self.b):
            return s(self.a)
        return s(self.a)*s(self.a*self.a-3*self.b*self.b)

    def __float__(self):
        return float(self.a)+float(self.b)*sqrt(3)

    def text(self):
        return f"{self.a} + ({self.b})*sqrt(3)"


C = ((1, 0, -1), (1, 1, 0), (0, 1, 1))
CELLS = list(itertools.product(range(3), range(3), range(2), range(2)))
ASSIGNMENTS = [tuple((g >> k) & 1 for k in range(6)) for g in range(64)]
A = [[int(g[x] == a and g[3+y] == b) for g in ASSIGNMENTS] for x, y, a, b in CELLS]
COEFF = [C[x][y]*(-1)**(a+b) for x, y, a, b in CELLS]
K = [sum(COEFF[i]*A[i][g] for i in range(36)) for g in range(64)]
U = Q3(0, F(1, 2))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def certificates(v):
    v = Q3.of(v)
    p = [(1+v*c)/4 for c in COEFF]
    q = [(2+3*v)/48 if k == 4 else (2-3*v)/48 if k == -4 else Q3() for k in K]
    gamma = [(1-v)/4 if k == 4 else Q3() for k in K]
    y = [(abs(c)-c)//2 for c in COEFF]
    z = [F(c, 8) for c in COEFF]
    return p, q, gamma, y, z


def verify_certificate(p, q, gamma, y, z):
    require(tuple(map(len, (p, q, gamma, y, z))) == (36, 64, 64, 36, 36), "shape")
    require(all(Q3.of(x).sign() >= 0 for x in p), "probabilities")
    require(sum(q) == Q3(1), "signed normalization")
    require(all(Q3.of(x).sign() >= 0 for x in gamma), "packing nonnegativity")
    require(all(Q3.of(x).sign() >= 0 for x in y), "CF dual nonnegativity")
    for i in range(36):
        require(sum(q[g]*A[i][g] for g in range(64)) == p[i], "signed projection")
        require((p[i]-sum(gamma[g]*A[i][g] for g in range(64))).sign() >= 0, "packing domination")
    for g in range(64):
        require((sum(Q3.of(y[i])*A[i][g] for i in range(36))-1).sign() >= 0, "CF dual cover")
        d = sum(Q3.of(z[i])*A[i][g] for i in range(36))-F(1, 2)
        require(d.sign() <= 0 and (d+1).sign() >= 0, "negative-mass dual interval")
    require(sum(Q3.of(y[i])*p[i] for i in range(36)) == sum(gamma), "CF gap")
    negative = sum((-x if x.sign() < 0 else Q3()) for x in q)
    require(sum(Q3.of(z[i])*p[i] for i in range(36))-F(1, 2) == negative, "negative-mass gap")
    for x, y in itertools.product(range(3), repeat=2):
        require(sum(p[12*x+4*y+a] for a in range(4)) == Q3(1), "context normalization")
        for a in range(2):
            require(sum(p[12*x+4*y+2*a+b] for b in range(2)) == Q3(F(1, 2)), "Alice marginal")
        for b in range(2):
            require(sum(p[12*x+4*y+2*a+b] for a in range(2)) == Q3(F(1, 2)), "Bob marginal")
    return Q3(1)-sum(gamma), negative


def matmul(a, b):
    return [[sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))]
            for i in range(len(a))]


def kron(a, b):
    return [[a[i//len(b)][j//len(b)]*b[i % len(b)][j % len(b)]
             for j in range(len(a)*len(b))] for i in range(len(a)*len(b))]


def quantum_table():
    # |Phi+><Phi+| is a normalized, symmetric projector, hence a density matrix.
    rho = [[Q3(F(1, 2)) if i in (0, 3) and j in (0, 3) else Q3()
            for j in range(4)] for i in range(4)]
    require(rho == list(map(list, zip(*rho))) and matmul(rho, rho) == rho
            and sum(rho[i][i] for i in range(4)) == Q3(1), "density")
    directions = [[(Q3(1), Q3()), (Q3(F(1, 2)), U), (Q3(-F(1, 2)), U)],
                  [(U, Q3(F(1, 2))), (Q3(), Q3(1)), (-U, Q3(F(1, 2)))]]
    effects = {}
    identity = [[Q3(int(i == j)) for j in range(2)] for i in range(2)]
    for side, setting in itertools.product(range(2), range(3)):
        z, x = directions[side][setting]
        observable = [[z, x], [x, -z]]
        require(matmul(observable, observable) == identity, "observable square")
        for a in range(2):
            effect = [[(identity[i][j]+(-1)**a*observable[i][j])/2 for j in range(2)]
                      for i in range(2)]
            require(effect == list(map(list, zip(*effect))) and matmul(effect, effect) == effect, "positive projector")
            effects[side, setting, a] = effect
        require([[effects[side, setting, 0][i][j]+effects[side, setting, 1][i][j]
                  for j in range(2)] for i in range(2)] == identity, "POVM completeness")
    table = []
    for x, y, a, b in CELLS:
        measured = matmul(rho, kron(effects[0, x, a], effects[1, y, b]))
        table.append(sum(measured[i][i] for i in range(4)))
    return table


def replay():
    parameters = [F(2, 3), F(3, 4), F(4, 5), F(7, 8), F(1), U]
    for v in parameters:
        cf, neg = verify_certificate(*certificates(v))
        require(cf == 4*neg, "factor four")
    p, q, gamma, y, z = certificates(U)
    require(quantum_table() == p, "all nine Born contexts")
    cf, neg = verify_certificate(p, q, gamma, y, z)
    require((cf-2*neg).sign() > 0, "strict quantum separation")
    import numpy as np
    from scipy.optimize import linprog
    matrix = np.array(A, dtype=float)
    values = np.array(list(map(float, p)))
    lp_cf = linprog(-np.ones(64), A_ub=matrix, b_ub=values, bounds=(0, None))
    lp_neg = linprog(np.r_[np.zeros(64), np.ones(64)], A_eq=np.c_[matrix, -matrix],
                     b_eq=values, bounds=(0, None))
    require(lp_cf.success and lp_neg.success, "numerical LP success")
    error = max(abs(1+lp_cf.fun-float(cf)), abs(lp_neg.fun-float(neg)))
    require(error < 1e-12, "numerical LP comparison")
    return dict(exact_parameter_cases=len(parameters), quantum_Born_cells=36,
                deterministic_assignments=64, exact_field="Q(sqrt(3))",
                CF=cf.text(), N_min=neg.text(), CF_minus_2N=(cf-2*neg).text(),
                ratio=4, numerical_LP_error=error,
                scope="Full nine-context two-party, three-setting quantum counterexample; no universal coefficient-four upper bound claimed")


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))

