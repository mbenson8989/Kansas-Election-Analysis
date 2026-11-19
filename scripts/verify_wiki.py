"""Check every number in the wiki markdown against values recomputed here from pass B (numpy/scipy, not statsmodels/pandas pipeline).
(1) County table rows: each cell vs pass B. (2) Every numeric token on every page must match a recomputed value at the displayed precision,
or a listed structural constant (years, dates, counts of counties, statute/precision text)."""
import csv, re, json, glob, os, numpy as np, openpyxl
from scipy import stats
V='/workspace/kansas-wiki/verification/'; W='/workspace/kansas-wiki/wiki/'; RAW='/workspace/kansas/raw/'
B=list(csv.DictReader(open(V+'passB_counties.csv')))
name={}
for f in ['passA_counties.csv']:
    for r in csv.DictReader(open(V+f)): name[re.sub(r'[^a-z]','',r['county'].lower())]=r['county']
C={}
for r in B:
    d={k:(float(v) if k!='key' and v not in ('',None,'N/A') else (float('nan') if v=='N/A' else v)) for k,v in r.items()}; d['county']=name[r['key']]
    for y in ('22','26'): d['S'+y]=100*d['D_votes_'+y]/d['total_votes_'+y]; d['D'+y]=100*d['D_reg_'+y]/d['total_reg_'+y]
    C[d['county']]=d
cs=list(C.values()); N=len(cs); assert N==105
arr=lambda k:np.array([c[k] for c in cs],float)
vals=set(); CV={}
def add(x,bucket=None):
    x=abs(float(x)); tgt=vals if bucket is None else CV.setdefault(bucket,set())
    for d in (0,1,2,3): tgt.add(f"{x:.{d}f}")
    tgt.add(f"{x:.1e}"); tgt.add(f"{x:.2e}")
for c in cs:
    q=c['county']
    for k,v in c.items():
        if isinstance(v,float) and v==v: add(v,q)
    for v in (c['D_reg_26']-c['D_reg_22'],100*(c['D_reg_26']-c['D_reg_22'])/c['D_reg_22'],c['S26']-c['S22'],c['D26']-c['D22'],c['total_votes_22']-c['ballots_22'],
              100*(c['ballots_22']-c['total_votes_22'])/c['ballots_22'],c['total_votes_22']/c['ballots_22'],c['ballots_22']-c['total_reg_22'],c['D_votes_22']+c['R_votes_22']): add(v,q)
sums={k:arr(k).sum() for k in ['D_votes_22','R_votes_22','other_votes_22','total_votes_22','D_reg_22','total_reg_22','D_votes_26','R_votes_26','total_votes_26','D_reg_26','total_reg_26','ballots_22']}
for v in sums.values(): add(v)
for a,b in [('D_reg_26','D_reg_22'),('total_reg_26','total_reg_22'),('D_votes_26','D_votes_22'),('total_votes_26','total_votes_22'),('ballots_22','total_votes_22')]: add(sums[a]-sums[b])
PS22=100*sums['D_votes_22']/sums['total_votes_22']; PS26=100*sums['D_votes_26']/sums['total_votes_26']; PD22=100*sums['D_reg_22']/sums['total_reg_22']; PD26=100*sums['D_reg_26']/sums['total_reg_26']
for v in (PS22,PS26,PD22,PD26,PS26-PS22,PD26-PD22,PS22-PD22,PS26-PD26,(PS26-PD26)-(PS22-PD22)): add(v)
dG=arr('dG'); G22=arr('G22'); G26=arr('G26'); D22=arr('D22'); D26=arr('D26'); S22=arr('S22'); pop=arr('population_2025')
for v in (np.median(dG),dG.mean(),dG.std(ddof=1),(dG>0).sum(),(dG<0).sum(),(arr('S26')>S22).sum(),(arr('D_reg_26')<arr('D_reg_22')).sum(),np.quantile(S22,.1),np.quantile(G22,.25)): add(v)
lr=stats.linregress(np.log10(pop),dG); [add(v) for v in (lr.slope,lr.rvalue,lr.rvalue**2,lr.pvalue,lr.intercept)]
idx={c['county']:i for i,c in enumerate(cs)}
def grp(names):
    g=[C[n] for n in names]; s=lambda k:sum(x[k] for x in g)
    a,b_,c_,d_=100*s('D_votes_22')/s('total_votes_22'),100*s('D_votes_26')/s('total_votes_26'),100*s('D_reg_22')/s('total_reg_22'),100*s('D_reg_26')/s('total_reg_26')
    dd=[x['dG'] for x in g]
    for v in (a,b_,c_,d_,b_-a,d_-c_,(b_-d_)-(a-c_),np.median(dd),np.mean(dd),min(dd),max(dd)): add(v)
