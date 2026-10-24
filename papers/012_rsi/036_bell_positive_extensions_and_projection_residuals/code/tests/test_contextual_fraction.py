import copy
import json
from fractions import Fraction as F
from pathlib import Path
import pytest
from contextual_fraction import replay, verify_case

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def counterexample():
    data = json.loads((ROOT/"data/contextual_fraction_certificates.json").read_text())
    return copy.deepcopy(next(c for c in data["cases"]
                              if c["name"] == "GHZ rnd2 (k=4, den=12)"))


def test_counterexample(counterexample):
    cf, neg = verify_case(counterexample)
    assert (cf, neg, cf-2*neg) == (F(19,64), F(25,256), F(13,128))


def test_all_certificate_cases():
    assert replay() == {"equal": 74, "less": 3, "greater": 1}


@pytest.mark.parametrize("field,mutation", [
    ("cf_primal", "increase"),
    ("cf_dual", "zero"),
    ("n_primal", "increase"),
    ("n_dual", "zero"),
    ("p", "short"),
    ("p", "boolean"),
    ("cf", "objective"),
])
def test_corrupt_certificate_rejected(counterexample, field, mutation):
    if mutation == "increase":
        counterexample[field][0] = str(F(counterexample[field][0])+1)
    elif mutation == "zero":
        counterexample[field] = ["0"]*len(counterexample[field])
    elif mutation == "short":
        counterexample[field].pop()
    elif mutation == "boolean":
        counterexample[field][0] = True
    else:
        counterexample[field] = "0"
    with pytest.raises(ValueError):
        verify_case(counterexample)

