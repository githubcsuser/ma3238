from fractions import Fraction as F
from math import exp

def matmul(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def solve(a,b):
 a=[list(map(F,row))+[F(y)] for row,y in zip(a,b)]
 for k in range(len(a)):
  p=next(i for i in range(k,len(a)) if a[i][k]);a[k],a[p]=a[p],a[k];v=a[k][k];a[k]=[x/v for x in a[k]]
  for i in range(len(a)):
   if i!=k:
    v=a[i][k];a[i]=[x-v*y for x,y in zip(a[i],a[k])]
 return [row[-1] for row in a]
checks=[]
P=[[F(2,3),F(1,3),0,0],[F(1,3),F(1,2),F(1,6),0],[0,F(1,3),F(1,2),F(1,6)],[0,0,F(1,2),F(1,2)]]
P2=matmul(P,P);assert P2[1]==[F(7,18),F(5,12),F(1,6),F(1,36)]
assert [P[1][k]*P[k][2]/P2[1][2] for k in range(4)]==[0,F(1,2),F(1,2),0]
checks.append('T2.4 queue construction, matrix power, bridge distribution')
P=[[F(3,4),F(1,4)],[F(1,3),F(2,3)]];b={'B':[F(1,5),F(3,5)],'S':[F(4,5),F(2,5)]};alpha=[F(3,4),F(1,4)]
for t,y in enumerate(['B','S','B']):
 if t:alpha=matmul([alpha],P)[0]
 z=sum(x*l for x,l in zip(alpha,b[y]));alpha=[x*l/z for x,l in zip(alpha,b[y])]
 if t==1:assert alpha==[F(26,37),F(11,37)]
assert z==F(194,555) and alpha[1]==F(249,388)
checks.append('T2.5 HMM filtering and next-observation probability')
p=F(1,3);q=1-p;N=4
u=[(1-(q/p)**i)/(1-(q/p)**N) for i in range(N+1)];v=[(N*u[i]-i)/(p-q) for i in range(N+1)]
assert u==[0,F(1,15),F(1,5),F(7,15),1] and v==[0,F(11,5),F(18,5),F(17,5),0]
checks.append('L4 gambler ruin probability and duration, biased case')
A=[[F(i==j) for j in range(1,5)] for i in range(1,5)];upper=[F(0)]*4;six=[F(0)]*4
for i in range(1,5):
 for j,prob in [(i+2,F(1,3)),(i-1,F(2,3))]:
  if 1<=j<=4:A[i-1][j-1]-=prob
  elif j>=5:upper[i-1]+=prob;six[i-1]+=prob*(j==6)
u=solve(A,upper);v=solve(A,six);probs=[1-u[1],u[1]-v[1],v[1]]
assert probs==[F(12,19),F(4,19),F(3,19)]
assert sum(x*y for x,y in zip([0,5,6],probs))==2
assert (sum(x*x*y for x,y in zip([0,5,6],probs))-4)/2==F(66,19)
checks.append('T4.1 nonunit jump overshoot, exit distribution, OST duration')
# Compound PGF via coefficients.
def mul(a,b):
 out=[F(0)]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):out[i+j]+=x*y
 return out
def compose(a,b):
 out=[F(0)]*(1+(len(a)-1)*(len(b)-1));power=[F(1)]
 for coeff in a:
  for i,x in enumerate(power):out[i]+=coeff*x
  power=mul(power,b)
 return out
phiN=[F(1,4),F(1,2),F(1,4)];phiX=[0,F(1,2),F(1,2)]
assert compose(phiN,phiX)==[F(1,4),F(1,4),F(5,16),F(1,8),F(1,16)]
checks.append('T4.3 compound PGF composition and coefficients')
f=[F(1,2),0,F(1,2)];g=[0,F(1,2),F(1,2)];h=compose(f,g)
assert h==[F(1,2),0,F(1,8),F(1,4),F(1,8)]
def moments(a):
 m=sum(i*p for i,p in enumerate(a));v=sum(i*i*p for i,p in enumerate(a))-m*m;return m,v
mf,sf=moments(f);mg,sg=moments(g);M,Sh=moments(h)
assert M==mf*mg and Sh==mf*sg+mg*mg*sf
for n in range(1,6):
 law=[0,F(1)]
 for t in range(n):law=compose(law,f if t%2==0 else g)
 mean,var=moments(law);ar=F(1);vr=F(0)
 for t in range(n):
  m,s=(mf,sf) if t%2==0 else (mg,sg);ar,vr=m*ar,m*m*vr+s*ar
 assert (mean,var)==(ar,vr)
checks.append('T4.5/T5.5 alternating composition order and moment recursions')
# Branching closed variance vs recurrence, including critical case.
for m,variance in [(F(3,4),F(11,16)),(F(1),F(2)),(F(3,2),F(1,4))]:
 V=F(0)
 for n in range(1,9):
  V=variance*m**(n-1)+m*m*V
  expected=n*variance if m==1 else variance*m**(n-1)*(m**n-1)/(m-1)
  assert V==expected
checks.append('Branching variance: subcritical, critical, supercritical')
# Vaccination moment formula with xi in {0,3}, conditional binomial.
import math
xi=[F(1,3),0,0,F(2,3)];a=F(1,4);thin=[sum(prob*math.comb(i,k)*a**k*(1-a)**(i-k) for i,prob in enumerate(xi) if i>=k) for k in range(4)]
m,s=moments(xi);assert moments(thin)==(a*m,a*a*s+a*(1-a)*m)
checks.append('T5.3 independent-child vaccination mean and variance')
print('\n'.join('PASS '+c for c in checks))