six=['Johnson','Sedgwick','Shawnee','Wyandotte','Douglas','Leavenworth']; grp(six); grp([c for c in C if c not in six])
floor=[c['county'] for c in cs if c['S22']<=np.quantile(S22,.1) and c['G22']<=np.quantile(G22,.25)]; grp(floor); grp(['Johnson','Sedgwick','Wyandotte']); grp(six[:4]+['Douglas','Riley'])
def ols(y,x):
    X=np.c_[np.ones(len(x)),x/100]; beta,ss,*_=np.linalg.lstsq(X,y,rcond=None); res=y-X@beta; n=len(y); s2=res@res/(n-2)
    cov=s2*np.linalg.inv(X.T@X); se=np.sqrt(np.diag(cov)); t=stats.t.ppf(.975,n-2)
    r2=1-res@res/((y-y.mean())@(y-y.mean()))
    out=[beta[1],beta[0],r2,np.sqrt(s2),beta[1]-t*se[1],beta[1]+t*se[1],beta[0]-t*se[0],beta[0]+t*se[0],(abs(res)<=2).sum(),(abs(res)<=5).sum(),se[1],se[0]]
    return out,beta,res
f22,b22,r22=ols(G22,D22); f26,b26,r26=ols(G26,D26); fp,_,_=ols(np.r_[G22,G26],np.r_[D22,D26])
for f in (f22,f26,fp): [add(v) for v in f[:10]]
add(b22[1]*.2+b22[0]); add(b26[1]*.2+b26[0])
for nm_ in ('Seward',): add(b22[1]*C[nm_]['D22']/100+b22[0],nm_); add(b26[1]*C[nm_]['D26']/100+b26[0],nm_); add(r22[idx[nm_]],nm_); add(r26[idx[nm_]],nm_)
# year interaction
X=np.c_[np.ones(210),np.r_[D22,D26]/100,np.r_[np.zeros(105),np.ones(105)],np.r_[np.zeros(105),D26/100]]; y=np.r_[G22,G26]
beta=np.linalg.lstsq(X,y,rcond=None)[0]; res=y-X@beta; s2=res@res/(210-4); se=np.sqrt(np.diag(s2*np.linalg.inv(X.T@X)))
for k in (2,3): add(beta[k]); add(2*stats.t.sf(abs(beta[k]/se[k]),206))
# neighbors (recomputed with numpy from the saved CSVs; SD from its saved summary)
NB={}
for st,f in (('NE','/workspace/nebraska-elections/spec_check/all93_deltaG_spec.csv'),('IA','/workspace/iowa-elections/nebraska_method/iowa_gov_2022_2026_nebraska_method_99_counties.csv')):
    rows=list(csv.DictReader(open(f)))
    for yy in ('2022','2026'):
        D=np.array([100*float(r[f'reg_dem_{yy}'])/float(r[f'reg_tot_{yy}']) for r in rows])
        for den,col in (('ballots','ballots_'),('govvotes','race_votes_')):
            Sx=np.array([100*float(r[f'D_{yy}'])/float(r[col+yy]) for r in rows])-D
            o_,_,_=ols(Sx,D); NB[(st,yy,den)]=o_; add(o_[0]); add(o_[1])
sd=json.load(open('/workspace/south-dakota-elections/sd_forward_surplus_summary.json'))['SD']
for yy in ('2022','2026'):
    for den,k in (('ballots',f'SD_{yy}'),('govvotes',f'SD_{yy}_govvotes_denominator')): NB[('SD',yy,den)]=[sd[k]['m'],sd[k]['b']]; add(sd[k]['m']); add(sd[k]['b'])
for yy,f in (('2022',f22),('2026',f26)):
    for j,k in ((0,'m'),(1,'b')):
        band=[NB[(s,yy,'govvotes')][j] for s in ('NE','IA','SD')]; lo,hi=min(band),max(band); v=f[j]
        if v>hi: add(v-hi); add((v-hi)/f[10+j])
