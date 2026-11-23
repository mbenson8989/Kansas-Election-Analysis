import json,re
from fractions import Fraction as F
B=json.load(open('pass2.json')); import csv
tot26={r['county']:int(r['holscher_D'])+int(r['masterson_R']) for r in csv.DictReader(open('/workspace/kansas/raw/ent2026_governor_transcribed.csv'))}
cand={c:v for c,v in B.items() if v['reg26']<v['reg22'] and v['v26']>v['v22']}
top=sorted(cand,key=lambda c:-F(cand[c]['gap_num'],cand[c]['gap_den']))[:10]
pop={}
for r in csv.DictReader(open('/workspace/kansas-wiki/verification/passB_counties.csv')): pop[r['key']]=int(r['population_2025'])
ok=set(); n=lambda x:f'{int(x):,}'
for c in top:
    v=B[c]; g=int(F(v['gap_num'],v['gap_den'])+F(1,2)); k=re.sub(r'[^a-z]','',c.lower())
    ok|={n(pop[k]),n(v['reg22']),n(v['reg26']),n(v['reg22']-v['reg26']),n(v['v22']),n(v['v26']),n(v['v26']-v['v22']),str(int(1000*F(v['v26']-v['v22'],v['v22'])+F(1,2))/10 if False else round(float(100*F(v['v26']-v['v22'],v['v22'])),1)),n(g),f"{float(100*F(v['gap_num'],v['gap_den'])/tot26[c]):.1f}"}
const={'1','2','3','4','5','6','7','8','9','10','14','105','2022','2026','2025','1080','1350','254','280','14399','17125','91','31','3','8','11','2020','00','0'}
txt=open('/workspace/kansas-wiki/wikiclone/Resources.md').read()
txt=re.sub(r'\(https?://[^)]*\)','',txt); txt=re.sub(r'https?://\S+','',txt)
bad=[t for t in re.findall(r'\d[\d,]*\.?\d*',txt) if t.rstrip('.,') not in ok|const|{x.rstrip('.') for x in const}]
print('unrecognised tokens:',bad)
# table rows must list ranks in order and counties
print(top)
