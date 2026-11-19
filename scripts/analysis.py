"""Kansas analysis from the verified pass A table (asserted identical to pass B). Locked formula, governor votes both years."""
import pandas as pd, numpy as np, json, statsmodels.api as sm
from scipy import stats
V='/workspace/kansas-wiki/verification/'; R='/workspace/kansas-wiki/repo/'
a=pd.read_csv(V+'passA_counties.csv',index_col='county'); b=pd.read_csv(V+'passB_counties.csv')
assert json.load(open(V+'compare_report.json'))['CLEAN']
o=a.sort_values('population_2025',ascending=False).copy()
def fit(y,x):
    X=sm.add_constant(np.asarray(x,float)/100); r=sm.OLS(np.asarray(y,float),X).fit(); res=r.resid
    ci=r.conf_int()
    return dict(n=int(len(y)),m=float(r.params[1]),m_se=float(r.bse[1]),m_ci=[float(ci[1,0]),float(ci[1,1])],b=float(r.params[0]),b_se=float(r.bse[0]),b_ci=[float(ci[0,0]),float(ci[0,1])],
        r2=float(r.rsquared),p_m=float(r.pvalues[1]),resid_sd=float(np.sqrt(np.sum(res**2)/(len(y)-2))),mae=float(np.mean(np.abs(res))),
        within_2=int(np.sum(np.abs(res)<=2)),within_5=int(np.sum(np.abs(res)<=5)),sd_y=float(np.std(y,ddof=1))),r
F={}
F['2022'],r22=fit(o.G22,o.D22); F['2026'],r26=fit(o.G26,o.D26)
F['pooled'],_=fit(np.r_[o.G22,o.G26],np.r_[o.D22,o.D26])
o['fit22']=r22.fittedvalues; o['res22']=o.G22-o.fit22; o['fit26']=r26.fittedvalues; o['res26']=o.G26-o.fit26
# Chow-style check: is 2026 line different from 2022 line? (pooled with year interaction)
Xp=np.c_[np.ones(210),np.r_[o.D22,o.D26]/100,np.r_[np.zeros(105),np.ones(105)],np.r_[np.zeros(105),o.D26/100]]
rp=sm.OLS(np.r_[o.G22,o.G26],Xp).fit(); F['year_interaction']=dict(d_intercept=float(rp.params[2]),p_d_intercept=float(rp.pvalues[2]),d_slope=float(rp.params[3]),p_d_slope=float(rp.pvalues[3]))
# ---- neighbors (computed here from the other states' saved county CSVs; SD from its saved summary) ----
NB={}
ne=pd.read_csv('/workspace/nebraska-elections/spec_check/all93_deltaG_spec.csv')
ia=pd.read_csv('/workspace/iowa-elections/nebraska_method/iowa_gov_2022_2026_nebraska_method_99_counties.csv')
for st,d in (('NE',ne),('IA',ia)):
    for y in (2022,2026):
        D=100*d[f'reg_dem_{y}']/d[f'reg_tot_{y}']
        NB[f'{st}_{y}_ballots']=fit(100*d[f'D_{y}']/d[f'ballots_{y}']-D,D)[0]
        NB[f'{st}_{y}_govvotes']=fit(100*d[f'D_{y}']/d[f'race_votes_{y}']-D,D)[0]
sd=json.load(open('/workspace/south-dakota-elections/sd_forward_surplus_summary.json'))['SD']
for y in (2022,2026):
    NB[f'SD_{y}_ballots']={k:sd[f'SD_{y}'][k] for k in ('n','m','b','r2','rmse_resid_sd')}
    NB[f'SD_{y}_govvotes']={k:sd[f'SD_{y}_govvotes_denominator'][k] for k in ('n','m','b','r2','rmse_resid_sd')}
