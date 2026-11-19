"""RESIDUAL LAYER, PASS B (no pandas, exact fractions). Re-runs pass_b.py (openpyxl/csv/HTML re-download parse of raw SOS files),
then computes the layer a second way: residual from vote shares directly (S26 - S22) and offset votes as D26 - S22*N26/100,
and checks the identity residual = dG - expected loss in exact arithmetic."""
import subprocess, csv, json
from fractions import Fraction as F
V='/workspace/kansas-wiki/verification/'
subprocess.run(['python3','/workspace/kansas-wiki/scripts/pass_b.py'],check=True,capture_output=True)
rows=list(csv.DictReader(open(V+'passB_counties.csv'))); out=[]
I=lambda r,k:int(r[k])
tot={k:0 for k in ['D_votes_22','total_votes_22','D_reg_22','total_reg_22','D_votes_26','total_votes_26','D_reg_26','total_reg_26']}
for r in rows:
    for k in tot: tot[k]+=I(r,k)
    s22=F(100*I(r,'D_votes_22'),I(r,'total_votes_22')); s26=F(100*I(r,'D_votes_26'),I(r,'total_votes_26'))
    d22=F(100*I(r,'D_reg_22'),I(r,'total_reg_22')); d26=F(100*I(r,'D_reg_26'),I(r,'total_reg_26'))
    exp_loss=d22-d26; resid=s26-s22; dG=(s26-d26)-(s22-d22)
    assert resid==dG-exp_loss
    off=I(r,'D_votes_26')-s22*I(r,'total_votes_26')/100
    assert off==resid*I(r,'total_votes_26')/100
    gap=I(r,'D_votes_26')-F(I(r,'D_votes_22')*I(r,'D_reg_26'),I(r,'D_reg_22'))
    out.append(dict(key=r['key'],population_2025=I(r,'population_2025'),dem_reg_lost=I(r,'D_reg_26')<I(r,'D_reg_22'),exp_loss=float(exp_loss),residual=float(resid),dG=float(dG),
                    offset_votes=float(off),gap_votes_ne=float(gap),resid_votes_ne_live=float(dG*I(r,'total_votes_26')/100),total_votes_26=I(r,'total_votes_26')))
with open(V+'residB_counties.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0])); w.writeheader(); [w.writerow({k:(repr(v) if isinstance(v,float) else v) for k,v in x.items()}) for x in out]
S22=F(100*tot['D_votes_22'],tot['total_votes_22']); S26=F(100*tot['D_votes_26'],tot['total_votes_26']); D22=F(100*tot['D_reg_22'],tot['total_reg_22']); D26=F(100*tot['D_reg_26'],tot['total_reg_26'])
N=tot['total_votes_26']; p=S26/100; s0=(D22-D26)/100
ST=dict(exp_loss=float(D22-D26),residual=float(S26-S22),offset_votes_pooled=float((S26-S22)*N/100),offset_votes_county_sum=float(sum(F(x['offset_votes']) for x in out)),
  offset_votes_sum_loss_counties=sum(x['offset_votes'] for x in out if x['dem_reg_lost']),offset_votes_sum_nonloss=sum(x['offset_votes'] for x in out if not x['dem_reg_lost']),
  gap_votes_ne_sum=sum(x['gap_votes_ne'] for x in out),resid_votes_ne_live_sum=sum(x['resid_votes_ne_live'] for x in out),
  offset_need={k:dict(switched=float((s0+a)*N),added=float((s0+a)*N/(1-p+s0+a))) for k,a in (('0',0),('1',F(1,100)),('2',F(2,100)))},
  n_resid_pos=sum(x['residual']>0 for x in out),n_resid_neg=sum(x['residual']<0 for x in out),n_loss=sum(x['dem_reg_lost'] for x in out))
json.dump(ST,open(V+'residB_statewide.json','w'),indent=1); print(json.dumps(ST)[:800])
