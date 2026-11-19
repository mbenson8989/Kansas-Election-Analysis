"""PDF table, pass A: pandas, from the pass A county table (pandas pipeline over raw SOS files)."""
import pandas as pd, json
V='/workspace/kansas-wiki/verification/'
a=pd.read_csv(V+'passA_counties.csv')
cols=['D_reg_22','D_reg_26','D_votes_22','D_votes_26','total_votes_22','total_votes_26','total_reg_26','population_2025']
tot=a[cols].sum(); tot['county']='Statewide total'
a['share26']=100*a.D_reg_26/a.total_reg_26
a=a.sort_values('share26',ascending=False,kind='mergesort')
t=pd.DataFrame([tot]); t['share26']=100*t.D_reg_26/t.total_reg_26
d=pd.concat([a,t],ignore_index=True)
c=lambda x:f"{int(x):,}"; s=lambda x:('+' if x>0 else ('-' if x<0 else ''))+f"{abs(int(x)):,}"
p=lambda x:('+' if x>0 else ('-' if x<0 else ''))+f"{abs(x):.1f}%"
out=[]
for _,r in d.iterrows():
    row=[r.county,c(r.population_2025),f"{r.share26:.1f}%"]
    for k in ('D_reg','D_votes','total_votes'):
        x,y=r[k+'_22'],r[k+'_26']; row+=[c(x),c(y),s(y-x),p(100*(y-x)/x)]
    out.append(row)
json.dump(out,open(V+'pdfA_rows.json','w'),indent=0); print(len(out),out[0],out[-1])
