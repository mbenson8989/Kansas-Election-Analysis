"""PASS C - cell-by-cell check of the Kansas 105-county PDF against the RAW SOS files only.
Independent of pass A/B and their CSVs: parses the raw SOS precinct workbook (party column), the raw SOS county
result pages (BeautifulSoup), the raw SOS registration workbooks and the raw Census file, recomputes every displayed
figure with exact decimal half-up rounding, and compares to the text extracted from the PDF with pdftotext."""
import openpyxl, csv, re, os, subprocess, json, sys
from decimal import Decimal as D, ROUND_HALF_UP
from bs4 import BeautifulSoup
RAW='/workspace/kansas/raw/'; HT='/workspace/kansas-wiki/verification/ent_refetch_20261119/'; V='/workspace/kansas-wiki/verification/'
PDF=sys.argv[1]
canon=lambda s: ''.join(ch for ch in str(s).lower() if ch.isalpha())
# 2022 governor votes: SOS precinct workbook. Statewide sheet by Party column; the four big counties from their own sheets' county-total rows
wb=openpyxl.load_workbook(RAW+'2022-General-Election-Governor-Results-By-Precinct.xlsx',read_only=True,data_only=True)
V22={}
it=wb['Governor'].iter_rows(values_only=True); h=next(it); ic,ip,iv=h.index('County'),h.index('Party'),h.index('Votes')
for r in it:
    if r[ic] is None: continue
    d=V22.setdefault(canon(r[ic]),[0,0]); v=r[iv] if isinstance(r[iv],(int,float)) else 0
    d[1]+=int(v); d[0]+=int(v) if r[ip]=='Democratic' else 0
for sh in wb.sheetnames[1:]:
    rows=list(wb[sh].iter_rows(values_only=True))
    hi=next(i for i,r in enumerate(rows) if any('Kelly' in str(c) for c in r)); hdr=rows[hi]
    gc=[j for j,c in enumerate(hdr) if any(n in str(c) for n in ('Kelly','Schmidt','Pyle','Cordell'))]; kc=[j for j in gc if 'Kelly' in str(hdr[j])][0]
    tr=[r for r in rows[hi+1:] if any('TOTAL' in str(c).upper() for c in r[:3] if c is not None)]
    assert len(tr)==1,(sh,len(tr)); assert canon(sh) not in V22
    V22[canon(sh)]=[int(tr[0][kc]),sum(int(tr[0][j]) for j in gc)]
# 2026 governor votes: SOS county pages (ent.sos.ks.gov, last updated 11/08/2026 9:15 PM), BeautifulSoup
V26={}; upd=set(); PREC=[]
for fn in os.listdir(HT):
    if not fn.endswith('.html'): continue
    s=BeautifulSoup(open(HT+fn,encoding='utf-8',errors='ignore').read(),'html.parser')
    h3=[x for x in s.find_all('h3') if x.get_text(strip=True)=='Governor / Lt. Governor']; assert len(h3)==1,fn
    txt=[]; node=h3[0]
    for el in node.find_all_next('p'):
        t=el.get_text(strip=True); txt.append(t)
        if len(txt)>40: break
    vals={}; i=0
    while i<len(txt)-1 and len(vals)<2:
        m=re.match(r'^([DR])-(.+)$',txt[i])
        if m and re.fullmatch(r'[\d,]+',txt[i+1]): vals[m.group(1)]=int(txt[i+1].replace(',','')); i+=2
        else: i+=1
    assert set(vals)=={'D','R'},(fn,txt[:12])
    V26[canon(fn[:-5])]=[vals['D'],vals['D']+vals['R']]
    pm=re.search(r'County Precincts Reporting:\s*(\d+)\s*of\s*(\d+)',s.get_text(' ')); PREC.append((int(pm.group(1)),int(pm.group(2))))
    lu=s.find(string=re.compile('Last Updated')); upd.add(lu.find_next('span').get_text(strip=True) if lu else '?')
# registration: SOS workbooks
def reg(f,sheet,cn,cd,ct):
    ws=openpyxl.load_workbook(RAW+f,read_only=True,data_only=True)[sheet]; it=ws.iter_rows(values_only=True); h=list(next(it)); out={}; gt=None
    for r in it:
        if r[h.index(cn)] is None: continue
        rec=(int(str(r[h.index(cd)]).replace(',','')),int(str(r[h.index(ct)]).replace(',','')))
        if str(r[h.index(cn)]).strip()=='Grand Total': gt=rec
        else: out[canon(r[h.index(cn)])]=rec
    return out,gt
R22,G22=reg('11-2022-Voter-Registration-Numbers-by-County.xlsx','Nov. 2022','Jurisdiction','Democratic','Grand Total')
R26,G26=reg('10-2026-Voter-Registration-Numbers-by-County.xlsx','By County','County','Democratic','Total')
POP={}
for r in csv.DictReader(open(RAW+'co-est2025-alldata.csv',encoding='latin-1')):
    if r['STATE']=='20' and r['COUNTY']!='000': POP[canon(r['CTYNAME'].replace(' County',''))]=int(r['POPESTIMATE2025'])
K=set(R26); assert len(K)==105 and K==set(R22)==set(V22)==set(V26)==set(POP),(len(K),len(V22),len(V26),len(POP))
# statewide checks against SOS published totals
off=open(RAW+'2022-General-Official-Vote-Totals.txt').read(); i0=off.index('Governor / Lt. Governor'); blk=off[i0:off.index('\nSecretary of State',i0)]
off_d=int(re.search(r'D-Laura Kelly[^\d]+([\d,]+)',blk).group(1).replace(',','')); off_t=sum(int(x.replace(',','')) for x in re.findall(r'\s([\d,]{5,})\s+[\d.]+%',blk))
SW=dict(reg22_sum_vs_grand_total=(tuple(map(sum,zip(*R22.values()))),G22),reg26_sum_vs_grand_total=(tuple(map(sum,zip(*R26.values()))),G26),
        gov22_sum_vs_official_totals_pdf=((sum(v[0] for v in V22.values()),sum(v[1] for v in V22.values())),(off_d,off_t)),
        gov26_D_sum_vs_holscher_551243=(sum(v[0] for v in V26.values()),551243),last_updated=sorted(upd))
