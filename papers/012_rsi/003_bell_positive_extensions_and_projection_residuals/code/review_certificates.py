"""Independent finite certificate checks; the supplied simplex is not Lean-certified."""
from pathlib import Path
from fractions import Fraction as F
import importlib.util
SOURCE=Path(__file__).resolve().parents[1]/'docs/source_inputs/verify_obstruction.py'
spec=importlib.util.spec_from_file_location('supplied_obstruction',SOURCE)
review=importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
def require(ok,msg):
    if not ok: raise ValueError(msg)
def dot(a,b):
    require(len(a)==len(b),'dimensions')
    return sum((x*y for x,y in zip(a,b)),F(0))
def check_repair(p,value,x,B,beta):
    require(len(p)==16 and len(x)==32 and len(B)==16,'dimensions')
    require(all(isinstance(z,F) for z in [*p,value,*x,*B,beta]),'exact inputs')
    q,u=x[:16],x[16:];local=review.T_apply(q)
    require(all(z>=0 for z in x) and sum(q)==1,'primal normalization')
    require(all(abs(a-b)<=v for a,b,v in zip(p,local,u)),'primal enclosure')
    require(all(abs(z)<=F(1,8) for z in B),'dual coordinates')
    require(all(dot(B,review.vertex_behavior(j))<=beta for j in range(16)),'dual vertices')
    require(sum(u)/8==value==dot(B,p)-beta,'objective equality')
    require(review.pi_weighted_norm(p,local)==value,'actual distance')
def check_negative(p,value,x,a,b):
    require(len(p)==16 and len(x)==32 and len(a)==16,'dimensions')
    require(all(isinstance(z,F) for z in [*p,value,*x,*a,b]),'exact inputs')
    qp,qm=x[:16],x[16:];q=[u-v for u,v in zip(qp,qm)]
    require(all(z>=0 for z in x) and sum(q)==1,'signed normalization')
    require(review.T_apply(q)==p,'signed preimage')
    require(all(-1<=dot(a,review.vertex_behavior(j))+b<=0 for j in range(16)),'dual feasibility')
    require(sum(qm)==value==dot(a,p)+b,'negative objective')
    require(sum(abs(z) for z in q)==1+2*value,'split cancellation')
def run():
    for v in [F(0),F(3,8),F(1,2),F(51,100),F(5,8),F(70,99),F(1)]:
        p=review.isotropic(v)
        st,val,x=review.lp_repair_distance(p);sd,dual,sol=review.lp_dual_repair(p)
        require(st==sd==review.OPTIMAL and val==dual,'repair status')
        check_repair(p,val,x,*sol)
        require(val==max(F(0),(2*v-1)/4),'repair formula')
        sn,neg,y=review.lp_negative_mass(p);snd,nd,soln=review.lp_dual_negative_mass(p)
        require(sn==snd==review.OPTIMAL and neg==nd,'signed status')
        check_negative(p,neg,y,*soln)
        require(neg==max(F(0),v-F(1,2)),'negative formula')
    p=review.isotropic(F(5,8));observed=p.copy()
    observed[review.CTX_IDX[(0,0,1,1)]]+=F(1,100)
    observed[review.CTX_IDX[(0,0,1,0)]]-=F(1,100)
    epsilon=review.pi_weighted_norm(observed,p)
    require(epsilon==F(1,400),'uncertainty radius')
    require((review.S_of(observed)-2-8*epsilon)/8==F(1,16),'actual-table floor')
    _,val,x=review.lp_repair_distance(observed);_,_,sol=review.lp_dual_repair(observed)
    check_repair(observed,val,x,*sol);require(val==F(13,200),'observed repair')
    print('PASS independent exact checks: 8 repair and 7 negative-mass certificates; actual-table uncertainty floor')
if __name__=='__main__':run()
