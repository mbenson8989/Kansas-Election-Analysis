"""PASS 2 (independent of the pandas builders): checks every number and every equipment/addressee cell on the Kansas Resources page,
the 105 clerk letters (text extracted from the PDFs), the AG letter and the equipment CSV against raw sources:
pass B county table (openpyxl/regex/fractions build from raw SOS files), raw Verified Voting CSVs (csv module), raw SOS officer HTML (regex),
KDOT district list, Census CSV, ZIP files on disk. Exact rational arithmetic. Prints mismatches; exit 1 if any."""
import csv,re,json,os,glob,subprocess,html,sys,zipfile
from fractions import Fraction as F
K='/workspace/kansas-resources/'; V='/workspace/kansas-wiki/verification/'; RAWK='/workspace/kansas/raw/'
mism=[]; checked=0
def chk(label,got,exp):
    global checked; checked+=1
    if str(got).strip()!=str(exp).strip(): mism.append((label,got,exp))
key=lambda s:re.sub(r'[^a-z]','',s.lower())
# ---------- truth: pass B ----------
B={r['key']:r for r in csv.DictReader(open(V+'passB_counties.csv'))}
I=lambda k,c:int(B[k][c])
names={}
with open(RAWK+'co-est2025-alldata.csv',encoding='latin-1') as f:
    for r in csv.DictReader(f):
        if r['STATE']=='20' and r['COUNTY']!='000':
            n=r['CTYNAME'][:-7]; names[key(n)]=dict(name=n,fips=r['STATE']+r['COUNTY'],pop=int(r['POPESTIMATE2025']))
assert len(names)==105 and set(names)==set(B)
def r1(x): # round half away from zero, Fraction -> 1 dp string
    s='-' if x<0 else ''; x=abs(x); q=int(x*10+F(1,2)); return f"{s}{q//10}.{q%10}"
def r2(x):
    s='-' if x<0 else ''; x=abs(x); q=int(x*100+F(1,2)); return f"{s}{q//100}.{q%100:02d}"
def chg(a,b,star=''):
    d=b-a; sg='+' if d>0 else ''; return f"{a:,} → {b:,}{star} ({sg}{d:,}{star}, {sg if d>0 else ''}{r1(F(100*d,a))}%{star})"
# ---------- truth: Verified Voting (csv module) ----------
def vv(year):
    out={}
    with open(K+f'raw/vv/vv{year}/verifier-machines.csv',newline='') as f:
        rd=csv.reader(f); next(rd); h=next(rd)
        for r in rd:
            if not r or not r[0]: continue
            d=dict(zip(h,r)); out.setdefault(d['FIPS code'][:5],[]).append(d)
    return out
M26,M22=vv(2026),vv(2022)
J={}
with open(K+'raw/vv/vv2026/verifier-jurisdictions.csv',newline='') as f:
    rd=csv.reader(f); next(rd); h=next(rd)
    for r in rd:
        if r and r[0]: d=dict(zip(h,r)); J[d['FIPS code'][:5]]=d
TABS=('Hand-Fed Optical Scanner','Batch-Fed Optical Scanner','Hybrid BMD/Tabulator')
lab=lambda d:f"{d['Manufacturer']} {d['Model']} ({d['Equipment Type']})"
EXP={}
for k,n in names.items():
    ms=M26[n['fips']]; ed=[d for d in ms if d['Election Day Standard']=='Yes' and d['Equipment Type'] in TABS]
    ml=[d for d in ms if d['Mail Ballot/Absentee Equipment']=='Yes' and d['Equipment Type'] in TABS]
    ac=[d for d in ms if d['Election Day Accessible']=='Yes' and d['Equipment Type'] in ('Ballot Marking Device','Hybrid BMD/Tabulator','DRE-Touchscreen')]
    ed22=[d for d in M22.get(n['fips'],[]) if d['Election Day Standard']=='Yes' and d['Equipment Type'] in TABS]
    EXP[k]=dict(County=n['name'],FIPS=n['fips'],Population=str(n['pop']),marking=J[n['fips']]['Election Day Marking Method'],
        vendor='; '.join(sorted({d['Manufacturer'] for d in ed})) or 'Not listed',edq='; '.join(sorted({lab(d) for d in ed})) or 'Not listed',
        mail='; '.join(sorted({lab(d) for d in ml})) or 'Not listed',acc='; '.join(sorted({lab(d) for d in ac})) or 'Not listed',
        vvpat=sorted({d['VVPAT'] for d in ms if d['Equipment Type'] in TABS+('Ballot Marking Device',)}),
        models26=sorted({(d['Model'],d['Equipment Type']) for d in ed}),models22=sorted({(d['Model'],d['Equipment Type']) for d in ed22}),
        central=bool(ed) and all(d['Equipment Type']=='Batch-Fed Optical Scanner' for d in ed),hybrid=any(d['Equipment Type']=='Hybrid BMD/Tabulator' for d in ed),
        paperpb=any(d['Equipment Type']=='Paper Poll Book' for d in ms))
