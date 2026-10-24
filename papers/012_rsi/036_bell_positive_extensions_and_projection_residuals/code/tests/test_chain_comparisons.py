import copy
import pytest
from chain_comparisons import load_certificate,verify_five,cycle_replay,grid_replay

def test_complete_quantum_certificate():
    assert verify_five(load_certificate())["ratio"] == "698/167"

def test_reject_changed_signed_projection():
    c=copy.deepcopy(load_certificate());c["q"]["0"]="0"
    with pytest.raises(ValueError):verify_five(c)

def test_reject_nonquantum_direction():
    c=copy.deepcopy(load_certificate());c["directions"][0][0][0]="2"
    with pytest.raises(ValueError,match="unit direction"):verify_five(c)

def test_reject_bad_dual():
    c=copy.deepcopy(load_certificate());c["cf_dual"]={}
    with pytest.raises(ValueError,match="cover"):verify_five(c)

def test_cycle_reconstruction_and_large_grid():
    assert cycle_replay(4)["ratio"]==6
    assert grid_replay(1000000)>2.82
