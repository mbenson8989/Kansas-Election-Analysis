import csv, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
src='/workspace/kansas-elections/charts/kansas_deltaG_spec_by_county_population_sorted.csv'
r=list(csv.DictReader(open(src)))
rows=[]
for x in r:
    s22=float(x['D_votes_22'])/float(x['total_votes_22'])*100; s26=float(x['D_votes_26'])/float(x['total_votes_26'])*100
    d22=int(float(x['D_reg_22'])); d26=int(float(x['D_reg_26']))
    rows.append(dict(county=x['county'],population=int(x['population_2025']),dem_share_2022=round(s22,2),dem_share_2026=round(s26,2),
      change_2022_2026=round(s26-s22,2),dem_registered_2022=d22,dem_registered_2026=d26,dem_registration_change_2022_2026=d26-d22,
      dem_registration_pct_change=round((d26-d22)/d22*100,2),G_2022=round(float(x['G22']),2),G_2026=round(float(x['G26']),2),delta_G=round(float(x['dG']),2),status_2026='unofficial'))
out='/workspace/kansas-elections/KS governor stacked share with Dem registration loss.csv'
with open(out,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(sorted(rows,key=lambda d:-d['population']))
floor=min(rows,key=lambda d:d['dem_share_2022']); ceil=max(rows,key=lambda d:d['delta_G'])
maxloss=max(-d['dem_registration_change_2022_2026'] for d in rows)
def chart(data,title_sort,xlabel,fn):
    n=len(data); xs=np.arange(n)
    fig,ax=plt.subplots(figsize=(24,9.5))
    s22=np.array([d['dem_share_2022'] for d in data]); s26=np.array([d['dem_share_2026'] for d in data])
    up=s26>=s22
    base=np.where(up,s22,s26)
    ax.bar(xs,base,color='#3a6fd8',width=0.8,zorder=2)
    ax.bar(xs,np.where(up,s26-s22,0),bottom=s22,color='#f5a623',width=0.8,zorder=2)
    # 2022 level marker where share fell
    for i in np.where(~up)[0]:
        ax.plot([i-0.4,i+0.4],[s22[i],s22[i]],color='#3a6fd8',lw=1.4,zorder=3)
        ax.bar(i,s22[i]-s26[i],bottom=s26[i],color='none',edgecolor='#3a6fd8',lw=0.6,ls=':',width=0.8,zorder=2)
    ymax=max(s26.max(),s22.max())*1.15; neg=ymax*0.45
    ax.set_ylim(-neg,ymax); ax.axhline(0,color='k',lw=0.8)
    ax2=ax.twinx(); scale=maxloss*1.1/neg  # counts per share-pt
    ax2.set_ylim(-neg*scale,ymax*scale)
    loss=np.array([min(d['dem_registration_change_2022_2026'],0) for d in data])
    ax2.bar(xs,loss,color='#0b1f4d',width=0.6,zorder=2)
    yt=[t for t in ax2.get_yticks() if t<=0]; ax2.set_yticks(yt); ax2.set_yticklabels([f'{int(t):,}' for t in yt]); ax2.set_ylim(-neg*scale,ymax*scale)
    ax2.set_ylabel('Loss of registered Democrats, 2022→2026 (count, below 0)')
    for i,d in enumerate(data):
        if loss[i]<-0.35*maxloss: ax2.text(i,loss[i]-maxloss*0.03,f"{loss[i]:,}",ha='center',va='top',fontsize=6)
    ax.set_xticks(xs); ax.set_xticklabels(data and [d['county'] for d in data],rotation=90,fontsize=7)
    ax.set_xlim(-1,n)
    for d,kind,col in [(ceil,'CEILING',"#c00000"),(floor,'FLOOR','#1f4e9c')]:
        i=data.index(d); top=max(d['dem_share_2022'],d['dem_share_2026'])
        txt=(f"{kind}: {d['county']}\n2022 {d['dem_share_2022']:.1f}% → 2026 {d['dem_share_2026']:.1f}%\n"
             f"share change {d['change_2022_2026']:+.2f}, ΔG {d['delta_G']:+.2f}\nDem reg {d['dem_registration_change_2022_2026']:+,}")
        tx=min(max(i,8),n-9)
        ax.annotate(txt,(i,top),xytext=(tx,top+ymax*0.18),ha='center',fontsize=8,color=col,fontweight='bold',
            bbox=dict(boxstyle='square',fc='white',ec=col),arrowprops=dict(arrowstyle='->',color=col))
    ax.set_ylabel('Democratic vote share (%), total bar above 0 = 2026 share')
    ax.set_xlabel(xlabel)
    ax.set_title(f'Kansas Governor Race: Democratic Vote Share Gain (above 0) vs. Loss of Registered Democrats (below 0), 2022→2026 (sorted by {title_sort})',fontsize=12,fontweight='bold')
    ax.legend(handles=[Patch(color='#3a6fd8',label='2022 Democratic vote share (2026 share where it fell)'),
        Patch(color='#f5a623',label='Gain in Democratic vote share 2022→2026'),
        Patch(fc='none',ec='#3a6fd8',ls=':',label='Drop in Democratic vote share (dotted, top line = 2022)'),
        Patch(color='#0b1f4d',label='Loss of registered Democrats 2022→2026 (count, right axis)')],loc='upper right',fontsize=8)
    ax.grid(axis='y',alpha=0.25)
    fig.text(0.01,0.005,'Share = Dem votes ÷ total governor votes (all candidates; no clean county ballots-cast data for Kansas) × 100, both years. Registration = all registered Democrats (active + inactive), SOS Nov 1 2022 and Oct 1 2026. '
      'Navy bars only for counties that lost registered Democrats. Floor = lowest 2022 Dem share; ceiling = highest ΔG. ΔG = G2026 − G2022 (locked formula). 2026 unofficial (election night; certification Dec 1). Source: Kansas Secretary of State. Method: Morissa Benson.',fontsize=7.5,wrap=True)
    plt.tight_layout(rect=(0,0.03,1,1)); plt.savefig(fn,dpi=150); plt.close()
chart(sorted(rows,key=lambda d:-d['dem_share_2022']),'2022 Dem share','County (highest to lowest 2022 Democratic vote share)',
      '/workspace/kansas-elections/KS governor stacked share with Dem registration loss by 2022 Dem share.png')
chart(sorted(rows,key=lambda d:-d['population']),'population, largest to smallest','County (largest to smallest population)',
      '/workspace/kansas-elections/KS governor stacked share with Dem registration loss by population.png')
lost=[d for d in rows if d['dem_registration_change_2022_2026']<0]; up=[d for d in rows if d['change_2022_2026']>0]
print('floor',floor['county'],floor['dem_share_2022'],floor['delta_G'],'ceil',ceil['county'],ceil['delta_G'])
print('lost reg',len(lost),sum(d['dem_registration_change_2022_2026'] for d in lost),'net',sum(d['dem_registration_change_2022_2026'] for d in rows),'share up',len(up))
for d in sorted(rows,key=lambda d:d['dem_registration_change_2022_2026'])[:5]: print(d['county'],d['dem_registration_change_2022_2026'],d['dem_registration_pct_change'])
for d in sorted(rows,key=lambda d:-d['dem_registration_change_2022_2026'])[:4]: print(d['county'],d['dem_registration_change_2022_2026'])
print(ceil)
