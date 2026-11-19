"""PASS A (pandas). Independent of analyze.py: reads raw Kansas SOS files directly with pandas.
G = 100*D_votes/total_governor_votes - 100*D_reg/total_reg (active+inactive). dG = G26 - G22."""
import pandas as pd, numpy as np, re
RAW='/workspace/kansas/raw/'; OUT='/workspace/kansas-wiki/verification/'
def nm(s): return str(s).strip().title().replace('Mcpherson','McPherson')
# ---- 2022 governor votes (precinct file) ----
x=pd.ExcelFile(RAW+'2022-General-Election-Governor-Results-By-Precinct.xlsx')
g=pd.read_excel(x,'Governor'); g['c']=g.County.map(nm)
piv=g.pivot_table(index='c',columns='Party',values='Votes',aggfunc='sum')
v22=pd.DataFrame({'D':piv['Democratic'],'R':piv['Republican'],'O':piv['Libertarian']+piv['independent']})
for sh in ['JOHNSON','SEDGWICK','SHAWNEE','WYANDOTTE']:
    d=pd.read_excel(x,sh,header=None)
    names=pd.Series([str(v).lower() for v in d.iloc[1].values],index=d.columns)
    tot=d[[('COUNTY TOTALS' in str(v).upper()) for v in d.iloc[:,1]]].iloc[0]
    row={'D':0,'R':0,'O':0}
    for j,n in names.items():
        if 'kelly' in n: row['D']+=tot[j]
        elif 'schmidt' in n: row['R']+=tot[j]
        elif 'cordell' in n or 'pyle' in n: row['O']+=tot[j]
    v22.loc[nm(sh)]=row
v22=v22.astype(int); v22['TOT']=v22.D+v22.R+v22.O
# ---- 2026 governor votes (SOS election-night site, transcribed) ----
t=pd.read_csv(RAW+'ent2026_governor_transcribed.csv'); t['c']=t.county.map(nm)
v26=pd.DataFrame({'D':t.set_index('c').holscher_D,'R':t.set_index('c').masterson_R}); v26['TOT']=v26.D+v26.R
# ---- registration ----
r22=pd.read_excel(RAW+'11-2022-Voter-Registration-Numbers-by-County.xlsx'); r22=r22[r22.Jurisdiction!='Grand Total'].dropna(subset=['Jurisdiction'])
r22=r22.assign(c=r22.Jurisdiction.map(nm)).set_index('c')
r26=pd.read_excel(RAW+'10-2026-Voter-Registration-Numbers-by-County.xlsx',sheet_name='By County'); r26=r26[r26.County!='Grand Total'].dropna(subset=['County'])
r26=r26.assign(c=r26.County.map(nm)).set_index('c')
# ---- turnout 2022 (ballots cast, advance-by-mail) ----
tu=pd.read_excel(RAW+'2022-General-Election-Turnout-Information.xlsx',header=None)
tu=tu[[str(v).endswith(' COUNTY') for v in tu[0]]]; tu=tu.assign(c=tu[0].str.replace(' COUNTY','').map(nm)).set_index('c')
# ---- population ----
p=pd.read_csv(RAW+'co-est2025-alldata.csv',encoding='latin-1'); p=p[(p.STATE==20)&(p.COUNTY>0)]
p=p.assign(c=p.CTYNAME.str.replace(' County','').map(nm)).set_index('c').POPESTIMATE2025
o=pd.DataFrame(index=sorted(v22.index)); o.index.name='county'
o['population_2025']=p
o['D_votes_22']=v22.D; o['R_votes_22']=v22.R; o['other_votes_22']=v22.O; o['total_votes_22']=v22.TOT
o['D_reg_22']=pd.to_numeric(r22.Democratic); o['total_reg_22']=pd.to_numeric(r22['Grand Total'])
o['D_votes_26']=v26.D; o['R_votes_26']=v26.R; o['total_votes_26']=v26.TOT
o['D_reg_26']=pd.to_numeric(r26.Democratic); o['total_reg_26']=pd.to_numeric(r26.Total)
o['ballots_22']=pd.to_numeric(tu[3]); o['adv_mail_22']=pd.to_numeric(tu[1],errors='coerce')  # 'N/A' in 4 counties (Bourbon, Cherokee, Osage, Rice)
for y in ('22','26'):
    o['S'+y]=100*o['D_votes_'+y]/o['total_votes_'+y]; o['D'+y]=100*o['D_reg_'+y]/o['total_reg_'+y]; o['G'+y]=o['S'+y]-o['D'+y]
o['dG']=o.G26-o.G22
assert len(o)==105 and not o.drop(columns='adv_mail_22').isna().any().any()
o=o.sort_values('population_2025',ascending=False)
o.to_csv(OUT+'passA_counties.csv',float_format='%.10f')
S={k:int(o[k].sum()) for k in ['D_votes_22','R_votes_22','other_votes_22','total_votes_22','D_reg_22','total_reg_22','D_votes_26','R_votes_26','total_votes_26','D_reg_26','total_reg_26','ballots_22']}; S['adv_mail_22_reported_sum']=int(o.adv_mail_22.sum()); S['adv_mail_22_NA']=sorted(o.index[o.adv_mail_22.isna()])
S['reg22_grand_total_row']=[int(pd.read_excel(RAW+'11-2022-Voter-Registration-Numbers-by-County.xlsx').query("Jurisdiction=='Grand Total'")[c].astype(int).iloc[0]) for c in ['Democratic','Grand Total']]
gt=pd.read_excel(RAW+'10-2026-Voter-Registration-Numbers-by-County.xlsx',sheet_name='By County').query("County=='Grand Total'")
S['reg26_grand_total_row']=[int(gt.Democratic.iloc[0]),int(gt.Total.iloc[0])]
import json; json.dump(S,open(OUT+'passA_statewide.json','w'),indent=1); print(json.dumps(S))
