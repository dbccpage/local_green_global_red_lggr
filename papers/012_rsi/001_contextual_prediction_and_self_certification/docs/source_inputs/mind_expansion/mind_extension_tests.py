#!/usr/bin/env python3
"""Deterministic toy counterexamples; not tests of consciousness or actual LLMs.
Runs with the Python standard library alone. Optional numpy/sympy add checks.
"""
import itertools, json, math
from pathlib import Path

CHECKS=0

def check(condition, message):
    global CHECKS
    CHECKS += 1
    if not condition:
        raise AssertionError(message)

def ambiguous(states, report, target):
    fibers={}
    for state in states:
        fibers.setdefault(report(state), set()).add(target(state))
    return {str(key):sorted(values) for key,values in fibers.items() if len(values)>1}

# Small exact bivariate integer polynomial algebra (no symbolic dependency).
def add(p,q):
    out=p.copy()
    for key,val in q.items(): out[key]=out.get(key,0)+val
    return {k:v for k,v in out.items() if v}
def scale(p,n): return {k:n*v for k,v in p.items() if n*v}
def mul(p,q):
    out={}
    for (i,j),a in p.items():
        for (k,l),b in q.items():
            out[(i+k,j+l)]=out.get((i+k,j+l),0)+a*b
    return {k:v for k,v in out.items() if v}
def pi_poly(x,y):
    u=add(add(x,y),scale(mul(x,x),-1))
    return (u,mul(u,u))
def pi(x):
    u=x[0]+x[1]-x[0]*x[0]
    return (u,u*u)
def flow(t,x): return pi(tuple(math.exp(t)*a for a in x))
def defect(t,s):
    direct=flow(t+s,(1.,1.))
    split=flow(t,flow(s,(1.,1.)))
    return tuple(a-b for a,b in zip(direct,split))

