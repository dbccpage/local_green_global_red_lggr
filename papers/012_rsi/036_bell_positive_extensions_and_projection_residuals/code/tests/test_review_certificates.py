from fractions import Fraction as F
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from review_certificates import check_repair,check_negative,review
@pytest.fixture
def repair():
    p=review.isotropic(F(5,8));_,v,x=review.lp_repair_distance(p)
    _,_,(B,b)=review.lp_dual_repair(p)
    return p,v,x,B,b
def test_review_repair(repair):check_repair(*repair)
def test_review_changed_primal(repair):
    p,v,x,B,b=repair;x[0]+=F(1,100)
    with pytest.raises(ValueError,match='normalization'):check_repair(p,v,x,B,b)
def test_review_bad_dual(repair):
    p,v,x,B,b=repair
    with pytest.raises(ValueError,match='vertices'):check_repair(p,v,x,B,b-F(1,100))
def test_review_false_objective(repair):
    p,v,x,B,b=repair
    with pytest.raises(ValueError,match='objective'):check_repair(p,v+F(1,100),x,B,b)
def test_review_negative_and_mutation():
    p=review.isotropic(F(1));_,v,x=review.lp_negative_mass(p)
    _,_,(a,b)=review.lp_dual_negative_mass(p);check_negative(p,v,x,a,b);a[0]+=1
    with pytest.raises(ValueError,match='feasibility'):check_negative(p,v,x,a,b)
