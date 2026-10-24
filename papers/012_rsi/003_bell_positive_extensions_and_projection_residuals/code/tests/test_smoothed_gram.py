from fractions import Fraction as F
from itertools import product
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from smoothed_gram import profile, certificate, behavior, local_cell


@pytest.mark.parametrize("bad", [True, 0, 1, 2.0, -2])
def test_rejects_invalid_profile_parameter(bad):
    with pytest.raises(ValueError):
        profile(bad)


def test_complete_nine_setting_bound_exceeds_four():
    c = certificate(3)
    assert c["contexts"] == 81
    assert c["cf_lower"] == F(46,73)
    assert c["negative_mass_upper"] == F(8,73)
    assert c["ratio_lower"] == F(23,4)
    for x,y in product(range(9), repeat=2):
        cells = [behavior(c,x,y,a,b) for a,b in product((-1,1),repeat=2)]
        assert min(cells) >= 0 and sum(cells) == 1


def test_hidden_coordinate_reproduces_off_chain_cell():
    c = certificate(3)
    s = c["norm_square"]
    for a,b in product((-1,1), repeat=2):
        assert local_cell(c,0,4,a,b)/s-(1-s)/s/4 == behavior(c,0,4,a,b)


def test_cycle_wrap_is_frustrated_and_not_dropped():
    c = certificate(4)
    n, v = c["settings"], c["visibility"]
    assert behavior(c,0,n-1,1,1) == (1-v)/4
    assert behavior(c,n-1,n-1,1,1) == (1+v)/4
