"""Two graphics Texas/Nebraska have that Kansas lacked: (1) 2022 Democratic share vs 2026 gain bars, (2) ceiling counties ΔG by population.
Data: pass A county table built from raw Kansas SOS files (governor-votes denominator, all registered voters)."""
import pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, json
A=pd.read_csv('/workspace/kansas-wiki/verification/passA_counties.csv')
OUT='/workspace/kansas-resources/out/'
A['gain']=A.S26-A.S22
# chart 1
d=A.sort_values('S22',ascending=False).reset_index(drop=True)
n_up=int((d.gain>0).sum()); n_dn=int((d.gain<0).sum())
fig,ax=plt.subplots(figsize=(22,7),dpi=200)
x=range(len(d))
ax.bar(x,d.S22,color='#4472C4',label='2022 Democratic share of governor votes (%)')
ax.bar(x,d.gain.clip(lower=0),bottom=d.S22,color='#ED7D31',label='Gain, 2022 to 2026* (points)')
ax.bar(x,d.gain.clip(upper=0),color='#C00000',label='Decline, 2022 to 2026* (points, shown below zero)')
ax.axhline(0,color='black',lw=0.8)
ax.set_xticks(list(x)); ax.set_xticklabels(d.county,rotation=90,fontsize=7)
ax.set_ylabel('Percentage points'); ax.set_xlabel('County (highest to lowest 2022 Democratic share)')
ax.set_title(f'Kansas Governor Race: 2022 Democratic Vote Share vs. Change to 2026*, All 105 Counties\nDemocratic share rose in {n_up} counties and fell in {n_dn}',fontsize=14,fontweight='bold')
ax.legend(loc='upper right',fontsize=9)
fig.text(0.01,0.005,'Share = Democratic governor votes ÷ total governor votes (all candidates) × 100. 2022: Kansas SOS official results. *2026: Kansas SOS unofficial election-night results (updated 11/08/2026), certification scheduled Dec 1, 2026. Method: Morissa Benson. Analytical observation, not a finding of wrongdoing.',fontsize=7)
ax.margins(x=0.005); fig.tight_layout(rect=(0,0.02,1,1)); fig.savefig(OUT+'KS_governor_2022_Dem_share_vs_gain_bar_chart.png'); plt.close(fig)
# chart 2
p=A.sort_values('population_2025',ascending=False).reset_index(drop=True)
top=p.nlargest(5,'dG')
fig,ax=plt.subplots(figsize=(22,7),dpi=200)
cols=['#C55A11' if c in set(top.county) else '#9DC3E6' for c in p.county]
ax.bar(range(len(p)),p.dG,color=cols)
for i,r in p.iterrows():
    if r.county in set(top.county):
        ax.annotate(f"{r.county} {r.dG:+.2f}*",(i,r.dG),xytext=((28 if r.county=='Montgomery' else (-10 if r.county=='Wyandotte' else 0)),6),textcoords='offset points',ha='center',fontsize=9,color='#C00000',fontweight='bold',bbox=dict(boxstyle='round,pad=0.2',fc='white',ec='#C00000'))
ax.axhline(0,color='black',lw=0.8)
ax.set_xticks(range(len(p))); ax.set_xticklabels(p.county,rotation=90,fontsize=7)
ax.set_ylabel('ΔG (percentage points)'); ax.set_title('Kansas 2026* ΔG by Population: Ceiling Counties Highlighted\nGovernor race, 2022 vs 2026, all 105 counties, largest to smallest population',fontsize=14,fontweight='bold')
fig.text(0.01,0.005,'G = (Dem governor votes ÷ total governor votes × 100) − (Dem registered ÷ total registered × 100), active plus inactive. ΔG = G2026 − G2022. *2026 unofficial (Kansas SOS, updated 11/08/2026; certification scheduled Dec 1, 2026). Population: Census July 1, 2025.',fontsize=7)
ax.margins(x=0.005); fig.tight_layout(rect=(0,0.02,1,1)); fig.savefig(OUT+'KS_Ceiling_Counties_DeltaG_by_Population.png'); plt.close(fig)
json.dump(dict(gain_up=n_up,gain_down=n_dn,ceiling=[(r.county,round(r.dG,2)) for _,r in top.iterrows()]),open(OUT+'charts_pass1.json','w'))
print(n_up,n_dn,[(r.county,round(r.dG,2)) for _,r in top.iterrows()])
