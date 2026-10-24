from fractions import Fraction as Q
from itertools import product
import pytest
from bell_certificates import check,isotropic,ASSIGNMENTS,ROWS

@pytest.mark.parametrize("v",[Q(i,8) for i in range(9)])
def test_exact_primal_dual_certificates(v):
    p,q,c,r=isotropic(v)
    assert check(p,q,c,r)["distance"]==max(Q(0),(2*v-1)/4)

def test_exhaustive_local_vertices():
    for l in ASSIGNMENTS:
        score=sum(a*b*(-1)**(x*y) for x,y,a,b in ROWS if l[x]==a and l[2+y]==b)
        assert abs(score)==2

def test_signed_extension_is_not_positive_certificate():
    p,q,c,r=isotropic(Q(1));bad=tuple(Q(1+(a0*(b0+b1)+a1*(b0-b1)),16) for a0,a1,b0,b1 in ASSIGNMENTS)
    with pytest.raises(ValueError,match="positive"):check(p,bad,c,r)

def test_reject_scaled_witness():
    p,q,c,r=isotropic(Q(3,4))
    with pytest.raises(ValueError,match="norm"):check(p,q,[2*x for x in c],r)

def test_reject_forged_optimum():
    p,q,c,r=isotropic(Q(3,4))
    with pytest.raises(ValueError,match="match"):check(p,q,c,r+Q(1,100))

def test_reject_wrong_feasible_extension():
    p,q,c,r=isotropic(Q(3,4))
    with pytest.raises(ValueError,match="match"):check(p,[Q(1,16)]*16,c,r)

def test_uncertainty_can_explain_all_of_margin():
    p,q,c,r=isotropic(Q(27,50))
    assert r==Q(1,50)
    assert check(p,q,c,r,Q(1,50))["guaranteed_distance"]==0

def test_uncertainty_retains_only_certified_remainder():
    p,q,c,r=isotropic(Q(3,4))
    assert check(p,q,c,r,Q(1,16))["guaranteed_distance"]==Q(1,16)

@pytest.mark.parametrize("bad",[True,0.5,"1/2"])
def test_inexact_or_ambiguous_values_rejected(bad):
    with pytest.raises(ValueError):isotropic(bad)

def test_negative_uncertainty_rejected():
    with pytest.raises(ValueError):check(*isotropic(Q(3,4)),uncertainty=-1)

def test_context_normalization_is_checked():
    p,q,c,r=isotropic(Q(3,4));p=list(p);p[0]+=Q(1,100)
    with pytest.raises(ValueError,match="probability"):check(p,q,c,r)
