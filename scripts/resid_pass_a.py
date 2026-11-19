"""RESIDUAL LAYER, PASS A (pandas). Re-runs pass_a.py (raw SOS files -> county table), then computes the NE/IA/SD reverse-factoring layer.
Formulas (source scripts):
  expected loss  = Dem reg share 2022 - Dem reg share 2026        NE statewide/scripts/analyze.py L17 (regdrop); IA iowa-wiki/repo/scripts/resolve.py (reg_share_loss); SD github_wiki_build_sd.py L11 (regdrop)
  residual       = dG - expected loss  (= S26 - S22)               NE analyze.py L18 (resid); IA resolve.py (residual); SD L11 (gain)
  offset votes   = residual / 100 * N26  (= D26 - S22/100 * N26)   NE analyze.py L19 (unexpl_votes); IA resolve.py (residual_votes); SD L11 (implied)
  Kansas: N26 = 2026 total governor votes (NE/IA/SD use ballots cast; the live NE wiki uses race votes).
Comparison lines: NE live wiki 'Gap in votes' = D26 - D22*(DemReg26/DemReg22); NE live wiki 'Residual votes' = N26 * dG / 100.
Statewide offset need (IA resolve.py pooled()): switched = s*N, added = s*N/(1-p+s), s = statewide reg-share drop (+0/1/2 pt cushion)."""
import subprocess, pandas as pd, numpy as np, json
V='/workspace/kansas-wiki/verification/'
subprocess.run(['python3','/workspace/kansas-wiki/scripts/pass_a.py'],check=True,capture_output=True)
o=pd.read_csv(V+'passA_counties.csv',index_col='county')
o['exp_loss']=o.D22-o.D26
o['residual']=o.dG-o.exp_loss
o['offset_votes']=o.residual/100*o.total_votes_26
o['offset_votes_alt']=o.D_votes_26-o.S22/100*o.total_votes_26
assert np.allclose(o.offset_votes,o.offset_votes_alt) and np.allclose(o.residual,o.S26-o.S22)
o['gap_votes_ne']=o.D_votes_26-o.D_votes_22*o.D_reg_26/o.D_reg_22
o['resid_votes_ne_live']=o.total_votes_26*o.dG/100
o['dem_reg_lost']=o.D_reg_26<o.D_reg_22
cols=['population_2025','dem_reg_lost','D_reg_22','D_reg_26','D22','D26','exp_loss','G22','G26','dG','S22','S26','residual','D_votes_22','D_votes_26','total_votes_26','offset_votes','gap_votes_ne','resid_votes_ne_live']
o=o.sort_values('population_2025',ascending=False)
o[cols].to_csv(V+'residA_counties.csv',float_format='%.10f')
T={k:float(o[k].sum()) for k in ['D_votes_22','total_votes_22','D_reg_22','total_reg_22','D_votes_26','total_votes_26','D_reg_26','total_reg_26']}
S22=100*T['D_votes_22']/T['total_votes_22']; S26=100*T['D_votes_26']/T['total_votes_26']; D22=100*T['D_reg_22']/T['total_reg_22']; D26=100*T['D_reg_26']/T['total_reg_26']
N=T['total_votes_26']; p=S26/100; s0=(D22-D26)/100
ST=dict(exp_loss=D22-D26,dG=(S26-D26)-(S22-D22),residual=S26-S22,offset_votes_pooled=(S26-S22)/100*N,offset_votes_county_sum=float(o.offset_votes.sum()),
  offset_votes_sum_loss_counties=float(o.offset_votes[o.dem_reg_lost].sum()),offset_votes_sum_nonloss=float(o.offset_votes[~o.dem_reg_lost].sum()),
  gap_votes_ne_sum=float(o.gap_votes_ne.sum()),resid_votes_ne_live_sum=float(o.resid_votes_ne_live.sum()),
  D_change=T['D_votes_26']-T['D_votes_22'],turnout_part=(T['D_votes_26']-T['D_votes_22'])-(S26-S22)/100*N,
  offset_need={k:dict(switched=(s0+a)*N,added=(s0+a)*N/(1-p+s0+a)) for k,a in (('0',0),('1',.01),('2',.02))},
  median_residual=float(o.residual.median()),mean_residual=float(o.residual.mean()),sd_residual=float(o.residual.std()),
  n_resid_pos=int((o.residual>0).sum()),n_resid_neg=int((o.residual<0).sum()),n_loss=int(o.dem_reg_lost.sum()),n_exp_loss_pos=int((o.exp_loss>0).sum()),
  median_exp_loss=float(o.exp_loss.median()))
X=np.c_[np.ones(105),o.exp_loss]; beta,*_=np.linalg.lstsq(X,o.dG.values,rcond=None); e=o.dG.values-X@beta
se=np.sqrt(np.diag(e@e/103*np.linalg.inv(X.T@X))); r2=1-e@e/((o.dG-o.dG.mean())**2).sum()
ST['ks_fit_dG_on_exp_loss']=dict(a=float(beta[0]),b=float(beta[1]),b_se=float(se[1]),a_se=float(se[0]),r2=float(r2))
json.dump(ST,open(V+'residA_statewide.json','w'),indent=1); print(json.dumps(ST,indent=0)[:2500])
print(o.sort_values('residual',ascending=False)[['residual','offset_votes']].head(5).round(2)); print(o.sort_values('residual')[['residual','offset_votes']].head(5).round(2))
print(o.sort_values('offset_votes',ascending=False)[['residual','offset_votes']].head(5).round(1)); print(o.sort_values('offset_votes')[['residual','offset_votes']].head(5).round(1))
