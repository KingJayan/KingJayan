import math
def ss(a,b,x):
    t=min(1,max(0,(x-a)/(b-a))); return t*t*(3-2*t)
def bump(u): return ss(0.50,0.66,u)*(1-ss(0.72,0.90,u))
A=3.0  # peak speed = 1+A times cruise
N=400
v=[1+A*bump(i/N) for i in range(N)]
cum=[0]
for x in v: cum.append(cum[-1]+x)
tot=cum[-1]
def P(u): return cum[round(u*N)]/tot
STEP=40
out=[]
def layer(name,n,stretch):
    kf=[];sk=[]
    for i in range(n*STEP+1):
        u=i/(n*STEP); k=min(int(u*n),n-1); f=u*n-k
        x=-(k+P(f))/n*880
        pct=f"{u*100:.3f}".rstrip('0').rstrip('.')
        kf.append(f"{pct}%{{transform:translateX({x:.2f}px)}}")
        sk.append(f"{pct}%{{transform:scaleX({1+stretch*bump(f):.3f})}}")
    out.append(f"@keyframes drift-{name}{{{''.join(kf)}}}")
    out.append(f"@keyframes blur-{name}{{{''.join(sk)}}}")
layer('fore',1,5.0); layer('mid',2,3.0); layer('deep',4,1.8)
open('kf.css','w').write('\n      '.join(out))
