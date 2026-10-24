"""Independent matrix-exponential and LP replay of the GHZ evolution.

Floating-point consistency evidence, separate from the real-number Lean proofs.
All probabilities are formed from tensor-product projectors, not the line formula.
"""
import itertools
import json
from math import asin, pi, sin, sqrt

import numpy as np
from scipy.linalg import expm
from scipy.optimize import linprog

from contextual_fraction import incidence


def experiment(t):
    """H = i(|000><111| - |111><000|), hbar = coupling = 1."""
    h = np.zeros((8, 8), dtype=complex)
    h[0, 7], h[7, 0] = 1j, -1j
    unitary = expm(-1j*t*h)
    psi = unitary[:, 0]
    x = np.array([[0, 1], [1, 0]], dtype=complex)
    y = np.array([[0, -1j], [1j, 0]], dtype=complex)
    probabilities = []
    coefficients = []
    for settings in itertools.product(range(2), repeat=3):
        chi = -1 if sum(settings) == 0 else 1 if sum(settings) == 2 else 0
        for outcomes in itertools.product(range(2), repeat=3):
            effects = [(np.eye(2)+(-1)**a*(x if s == 0 else y))/2
                       for s, a in zip(settings, outcomes)]
            projector = np.kron(np.kron(effects[0], effects[1]), effects[2])
            probabilities.append(float(np.vdot(psi, projector@psi).real))
            coefficients.append(chi*(-1)**sum(outcomes))
    return unitary, psi, np.array(probabilities), np.array(coefficients)


def optima(p):
    a = np.array(incidence(3)[3], dtype=float)
    cf = linprog(-np.ones(64), A_ub=a, b_ub=p, bounds=(0, None), method="highs")
    neg = linprog(np.r_[np.zeros(64), np.ones(64)], A_eq=np.c_[a, -a],
                  b_eq=p, bounds=(0, None), method="highs")
    if not cf.success or not neg.success:
        raise ValueError("Independent LP replay failed")
    return 1+cf.fun, neg.fun


def replay():
    times = sorted(set([0, pi/12, pi/4, *np.linspace(0, pi/4, 17)]))
    max_born_error = max_optimum_error = max_unitary_error = 0.0
    for t in times:
        u, psi, p, coeff = experiment(t)
        exact_state = np.zeros(8, dtype=complex)
        exact_state[0], exact_state[7] = np.cos(t), -np.sin(t)
        if not np.allclose(psi, exact_state, atol=2e-14, rtol=0):
            raise ValueError("Hamiltonian trajectory differs")
        max_unitary_error = max(max_unitary_error, float(np.max(np.abs(u.conj().T@u-np.eye(8)))))
        max_born_error = max(max_born_error, float(np.max(np.abs(p-(1+sin(2*t)*coeff)/8))))
        cf, neg = optima(p)
        expected = max(0, 2*sin(2*t)-1)
        max_optimum_error = max(max_optimum_error, abs(cf-expected), abs(2*neg-expected))
    for eta in [0, .1, .5, 1, 1.9]:
        start = asin((2+eta)/4)/2
        for t in [start-1e-5, start, start+1e-5]:
            _, _, p, coeff = experiment(t)
            margin = float(coeff@p)-2-eta
            if abs(t-start) < 1e-10:
                if abs(margin) > 2e-14:
                    raise ValueError("Noisy boundary is not exact")
            elif (margin > 0) != (t > start):
                raise ValueError("Noisy exit interval reversed")
    if max(max_born_error, max_optimum_error, max_unitary_error) > 2e-12:
        raise ValueError("Numerical reproduction exceeds tolerance")
    return dict(times=len(times), born_cells=64*len(times), LP_solves=2*len(times),
                noisy_boundary_checks=15, max_born_error=max_born_error,
                max_optimum_error=max_optimum_error, max_unitary_error=max_unitary_error,
                CHSH_CF_cap=sqrt(2)-1, CHSH_N_cap=(sqrt(2)-1)/2,
                Mermin_CF_endpoint=1, Mermin_N_endpoint=.5,
                scope="Numerical consistency of explicit matrix evolution and independent LP solves; not an experimental result")


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2))
