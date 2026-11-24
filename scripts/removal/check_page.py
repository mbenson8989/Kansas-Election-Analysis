"""Number-by-number check of Removal-Simulation.md against PASS 2 (independent of the builder, which reads pass 1)."""
import json, re
from fractions import Fraction
B=json.load(open('pass2.json')); md=open('Removal-Simulation.md').read()
RN={'Governor':'Governor / Lt. Governor','US Senate':'United States Senate','Secretary of State':'Secretary of State','State Treasurer':'State Treasurer','Commissioner of Insurance':'Commissioner of Insurance'}
SK={'Main scenario, variant 1':'pos_rm','Main scenario, variant 2':'pos_ra','Secondary scenario, variant 1':'all_rm','Secondary scenario, variant 2':'all_ra'}
nums=lambda s:[float(x.replace(',','').replace('−','-')) for x in re.findall(r'[−+-]?\d[\d,]*\.?\d*',s)]
bad=[]; n=[0]
def eq(got,exp,dec,lab):
    n[0]+=1
    if f"{abs(got):.{dec}f}"!=f"{abs(round(exp,dec)) if dec else abs(exp):.{dec}f}" or (got<0)!=(round(exp,dec)<0 and round(exp,dec)!=0):
        # sign carried by D/R label for margins handled by caller
        bad.append((lab,got,exp))
def chkcell(cell,vals,decs,lab,signed=True):
    g=nums(cell)
    if len(g)!=len(vals): bad.append((lab,'count',cell,vals)); return
    for x,v,d in zip(g,vals,decs):
        n[0]+=1
        if round(abs(x),d)!=round(abs(v),d) or (signed and (x<0)!=(v<0) and round(v,d)!=0): bad.append((lab,cell,v))
def marg(cell,mp,mv,lab):
    n[0]+=1; side='D' if mv>0 else 'R'
    if not cell.strip().startswith(side): bad.append((lab,'side',cell))
    chkcell(cell,[abs(mp),abs(mv)] if 'votes' in cell else [abs(mp)],[2,0],lab,signed=False)
lines=md.split('\n'); sec=None; tables=0
cty=B['county']; race=B['race']
top=sorted(cty,key=lambda c:(-cty[c]['rv'],-cty[c]['rp']*cty[c]['gov_T']))[:10]
popord=sorted(cty,key=lambda c:-cty[c]['pop']); seen105=[]; seentop=[]
for ln in lines:
    if ln.startswith('#'): sec=ln; continue
    if not ln.startswith('|') or ln.startswith('|---'): continue
    c=[x.strip() for x in ln.strip('|').split('|')]
    if c[0] in ('Race','Rank','County','Constant'): continue
    if c[0].startswith('Multiplier'): chkcell(c[2],[B['refit'][0]],[4],'m'); continue
    if c[0].startswith('Offset'): chkcell(c[2],[B['refit'][1]],[4],'b'); continue
    if 'Before (2026' in sec:
        v=race[RN[c[0]]]['base']; chkcell(c[3],[v[3]],[2],c[0]); chkcell(c[4],[v[4]],[2],c[0]); marg(c[5],v[5],v[0]-v[1],c[0])
        cands=list(B['race_county']['Allen'][RN[c[0]]]); n[0]+=1
        if c[1]!=cands[0][2:] or c[2]!=cands[1][2:]: bad.append(('names',c))
        n[0]+=1
        if c[6]!=('D' if v[5]>0 else 'R')+(' (competitive)' if abs(v[5])<=5 else ''): bad.append(('status',c))
        continue
    k=[SK[s] for s in SK if s in sec]
    if k:
        b=race[RN[c[0]]]['base']; v=race[RN[c[0]]][k[0]]
        chkcell(c[1],[b[3],v[3]],[2,2],c[0]); marg(c[2],b[5],b[0]-b[1],c[0]); marg(c[3],v[5],v[0]-v[1],c[0]); chkcell(c[4],[v[5]-b[5]],[2],c[0]+'chg')
        n[0]+=1
        if c[5]!=('D' if v[5]>0 else 'R')+(' (competitive)' if abs(v[5])<=5 else ''): bad.append(('status',c))
        continue
    if 'Top ten' in sec:
        i=int(c[0]); co=top[i-1]; seentop.append(c[1]); v=cty[co]; g=B['race_county'][co]['Governor / Lt. Governor']
        d=sum(x for kk,x in g.items() if kk[:2]=='D-'); r=sum(x for kk,x in g.items() if kk[:2]=='R-'); T=v['gov_T']; k_=v['rv']
        n[0]+=1
        if c[1]!=co: bad.append(('rank',c[1],co))
        chkcell(c[2],[v['pop']],[0],co); chkcell(c[3],[v['D']],[2],co); chkcell(c[4],[v['S']],[2],co); chkcell(c[5],[v['fit']],[2],co); chkcell(c[6],[v['rp']],[2],co)
        chkcell(c[7],[k_],[0],co); chkcell(c[8],[d,d-k_],[0,0],co); chkcell(c[9],[T,T-k_],[0,0],co)
        chkcell(c[10],[float(Fraction(100*d,T)),float(Fraction(100*(d-k_),T-k_))],[2,2],co)
        marg(c[11],float(Fraction(100*(d-r),T)),d-r,co+'m0'); marg(c[12],float(Fraction(100*(d-k_-r),T-k_)),d-k_-r,co+'m1'); marg(c[13],float(Fraction(100*(d-k_-r-k_),T)),d-2*k_-r,co+'m2')
        continue
    if 'All 105' in sec:
        co=c[0]; seen105.append(co); v=cty[co]
        chkcell(c[1],[v['pop']],[0],co); chkcell(c[2],[v['D']],[2],co); chkcell(c[3],[v['S']],[2],co); chkcell(c[4],[v['fit']],[2],co); chkcell(c[5],[v['rp']],[2],co); chkcell(c[6],[v['rv']],[0],co); chkcell(c[7],[max(v['rv'],0)],[0],co)
        continue
    bad.append(('unchecked row',ln))
