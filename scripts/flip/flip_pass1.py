"""PASS 1: pandas, reads RAW SOS files directly (not the earlier verification CSVs)."""
import pandas as pd, json, re
R='/workspace/kansas/raw/'
nm=lambda s:str(s).strip().title().replace('Mcpherson','McPherson')
x=pd.ExcelFile(R+'2022-General-Election-Governor-Results-By-Precinct.xlsx')
g=pd.read_excel(x,'Governor'); g['c']=g.County.map(nm)
d22=g[g.Party=='Democratic'].groupby('c').Votes.sum().astype(int).to_dict()
for sh in ['JOHNSON','SEDGWICK','SHAWNEE','WYANDOTTE']:
    d=pd.read_excel(x,sh,header=None); h=[str(v) for v in d.iloc[1]]
    row=d[[('COUNTY TOTALS' in str(v).upper()) for v in d.iloc[:,1]]].iloc[0]
    d22[nm(sh)]=int(sum(row[j] for j,n in enumerate(h) if 'Kelly' in n))
t=pd.read_csv(R+'ent2026_governor_transcribed.csv'); d26={nm(a):int(b) for a,b in zip(t.county,t.holscher_D)}
r22=pd.read_excel(R+'11-2022-Voter-Registration-Numbers-by-County.xlsx'); r22=r22[r22.Jurisdiction!='Grand Total'].dropna(subset=['Jurisdiction'])
reg22={nm(a):int(b) for a,b in zip(r22.Jurisdiction,r22.Democratic)}
r26=pd.read_excel(R+'10-2026-Voter-Registration-Numbers-by-County.xlsx',sheet_name='By County'); r26=r26[r26.County!='Grand Total'].dropna(subset=['County'])
reg26={nm(a):int(b) for a,b in zip(r26.County,r26.Democratic)}
p=pd.read_csv(R+'co-est2025-alldata.csv',encoding='latin-1'); p=p[(p.STATE==20)&(p.COUNTY>0)]
pop={nm(a.replace(' County','')):int(b) for a,b in zip(p.CTYNAME,p.POPESTIMATE2025)}
tot26={nm(a):int(b)+int(c) for a,b,c in zip(t.county,t.holscher_D,t.masterson_R)}
out={}
for c in d22:
    gap=d26[c]-d22[c]*reg26[c]/reg22[c]
    out[c]=dict(reg22=reg22[c],reg26=reg26[c],v22=d22[c],v26=d26[c],gap=gap,pop=pop[c],tot26=tot26[c])
assert len(out)==105
json.dump(out,open('pass1.json','w'),indent=1)
cand={c:v for c,v in out.items() if v['reg26']<v['reg22'] and v['v26']>v['v22']}
top=sorted(cand,key=lambda c:-cand[c]['gap'])[:12]
print(len(cand)); [print(c,out[c]) for c in top]
