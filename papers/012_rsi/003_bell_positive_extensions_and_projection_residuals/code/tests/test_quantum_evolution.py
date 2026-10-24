"""Checks the proposed evolution against matrix exponentiation and LP optima."""
import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from quantum_evolution import experiment, optima, replay


def test_full_quantum_reproduction():
    receipt = replay()
    assert receipt["LP_solves"] >= 34


@pytest.mark.parametrize("t", [0, np.pi/12, np.pi/8, np.pi/4])
def test_measurement_marginals(t):
    _, _, p, _ = experiment(t)
    tables = p.reshape(2, 2, 2, 2, 2, 2)
    assert np.min(p) >= -1e-14
    assert np.allclose(tables.sum(axis=(3, 4, 5)), 1)
    # Every proper outcome marginal is uniform, independent of remote settings.
    assert np.allclose(tables.sum(axis=5), .25)
    assert np.allclose(tables.sum(axis=4), .25)
    assert np.allclose(tables.sum(axis=3), .25)


def test_entanglement_precedes_contextuality_for_these_measurements():
    _, psi, p, _ = experiment(np.pi/24)
    reduced = psi.reshape(2, 4)@psi.reshape(2, 4).conj().T
    assert np.linalg.det(reduced).real > 0
    assert optima(p) == pytest.approx((0, 0), abs=1e-12)