# versions from county API
VER={}
for fpath in glob.glob(K+'raw/vv/county_api_2026/*.json'):
    d=json.load(open(fpath)); fips=os.path.basename(fpath)[:5]
    VER[fips]=[m for m in d['machines'] if m['equip_type'] in TABS+('Ballot Marking Device',) and (m['hardware_version'] or m['firmware_version'] or m['software_version'])]
# ---------- 1. Resources page: equipment table ----------
P=open(K+'out/Resources.md').read()
rows=[l for l in P.split('\n') if l.startswith('| ') and re.match(r'\| [A-Z][a-zA-Z ]+ \| 20\d{3} \|',l)]
chk('equipment rows on page',len(rows),105)
prev=10**9
for l in rows:
    c=[x.strip() for x in l.strip('|').split(' | ')]
    k=key(c[0]); e=EXP[k]
    for lab_,i,v in [('FIPS',1,e['FIPS']),('Population',2,e['Population']),('marking',3,e['marking']),('vendor',4,e['vendor']),('ED eq',5,e['edq']),('mail',6,e['mail']),('acc',7,e['acc'])]: chk(f'{c[0]} {lab_}',c[i],v)
    chk(f'{c[0]} vvpat',c[8],'VVPAT: N/A (Verified Voting does not list a VVPAT for these systems)' if e['vvpat']==['N/A'] else 'VVPAT: '+'/'.join(e['vvpat']))
    vers=VER[e['FIPS']]
    chk(f'{c[0]} versions',c[9],'Not listed by Verified Voting' if not vers else '; '.join(sorted({m['model']+': hardware '+m['hardware_version']+' (other version fields blank)' for m in vers})))
    chk(f'{c[0]} status',c[10],'Confirmed' if e['edq']!='Not listed' else 'Unconfirmed')
    chk(f'{c[0]} source',c[11],f"[Verifier](https://verifiedvoting.org/verifier/#mode/navigate/map/ppEquip/mapType/normal/year/2026/state/20/county/{e['FIPS'][2:]})")
    notes=c[12]
    chk(f'{c[0]} change note',('changed from 2022' in notes),e['models26']!=e['models22'])
    chk(f'{c[0]} central note',('central-count' in notes),e['central']); chk(f'{c[0]} hybrid note',('hybrid' in notes),e['hybrid'])
    chk(f'{c[0]} sort',int(c[2])<=prev,True); prev=int(c[2])
# vendor summary
tot=sum(n['pop'] for n in names.values()); chk('total pop',f"{tot:,}" in P,True)
vend={}
for k,e in EXP.items(): vend.setdefault(e['vendor'],[]).append(int(e['Population']))
for v,pops in vend.items():
    line=f"- **{v}:** {len(pops)} counties ({r1(F(100*len(pops),105))}% of counties); population {sum(pops):,} ({r1(F(100*sum(pops),tot))}% of the 105-county total of {tot:,})"
    chk('vendor line '+v, line in P, True)