def run():
    results={}
    states=list(itertools.product((0,1),repeat=2))
    xor=lambda s:s[0]^s[1]
    ra=lambda s:s[0]
    rb=lambda s:s[1]
    joint=lambda s:(ra(s),rb(s))
    duplicate=lambda s:(ra(s),ra(s))
    blind_a=ambiguous(states,ra,xor); blind_b=ambiguous(states,rb,xor)
    check(bool(blind_a),'First report must be insufficient')
    check(bool(blind_b),'Second report must be insufficient')
    check(not ambiguous(states,joint,xor),'Joint reports must suffice')
    check(bool(ambiguous(states,duplicate,xor)),'Duplicate does not help')
    results['distributed_xor']={'individual_report_ambiguities':[blind_a,blind_b],
        'joint_sufficient':True,'duplicate_sufficient':False,
        'scope':'Information complementarity only; no integration or phenomenology inference.'}

    hidden=(0,1)
    check(bool(ambiguous(hidden,lambda h:0,lambda h:h)),'Report is blind')
    check(not ambiguous(hidden,lambda h:(0,h),lambda h:h),'Retained state distinguishes')
    results['report_vs_whole_agent']={'report_sufficient':False,'report_plus_retained_state_sufficient':True,
        'scope':'Retained state is an abstract embodied-state coordinate, not an empirical model.'}

    first=lambda s:s[0]
    identity=lambda s:s
    swap=lambda s:(s[1],s[0])
    same_pairs=[(s,t) for s in states for t in states if first(s)==first(t)]
    check(all(first(identity(s))==first(identity(t)) for s,t in same_pairs),'Identity respects quotient')
    witnesses=[(s,t) for s,t in same_pairs if first(swap(s))!=first(swap(t))]
    check(bool(witnesses),'Swap destroys quotient')
    results['action_expansion']={'identity_respects_first_bit_quotient':True,
        'swap_respects_first_bit_quotient':False,'witness':witnesses[0]}

    m=(1,1); P=((-1,1),(-2,2))
    matvec=lambda M,x:tuple(sum(a*b for a,b in zip(row,x)) for row in M)
    check(pi(m)==m,'Base point lies on manifold')
    check(matvec(P,m)==(0,0),'P A n vanishes with A=I, n=m')
    # u_x=-1,u_y=1,u_xx=-2 at m. Since Du[m]=0,
    # Hessian of u^2 on (m,m) = 2*u*D2u[m,m] = -4.
    hessian=(-2,-4)
    tscale={(0,0):1,(1,0):1}; sscale={(0,0):1,(0,1):1}
    both=mul(tscale,sscale)
    direct=pi_poly(both,both)
    inner=pi_poly(sscale,sscale)
    split=pi_poly(mul(tscale,inner[0]),mul(tscale,inner[1]))
    exact=tuple(add(a,scale(b,-1)) for a,b in zip(direct,split))
    coeff=tuple(p.get((1,1),0) for p in exact)
    check(coeff==hessian,'Exact mixed defect coefficient equals curvature term')
    finite=[]
    for h in (0.01,0.003,0.001,0.0003):
        # Central mixed derivative is stable and second-order accurate.
        pp,pm,mp,mm=defect(h,h),defect(h,-h),defect(-h,h),defect(-h,-h)
        estimate=tuple((a-b-c+d)/(4*h*h) for a,b,c,d in zip(pp,pm,mp,mm))
        finite.append({'h':h,'coefficient':estimate,'max_abs_error':max(abs(a-b) for a,b in zip(estimate,hessian))})
    check(finite[-1]['max_abs_error']<1e-5,'Finite differences agree')
    sympy_result=None
    try:
        import sympy as sp
        t,s=sp.symbols('t s')
        def ps(x,y):
            u=x+y-x*x
            return (u,u*u)
        d=ps(sp.exp(t+s),sp.exp(t+s)); inn=ps(sp.exp(s),sp.exp(s))
        comp=ps(sp.exp(t)*inn[0],sp.exp(t)*inn[1])
        sympy_result=[int(sp.diff(a-b,t,s).subs({t:0,s:0})) for a,b in zip(d,comp)]
        check(sympy_result==list(hessian),'Symbolic exponential mixed derivative agrees')
    except ImportError: pass
    results['nonlinear_retraction']={'P':P,'a':m,'n':m,'v':(0,0),'P_A_n':matvec(P,m),
        'hessian_a_n':hessian,'exact_mixed_coefficient':coeff,'finite_differences':finite,
        'optional_sympy_exponential_check':sympy_result,
        'defect_convention':'F_(t+s)(m) - F_t(F_s(m)), F_t(x)=Pi(exp(t)*x)',
        'exact_polynomial_variables':'h=exp(t)-1, k=exp(s)-1; hk coefficient equals ts coefficient',
        'scope':'Pi is a nonlinear retraction, not the Euclidean nearest-point projection.'}

    eta=.1; bound=0.; rows=[]
    for step in range(1,7):
        bound+=eta
        rows.append({'step':step,'certificate_bound':bound,'actual_error':0.})
    check(rows[-1]['certificate_bound']>.5,'Certificate budget exhausted')
    check(all(r['actual_error']==0 for r in rows),'Upper-bound exhaustion need not be actual failure')
    margin=.3; lipschitz=2.; radius=.05
    check(margin>2*lipschitz*radius,'Winner remains robust under two score perturbations')
    # At a reset: e+ <= L_reset * e- + jump. Omission is unsound.
    before=.05; reset_lipschitz=1.; jump=.4
    after=reset_lipschitz*before+jump
    check(after>=jump,'Reset jump included in certificate')
    check(before<jump,'Ignoring jump would underbound chosen actual reset error')
    results['certificates']={'accumulation':rows,'budget':.5,'actual_error_zero_despite_exhaustion':True,
        'decision_example':{'score_margin':margin,'per_score_L':lipschitz,'state_error_bound':radius,
        'worst_margin_loss':2*lipschitz*radius,'robust':True},
        'reset_example':{'pre_reset_bound':before,'reset_L':reset_lipschitz,'jump_bound':jump,'post_reset_bound':after,
        'possible_actual_reset_error':jump}}

    # A=I4 and C=I4: O=[I; I; I; I] has rank 4 without cross-coordinate coupling.
    n=4; ident=[[int(i==j) for j in range(n)] for i in range(n)]
    observability=ident*n
    check(all(ident[i][j]==0 for i in range(n) for j in range(n) if i!=j),'No cross-channel dynamics')
    check(observability[:n]==ident,'Identity minor certifies rank four exactly')
    numerical_rank=None
    try:
        import numpy as np
        numerical_rank=int(np.linalg.matrix_rank(np.array(observability)))
        check(numerical_rank==n,'Numerical observability rank agrees')
    except ImportError: pass
    results['independent_memory_bank']={'A':ident,'C':ident,'observability_rank_exact':n,
        'optional_numpy_rank':numerical_rank,'cross_coordinate_coupling':False,
        'scope':'Full observability is a linear-algebra property, not evidence of causal integration or phenomenology.'}
    return {'status':'passed','test_groups':len(results),'assertions_passed':CHECKS,
        'caveat':'Constructed deterministic examples only: no human or LLM experiments, no consciousness measurement or empirical claims.',
        'results':results}

if __name__=='__main__':
    output=run()
    destination=Path(__file__).with_name('mind_extension_results.json')
    destination.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'status':output['status'],'test_groups':output['test_groups'],
        'assertions_passed':output['assertions_passed'],'results_file':str(destination)},indent=2))
