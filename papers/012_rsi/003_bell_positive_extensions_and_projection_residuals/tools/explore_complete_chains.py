"""Optional floating-point LP exploration for the table in Section 8.5.

These values are not exact certificates. The separate rational 5x5 example
is checked by code/chain_comparisons.py without invoking an optimizer.
"""
import argparse
import itertools
import json

import numpy as np
from scipy.optimize import linprog


def explore(n):
    assignments = np.array(list(itertools.product([-1, 1], repeat=2*n)))
    rows, probabilities = [], []
    for x, y in itertools.product(range(n), repeat=2):
        correlation = np.cos((x-y-.5)*np.pi/n)
        for a, b in itertools.product([-1, 1], repeat=2):
            rows.append(((assignments[:, x] == a) &
                         (assignments[:, n+y] == b)).astype(float))
            probabilities.append((1+a*b*correlation)/4)
    matrix, point = np.array(rows), np.array(probabilities)
    count = len(assignments)
    packing = linprog(-np.ones(count), A_ub=matrix, b_ub=point, bounds=(0, None))
    signed = linprog(np.r_[np.zeros(count), np.ones(count)],
                     A_eq=np.c_[matrix, -matrix], b_eq=point, bounds=(0, None))
    if not packing.success or not signed.success:
        raise RuntimeError((packing.message, signed.message))
    cf, negative = 1+packing.fun, signed.fun
    return dict(settings_per_party=n, CF=cf, N_min=negative,
                complete_ratio=cf/negative, cycle_ratio=2*n-2,
                scope='Floating-point LP exploration; no exact certificate')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--max-settings', type=int, choices=range(2, 8), default=7)
    args = parser.parse_args()
    for n in range(2, args.max_settings+1):
        print(json.dumps(explore(n)), flush=True)
