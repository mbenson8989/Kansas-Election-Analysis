"""US House KS-1..KS-4 removal simulation, PASS 1 (BeautifulSoup; residual votes from pass1.json)."""
import json, glob, os
from fractions import Fraction as F
from bs4 import BeautifulSoup
ENT='/workspace/kansas-wiki/verification/ent_refetch_20261119/'
P1=json.load(open('pass1.json')); RV={c:v['resid_votes'] for c,v in P1['counties'].items()}
nm=lambda s: str(s).strip().title().replace('Mcpherson','McPherson')
H={}; STATE={}
for f in sorted(glob.glob(ENT+'*.html')):
    c=nm(os.path.basename(f)[:-5]); pane=BeautifulSoup(open(f).read(),'html.parser').find(id='party-county-all')
    for race in pane.find_all('div',class_='race'):
        h=race.find('h3').get_text(strip=True)
        if not h.startswith('United States House of Representatives'): continue
        d=int(h.split()[-1]); rows={}
        for row in race.find('div',class_='race-candidate-list').find_all('div',class_='row',recursive=False):
            ps=[p.get_text(strip=True) for p in row.find_all('p')]
            if len(ps)==5: rows[ps[0]]=int(ps[1].replace(',','')); STATE.setdefault(d,{})[ps[0]]=int(ps[3].replace(',',''))
        H.setdefault(c,{})[d]=rows
assert len(H)==105
def alloc(k,tot):  # largest remainder, sign preserved; ties -> lower district
    if k==0: return {d:0 for d in tot}
    s=1 if k>0 else -1; a=abs(k); T=sum(tot.values()); ex={d:F(a*t,T) for d,t in tot.items()}
    base={d:int(x) for d,x in ex.items()}; left=a-sum(base.values())
    for d in sorted(tot,key=lambda d:(-(ex[d]-base[d]),d))[:left]: base[d]+=1
    return {d:s*v for d,v in base.items()}
A={}
for c in H:
    tot={d:sum(r.values()) for d,r in H[c].items()}
    A[c]={'pos':alloc(max(RV[c],0),tot),'all':alloc(RV[c],tot),'tot':tot}
OUT={'state_page':{str(d):v for d,v in STATE.items()},'districts':{},'split':{c:{k:{str(d):x for d,x in v.items()} for k,v in A[c].items()} for c in A if len(H[c])>1}}
for d in sorted(STATE):
    cand=list(STATE[d]); Dc=[x for x in cand if x[:2]=='D-'][0]; Rc=[x for x in cand if x[:2]=='R-'][0]
    cs=[c for c in H if d in H[c]]
    assert all(sum(H[c][d][x] for c in cs)==STATE[d][x] for x in cand)
    res={'candidates':cand,'counties':len(cs),'removed_pos':sum(A[c]['pos'][d] for c in cs),'net_all':sum(A[c]['all'][d] for c in cs)}
    for key,sc,mode in (('baseline',None,'remove'),('positive_only|remove','pos','remove'),('positive_only|reassign','pos','reassign'),('all_residuals|remove','all','remove'),('all_residuals|reassign','all','reassign')):
        D=R=T=0
        for c in cs:
            k=A[c][sc][d] if sc else 0; x=H[c][d]
            D+=x[Dc]-k; R+=x[Rc]+(k if mode=='reassign' else 0); T+=sum(x.values())-(k if mode=='remove' else 0)
        res[key]=dict(D=D,R=R,total=T,D_share=float(F(100*D,T)),R_share=float(F(100*R,T)),margin_pts=float(F(100*(D-R),T)),margin_votes=D-R)
    OUT['districts'][str(d)]=res
OUT['county_house']={c:{str(d):r for d,r in H[c].items()} for c in H}
json.dump(OUT,open('house_pass1.json','w'),indent=1)
for d,v in OUT['districts'].items(): print(d,v['candidates'],v['counties'],v['removed_pos'],v['net_all'],[(k,round(v[k]['margin_pts'],2),v[k]['margin_votes']) for k in v if isinstance(v[k],dict)])
print(OUT['split'])