mmc={}
for e in EXP.values(): mmc[e['marking']]=mmc.get(e['marking'],0)+1
chk('marking counts', f"{mmc['Hand marked paper ballots and BMDs']} counties use hand-marked" in P and f"and {mmc['Ballot Marking Devices for all voters']} use BMDs for all voters" in P, True)
order=[EXP[key(l.split(' | ')[0].strip('| '))]['County'] for l in rows]
def listed(cond): return ', '.join(c for c in order if cond(EXP[key(c)]))
chk('central list', f"{sum(e['central'] for e in EXP.values())} counties ({listed(lambda e:e['central'])})" in P, True)
chk('change list', f"{sum(e['models26']!=e['models22'] for e in EXP.values())} counties ({listed(lambda e:e['models26']!=e['models22'])})" in P, True)
ren=sum(1 for e in EXP.values() if e['models26']==e['models22'] and 'Dominion' in e['vendor'] )
chk('rename count', f"in {ren} counties the 2022 record lists" in P, True)
chk('paper pollbook count', f"{sum(e['paperpb'] for e in EXP.values())} counties list a paper poll book" in P, True)
vc=[EXP[key(c)]['County'] for c in order if VER[EXP[key(c)]['FIPS']]]
chk('version list', f"in {len(vc)} counties ({', '.join(vc)}" in P, True)
chk('unconfirmed 0', '**0 counties are unconfirmed**' in P and all(e['edq']!='Not listed' for e in EXP.values()), True)
# ---------- 2. equipment CSV ----------
with open(K+'out/KS_105_County_Voting_Equipment_VerifiedVoting.csv',newline='') as f:
    for r in csv.DictReader(f):
        e=EXP[key(r['County'])]; chk(r['County']+' csv pop',r['Population'],e['Population']); chk(r['County']+' csv ed',r['ED tabulator equipment'],e['edq']); chk(r['County']+' csv fips',r['FIPS'],e['FIPS'])
# ---------- 3. clerk ZIPs and districts ----------
D=json.load(open(K+'raw/regions/kdot_districts.json'))
allc=[]
for dk,v in D.items():
    if not dk.startswith('District'): continue
    allc+=v; n,name=dk.split(' ',2)[1],dk.split(' ',2)[2]; zn=f"Kansas_Clerk_Letters_District_{n}_{name.replace(' Kansas','').replace(' ','_')}"
    z=zipfile.ZipFile(K+f'pkg/{zn}.zip'); pdfs=[x for x in z.namelist() if x.endswith('.pdf')]; docs=[x for x in z.namelist() if x.endswith('.docx')]
    chk(zn+' pdf count',len(pdfs),len(v)); chk(zn+' docx count',len(docs),len(v))
    mbs=f"{os.path.getsize(K+f'pkg/{zn}.zip')/1e6:.1f} MB"
    chk(zn+' page line', f"(ZIP, {len(v)} counties, {mbs})]" in P, True)
    chk(zn+' table', f"| {len(v)} | {', '.join(sorted(v))} |" in P, True)
chk('districts cover 105 once',sorted(map(key,allc)),sorted(names))
za=zipfile.ZipFile(K+'pkg/Kansas_Clerk_Letters_All_105_Counties.zip'); chk('all zip pdfs',len([x for x in za.namelist() if x.endswith('.pdf')]),105); chk('all zip docx',len([x for x in za.namelist() if x.endswith('.docx')]),105)
chk('all zip size line',f"(ZIP, 105 counties, {os.path.getsize(K+'pkg/Kansas_Clerk_Letters_All_105_Counties.zip')/1e6:.1f} MB)" in P,True)
# ---------- 4. clerk letters: text from PDFs vs pass B and SOS HTML ----------
sos=open(K+'raw/sos/county_election_officers_all.html',encoding='utf-8',errors='ignore').read()
OFF={}
for tr in re.findall(r'<tr[^>]*>(.*?)</tr>',sos,re.S):
    td=[html.unescape(re.sub(r'<[^>]+>','',x)).strip() for x in re.findall(r'<td[^>]*>(.*?)</td>',tr,re.S)]
    if len(td)==11: OFF[key(td[0])]=[re.sub(r'\s+',' ',x) for x in td]
