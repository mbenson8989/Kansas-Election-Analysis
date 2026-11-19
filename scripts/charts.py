import pandas as pd, numpy as np, json, matplotlib, shutil, subprocess
matplotlib.use('Agg'); import matplotlib.pyplot as plt
R='/workspace/kansas-wiki/repo/'
o=pd.read_pickle('/tmp/ks_o.pkl'); J=json.load(open(R+'KS_results_summary.json')); K=J['K']; F=J['fits']
cap=list(K['top5']); flo=K['floor_counties']
NOTE='*2026 UNOFFICIAL: Kansas SOS election-night results (ent.sos.ks.gov, last updated 11/08/2026 9:15 PM); state certification due Dec 1, 2026.'
# ---------- 1. County slope chart (Nebraska style) ----------
fig,ax=plt.subplots(figsize=(10,12))
for c,r in o.iterrows():
    if c in cap or c in flo: continue
    ax.plot([0,1],[r.G22,r.G26],color='#bbbbbb',lw=0.8,alpha=0.8,zorder=1)
for c in flo:
    r=o.loc[c]; ax.plot([0,1],[r.G22,r.G26],color='#1f5fbf',lw=2.2,zorder=2,marker='o',ms=4)
for c in cap:
    r=o.loc[c]; ax.plot([0,1],[r.G22,r.G26],color='#e8590c',lw=3,zorder=3,marker='o')
def stack(items,gap):
    items=sorted(items,key=lambda t:t[1]); ys=[t[1] for t in items]
    for k in range(1,len(ys)): ys[k]=max(ys[k],ys[k-1]+gap)
    return [(t[0],y) for t,y in zip(items,ys)]
for c,y in stack([(c,o.loc[c,'G26']) for c in cap],0.75):
    ax.text(1.03,y,f"{c} {o.loc[c,'dG']:+.2f} pts",va='center',color='#b02a00',fontweight='bold',fontsize=10)
for c,y in stack([(c,o.loc[c,'G22']) for c in flo],0.62):
    ax.text(-0.03,y,f"{c} {o.loc[c,'dG']:+.2f} pts",va='center',ha='right',color='#1f4e9a',fontweight='bold',fontsize=9)
ax.set_xticks([0,1]); ax.set_xticklabels(['2022 (official)','2026* (unofficial)'],fontsize=12); ax.set_xlim(-0.5,1.5)
ax.set_ylabel('G = Dem vote share of governor votes − Dem registration share (points)')
ax.set_title('Kansas G 2022 to G 2026* — County Slope Chart\nGovernor race; 105 counties. Orange: 5 ceiling counties (largest ΔG). Blue: 10 floor counties\n(most Republican baseline). Labels show ΔG = G2026* − G2022.',fontsize=12)
ax.grid(axis='y',alpha=0.3)
fig.text(0.01,0.01,NOTE,fontsize=8)
plt.tight_layout(rect=(0,0.02,1,1)); plt.savefig(R+'KS_Slope_G2022_to_G2026_County_Slope_Chart.png',dpi=150); plt.close()
# ---------- 2. Forward surplus fit S = m*(D/100)+b ----------
fig,axs=plt.subplots(1,2,figsize=(14,6.5),sharey=True)
for ax,y,lab in ((axs[0],'22','2022 (official)'),(axs[1],'26','2026* (unofficial)')):
    f=F['20'+y]; x=o['D'+y]; s=o['G'+y]
    ax.scatter(x,s,s=18,color='#888',zorder=2)
    ax.scatter(o.loc[cap,'D'+y],o.loc[cap,'G'+y],s=40,color='#e8590c',zorder=3,label='ceiling (top-5 ΔG)')
    ax.scatter(o.loc[flo,'D'+y],o.loc[flo,'G'+y],s=30,color='#1f5fbf',zorder=3,label='floor (bottom cluster)')
    xx=np.linspace(x.min(),x.max(),50); ax.plot(xx,f['m']*xx/100+f['b'],color='black',lw=1.6,label=f"fit: S = {f['m']:.2f}·(D/100) + {f['b']:.2f}")
    ax.fill_between(xx,f['m']*xx/100+f['b']-f['resid_sd'],f['m']*xx/100+f['b']+f['resid_sd'],color='#999',alpha=0.15,label=f"±1 residual SD ({f['resid_sd']:.2f} pts)")
    for c in cap: ax.annotate(c,(o.loc[c,'D'+y],o.loc[c,'G'+y]),xytext=(4,3),textcoords='offset points',fontsize=8,color='#b02a00')
    ax.set_title(f"{lab}: R² = {f['r2']:.3f}, n = 105",fontsize=11); ax.set_xlabel('D = Democratic registration share (%)'); ax.grid(alpha=0.3); ax.legend(fontsize=8,loc='upper left')
