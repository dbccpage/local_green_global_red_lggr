from fractions import Fraction as F
from itertools import product
import json
import numpy as np
from scipy.optimize import linprog

# CHSH row order: x, y, a, b. Assignment order: a0, a1, b0, b1.
signs = (-1, 1)
assignments = list(product(signs, repeat=4))
rows = list(product(range(2), range(2), signs, signs))
K = [a0*(b0+b1)+a1*(b0-b1) for a0,a1,b0,b1 in assignments]
assert K.count(2) == K.count(-2) == 8
T = np.array([[int(l[x] == a and l[2+y] == b) for l in assignments]
              for x,y,a,b in rows], dtype=float)
coeff = np.array([a*b*(-1)**(x*y) for x,y,a,b in rows], dtype=float)
exact_rows = []
for v in (F(0), F(1,4), F(1,2), F(3,4), F(1)):
    q = [(1+v*k)/16 for k in K]
    p = [(1+v*a*b*(-1)**(x*y))/4 for x,y,a,b in rows]
    assert sum(q) == 1
    for i, (x,y,a,b) in enumerate(rows):
        assert sum(w for l,w in zip(assignments,q)
                   if l[x] == a and l[2+y] == b) == p[i]
    assert sum(F(int(c))*u for c,u in zip(coeff,p)) == 4*v
    assert sum(-w for w in q if w < 0) == max(F(0), v-F(1,2))
    if v <= F(1,2):
        assert all(w >= 0 for w in q)
    else:
        boundary = [(1+F(1,2)*a*b*(-1)**(x*y))/4 for x,y,a,b in rows]
        cost = sum(abs(u-w) for u,w in zip(p,boundary))/8
        assert cost == (2*v-1)/4
    exact_rows.append(str(v))

# Independent linear programs for behavioral distance and negative mass.
I = np.eye(16)
Aub = np.block([[-T,-I],[T,-I]])
Aeq = np.r_[np.ones(16), np.zeros(16)][None,:]
errors = []
for v in (0., .25, .5, .6, 1/np.sqrt(2), .75, 1.):
    p = (1+v*coeff)/4
    res = linprog(np.r_[np.zeros(16),np.ones(16)/8],
                  A_ub=Aub, b_ub=np.r_[-p,p],
                  A_eq=Aeq, b_eq=[1], bounds=(0,None), method='highs')
    assert res.success
    err = abs(res.fun-max(0.,(2*v-1)/4))
    errors.append(err)
    assert err < 1e-9
    Aneg = np.vstack([np.c_[T,-T],np.r_[np.ones(16),-np.ones(16)]])
    neg = linprog(np.r_[np.zeros(16),np.ones(16)],
                  A_eq=Aneg, b_eq=np.r_[p,1.],
                  bounds=(0,None), method='highs')
    assert neg.success
    err = abs(neg.fun-max(0.,v-.5))
    errors.append(err)
    assert err < 1e-9

X = np.array([[0,1],[1,0]], dtype=complex)
Y = np.array([[0,-1j],[1j,0]], dtype=complex)
Z = np.diag([1.,-1.]).astype(complex)
H = np.array([[1,1],[1,-1]], dtype=complex)/np.sqrt(2)
def trace_norm(a):
    return float(np.abs(np.linalg.eigvalsh(a)).sum())
def density(v):
    return np.outer(v, v.conj())
def kron3(a,b,c):
    return np.kron(np.kron(a,b),c)

# Independently evaluate state residuals and chosen optimal CHSH observables.
state_errors = []
for t in (.001, .07, .2, np.pi/8, np.pi/4):
    u,w = np.cos(t),np.sin(t)
    psi = np.array([u,0,0,-1j*w])
    rho = density(psi)
    reduced = np.diag([u*u,w*w])
    c = abs(np.sin(2*t))
    err = abs(trace_norm(rho-np.kron(reduced,reduced))-(c+c*c/2))
    state_errors.append(err)
    assert err < 1e-12
    schmidt = density(np.array([u,0,0,w], dtype=complex))
    b0,b1 = (Z+c*X)/np.sqrt(1+c*c),(Z-c*X)/np.sqrt(1+c*c)
    B = np.kron(Z,b0+b1)+np.kron(X,b0-b1)
    err = abs(np.trace(B@schmidt).real-2*np.sqrt(1+c*c))
    state_errors.append(err)
    assert err < 1e-12

