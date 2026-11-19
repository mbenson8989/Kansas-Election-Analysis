# Wiki copy of /workspace/kansas/deltaG_scatter_names.py: reads the verified pass-A table; orange dots relabelled 'Bottom 5 ΔG'
import csv, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import stats
r=list(csv.DictReader(open('/workspace/kansas-wiki/verification/passA_counties.csv')))
r.sort(key=lambda x:-int(x['population_2025']))
names=[x['county'] for x in r]; pop=np.array([int(x['population_2025']) for x in r]); dg=np.array([float(x['dG']) for x in r])
# verify locked formula from raw columns
for x,d in zip(r,dg):
    g22=float(x['D_votes_22'])/float(x['total_votes_22'])*100-float(x['D_reg_22'])/float(x['total_reg_22'])*100
    g26=float(x['D_votes_26'])/float(x['total_votes_26'])*100-float(x['D_reg_26'])/float(x['total_reg_26'])*100
    assert abs((g26-g22)-d)<0.001, x['county']
lp=np.log10(pop); res=stats.linregress(lp,dg)
n=len(r); xs=np.arange(n)
fig,ax=plt.subplots(figsize=(22,8))
floor=['Russell','Jewell','Marshall','Ottawa','Chase']
cols=['#d62728' if c=='Seward' else '#ff7f0e' if c in floor else '#1f77b4' for c in names]
ax.scatter(xs,dg,c=cols,s=[110 if c=='Seward' or c in floor else 38 for c in names],edgecolor='k',linewidth=0.5,zorder=3)
ax.plot(xs,res.intercept+res.slope*lp,'k-',lw=2,zorder=2,label=f'Trend vs log population: {res.slope:+.2f} pts per 10× population (R² = {res.rvalue**2:.3f}, p = {res.pvalue:.1e})')
m=dg.mean(); ax.axhline(m,ls='--',color='gray',lw=1,label=f'Statewide mean ΔG {m:+.2f} (median {np.median(dg):+.2f})')
ax.axhline(0,color='k',lw=0.6)
i=names.index('Seward'); ax.annotate(f'Ceiling callout: Seward {dg[i]:+.2f}',(i,dg[i]),xytext=(i+4,dg[i]-0.5),fontsize=11,fontweight='bold',color='#d62728',arrowprops=dict(arrowstyle='-',color='#d62728'))
for c in floor:
    i=names.index(c); ax.annotate(f'{c} {dg[i]:+.2f}',(i,dg[i]),xytext=(0,-14),textcoords='offset points',ha='center',fontsize=8,color='#b35900')
ax.scatter([],[],c='#ff7f0e',edgecolor='k',s=110,label='Bottom 5 ΔG: Russell, Jewell, Marshall, Ottawa, Chase')
ax.scatter([],[],c='#d62728',edgecolor='k',s=110,label='Ceiling callout: Seward')
ax.set_xticks(xs); ax.set_xticklabels([f'{c} {p:,}' for c,p in zip(names,pop)],rotation=90,fontsize=7)
ax.set_xlim(-1,n); ax.set_ylabel('Delta-G (2026 G − 2022 G), percentage points')
ax.set_title('Kansas Statewide: Delta-G by county, largest to smallest population (Locked Formula)',fontsize=14,fontweight='bold')
ax.grid(alpha=0.25); ax.legend(loc='upper right',fontsize=9)
fig.text(0.01,0.005,'G = [(Vp ÷ Vt) × 100] − [(Rp ÷ Rt) × 100]; Vt = total governor votes, all candidates (no county write-ins reported); Rt = all registered voters (active + inactive). ΔG = G2026 − G2022. '
 '2026* UNOFFICIAL (SOS election night, last updated 11/08/2026 9:15 PM, all 105 counties; certification Dec 1). Registration Nov 1 2022 / Oct 1 2026. Population: Census July 1 2025. Source: Kansas Secretary of State.',fontsize=8)
plt.tight_layout(rect=(0,0.02,1,1))
out='/workspace/kansas-wiki/repo/KS_DeltaG_by_Population_Scatter_Names.png'
plt.savefig(out,dpi=150); print(out, n, res.slope, res.rvalue**2, res.pvalue, m)
