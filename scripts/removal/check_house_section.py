"""Check the appended top-of-ballot section against PASS 2 outputs (pass2.json, house_pass2.json); confirm prefix unchanged."""
import json, re
from fractions import Fraction
md=open('Removal-Simulation_new.md').read(); base=open('/workspace/kansas-wiki/wikiclone/Removal-Simulation.md').read()
bad=[]; n=[0]
def ok(c,lab):
    n[0]+=1
    if not c: bad.append(lab)
ok(md.startswith(base.rstrip('\n')+'\n'),'prefix changed')
sec=md[len(base.rstrip('\n'))+1:]
B=json.load(open('pass2.json')); H=json.load(open('house_pass2.json'))
RN={'US Senate':'United States Senate','Governor':'Governor / Lt. Governor','Secretary of State':'Secretary of State','State Treasurer':'State Treasurer','Commissioner of Insurance':'Commissioner of Insurance'}
def race(name):
    if name.startswith('US House KS-'): return H['districts'][name[-1]]
    return B['race'][RN[name]]
K=['base','pos_rm','pos_ra','all_rm','all_ra']
def M(v,votes=False):
    p=v[5]; s=(f"D +{p:.2f}" if p>0 else f"R +{-p:.2f}")
    return s+(f" ({abs(v[0]-v[1]):,} votes)" if votes else '')
def S(v): return ('D' if v[0]>v[1] else 'R')+(' (competitive)' if abs(v[5])<=5 else '')
W=lambda v:'D' if v[0]>v[1] else 'R'
pop={c:v['pop'] for c,v in B['county'].items()}
sub=None; seen=[]
for ln in sec.split('\n'):
    if ln.startswith('#'): sub=ln; continue
    if not ln.startswith('|') or ln.startswith('|---'): continue
    c=[x.strip() for x in ln.strip('|').split('|')]
    if c[0] in ('Level','Group','District','County'): continue
    if 'Combined' in sub:
        v=race(c[1]); ok(c[0]==('Federal' if c[1].startswith('US') else 'State'),ln)
        for i,k in enumerate(K): ok(c[2+i]==M(v[k]),(ln,k))
        ok(c[7]==('Flips D → R' if W(v['base'])!=W(v['pos_rm']) else 'No'),ln); seen.append(c[1]); continue
    if 'Seats' in sub:
        names=['US Senate','US House KS-1','US House KS-2','US House KS-3','US House KS-4'] if c[0].startswith('Federal') else (['US House KS-1','US House KS-2','US House KS-3','US House KS-4'] if c[0].startswith('US House') else ['Governor','Secretary of State','State Treasurer','Commissioner of Insurance'])
        for i,k in enumerate(K):
            d=sum(W(race(x)[k])=='D' for x in names); ok(c[1+i]==f"{d} D, {len(names)-d} R",(ln,k))
        continue
    if 'US House districts in detail' in sub and len(c)==10:
        v=H['districts'][c[0][-1]]
        ok(c[1]==v['cands'][0][2:] and c[2]==v['cands'][1][2:],ln); ok(c[3]==str(v['n']),ln); ok(c[4]==f"{v['removed']:,}",ln)
        ok(c[5]==f"{v['base'][3]:.2f}% → {v['pos_rm'][3]:.2f}%",ln); ok(c[6]==M(v['base'],1),ln); ok(c[7]==M(v['pos_rm'],1),ln); ok(c[8]==M(v['pos_ra'],1),ln); ok(c[9]==S(v['pos_rm']),ln); continue
    if 'US House districts in detail' in sub and len(c)==6:
        v=H['districts'][c[0][-1]]; nn=v['net']
        ok(c[1]==('−' if nn<0 else '+')+f"{abs(nn):,}",ln); ok(c[2]==M(v['base'],1),ln); ok(c[3]==M(v['all_rm'],1),ln); ok(c[4]==M(v['all_ra'],1),ln); ok(c[5]==S(v['all_ra']),ln); continue
    if 'Split' in sub:
        co=c[0]; d=c[2][-1]; s=H['split'][co]; w=s['w']; T=sum(w.values()); rv=B['county'][co]['rv']
        ok(c[1]==f"{pop[co]:,}",ln); ok(c[3]==f"{w[d]:,}",ln); ok(c[4]==f"{float(Fraction(100*w[d],T)):.2f}%",ln)
        ok(c[5]==('−' if rv<0 else '+')+f"{abs(rv):,}",ln); ok(c[6]==f"{s['pos'][d]:,}",ln); a=s['all'][d]; ok(c[7]==('−' if a<0 else '+' if a>0 else '')+f"{abs(a):,}",ln)
        ok(sum(s['pos'].values())==max(rv,0) and sum(s['all'].values())==rv,co+' alloc sum'); seen.append(co+d); continue
    bad.append(('unchecked',ln))
ok(seen[:9]==['US Senate','US House KS-1','US House KS-2','US House KS-3','US House KS-4','Governor','Secretary of State','State Treasurer','Commissioner of Insurance'],'combined rows')
ok([x[:-1] for x in seen[9:]]==[c for c in sorted(H['split'],key=lambda c:-pop[c]) for _ in H['split'][c]['w']],'split order')
# prose tokens
allowed={'2026','24','11','0','1','2','3','4','5','9','15','08','16','67.6004','6.3014','100'}
for k in ('United States Senate','Governor / Lt. Governor'): 
    for kk in K: allowed.add(f"{abs(B['race'][k][kk][5]):.2f}")
for d,v in H['districts'].items():
    for kk in K: allowed.add(f"{abs(v[kk][5]):.2f}")
allowed.add(f"{sum(v['removed'] for v in H['districts'].values()):,}")
ok(sum(v['removed'] for v in H['districts'].values())==B['pos'],'removed sum = statewide pos')
for ln in sec.split('\n'):
    if ln.startswith('|'): continue
    for t in re.findall(r'\d[\d,]*\.?\d*',re.sub(r'KS-\d','',ln)):
        t=t.rstrip('.,'); n[0]+=1
        if t not in allowed: bad.append(('prose',t,ln[:70]))
# prose claims
g=B['race']['Governor / Lt. Governor']; races=[B['race'][RN[x]] for x in RN]+list(H['districts'].values())
ok(sum(W(r['base'])!=W(r['pos_rm']) for r in races)==1 and W(g['pos_rm'])=='R','only governor flips')
ok(all(W(v[k])==W(v['base']) for v in H['districts'].values() for k in K),'no house seat change')
ok([d for d,v in H['districts'].items() if any(abs(v[k][5])<=5 for k in K)]==['2'] and abs(H['districts']['2']['all_ra'][5])<=5 and all(abs(H['districts']['2'][k][5])>5 for k in K[:4]),'KS-2 claim')
ok(all(H['districts'][d]['pos_rm'][5]<H['districts'][d]['base'][5] for d in '124'),'R margins widen')
ok(set(H['split'])=={'Douglas','Jackson','Pawnee','Wyandotte'},'split set')
ok('Attorney General race is excluded by design' in sec and 'UNOFFICIAL' in sec and 'not evidence of injected votes' in sec,'framing')
print('checks',n[0],'mismatches',len(bad)); [print(x) for x in bad[:20]]
json.dump({'checks':n[0],'mismatches':bad},open('house_page_check.json','w'),default=str,indent=1)