# Three-party witness and classical control.
mermin_values = []
for xa,ya,xb,yb,xc,yc in product(signs,repeat=6):
    mermin_values.append(xa*xb*xc-xa*yb*yc-ya*xb*yc-ya*yb*xc)
assert set(mermin_values) == {-2,2}
ghz = np.zeros(8, dtype=complex)
ghz[0] = ghz[7] = 1/np.sqrt(2)
Bg = kron3(X,X,X)-kron3(X,Y,Y)-kron3(Y,X,Y)-kron3(Y,Y,X)
rhog = density(ghz)
classical = np.diag([.5,0,0,0,0,0,0,.5])
assert np.isclose(np.trace(Bg@rhog),4)
assert np.isclose(np.trace(Bg@classical),0)
assert np.isclose(trace_norm(rhog-np.eye(8)/8),7/4)
assert np.isclose(trace_norm(classical-np.eye(8)/8),3/2)

# The eight-context Q_1 table uses GHZ-minus and the opposite Mermin orientation.
ghz_minus = ghz.copy()
ghz_minus[7] *= -1
q_errors = []
for ctx in product((0, 1), repeat=3):
    chi = -1 if sum(ctx) == 0 else 1 if sum(ctx) == 2 else 0
    for out in product((0, 1), repeat=3):
        effects = [(np.eye(2)+(-1)**a*(X,Y)[x])/2 for x,a in zip(ctx,out)]
        actual = np.vdot(ghz_minus, kron3(*effects) @ ghz_minus).real
        expected = (1+chi*(-1)**sum(out))/8
        q_errors.append(abs(actual-expected))
assert max(q_errors) < 1e-12

# Eight-context repair normalization: weighted TV is the L1 table norm / 16.
from contextual_fraction import incidence
_, _, cells3, model3 = incidence(3)
T3 = np.array(model3, dtype=float)
I3 = np.eye(64)
c3 = np.array([(-1 if sum(ctx)==0 else 1 if sum(ctx)==2 else 0)*(-1)**sum(out)
               for ctx,out in cells3])
mermin_repair_errors = []
for v in (0., .375, .5, .625, .7, 1.):
    p3 = (1+v*c3)/8
    result = linprog(np.r_[np.zeros(64),np.ones(64)/16],
                     A_ub=np.block([[-T3,-I3],[T3,-I3]]), b_ub=np.r_[-p3,p3],
                     A_eq=np.r_[np.ones(64),np.zeros(64)][None,:], b_eq=[1],
                     bounds=(0,None), method='highs')
    assert result.success
    mermin_repair_errors.append(abs(result.fun-max(0.,2*v-1)/8))
assert max(mermin_repair_errors) < 1e-12

# Equal-population states with opposite future output probabilities.
plus = np.array([1,1],dtype=complex)/np.sqrt(2)
minus = np.array([1,-1],dtype=complex)/np.sqrt(2)
assert np.allclose(abs(plus)**2,abs(minus)**2)
assert np.isclose(abs((H@plus)[0])**2,1)
assert np.isclose(abs((H@minus)[0])**2,0)

# Exact fiber widths and a finite version of the recursion lower bound.
histories = list(product((0,1),repeat=2))
f = lambda h: F(h[0]+2*h[1])
for report in (0,1):
    values = [f(h) for h in histories if h[0] == report]
    lo,hi = min(values),max(values)
    assert (hi-lo)/2 == 1
    midpoint = (hi+lo)/2
    assert max(abs(z-midpoint) for z in values) == 1
    for guess in (F(k,4) for k in range(-8,21)):
        assert abs(guess-lo)+abs(guess-hi) >= hi-lo
# Observing both coordinates makes every fiber a singleton.
assert len(set(histories)) == len(histories)

print(json.dumps({
    'status':'passed',
    'exact_CHSH_parameters':exact_rows,
    'floating_LP_parameters':7,
    'max_LP_absolute_error':max(errors),
    'two_qubit_times_checked':5,
    'max_state_absolute_error':max(state_errors),
    'Mermin_assignments_checked':len(mermin_values),
    'Mermin_Q1_Born_cells_checked':len(q_errors),
    'Mermin_Q1_max_absolute_error':max(q_errors),
    'Mermin_repair_parameters_checked':len(mermin_repair_errors),
    'Mermin_repair_max_absolute_error':max(mermin_repair_errors),
    'phase_fiber_and_finite_inference_checks':'passed'
},indent=2))
