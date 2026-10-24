"""Independent exhaustive checks and explicit limits of the companion bridge."""
import hashlib
import itertools
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "code"))
import epistemic_kernel as k
import future_observation as f


def test_all_256_bit_pair_updates_obey_word_criterion():
    states = tuple(k.K2)
    report = {s: s[0] for s in states}
    for values in itertools.product(states, repeat=4):
        updates = {"u": dict(zip(states, values))}
        one_step = f.preserves_fibers(report, updates)
        assert f.reports_agree_through(report, updates, 1) == one_step
        assert f.reports_agree_through(report, updates, 4) == one_step


def test_two_updates_and_all_words_through_six():
    states = tuple(k.K2)
    report = {s: s[0] for s in states}
    updates = {"flip_hidden": {s: (s[0], 1 - s[1]) for s in states},
               "flip_report": {s: (1 - s[0], s[1]) for s in states}}
    assert f.preserves_fibers(report, updates)
    assert f.reports_agree_through(report, updates, 6)
    # Same initial fiber, but a different full-state task remains unrecoverable.
    assert report[(0, 0)] == report[(0, 1)]
    assert f.run_word(updates, ("flip_hidden",), (0, 0)) != f.run_word(updates, ("flip_hidden",), (0, 1))


def test_swap_refutes_privacy_without_preservation():
    report = {s: s[0] for s in k.K2}
    updates = {"swap": {s: k.swap(s) for s in k.K2}}
    assert f.reports_agree_through(report, updates, 0)
    assert not f.preserves_fibers(report, updates)
    assert not f.reports_agree_through(report, updates, 1)


@pytest.mark.parametrize("updates", [{"u": {}}, {"u": {0: 2, 1: 1}}])
def test_undeclared_update_states_refused(updates):
    with pytest.raises(ValueError, match="endomorphisms"):
        f.preserves_fibers({0: 0, 1: 0}, updates)


@pytest.mark.parametrize("depth", [-1, 0.5])
def test_invalid_depth_refused(depth):
    with pytest.raises(ValueError, match="nonnegative integer"):
        f.reports_agree_through({0: 0}, {}, depth)


def test_provenance_acceptance_does_not_certify_action_safety():
    receipt = k.verify_three_role("a", "p", "e", "a", "r", "certificate", ["r"])
    proposed_action = 1
    safe_actions = {0}
    assert receipt["authority_effect"] == "None"
    assert proposed_action not in safe_actions


@pytest.mark.parametrize("basis", ["unknown", "", "CERTIFICATE"])
def test_unknown_basis_is_a_typed_refusal(basis):
    with pytest.raises(k.Refusal) as exc:
        k.verify_three_role("a", "p", "e", "a", "r", basis, ["r"])
    assert exc.value.kind == "MALFORMED"


def test_verbatim_source_custody():
    record = json.loads((ROOT / "docs/source_lineage.json").read_text(encoding="utf-8"))
    for target, source in record["verbatim_archival_documents"].items():
        assert hashlib.sha256((ROOT / target).read_bytes()).hexdigest() == record["precursor_files_sha256"][source]
    for module in ("ResultI", "ResultII", "ResultIII", "ResultIV"):
        path = f"lean4/{module}.lean"
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == record["precursor_files_sha256"][path]


def test_future_word_order_is_left_to_right():
    updates = {"zero": {0: 0, 1: 0}, "flip": {0: 1, 1: 0}}
    assert f.run_word(updates, ("zero", "flip"), 1) == 1
    assert f.run_word(updates, ("flip", "zero"), 1) == 0