chk('SOS officer rows',len(OFF),105)
s=lambda c:sum(int(B[k][c]) for k in B)
SW=f"Statewide, registered Democrats changed {chg(s('D_reg_22'),s('D_reg_26'))} and Democratic votes for governor changed {chg(s('D_votes_22'),s('D_votes_26'),'*')}."
COMM={'johnson','sedgwick','shawnee','wyandotte'}
for k,n in names.items():
    fn=K+f"letters/clerk/PDF/{n['name'].replace(' ','_')}_County_Clerk_Letter.pdf"
    t=subprocess.run(['pdftotext','-raw',fn,'-'],capture_output=True,text=True).stdout; t1=re.sub(r'\s+',' ',t)
    o=OFF[k]; title='Election Commissioner' if k in COMM else 'County Clerk'
    addr=o[6]+(', '+o[7] if o[7] else '')
    chk(n['name']+' addressee', f"{o[1]} {title}, {n['name']} County {addr} {o[8]}, KS {o[10]}" in t1, True)
    chk(n['name']+' salutation', f"Dear {title} {o[1].replace('(Jamie) ','').split()[-1]}:" in t1, True)
    chk(n['name']+' reg line', f"Registered Democrats, Nov. 1, 2022 to Oct. 1, 2026: {chg(I(k,'D_reg_22'),I(k,'D_reg_26'))}" in t1, True)
    chk(n['name']+' Dvotes line', f"Democratic votes for governor, 2022 to 2026: {chg(I(k,'D_votes_22'),I(k,'D_votes_26'),'*')}" in t1, True)
    chk(n['name']+' total line', f"Total votes for governor (all candidates), 2022 to 2026: {chg(I(k,'total_votes_22'),I(k,'total_votes_26'),'*')}" in t1, True)
    chk(n['name']+' statewide', SW in t1, True)
    dr=I(k,'D_reg_26')-I(k,'D_reg_22'); dv=I(k,'D_votes_26')-I(k,'D_votes_22')
    pat={(True,True):'Democratic registration declined while Democratic votes for governor rose',(True,False):'Democratic registration and Democratic votes for governor both declined',(False,True):'Democratic registration and Democratic votes for governor both rose',(False,False):'Democratic registration rose while Democratic votes for governor declined'}[(dr<0,dv>0)]
    chk(n['name']+' pattern', pat in t1, True)
    chk(n['name']+' equipment', f"election-day tabulator as {EXP[k]['edq']}; please" in t1, True)
    chk(n['name']+' no AG race', 'Attorney General race' not in t1, True)
# ---------- 5. charts / flip / method numbers ----------
S=lambda k,y:F(100*I(k,'D_votes_'+y),I(k,'total_votes_'+y)); Dr=lambda k,y:F(100*I(k,'D_reg_'+y),I(k,'total_reg_'+y))
up=sum(1 for k in B if S(k,'26')>S(k,'22')); dn=sum(1 for k in B if S(k,'26')<S(k,'22'))
chk('gain caption', f"rose in {up} counties and fell in {dn}\\*" in P, True)
dG={k:(S(k,'26')-Dr(k,'26'))-(S(k,'22')-Dr(k,'22')) for k in B}
top=sorted(B,key=lambda k:-dG[k])[:5]
chk('ceiling caption', "Ceiling counties (the five highest ΔG): "+', '.join(f"{names[k]['name']} +{r2(dG[k])}\\*" for k in top)+"." in P, True)
cj=json.load(open(K+'out/charts_pass1.json')); chk('chart pass1 json up/down',(cj['gain_up'],cj['gain_down']),(up,dn))
chk('chart pass1 ceiling',[(c,f"{v:.2f}") for c,v in cj['ceiling']],[(names[k]['name'],r2(dG[k])) for k in top])
# OLS S on D (surplus = S - D share)
def ols(y):
    xs=[Dr(k,y)/100 for k in B]; ys=[S(k,y)-Dr(k,y) for k in B]; n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    sxx=sum((x-mx)**2 for x in xs); sxy=sum((x-mx)*(yy-my) for x,yy in zip(xs,ys)); m=sxy/sxx; b=my-m*mx
    ssr=sum((yy-(m*x+b))**2 for x,yy in zip(xs,ys)); sst=sum((yy-my)**2 for yy in ys); return m,b,1-ssr/sst
for y,lab_ in (('22','**2022:**'),('26','**2026\\* (unofficial):**')):
    m,b,r=ols(y); line=f"{lab_} S = {float(m):.2f} × (D/100) + {float(b):.2f}, R² {float(r):.3f}"
    chk('fit '+y, line in P, True)
