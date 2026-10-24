from fractions import Fraction

import pytest

from chained_quantum import Q3, U, certificates, quantum_table, replay, verify_certificate


def test_full_quantum_certificate():
    receipt = replay()
    assert receipt['ratio'] == 4
    assert receipt['quantum_Born_cells'] == 36


def test_exact_radical_order():
    assert (U-Fraction(2, 3)).sign() == 1
    assert (U-1).sign() == -1
    assert (U*U-Fraction(3, 4)).sign() == 0
    assert (-U+Fraction(2, 3)).sign() == -1


def test_signed_certificate_mutation_rejected():
    p, q, gamma, y, z = certificates(U)
    q[0] += Fraction(1, 100)
    with pytest.raises(ValueError, match='normalization'):
        verify_certificate(p, q, gamma, y, z)


def test_unscored_context_mutation_rejected():
    p, q, gamma, y, z = certificates(U)
    # (x,y)=(0,1) is absent from the chained score but present in the model.
    p[4] += Fraction(1, 100)
    with pytest.raises(ValueError, match='projection'):
        verify_certificate(p, q, gamma, y, z)


def test_cover_mutation_rejected():
    p, q, gamma, y, z = certificates(U)
    y = [0]*36
    with pytest.raises(ValueError, match='cover'):
        verify_certificate(p, q, gamma, y, z)


def test_boundary_and_born_rows():
    cf, neg = verify_certificate(*certificates(Fraction(2, 3)))
    assert cf == neg == Q3()
    assert quantum_table() == certificates(U)[0]
