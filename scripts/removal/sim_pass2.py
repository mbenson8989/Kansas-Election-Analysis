"""Removal simulation PASS 2 (independent): regex parse of raw ENT HTML, openpyxl registration, csv population.
Integer/Fraction math written separately from pass 1."""
import re, os, csv, json
from fractions import Fraction
import openpyxl
D='/workspace/kansas-wiki/verification/ent_refetch_20261119/'; RAW='/workspace/kansas/raw/'
WANT=['Governor / Lt. Governor','United States Senate','Secretary of State','State Treasurer','Commissioner of Insurance']
def canon(s):
    s=s.strip().lower(); return 'McPherson' if s=='mcpherson' else ' '.join(w.capitalize() for w in s.split())
res={}
for fn in os.listdir(D):
    if not fn.endswith('.html'): continue
    h=open(D+fn,encoding='utf-8').read()
    h=h[h.index('id="party-county-all"'):]
    blocks=re.split(r'<div class="race">',h)[1:]
    cty=canon(fn[:-5]); res[cty]={}
    for bl in blocks:
        t=re.search(r'<h3>(.*?)</h3>',bl).group(1).strip()
        if t not in WANT: continue
        lst=bl[bl.index('race-candidate-list'):]
        lst=lst[:lst.index('Candidate')] if 'Candidate' in lst else lst
        cells=re.findall(r'<div class="col-4">\s*<p>(.*?)</p>\s*</div>\s*<div class="col-2">\s*<p>([\d,]+)</p>',lst)
        res[cty][t]={a:int(b.replace(',','')) for a,b in cells}
assert len(res)==105 and all(len(v)==5 for v in res.values())
wb=openpyxl.load_workbook(RAW+'10-2026-Voter-Registration-Numbers-by-County.xlsx',read_only=True,data_only=True)
ws=wb['By County']; rows=list(ws.iter_rows(values_only=True)); hdr=list(rows[0])
ic,idm,it=hdr.index('County'),hdr.index('Democratic'),hdr.index('Total')
reg={canon(r[ic]):(int(r[idm]),int(r[it])) for r in rows[1:] if r[ic] and str(r[ic]).strip()!='Grand Total'}
pop={}
with open(RAW+'co-est2025-alldata.csv',encoding='latin-1') as f:
    for r in csv.DictReader(f):
        if r['STATE']=='20' and r['COUNTY']!='000': pop[canon(r['CTYNAME'][:-7])]=int(r['POPESTIMATE2025'])
assert set(reg)==set(res)==set(pop)
m=Fraction(676004,10000); b=Fraction(63014,10000)
def half_up(q):
    s=-1 if q<0 else 1; q=abs(q); return s*((q*2+1)//2)
cty={}
for c,races in res.items():
    g=races['Governor / Lt. Governor']; dv=sum(v for k,v in g.items() if k[:2]=='D-'); tot=sum(g.values())
    dr,tr=reg[c]; dshare=Fraction(dr*100,tr); S=Fraction(dv*100,tot)-dshare; fitted=m*dshare/100+b; rp=S-fitted
    cty[c]={'pop':pop[c],'D':dshare,'S':S,'fit':fitted,'rp':rp,'rv':half_up(rp*tot/100),'gov_D':dv,'gov_T':tot}
# own refit with normal equations
N=len(cty); X=[cty[c]['D']/100 for c in cty]; Y=[cty[c]['S'] for c in cty]
sx,sy,sxx,sxy=sum(X),sum(Y),sum(x*x for x in X),sum(x*y for x,y in zip(X,Y))
mf=(N*sxy-sx*sy)/(N*sxx-sx*sx); bf=(sy-mf*sx)/N
out={'refit':[float(mf),float(bf)],'county':{},'race':{}}
for c,v in cty.items(): out['county'][c]={k:(float(x) if isinstance(x,Fraction) else x) for k,x in v.items()}
for t in WANT:
    def tally(f,reassign):
        d=r_=tt=0
        for c in res:
            x=res[c][t]; k=f(cty[c]['rv'])
            dv=sum(v for kk,v in x.items() if kk[:2]=='D-'); rv=sum(v for kk,v in x.items() if kk[:2]=='R-'); T=sum(x.values())
            assert dv-k>=0
            d+=dv-k; r_+=rv+(k if reassign else 0); tt+=T-(0 if reassign else k)
        return [d,r_,tt,float(Fraction(100*d,tt)),float(Fraction(100*r_,tt)),float(Fraction(100*(d-r_),tt))]
    out['race'][t]={'base':tally(lambda k:0,False),'pos_rm':tally(lambda k:k if k>0 else 0,False),'pos_ra':tally(lambda k:k if k>0 else 0,True),
                    'all_rm':tally(lambda k:k,False),'all_ra':tally(lambda k:k,True)}
out['pos']=sum(v['rv'] for v in cty.values() if v['rv']>0); out['neg']=sum(v['rv'] for v in cty.values() if v['rv']<0)
out['sum_rp']=float(sum(v['rp'] for v in cty.values()))
out['race_county']={c:res[c] for c in res}
json.dump(out,open('pass2.json','w'),indent=1)
print(out['refit'],out['pos'],out['neg'],out['sum_rp'])
for t,v in out['race'].items(): print(t,{k:[round(z,2) if isinstance(z,float) else z for z in x] for k,x in v.items()})
