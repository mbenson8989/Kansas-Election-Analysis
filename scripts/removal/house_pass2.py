"""US House PASS 2 (independent): regex parse of raw ENT HTML; residual votes from pass2.json; own allocation code."""
import re, os, json
from fractions import Fraction
D='/workspace/kansas-wiki/verification/ent_refetch_20261119/'
P2=json.load(open('pass2.json')); rv={c:v['rv'] for c,v in P2['county'].items()}
def canon(s):
    s=s.strip().lower(); return 'McPherson' if s=='mcpherson' else ' '.join(w.capitalize() for w in s.split())
house={}; statewide={}
for fn in os.listdir(D):
    if not fn.endswith('.html'): continue
    h=open(D+fn,encoding='utf-8').read(); h=h[h.index('id="party-county-all"'):]
    for bl in re.split(r'<div class="race">',h)[1:]:
        m=re.search(r'<h3>United States House of Representatives (\d)</h3>',bl)
        if not m: continue
        lst=bl[bl.index('race-candidate-list'):]; lst=lst[:lst.index('Candidate')] if 'Candidate' in lst else lst
        cells=re.findall(r'<div class="col-4">\s*<p>(.*?)</p>\s*</div>\s*<div class="col-2">\s*<p>([\d,]+)</p>\s*</div>\s*<div class="col-2">\s*<p>[^<]*</p>\s*</div>\s*<div class="col-2">\s*<p>([\d,]+)</p>',lst)
        dn=int(m.group(1)); house.setdefault(canon(fn[:-5]),{})[dn]={a:int(b.replace(',','')) for a,b,_ in cells}
        for a,_,s in cells: statewide.setdefault(dn,{})[a]=int(s.replace(',',''))
assert len(house)==105
def split_votes(k,weights):
    n=abs(k); tw=sum(weights.values()); out={}; rem=[]
    for d in sorted(weights):
        q,r=divmod(n*weights[d],tw); out[d]=q; rem.append((-Fraction(r,tw),d))
    for _,d in sorted(rem)[:n-sum(out.values())]: out[d]+=1
    return {d:(v if k>=0 else -v) for d,v in out.items()}
alloc={}
for c,ds in house.items():
    w={d:sum(x.values()) for d,x in ds.items()}
    alloc[c]={'pos':split_votes(rv[c] if rv[c]>0 else 0,w),'all':split_votes(rv[c],w)}
out={}
for dn in sorted(statewide):
    def run(sc,re_):
        d=r=t=0
        for c,ds in house.items():
            if dn not in ds: continue
            x=ds[dn]; k=alloc[c][sc][dn] if sc else 0
            dv=sum(v for a,v in x.items() if a.startswith('D-')); rr=sum(v for a,v in x.items() if a.startswith('R-'))
            assert dv-k>=0
            d+=dv-k; r+=rr+(k if re_ else 0); t+=sum(x.values())-(0 if re_ else k)
        return [d,r,t,float(Fraction(100*d,t)),float(Fraction(100*r,t)),float(Fraction(100*(d-r),t))]
    tot={a:sum(ds[dn][a] for ds in house.values() if dn in ds) for a in statewide[dn]}
    assert tot==statewide[dn], dn
    out[str(dn)]={'base':run(None,False),'pos_rm':run('pos',False),'pos_ra':run('pos',True),'all_rm':run('all',False),'all_ra':run('all',True),
        'removed':sum(alloc[c]['pos'].get(dn,0) for c in house),'net':sum(alloc[c]['all'].get(dn,0) for c in house),'n':sum(dn in ds for ds in house.values()),'cands':list(statewide[dn])}
res={'districts':out,'split':{c:{'pos':alloc[c]['pos'],'all':alloc[c]['all'],'w':{d:sum(x.values()) for d,x in house[c].items()}} for c in house if len(house[c])>1},'house':house}
json.dump(res,open('house_pass2.json','w'),indent=1)
for d,v in out.items(): print(d,v['n'],v['removed'],v['net'],{k:[round(z,2) if isinstance(z,float) else z for z in v[k]] for k in ('base','pos_rm','pos_ra','all_rm','all_ra')})