FLAG={}
for y in ('2022','2026'):
    for den in ('govvotes','ballots'):
        for k in ('m','b'):
            vals=[NB[f'{s}_{y}_{den}'][k] for s in ('NE','IA','SD')]; lo,hi=min(vals),max(vals); v=F[y][k]; se=F[y][k+'_se']
            dist=0 if lo<=v<=hi else (lo-v if v<lo else v-hi)
            FLAG[f'{k}_{y}_{den}']=dict(KS=v,KS_ci=F[y][k+'_ci'],band=[lo,hi],neighbors={s:NB[f'{s}_{y}_{den}'][k] for s in ('NE','IA','SD')},outside=bool(dist>0),distance=dist,
                distance_in_KS_SE=dist/se,band_width=hi-lo,KS_ci_overlaps_band=bool(F[y][k+'_ci'][1]>=lo and F[y][k+'_ci'][0]<=hi))
# ---- floor / ceiling ----
q10=o.S22.quantile(.10); q25=o.G22.quantile(.25)
FL=o[(o.S22<=q10)&(o.G22<=q25)].sort_values('S22')
PRIOR_FL=['Wallace','Chautauqua','Sheridan','Ness','Wichita','Cheyenne','Scott','Morton','Gove','Logan']
CEIL3=['Johnson','Sedgwick','Wyandotte']; CEIL6=CEIL3+['Douglas','Riley','Shawnee']
lr=stats.linregress(np.log10(o.population_2025),o.dG)
top5=o.dG.sort_values(ascending=False).head(5); bot5=o.dG.sort_values().head(5)
low5S=o.S22.sort_values().head(5); low5G=o.G22.sort_values().head(5)
K=dict(floor_rule=f'2022 D vote share <= 10th percentile ({q10:.2f}%) AND G2022 <= 25th percentile ({q25:.2f})',floor_counties=list(FL.index),floor_matches_prior=sorted(FL.index)==sorted(PRIOR_FL),
  floor_mean=float(FL.dG.mean()),floor_median=float(FL.dG.median()),ceiling3_mean=float(o.loc[CEIL3].dG.mean()),ceiling3_median=float(o.loc[CEIL3].dG.median()),ceiling6_mean=float(o.loc[CEIL6].dG.mean()),ceiling6_median=float(o.loc[CEIL6].dG.median()),ceil3_dG={c:float(o.loc[c,'dG']) for c in CEIL6},floor_dG=FL.dG.to_dict(),floor_S22=FL.S22.to_dict(),floor_G22=FL.G22.to_dict(),floor_G26=FL.G26.to_dict(),
  slope=float(lr.slope),slope_r=float(lr.rvalue),slope_p=float(lr.pvalue),slope_r2=float(lr.rvalue**2),slope_intercept=float(lr.intercept),
  mean_dG=float(o.dG.mean()),median_dG=float(o.dG.median()),sd_dG=float(o.dG.std()),n_pos=int((o.dG>0).sum()),n_neg=int((o.dG<0).sum()),
  top5=top5.to_dict(),bot5=bot5.to_dict(),lowest5_S22=low5S.to_dict(),lowest5_G22=low5G.to_dict(),
  pooled=dict(S22=100*o.D_votes_22.sum()/o.total_votes_22.sum(),D22=100*o.D_reg_22.sum()/o.total_reg_22.sum(),S26=100*o.D_votes_26.sum()/o.total_votes_26.sum(),D26=100*o.D_reg_26.sum()/o.total_reg_26.sum()),
  n_Dreg_fell=int((o.D_reg_26<o.D_reg_22).sum()),n_S_rose=int((o.S26>o.S22).sum()),n_G_rose=int((o.G26>o.G22).sum()))
