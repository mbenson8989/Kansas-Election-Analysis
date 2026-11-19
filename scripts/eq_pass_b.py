"""Pass B for the Kansas final fitted equations: exact rational arithmetic from the pass B integer counts (no pandas/statsmodels)."""
import csv, json
from fractions import Fraction as F
from decimal import Decimal, getcontext
from scipy.stats import t as tdist
getcontext().prec=40
V='/workspace/kansas-wiki/verification/'
rows=list(csv.DictReader(open(V+'passB_counties.csv'))); assert len(rows)==105
I=lambda r,k:int(r[k])
def shares(r):
    D22=F(100*I(r,'D_reg_22'),I(r,'total_reg_22')); D26=F(100*I(r,'D_reg_26'),I(r,'total_reg_26'))
    S22=F(100*I(r,'D_votes_22'),I(r,'total_votes_22')); S26=F(100*I(r,'D_votes_26'),I(r,'total_votes_26'))
    return dict(D22=D22,D26=D26,G22=S22-D22,G26=S26-D26,dG=(S26-D26)-(S22-D22),el=D22-D26)
X={r['key']:shares(r) for r in rows}
sqrt=lambda f: float((Decimal(f.numerator)/Decimal(f.denominator)).sqrt())
def ols(y,x):
    n=len(y); mx=sum(x)/n; my=sum(y)/n
    sxx=sum((a-mx)**2 for a in x); sxy=sum((a-mx)*(b-my) for a,b in zip(x,y)); syy=sum((b-my)**2 for b in y)
    m=sxy/sxx; c=my-m*mx; sse=sum((b-c-m*a)**2 for a,b in zip(x,y)); s2=sse/(n-2)
    mse=sqrt(s2/sxx); cse=sqrt(s2*(F(1,n)+mx*mx/sxx)); tval=float(m)/mse
    return dict(n=n,const=float(c),mult=float(m),const_se=cse,mult_se=mse,mult_t=tval,mult_p=float(2*tdist.sf(abs(tval),n-2)),r2=float(1-sse/syy),resid_sd=sqrt(s2)),(c,m)
K=list(X)
O={}
O['dG_on_exp_loss'],(c,m)=ols([X[k]['dG'] for k in K],[X[k]['el'] for k in K])
O['fwd_2022'],_=ols([X[k]['G22'] for k in K],[X[k]['D22']/100 for k in K])
O['fwd_2026'],_=ols([X[k]['G26'] for k in K],[X[k]['D26']/100 for k in K])
O['fwd_pooled'],_=ols([X[k]['G22'] for k in K]+[X[k]['G26'] for k in K],[X[k]['D22']/100 for k in K]+[X[k]['D26']/100 for k in K])
for c_ in ('seward','johnson'):
    x=X[c_]; fit=c+m*x['el']
    O['ex_'+c_.capitalize()]=dict(exp_loss=float(x['el']),dG=float(x['dG']),fitted_dG=float(fit),distance=float(x['dG']-fit))
json.dump(O,open(V+'eqB.json','w'),indent=1); print(json.dumps(O,indent=1))
