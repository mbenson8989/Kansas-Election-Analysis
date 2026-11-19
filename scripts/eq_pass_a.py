"""Pass A for the Kansas final fitted equations: statsmodels OLS on the pass A float tables."""
import pandas as pd, numpy as np, json, statsmodels.api as sm
V='/workspace/kansas-wiki/verification/'
a=pd.read_csv(V+'passA_counties.csv',index_col='county'); r=pd.read_csv(V+'residA_counties.csv',index_col='county').loc[a.index]
def ols(y,x):
    f=sm.OLS(np.asarray(y,float),sm.add_constant(np.asarray(x,float))).fit()
    return dict(n=int(f.nobs),const=f.params[0],mult=f.params[1],const_se=f.bse[0],mult_se=f.bse[1],mult_t=f.tvalues[1],mult_p=f.pvalues[1],r2=f.rsquared,resid_sd=float(np.sqrt(f.ssr/(f.nobs-2))))
O={'dG_on_exp_loss':ols(r.dG,r.exp_loss),'fwd_2022':ols(a.G22,a.D22/100),'fwd_2026':ols(a.G26,a.D26/100),'fwd_pooled':ols(np.r_[a.G22,a.G26],np.r_[a.D22,a.D26]/100)}
e=O['dG_on_exp_loss']; s=r.loc['Seward']; j=r.loc['Johnson']
for c,row in (('Seward',s),('Johnson',j)):
    fit=e['const']+e['mult']*row.exp_loss
    O['ex_'+c]=dict(exp_loss=row.exp_loss,dG=row.dG,fitted_dG=fit,distance=row.dG-fit)
O={k:{kk:float(vv) for kk,vv in v.items()} for k,v in O.items()}
json.dump(O,open(V+'eqA.json','w'),indent=1); print(json.dumps(O,indent=1))