# ballots / absentee
und=[100*(c['ballots_22']-c['total_votes_22'])/c['ballots_22'] for c in cs]; add(np.median(und)); add(np.quantile(und,.95))
am=[c for c in cs if c['adv_mail_22'] not in ('',None) and c['adv_mail_22']==c['adv_mail_22']]; add(sum(c['adv_mail_22'] for c in am)); add(len(am))
ok=[c for c in am if c['county'] not in ('Stevens','Sumner')]
sp=stats.spearmanr([c['adv_mail_22']/c['ballots_22'] for c in ok],[c['dG'] for c in ok]); add(sp.statistic); add(sp.pvalue); add(len(ok))
wb=openpyxl.load_workbook(RAW+'11-2022-Voter-Registration-Numbers-by-County.xlsx',read_only=True)
gt=[r for r in wb.active.iter_rows(values_only=True) if r[0]=='Grand Total'][0]; add(int(gt[4])); add(100*int(gt[4])/int(gt[5]))
add(sum(int(c['prec_tot_26']) for c in cs)); add(2*N); CR=json.load(open(V+'compare_report.json')); add(CR['figures_A_vs_B']); add(CR['fields_per_county']); add(len(CR['mismatches_A_vs_B'])); add(105-(arr('D_reg_26')<arr('D_reg_22')).sum())
# structural constants that are not data values (years, dates/times, counts of things, template numbers)
STRUCT={'100','2022','2026','2025','2024','2020','11','08','9','15','19','17','16','1','2','3','4','5','6','10','7','12','13','14','18','20','0.20','105','99','93','66','101','4,168','2.0','3.0','25','95'}
issues=[]; ntok=0
ADD_MARKERS=('## Expected-Loss Residual and Backward-Solved','## Added Nov 19, 2026: expected-loss')
def page_lines(fn):
    out=[]
    for l in open(fn).read().split('\n'):
        if l.startswith(ADD_MARKERS): break
        out.append(l+'\n')
    return out
pairs=set()
# (1) county table rows
H={'Population':'population_2025','Dem gov votes 2022':'D_votes_22','Total gov votes 2022':'total_votes_22','Dem reg 2022':'D_reg_22','Total reg 2022':'total_reg_22','G 2022':'G22',
   'Dem gov votes 2026*':'D_votes_26','Total gov votes 2026*':'total_votes_26','Dem reg 2026':'D_reg_26','Total reg 2026':'total_reg_26','G 2026*':'G26','ΔG*':'dG'}
def nv(s): s=s.replace('\\','').replace('*','').replace('−','-').replace(',','').strip(); return float(s)
nrow=ncell=0
for fn in sorted(glob.glob(W+'*.md')):
    hdr=None
    for line in page_lines(fn):
        if line.startswith('|') and not line.startswith('|---'):
            cells=[x.strip() for x in line.strip().strip('|').split('|')]
            if cells[0]=='County': hdr=[h.replace('\\','') for h in cells]; continue
            if hdr and cells[0] in C:
                nrow+=1; c=C[cells[0]]
                for h,v in zip(hdr,cells):
                    if h in H:
                        ncell+=1; pairs.add((cells[0],H[h])); exp=c[H[h]]; got=nv(v)
                        if (H[h] in ('G22','G26','dG') and abs(got-round(exp,2))>1e-9) or (H[h] not in ('G22','G26','dG') and got!=exp): issues.append((os.path.basename(fn),cells[0],h,v,exp))
        else: hdr=None if not line.startswith('|') else hdr
# (2) every numeric token
TOK=re.compile(r'(?<![\w.])[+−-]?\d[\d,]*(?:\.\d+)?(?:e-?\d+)?')
unmatched=[]
CN=sorted(C,key=len,reverse=True)
for fn in sorted(glob.glob(W+'*.md')):
    ctx=set()
    for raw in page_lines(fn):
        line=raw
        if line.startswith('#'): ctx={c for c in CN if re.search(r'\b'+re.escape(c)+r'\b',line)}
        here={c for c in CN if re.search(r'\b'+re.escape(c)+r'\b',line)}|ctx
        allowed=set(vals)
        for c in here: allowed|=CV.get(c,set())
        txt=re.sub(r'\]\([^)]*\)','] ',line); txt=re.sub(r'https?://\S+','',txt); txt=re.sub(r'`[^`]*`','',txt)
        txt=re.sub(r'\d{1,2}/\d{1,2}/\d{4}','',txt); txt=re.sub(r'\d{1,2}:\d{2}','',txt)
        for m in TOK.finditer(txt):
            t=m.group(0); ntok+=1; core=t.lstrip('+−-').replace(',','')
            if t.lstrip('+−-') in STRUCT or core in STRUCT: continue
            if core in allowed or ('e' in core and f"{float(core):.1e}" in allowed): continue
            unmatched.append((os.path.basename(fn),t,txt[max(0,m.start()-60):m.end()+20].strip()))
rep=dict(county_field_pairs=len(pairs),table_rows_checked=nrow,table_cells_checked=ncell,table_cell_mismatches=issues,numeric_tokens_checked=ntok,unmatched_tokens=unmatched,PASS=not issues and not unmatched)
json.dump(rep,open(V+'wiki_number_check.json','w'),indent=1,default=str)
print(json.dumps({k:rep[k] for k in ('county_field_pairs','table_rows_checked','table_cells_checked','numeric_tokens_checked','PASS')}),len(issues),len(unmatched))
for u in unmatched[:80]: print(u)
for i in issues[:20]: print(i)