axs[0].set_ylabel('S = Dem vote share − Dem registration share (points)')
fig.suptitle('Kansas forward surplus fit, least squares across 105 counties (governor votes denominator, both years)',fontsize=12)
fig.text(0.01,0.01,NOTE,fontsize=8); plt.tight_layout(rect=(0,0.03,1,0.96)); plt.savefig(R+'KS_Forward_Surplus_Fit_S_vs_D.png',dpi=140); plt.close()
# ---------- 3. existing Nebraska-style charts: regenerate from the verified CSV, then copy ----------
for s in ('stacked_regloss.py','deltaG_scatter_names.py'):
    subprocess.run(['python3','/workspace/kansas/'+s],check=True,cwd='/workspace/kansas',capture_output=True)
cp={'/workspace/kansas-elections/KS governor stacked share with Dem registration loss by 2022 Dem share.png':'KS_Stacked_Share_Reg_Loss_by_2022_Dem_Share.png',
    '/workspace/kansas-elections/KS governor stacked share with Dem registration loss by population.png':'KS_Stacked_Share_Reg_Loss_by_Population.png',
}
for a,b in cp.items(): shutil.copy(a,R+b)
print('ok')
subprocess.run(['python3','/workspace/kansas-wiki/scripts/scatter_wiki.py'],check=True,capture_output=True)
# ---------- 4. ΔG bars by population, ceiling / floor marked ----------
fig,ax=plt.subplots(figsize=(22,8)); xs=np.arange(len(o))
cols=['#e8590c' if c in cap else '#1f5fbf' if c in flo else '#9a9a9a' for c in o.index]
ax.bar(xs,o.dG,color=cols)
ax.axhline(0,color='k',lw=0.6); ax.axhline(K['median_dG'],ls='--',color='gray',lw=1,label=f"County median ΔG {K['median_dG']:+.2f} (mean {K['mean_dG']:+.2f})")
ax.axhline(K['floor_median'],ls=':',color='#1f5fbf',lw=1.4,label=f"Floor constant (median ΔG of 10 floor counties) {K['floor_median']:+.2f}")
ax.axhline(K['ceiling3_median'],ls=':',color='#b02a00',lw=1.4,label=f"Ceiling constant (median ΔG, Johnson/Sedgwick/Wyandotte) {K['ceiling3_median']:+.2f}")
for c in cap:
    i=list(o.index).index(c); ax.text(i,o.loc[c,'dG']+0.3,f"{o.loc[c,'dG']:+.2f}",ha='center',fontsize=8,color='#b02a00',fontweight='bold')
ax.bar([0],[0],color='#e8590c',label='Ceiling counties: 5 largest ΔG'); ax.bar([0],[0],color='#1f5fbf',label='Floor counties: most Republican baseline (bottom cluster)')
ax.set_xticks(xs); ax.set_xticklabels([f"{c} {p:,}" for c,p in zip(o.index,o.population_2025)],rotation=90,fontsize=7); ax.set_xlim(-1,len(o))
ax.set_ylabel('ΔG = G2026* − G2022 (points)'); ax.grid(axis='y',alpha=0.25); ax.legend(fontsize=9,loc='upper right')
ax.set_title('Kansas governor ΔG by county, largest to smallest population (locked formula, governor-votes denominator both years)',fontsize=13,fontweight='bold')
fig.text(0.01,0.005,NOTE,fontsize=8); plt.tight_layout(rect=(0,0.02,1,1)); plt.savefig(R+'KS_DeltaG_Bars_by_Population.png',dpi=140); plt.close()
print('ok2')