K['pooled'].update(G22=K['pooled']['S22']-K['pooled']['D22'],G26=K['pooled']['S26']-K['pooled']['D26']); K['pooled']['dG']=K['pooled']['G26']-K['pooled']['G22']
# ---- Texas-style ballots check, 2022 only (2026 county ballots cast not posted) ----
tu=pd.read_excel('/workspace/kansas/raw/2022-General-Election-Turnout-Information.xlsx',header=None)
tu=tu[[str(v).endswith(' COUNTY') for v in tu[0]]]; tu.index=[str(v)[:-7].title().replace('Mcpherson','McPherson') for v in tu[0]]
o['reg_in_turnout_file_22']=pd.to_numeric(tu[5]).reindex(o.index)
o['DR_22']=o.D_votes_22+o.R_votes_22
o['undervote_pct_22']=100*(o.ballots_22-o.total_votes_22)/o.ballots_22
o['DR_gt_ballots_22']=o.DR_22>o.ballots_22; o['gov_gt_ballots_22']=o.total_votes_22>o.ballots_22
o['ballots_gt_reg_22']=o.ballots_22>o.reg_in_turnout_file_22
und=o.undervote_pct_22; core=und[(und>=0)]
TX=dict(DR_gt_ballots=list(o.index[o.DR_gt_ballots_22]),gov_gt_ballots=list(o.index[o.gov_gt_ballots_22]),ballots_gt_reg=list(o.index[o.ballots_gt_reg_22]),
  undervote_median=float(und.median()),undervote_p95=float(und.quantile(.95)),undervote_gt5=list(und[und>5].index),
  detail={c:dict(ballots=int(o.loc[c,'ballots_22']),gov=int(o.loc[c,'total_votes_22']),DR=int(o.loc[c,'DR_22']),reg_turnout_file=int(o.loc[c,'reg_in_turnout_file_22']),reg_nov1=int(o.loc[c,'total_reg_22']),undervote_pct=float(und[c]))
          for c in sorted(set(o.index[o.gov_gt_ballots_22|o.ballots_gt_reg_22|o.DR_gt_ballots_22])|set(und[und>5].index)|{'Stevens','Sumner','Montgomery'})})
TX['statewide_ballots_22']=int(o.ballots_22.sum()); TX['statewide_gov_22']=int(o.total_votes_22.sum())
# ---- absentee 2022 (ballots returned by mail; not by candidate) ----
ABS=dict(adv_mail_sum_101=int(o.adv_mail_22.sum()),na=list(o.index[o.adv_mail_22.isna()]),share_of_ballots=float(o.adv_mail_22.sum()/o.ballots_22[o.adv_mail_22.notna()].sum()*100))
o['adv_mail_share_22']=100*o.adv_mail_22/o.ballots_22
ok=o.adv_mail_22.notna()&~o.index.isin(['Stevens','Sumner'])
c_=stats.spearmanr(o.adv_mail_share_22[ok],o.dG[ok]); ABS['spearman_mailshare22_vs_dG']=dict(rho=float(c_.statistic),p=float(c_.pvalue),n=int(ok.sum()))
# ---- tiers & output ----
tier=pd.Series('',index=o.index)
for c in FL.index: tier[c]='floor (bottom cluster)'
for c in top5.index: tier[c]=(tier[c]+'; ' if tier[c] else '')+'ceiling (top-5 dG)'
for c in bot5.index: tier[c]=(tier[c]+'; ' if tier[c] else '')+'bottom-5 dG'
o['flag']=tier
o['D_reg_change']=o.D_reg_26-o.D_reg_22; o['D_reg_pct_change']=100*o.D_reg_change/o.D_reg_22
cols=['population_2025','flag','D_votes_22','R_votes_22','other_votes_22','total_votes_22','D_reg_22','total_reg_22','S22','D22','G22','D_votes_26','R_votes_26','total_votes_26','D_reg_26','total_reg_26','S26','D26','G26','dG','D_reg_change','D_reg_pct_change','fit22','res22','fit26','res26','ballots_22','adv_mail_22','undervote_pct_22']
out=o[cols].copy(); out.insert(0,'status_2026','UNOFFICIAL (SOS election night, last updated 11/08/2026 9:15 PM)')
out.round(6).to_csv(R+'KS_Governor_2022_2026_DeltaG_by_County.csv')
o.to_pickle('/tmp/ks_o.pkl')
J=dict(fits=F,neighbors=NB,neighbor_flag=FLAG,K=K,TX=TX,ABS=ABS)
json.dump(J,open(R+'KS_results_summary.json','w'),indent=1,default=float)
print(json.dumps({k:F[k] for k in F},indent=0,default=float)[:1800]); print(json.dumps(FLAG,default=float)[:2500]); print(json.dumps(K,default=float)[:3000]); print(json.dumps(TX,default=float)[:3500]); print(ABS)
