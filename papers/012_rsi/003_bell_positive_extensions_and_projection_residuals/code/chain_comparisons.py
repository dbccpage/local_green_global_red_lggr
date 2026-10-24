"""Exact full-table quantum certificates and independently constructed cycle replays."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json
import math

ROOT = Path(__file__).resolve().parents[1]

def require(ok, message):
    if not ok:
        raise ValueError(message)

def dot(a, b):
    return sum(x*y for x, y in zip(a, b))

def matmul(a, b):
    return [[sum(a[i][k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]

def kron(a, b):
    return [[a[i//2][j//2]*b[i%2][j%2] for j in range(4)] for i in range(4)]

def load_certificate():
    return json.loads((ROOT/'data/five_setting_certificates.json').read_text())

def verify_five(cert):
    dirs = [[[F(z), F(x)] for z, x in side] for side in cert['directions']]
    require(len(dirs)==2 and all(len(side)==5 for side in dirs), 'direction shape')
    effects={}
    for side, setting in product(range(2),range(5)):
        z,x=dirs[side][setting]
        require(z*z+x*x==1, 'unit direction')
        for a in (-1,1):
            E=[[(1+a*z)/2,a*x/2],[a*x/2,(1-a*z)/2]]
            require(matmul(E,E)==E and E[0][1]==E[1][0], 'positive projector')
            effects[side,setting,a]=E
        require([[effects[side,setting,-1][i][j]+effects[side,setting,1][i][j] for j in range(2)] for i in range(2)]==[[1,0],[0,1]], 'POVM completeness')
    rho=[[F(1,2) if i in (0,3) and j in (0,3) else F(0) for j in range(4)] for i in range(4)]
    require(matmul(rho,rho)==rho and sum(rho[i][i] for i in range(4))==1,'density')
    cells=list(product(range(5),range(5),(-1,1),(-1,1)))
    assignments=list(product((-1,1),repeat=10))
    A=[[int(g[x]==a and g[5+y]==b) for g in assignments] for x,y,a,b in cells]
    p=[]
    for x,y,a,b in cells:
        product_matrix=matmul(rho,kron(effects[0,x,a],effects[1,y,b]))
        value=sum(product_matrix[i][i] for i in range(4))
        require(value==(1+a*b*dot(dirs[0][x],dirs[1][y]))/4, 'Born formula')
        require(value>=0,'probability')
        p.append(value)
    def vector(key, length):
        require(all(str(int(k))==k and 0<=int(k)<length for k in cert[key]),'certificate index')
        return [F(cert[key].get(str(i),'0')) for i in range(length)]
    q=vector('q',1024);h=vector('gamma',1024);y=vector('cf_dual',100);z=vector('negative_dual',100)
    require(sum(q)==1,'signed normalization')
    require(min(h)>=0 and min(y)>=0,'packing/cover nonnegativity')
    for i in range(100):
        require(dot(A[i],q)==p[i],'signed projection')
        require(dot(A[i],h)<=p[i],'packing domination')
    for j in range(1024):
        col=[A[i][j] for i in range(100)]
        require(dot(y,col)>=1,'cover')
        require(-1<=dot(z,col)<=0,'negative dual')
    N=sum(max(-x,0) for x in q);cf=1-sum(h)
    require(sum(h)==dot(y,p),'CF optimality gap')
    require(N==dot(z,p),'negative-mass optimality gap')
    require(cf==F(698,925) and N==F(167,925) and cf>4*N,'strict factor-four counterexample')
    return dict(contexts=25,born_cells=100,assignments=1024,CF=str(cf),N_min=str(N),ratio=str(cf/N),margin=str(cf-4*N))

def cycle_replay(n):
    require(type(n) is int and n>=2,'cycle size')
    m=2*n;v=F(m-1,m);r=F(m-2,m)
    P=(1+v/r)/2;Q=(1-v/r)/2
    signed={};packing={}
    for j,flip in product(range(m),(-1,1)):
        base=tuple(flip if k<=j else -flip for k in range(m))
        opposite=tuple(a*(-1)**k for k,a in enumerate(base))
        signed[base]=signed.get(base,F(0))+P/(2*m)
        signed[opposite]=signed.get(opposite,F(0))+Q/(2*m)
        packing[base]=packing.get(base,F(0))+(1-v)/4
    require(sum(signed.values())==1,'cycle normalization')
    for i,a,b in product(range(m),(-1,1),(-1,1)):
        target=-1 if i==m-1 else 1
        p=(1+a*b*target*v)/4
        row=lambda g:g[i]==a and g[(i+1)%m]==b
        require(sum(w for g,w in signed.items() if row(g))==p,'cycle full-cell projection')
        require(sum(w for g,w in packing.items() if row(g))<=p,'cycle packing')
    for g in product((-1,1),repeat=m):
        bad=sum(g[i]*g[(i+1)%m]!=(-1 if i==m-1 else 1) for i in range(m))
        require(bad%2==1 and 1<=bad<=m-1,'cycle parity')
        require(-1<=F(1-bad,m-2)<=0,'cycle negative dual')
    N=sum(max(-x,0) for x in signed.values());cf=1-sum(packing.values())
    require(N==(n*v-n+1)/(2*n-2) and cf==(2*n-2)*N,'cycle exact comparison')
    u=math.cos(math.pi/(2*n))
    require(u>1-1/n,'quantum visibility')
    return dict(settings_per_party=n,cycle_contexts=m,exact_visibility=str(v),ratio=2*n-2,quantum_CF=n*u-n+1,quantum_N=(n*u-n+1)/(2*n-2))

def grid_replay(n):
    a=(n//2)*math.pi/n;b=(n//4+.5)*math.pi/n;c=(3*n//4+.5)*math.pi/n
    S=math.cos(b)+math.cos(a-b)+math.cos(a-c)-math.cos(c)
    require(S>=2*math.sqrt(2)-6*math.pi/n-1e-12,'analytic CHSH floor')
    if n>=64:
        require((S-2)/4>=F(17,160)-1e-12,'complete-table negative mass floor')
    return S

def replay():
    result=verify_five(load_certificate())
    result['cycle_replays']=[cycle_replay(n) for n in range(2,8)]
    sizes=list(range(4,129))+[256,1024,1000000]
    for n in sizes:grid_replay(n)
    result['grid_checks']=len(sizes)
    result['scope']='Exact complete 5x5 counterexample; exact finite cycle replays; floating consistency for analytic all-size bounds. The cycle parity quotient and a full Bell table are distinct models.'
    return result

if __name__=='__main__':
    print(json.dumps(replay(),indent=2))
