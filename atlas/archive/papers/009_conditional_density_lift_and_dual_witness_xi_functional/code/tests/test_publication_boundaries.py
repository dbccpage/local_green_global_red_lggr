"""Counterexamples separating exact certificates from numerical approximations."""
from fractions import Fraction

import numpy as np
import pytest

from mod_conditional_density_lift_core import ConditionalDensityLift, ZeroObstructionCertificate


def test_zero_certificate_cannot_be_reused_for_an_unrelated_cochain():
    certificate = ZeroObstructionCertificate(np.array([[1.0]]), np.array([1.0]), np.array([1.0]))
    with pytest.raises(ValueError, match="does not match"):
        ConditionalDensityLift.compute_xi([2.0], [1.0], zero_certificate=certificate)


def test_approximate_zero_is_not_an_exact_certificate():
    certificate = ZeroObstructionCertificate(
        np.array([[1.0]]), np.array([1.0]), np.array([1.0 + 2**-40])
    )
    assert not certificate.verify()


def test_unrepresentable_mass_is_not_silently_clipped():
    with pytest.raises(FloatingPointError, match="mass"):
        ConditionalDensityLift.lift([1e308, 1e308])


@pytest.mark.parametrize("value", [True, 1.5, "2", Fraction(3, 2)])
def test_exact_integer_weight_inputs_are_not_coerced(value):
    with pytest.raises(TypeError, match="integer"):
        ConditionalDensityLift.normalized_abs_weights([value, 1])
