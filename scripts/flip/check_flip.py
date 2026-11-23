"""Independent check of rendered-graphic strings vs PASS 2 (exact fractions; separate raw readers)."""
import json
from fractions import Fraction as F
B=json.load(open('pass2.json')); man=json.load(open('manifest.json')); rows=json.load(open('rows.json'))
n=lambda x:f'{int(x):,}'; bad=0
assert sum(v['v26'] for v in B.values())==551243 and sum(v['v22'] for v in B.values())==499849 and sum(v['reg22'] for v in B.values())==523317 and sum(v['reg26'] for v in B.values())==521669
cand={c:v for c,v in B.items() if v['reg26']<v['reg22'] and v['v26']>v['v22']}
top=sorted(cand,key=lambda c:-F(cand[c]['gap_num'],cand[c]['gap_den']))[:10]
tot26={}
import csv
for r in csv.DictReader(open('/workspace/kansas/raw/ent2026_governor_transcribed.csv')): tot26[r['county']]=int(r['holscher_D'])+int(r['masterson_R'])
assert [m['file'].split('_',3)[3][:-4].replace('_',' ') for m in man]==top,(top)
for i,(c,m) in enumerate(zip(top,man)):
    v=B[c]; gap=F(v['gap_num'],v['gap_den']); g=int(gap+F(1,2)); pct=100*gap/tot26[c]
    exp=[c.upper()+' COUNTY',n(v['reg22']),n(v['reg26']),n(v['reg22']-v['reg26']),n(v['v22']),n(v['v26']),n(v['v26']-v['v22']),f"{100*F(v['v26']-v['v22'],v['v22']):.0f}" if False else str(int(100*F(v['v26']-v['v22'],v['v22'])+F(1,2))),n(g),f'{float(pct):.1f}']
    if exp!=m['strings']: bad+=1; print('MISMATCH',c,exp,m['strings'])
    r=rows[i]
    if (r['flip'],r['reg22'],r['reg26'],r['v22'],r['v26'])!=(g,v['reg22'],v['reg26'],v['v22'],v['v26']): bad+=1; print('ROW',c)
print('graphics checked',len(top),'mismatches',bad)