sw_ok=all(v[0]==v[1] for k,v in SW.items() if k!='last_updated') and SW['reg22_sum_vs_grand_total'][1]==(523317,1975535) and SW['reg26_sum_vs_grand_total'][1]==(521669,2027520)
# expected display strings
def q1(n,d): x=(D(n)/D(d)).quantize(D('0.1'),rounding=ROUND_HALF_UP); return x
pc=lambda n,d: ('+' if n>0 else '-' if n<0 else '')+str(abs(q1(100*n,d)))+'%'
sg=lambda x: ('+' if x>0 else '-' if x<0 else '')+f"{abs(x):,}"
NAME={canon(r[0]):r[0] for r in [[x] for x in []]}
names={}
ws=openpyxl.load_workbook(RAW+'10-2026-Voter-Registration-Numbers-by-County.xlsx',read_only=True,data_only=True)['By County']
for r in list(ws.iter_rows(values_only=True))[1:]:
    if r[1] and r[1]!='Grand Total': names[canon(r[1])]=str(r[1]).strip()
def rowfor(name,pop,r22,r26,v22,v26):
    out=[name,f"{pop:,}",str(q1(100*r26[0],r26[1]))+'%']
    for a,b in ((r22[0],r26[0]),(v22[0],v26[0]),(v22[1],v26[1])): out+=[f"{a:,}",f"{b:,}",sg(b-a),pc(b-a,a)]
    return out
EXP={}
for k in K: EXP[names[k]]=rowfor(names[k],POP[k],R22[k],R26[k],V22[k],V26[k])
S=lambda dct,i: sum(v[i] for v in dct.values())
EXP['Statewide total']=rowfor('Statewide total',sum(POP.values()),(S(R22,0),S(R22,1)),(S(R26,0),S(R26,1)),(S(V22,0),S(V22,1)),(S(V26,0),S(V26,1)))
order=sorted(K,key=lambda k:(-D(R26[k][0])/D(R26[k][1])))
# PDF text
txt=subprocess.run(['pdftotext','-layout',PDF,'-'],capture_output=True,text=True).stdout
pages=txt.split('\f'); got=[]; tokre=re.compile(r'[+\-]?[\d,]+(?:\.\d+)?%?')
for pg in pages:
    for line in pg.split('\n'):
        m=re.match(r'^\s*([A-Z][A-Za-z]+(?: total)?)\s+((?:[+\-]?[\d,]+(?:\.\d+)?%?\s+){13}[+\-]?[\d,]+(?:\.\d+)?%?)\s*$',line)
        if m and (m.group(1) in EXP): got.append([m.group(1)]+m.group(2).split())
cols=['County','Population (Jul 1, 2025)','Dem Reg Share 2026 %','Dem Reg 2022','Dem Reg 2026','Reg Change #','Reg Change %','Dem Gov Votes 2022','Dem Gov Votes 2026*','Vote Change #','Vote Change %','Total Gov Votes 2022','Total Gov Votes 2026*','Total Gov Vote Change #','Total Gov Vote Change %']
mism=[]; cells=0
for g in got:
    e=EXP[g[0]]
    for j,(a,b) in enumerate(zip(g,e)):
        cells+=1
        if a!=b: mism.append(dict(county=g[0],column=cols[j],pdf=a,raw=b))
names_pdf=[g[0] for g in got]
order_ok=names_pdf==[names[k] for k in order]+['Statewide total']
# notes/legend facts
up=[names[k] for k in order if R26[k][0]>R22[k][0]]; dn=[k for k in K if V26[k][0]<V22[k][0]]
flat=re.sub(r'\s+',' ',subprocess.run(['pdftotext',PDF,'-'],capture_output=True,text=True).stdout)
facts=dict(legend_reg_rose_list=f"Democratic registration rose ({len(up)}): {', '.join(up)}" in flat, votes_fell_count=f"Democratic governor votes fell ({len(dn)} counties)" in flat,
           leads_by_share=names[order[0]]=='Douglas', leads_raw=names[max(K,key=lambda k:R26[k][0])]=='Johnson',
           precincts_4168=(sum(a for a,b in PREC)==sum(b for a,b in PREC)==4168 and 'all 4,168 precincts reporting' in flat), pages=len([p for p in pages if p.strip()]), page_labels=all(f'Page {i} of {len([p for p in pages if p.strip()])}' in pages[i-1] for i in range(1,len([p for p in pages if p.strip()])+1)),
           header_repeats=all('Dem Reg' in p and 'County' in p for p in pages if p.strip()))
rep=dict(rows_found=len(got),expected_rows=106,cells_checked=cells,mismatches=mism,order_matches_raw_sort=order_ok,statewide_checks=SW,statewide_ok=sw_ok,facts=facts,
         PASS=len(got)==106 and cells==1590 and not mism and order_ok and sw_ok and all(v for k,v in facts.items() if k!='pages'))
json.dump(rep,open(V+'pdf_raw_cell_check.json','w'),indent=1,default=str)
print(json.dumps({k:v for k,v in rep.items() if k!='mismatches'},indent=1,default=str)); print('mismatches',len(mism)); [print(x) for x in mism[:30]]
