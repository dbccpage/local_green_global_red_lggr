"""Exact finite CHSH distance certificates; no floating solver is trusted."""
from fractions import Fraction as Q
from itertools import product
ASSIGNMENTS=tuple(product((-1,1),repeat=4))
ROWS=tuple(product(range(2),range(2),(-1,1),(-1,1)))
def rational(v):
    if type(v) not in (int,Q):raise ValueError("exact integer/Fraction required")
    return Q(v)
def check(p,q,c,claimed,uncertainty=Q(0)):
    if (len(p),len(q),len(c))!=(16,16,16):raise ValueError("CHSH dimensions")
    p,q,c=tuple(map(rational,p)),tuple(map(rational,q)),tuple(map(rational,c))
    claimed,uncertainty=rational(claimed),rational(uncertainty)
    if uncertainty<0 or any(v<0 for v in p) or any(sum(p[4*j:4*j+4])!=1 for j in range(4)):raise ValueError("probability table or uncertainty")
    if any(v<0 for v in q) or sum(q)!=1:raise ValueError("positive normalized extension required")
    local=tuple(sum(w for l,w in zip(ASSIGNMENTS,q) if l[x]==a and l[2+y]==b) for x,y,a,b in ROWS)
    upper=sum(abs(a-b) for a,b in zip(p,local))/8
    # Dual unit ball for uniform-setting TV: 8 max |c_i| <= 1.
    if 8*max(map(abs,c))>1:raise ValueError("dual norm exceeds one")
    beta=max(sum(ci for ci,(x,y,a,b) in zip(c,ROWS) if l[x]==a and l[2+y]==b) for l in ASSIGNMENTS)
    lower=max(Q(0),sum(ci*pi for ci,pi in zip(c,p))-beta)
    if lower!=upper or upper!=claimed:raise ValueError("primal and dual bounds do not match claimed optimum")
    return {"distance":upper,"guaranteed_distance":max(Q(0),lower-uncertainty)}
def isotropic(v):
    v=rational(v)
    if not 0<=v<=1:raise ValueError("visibility outside [0,1]")
    p=tuple((1+v*a*b*(-1)**(x*y))/4 for x,y,a,b in ROWS)
    w=min(v,Q(1,2))
    q=tuple((1+w*(a0*(b0+b1)+a1*(b0-b1)))/16 for a0,a1,b0,b1 in ASSIGNMENTS)
    c=tuple(Q(a*b*(-1)**(x*y),8) if v>Q(1,2) else Q(0) for x,y,a,b in ROWS)
    return p,q,c,max(Q(0),(2*v-1)/4)
