"""Check every number in the appended sections against values recomputed here from PASS B outputs (exact-fraction pass + pass B county table)."""
import csv, re, json, numpy as np
from fractions import Fraction as F
V='/workspace/kansas-wiki/verification/'; A='/workspace/kansas-wiki/addendum/'
key=lambda s:re.sub(r'[^a-z]','',s.lower())
names={key(r['county']):r['county'] for r in csv.DictReader(open(V+'passA_counties.csv'))}
B={names[r['key']]:r for r in csv.DictReader(open(V+'passB_counties.csv'))}
RB={names[r['key']]:r for r in csv.DictReader(open(V+'residB_counties.csv'))}; SB=json.load(open(V+'residB_statewide.json'))
vals=set(); CV={}
def add(x,b=None):
    x=abs(float(x)); t=vals if b is None else CV.setdefault(b,set())
    for d in (0,1,2,3): t.add(f"{x:.{d}f}")
C={}
for c,r in B.items():
    I=lambda k:int(r[k]); d=dict(pop=I('population_2025'),DR22=I('D_reg_22'),DR26=I('D_reg_26'),N26=I('total_votes_26'),DV26=I('D_votes_26'),
       D22=100*I('D_reg_22')/I('total_reg_22'),D26=100*I('D_reg_26')/I('total_reg_26'),S22=100*I('D_votes_22')/I('total_votes_22'),S26=100*I('D_votes_26')/I('total_votes_26'))
    d.update({k:float(RB[c][k]) for k in ('exp_loss','residual','dG','offset_votes','gap_votes_ne')}); C[c]=d
    for v in d.values(): add(v,c)
for k,v in SB.items():
    if isinstance(v,dict):
        for c in v.values(): [add(x) for x in c.values()]
    else: add(v)
tot=lambda k:sum(int(r[k]) for r in B.values())
S22=100*tot('D_votes_22')/tot('total_votes_22'); S26=100*tot('D_votes_26')/tot('total_votes_26'); D22=100*tot('D_reg_22')/tot('total_reg_22'); D26=100*tot('D_reg_26')/tot('total_reg_26')
for v in (S22,S26,D22,D26,(S26-D26)-(S22-D22),tot('total_votes_26'),tot('D_votes_26')-tot('D_votes_22'),tot('other_votes_22'),tot('D_votes_26')-tot('D_votes_22')-SB['offset_votes_pooled']): add(v)
res=np.array([C[c]['residual'] for c in C]); dG=np.array([C[c]['dG'] for c in C]); el=np.array([C[c]['exp_loss'] for c in C])
for v in (np.median(res),res.mean(),res.std(ddof=1),(res>0).sum(),(res<0).sum(),sum(1 for c in B if int(B[c]['D_reg_26'])>=int(B[c]['D_reg_22']))): add(v)
X=np.c_[np.ones(105),el]; beta=np.linalg.lstsq(X,dG,rcond=None)[0]; e=dG-X@beta; se=np.sqrt(np.diag(e@e/103*np.linalg.inv(X.T@X)))
for v in (*beta,se[1],1-e@e/((dG-dG.mean())**2).sum()): add(v)
hi=[c for c in C if C[c]['S22']>S22]; add(100*sum(int(B[c]['total_votes_22']) for c in hi)/tot('total_votes_22')); add(100*sum(int(B[c]['total_votes_26']) for c in hi)/tot('total_votes_26'))
CR=json.load(open(V+'resid_compare_report.json')); add(CR['figures_compared'])
STRUCT={'100','2022','2026','105','1','2','3','4','5','6','12','19','11','08','9','15','16','0'}
H={'Population':'pop','Expected loss (pts)':'exp_loss','ΔG*':'dG','Residual* (pts)':'residual','Total gov votes 2026*':'N26','Backward-solved offset votes*':'offset_votes','Gap in votes* (NE comparison)':'gap_votes_ne'}
issues=[]; unmatched=[]; ncell=nrow=ntok=0
TOK=re.compile(r'(?<![\w.])[+−-]?\d[\d,]*(?:\.\d+)?')
WK='/workspace/kansas-wiki/wikiclone/'
def section(page,marker,stop=('---',)):
    L=open(WK+page).read().split('\n'); i=next(k for k,l in enumerate(L) if l.startswith(marker)); out=[]
    for l in L[i:]:
        if page=='Home.md' and l.strip() in stop: break   # Home: the section ends at the page footer
        out.append(l+'\n')
    return out
SECT={'Reverse-Math.append.md':section('Reverse-Math.md','## Expected-Loss Residual and Backward-Solved'),'Home.append.md':section('Home.md','## Added Nov 19, 2026: expected-loss')}
pairs=set()
for fn in ('Reverse-Math.append.md','Home.append.md'):
    hdr=None; ctx=set()
    for line in SECT[fn]:
        if line.startswith('|') and not line.startswith('|---'):
            cells=[x.strip().replace('\\','') for x in line.strip().strip('|').split('|')]
            if cells[0]=='County': hdr=cells; continue
            cn=cells[0].replace(' †','')
            if hdr and cn in C:
                nrow+=1
                for h,v in zip(hdr,cells):
                    if h in H:
                        ncell+=1; pairs.add((cn,H[h])); exp=C[cn][H[h]]; got=float(v.replace('*','').replace('−','-').replace(',','').replace('+',''))
                        tol=0.5000001 if H[h] in ('offset_votes','gap_votes_ne') else (0.005000001 if H[h] in('exp_loss','dG','residual') else 0)
                        if abs(got-exp)>tol: issues.append((fn,cn,h,v,exp))
                    if h in('Dem reg 2022 → 2026','Dem reg share 2022 → 2026'):
                        ncell+=1; pairs.add((cn,h)); a,b=[float(x.replace('%','').replace(',','')) for x in v.split('→')]
                        ea,eb=(C[cn]['DR22'],C[cn]['DR26']) if 'share' not in h else (C[cn]['D22'],C[cn]['D26'])
                        if abs(a-ea)>0.005000001 or abs(b-eb)>0.005000001: issues.append((fn,cn,h,v,(ea,eb)))
        if line.startswith('#'): ctx={c for c in C if re.search(r'\b'+re.escape(c)+r'\b',line)}
        here={c for c in C if re.search(r'\b'+re.escape(c)+r'\b',line)}|ctx
        allowed=set(vals)
        for c in here: allowed|=CV[c]
        txt=re.sub(r'\]\([^)]*\)','] ',line); txt=re.sub(r'https?://\S+','',txt); txt=re.sub(r'`[^`]*`','',txt)
        txt=re.sub(r'\d{1,2}/\d{1,2}/\d{4}','',txt); txt=re.sub(r'\d{1,2}:\d{2}','',txt); txt=re.sub(r'(Nov|Oct|Dec) \d{1,2}','',txt)
        for m in TOK.finditer(txt):
            t=m.group(0); ntok+=1; core=t.lstrip('+−-').replace(',','')
            if core in STRUCT or core in allowed: continue
            unmatched.append((fn,t,txt[max(0,m.start()-60):m.end()+15].strip()))
rep=dict(county_field_pairs=len(pairs),table_rows=nrow,table_cells=ncell,cell_mismatches=issues,tokens=ntok,unmatched=unmatched,PASS=not issues and not unmatched)
json.dump(rep,open(V+'addendum_number_check.json','w'),indent=1,default=str)
print({k:rep[k] for k in ('county_field_pairs','table_rows','table_cells','tokens','PASS')},len(issues),len(unmatched))
for u in unmatched[:40]: print(u)
for i in issues[:20]: print(i)