n[0]+=2
if seen105!=popord: bad.append('105 order/coverage')
if seentop!=top: bad.append('top10 order')
# prose numbers: every numeric token outside tables must be in the allowed set built from pass 2
pos=B['pos']; neg=B['neg']; npos=sum(1 for v in cty.values() if v['rv']>0)
f2=lambda x:f"{abs(x):.2f}"; fc=lambda x:f"{abs(x):,}"
allowed={'2026','2025','2022','105','5','1','2','3','4','6','11','08','9','15','19','16','0','67.6004','6.3014','100','10','470','0.02','0.01','14','399'}
allowed|={fc(pos),fc(neg),str(npos),str(105-npos),fc(pos+neg),f"{abs(B['sum_rp']):.4f}",fc(sum(cty[c]['rv'] for c in top))}
for t,d in race.items():
    for kk,v in d.items(): allowed|={f2(v[5]),fc(v[0]-v[1])}
prose=[l for l in lines if not l.startswith('|')]
for l in prose:
    l2=re.sub(r'\(https?://[^)]*\)|\[ent\.sos\.ks\.gov\]|co-est2025-alldata|\(Locked-Kansas-Formula\)','',l)
    for tok in re.findall(r'\d[\d,]*\.?\d*',l2):
        tok=tok.rstrip('.,'); n[0]+=1
        if tok not in allowed: bad.append(('prose',tok,l[:80]))
# claim checks
g=race['Governor / Lt. Governor']; s=race['United States Senate']
claims={'gov flips pos_rm':g['pos_rm'][5]<0<g['base'][5],'gov flips pos_ra':g['pos_ra'][5]<0,'senate competitive not flip':all(0<s[k][5]<=5 for k in('pos_rm','pos_ra')) and s['base'][5]>5,
 'no winner change all':all((v['all_rm'][5]>0)==(v['base'][5]>0)==(v['all_ra'][5]>0) for v in race.values()),'senate all_rm inside 5':s['all_rm'][5]<=5,
 'SoS/Ins stay competitive':all(abs(race[t][k][5])<=5 for t in('Secretary of State','Commissioner of Insurance') for k in('base','pos_rm','pos_ra')),
 'treasurer not competitive':all(abs(race['State Treasurer'][k][5])>5 for k in('base','pos_rm','pos_ra'))}
# share-point alternative within 0.02 pts
for t in RN.values():
    if t.startswith('Gov'): continue
    d=r=T=0
    for c in cty:
        x=B['race_county'][c][t]; tt=sum(x.values()); k=round(Fraction(max(cty[c]['rp'],0))*tt/100)
        d+=sum(v for kk,v in x.items() if kk[:2]=='D-')-k; r+=sum(v for kk,v in x.items() if kk[:2]=='R-'); T+=tt-k
    claims['sharept '+t]=abs(100*(d-r)/T-race[t]['pos_rm'][5])<=0.02
for kk,ok in claims.items():
    n[0]+=1
    if not ok: bad.append(('claim',kk))
for w in ['Attorney General race is excluded by design','not evidence of injected votes','UNOFFICIAL','removed entirely']:
    n[0]+=1
    if w not in md: bad.append(('missing',w))
print('checks',n[0],'mismatches',len(bad)); [print(b) for b in bad[:30]]
json.dump({'checks':n[0],'mismatches':bad},open('page_check.json','w'),indent=1,default=str)