# flip table rows
for l in P.split('\n'):
    m_=re.match(r'\| (\d+) \| ([A-Za-z ]+) \| ([\d,]+) \| ([\d,]+) → ([\d,]+) \(([-+\d,]+)\) \| ([\d,]+) → ([\d,]+)\\\* \(([-+\d,]+)\\\*, ([-+\d.]+)%\\\*\) \| \*\*\+([\d,]+)\\\*\*\* \| ([\d.]+)% \|',l)
    if not m_: continue
    k=key(m_.group(2)); g=lambda i:int(m_.group(i).replace(',','').replace('+',''))
    r22,r26,v22,v26=I(k,'D_reg_22'),I(k,'D_reg_26'),I(k,'D_votes_22'),I(k,'D_votes_26')
    val=v26-F(v22*r26,r22)
    for lab_,got,exp in [('pop',g(3),names[k]['pop']),('r22',g(4),r22),('r26',g(5),r26),('dr',g(6),r26-r22),('v22',g(7),v22),('v26',g(8),v26),('dv',g(9),v26-v22),('pct',m_.group(10).lstrip('+'),r1(F(100*(v26-v22),v22))),('value',g(11),int(val+F(1,2))),('share',m_.group(12),r1(100*val/I(k,'total_votes_26')))]:
        chk(f'flip {m_.group(2)} {lab_}',got,exp)
    checked_flip=True
nflip=len([l for l in P.split('\n') if re.match(r'\| \d+ \| [A-Za-z ]+ \| [\d,]+ \| [\d,]+ →',l)]); chk('flip rows parsed',nflip,10)
# ---------- 6. every remaining numeric token on the page must be accounted for ----------
txt=re.sub(r'\]\([^)]*\)',']',P); txt=re.sub(r'https?://\S+','',txt)
txt='\n'.join(l for l in txt.split('\n') if not re.match(r'\| [A-Z][a-zA-Z ]+ \| 20\d{3} \|',l))  # equipment rows checked cell by cell above
ok=set()
def add(*xs):
    for x in xs: ok.add(str(x))
for k in B:
    for c in ('D_reg_22','D_reg_26','D_votes_22','D_votes_26','total_votes_26','population_2025'): add(f"{int(B[k][c]):,}")
    add(f"{int(B[k]['D_reg_22'])-int(B[k]['D_reg_26']):,}",f"{int(B[k]['D_votes_26'])-int(B[k]['D_votes_22']):,}")
    v=I(k,'D_votes_26')-F(I(k,'D_votes_22')*I(k,'D_reg_26'),I(k,'D_reg_22')); add(f"{int(v+F(1,2)):,}",r1(100*v/I(k,'total_votes_26')),r1(F(100*(I(k,'D_votes_26')-I(k,'D_votes_22')),I(k,'D_votes_22'))),r2(dG[k]))
for v,pops in vend.items(): add(len(pops),r1(F(100*len(pops),105)),f"{sum(pops):,}",r1(F(100*sum(pops),tot)))
add(f"{tot:,}",up,dn,*mmc.values(),len(vc),ren,sum(e['central'] for e in EXP.values()),sum(e['models26']!=e['models22'] for e in EXP.values()),sum(e['paperpb'] for e in EXP.values()))
for y in ('22','26'):
    m,b,r=ols(y); add(f"{float(m):.2f}",f"{float(b):.2f}",f"{float(r):.3f}")
for zf in glob.glob(K+'pkg/*.zip'): add(f"{os.path.getsize(zf)/1e6:.1f}")
for v in D.values():
    if isinstance(v,list): add(len(v))
STRUCT={'2022','2026','2025','2023','2020','105','101','93','254','280','254','1080','1350','14399','17125','91','52','20701','25','45','75','2708','2422','1122','3009','3107','4404','4610','4611','215','216','217','218','219','221','228','704','2025-25','22','6','5','4','3','2','1','0','10','11','12','13','14','15','16','17','18','19','20','24','30','31','40','1%','8','9','7','00','1960','100','80','3.0','1:25','10810','0946','2(a)','4','16','24','2026,','11','26','1:00','9:15','8:20','08'}  # 08 = month/day in the SOS timestamp 11/08/2026
toks=re.findall(r'\d[\d,]*(?:\.\d+)?',txt)
bad=sorted({t for t in toks if t.rstrip('.,') not in ok and t.rstrip('.,') not in STRUCT})
# ---------- report ----------
res=dict(checked=checked,mismatches=mism,unexplained_numeric_tokens=bad)
json.dump(res,open(K+'out/verify_resources_pass2.json','w'),indent=1,default=str)
print('checks:',checked,'mismatches:',len(mism)); [print('  MISMATCH',m) for m in mism[:40]]
print('unexplained numeric tokens on Resources page:',bad)
sys.exit(1 if mism else 0)
