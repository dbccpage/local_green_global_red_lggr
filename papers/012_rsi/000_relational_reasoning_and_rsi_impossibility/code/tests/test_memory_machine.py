from itertools import product

import pytest
from memory_machine import append_checked, compatible, encode, gated_overwrite, recall_checked, swap

PAIRS = tuple(product((False, True), repeat=2))


def test_every_small_archive_update_and_fresh_recall():
    for n in range(4):
        for rows in product(PAIRS, repeat=n):
            for label, candidate in PAIRS:
                recalled = recall_checked(rows, label, candidate)
                if recalled is not None:
                    assert (label, recalled) in rows
                    assert all(p[1] == recalled for p in rows if p[0] == label)
            for fresh in PAIRS:
                next_rows = append_checked(rows, (fresh,))
                if next_rows is not None:
                    assert next_rows[:n] == rows
                    assert compatible(next_rows)
                else:
                    assert any(p[0] == q[0] and p[1] != q[1] for p in rows+(fresh,) for q in rows+(fresh,))


def test_contradiction_and_stale_recall_refuse():
    old = ((False, False),)
    assert append_checked(old, ((False, True),)) is None
    assert old == ((False, False),)
    assert recall_checked(old+((False, True),), False, False) is None
    assert recall_checked((), False, False) is None


def test_encoding_and_updates_preserve_future_readout():
    for state in PAIRS:
        for n in range(7):
            for word in product((False, True), repeat=n):
                real, memory = state, encode(state)
                for action in word:
                    real, memory = swap(real, action), swap(memory, action)
                assert memory[1] == real[0]


def test_first_bit_counterexample():
    x, y = (False, False), (False, True)
    assert x[0] == y[0]
    assert swap(x, True)[0] != swap(y, True)[0]


def test_gate_preserves_invariant_for_all_four_step_words():
    for state in PAIRS[:-1]:
        for word in product(PAIRS, repeat=4):
            actual = state
            for candidate in word:
                actual = gated_overwrite(actual, candidate)
                assert actual != (True, True)


def test_gate_needs_a_safe_initial_state():
    assert gated_overwrite((True, True), (True, True)) == (True, True)
    assert gated_overwrite((False, False), (True, True)) == (False, False)


def test_exact_input_types():
    for bad in ((0, False), (False, 1), [False, False], (False,)):
        with pytest.raises(ValueError):
            encode(bad)
    with pytest.raises(ValueError):
        append_checked([], ())
    with pytest.raises(ValueError):
        swap((False, False), 1)
