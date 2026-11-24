"""Removal simulation PASS 1: BeautifulSoup parse of the raw SOS ENT county pages + pandas registration/population.
Exact Fraction arithmetic. Residual uses the published Locked constants m=67.6004, b=6.3014."""
import json, glob, os
from fractions import Fraction as F
import pandas as pd
from bs4 import BeautifulSoup
ENT='/workspace/kansas-wiki/verification/ent_refetch_20261119/'; RAW='/workspace/kansas/raw/'
RACES={'Governor / Lt. Governor':'Governor','United States Senate':'US Senate','Secretary of State':'Secretary of State',
       'State Treasurer':'State Treasurer','Commissioner of Insurance':'Commissioner of Insurance'}  # Attorney General excluded by design
nm=lambda s: str(s).strip().title().replace('Mcpherson','McPherson')
V={}; CAND={}; STATE={}
for f in sorted(glob.glob(ENT+'*.html')):
    c=nm(os.path.basename(f)[:-5]); s=BeautifulSoup(open(f).read(),'html.parser')
    pane=s.find(id='party-county-all'); V[c]={}
    for race in pane.find_all('div',class_='race'):
        h=race.find('h3').get_text(strip=True)
        if h not in RACES: continue
        rows={}
        for row in race.find('div',class_='race-candidate-list').find_all('div',class_='row',recursive=False):
            ps=[p.get_text(strip=True) for p in row.find_all('p')]
            if len(ps)==5:
                rows[ps[0]]=int(ps[1].replace(',','')); STATE.setdefault(RACES[h],{})[ps[0]]=int(ps[3].replace(',',''))
        V[c][RACES[h]]=rows; CAND.setdefault(RACES[h],list(rows))
assert len(V)==105
r=pd.read_excel(RAW+'10-2026-Voter-Registration-Numbers-by-County.xlsx',sheet_name='By County')
r=r[r.County!='Grand Total'].dropna(subset=['County']); r=r.assign(c=r.County.map(nm)).set_index('c')
p=pd.read_csv(RAW+'co-est2025-alldata.csv',encoding='latin-1'); p=p[(p.STATE==20)&(p.COUNTY>0)]
p=p.assign(c=p.CTYNAME.str.replace(' County','').map(nm)).set_index('c').POPESTIMATE2025
M=F('67.6004'); B=F('6.3014')
def rnd(x): # round half away from zero
    q=abs(x); n=int(q); n+= (q-n)>=F(1,2); return n if x>=0 else -n
C={}
for c in V:
    g=V[c]['Governor']; D=[v for k,v in g.items() if k.startswith('D-')][0]; T=sum(g.values())
    dreg=int(r.loc[c,'Democratic']); treg=int(r.loc[c,'Total'])
    Dsh=F(100*dreg,treg); S=F(100*D,T)-Dsh; fit=M*Dsh/100+B; res=S-fit
    C[c]=dict(pop=int(p[c]),dreg=dreg,treg=treg,D=float(Dsh),S=float(S),fit=float(fit),resid_pts=float(res),resid_votes_exact=float(res*T/100),resid_votes=rnd(res*T/100),gov_total=T)
# refit check
xs=[F(100*C[c]['dreg'],C[c]['treg'])/100 for c in sorted(C)]
ys=[F(100*[v for k,v in V[c]['Governor'].items() if k.startswith('D-')][0],C[c]['gov_total'])-F(100*C[c]['dreg'],C[c]['treg']) for c in sorted(C)]
n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
m=sum((x-mx)*(y-my) for x,y in zip(xs,ys))/sum((x-mx)**2 for x in xs); b=my-m*mx
REF=dict(m_refit=float(m),b_refit=float(b),m_used=float(M),b_used=float(B))
def agg(race, sel, mode):
    """sel(r)->signed votes removed from D; mode 'remove' (total shrinks) or 'reassign' (to R)."""
    Dc=[k for k in CAND[race] if k.startswith('D-')][0]; Rc=[k for k in CAND[race] if k.startswith('R-')][0]
    d=rr=t=0
    for c in V:
        x=V[c][race]; k=sel(C[c]['resid_votes']); dd=x[Dc]-k; rv=x[Rc]+(k if mode=='reassign' else 0); tt=sum(x.values())-(k if mode=='remove' else 0)
        d+=dd; rr+=rv; t+=tt
    return dict(D=d,R=rr,total=t,D_share=float(F(100*d,t)),R_share=float(F(100*rr,t)),margin_pts=float(F(100*(d-rr),t)),margin_votes=d-rr)
OUT={'constants':REF,'candidates':CAND,'state_page_totals':STATE,'counties':C,'races':{}}
for race in RACES.values():
    OUT['races'][race]={'baseline':agg(race,lambda v:0,'remove')}
    for scen,sel in (('positive_only',lambda v:max(v,0)),('all_residuals',lambda v:v)):
        for mode in ('remove','reassign'):
            OUT['races'][race][f'{scen}|{mode}']=agg(race,sel,mode)
    # county sums equal state page totals?
    OUT['races'][race]['county_sum_matches_state_page']=all(sum(V[c][race][k] for c in V)==STATE[race][k] for k in CAND[race])
OUT['sum_pos_votes']=sum(max(C[c]['resid_votes'],0) for c in C); OUT['sum_neg_votes']=sum(min(C[c]['resid_votes'],0) for c in C)
OUT['sum_all_votes']=OUT['sum_pos_votes']+OUT['sum_neg_votes']; OUT['n_pos']=sum(C[c]['resid_votes']>0 for c in C)
OUT['sum_resid_pts']=float(sum(F(C[c]['resid_pts']) for c in C))
OUT['county_race']={c:{race:V[c][race] for race in RACES.values()} for c in V}
json.dump(OUT,open('pass1.json','w'),indent=1)
print(json.dumps(REF)); print('pos',OUT['sum_pos_votes'],'neg',OUT['sum_neg_votes'],'n_pos',OUT['n_pos'])
for race,d in OUT['races'].items():
    print(race, d['county_sum_matches_state_page'])
    for k,v in d.items():
        if isinstance(v,dict): print('  ',k,round(v['D_share'],2),round(v['R_share'],2),round(v['margin_pts'],2),v['margin_votes'])
