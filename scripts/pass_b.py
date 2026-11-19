"""PASS B (no pandas). Written separately from pass A: openpyxl cell iteration, csv module, regex over the
SOS county HTML pages re-downloaded from ent.sos.ks.gov on 2026-11-19, exact rational arithmetic (fractions)."""
import openpyxl, csv, re, html, json, os
from fractions import Fraction as F
RAW='/workspace/kansas/raw/'; V='/workspace/kansas-wiki/verification/'; HT=V+'ent_refetch_20261119/'
def key(s): return re.sub(r'[^a-z]','',str(s).lower())   # 'McPherson'->'mcpherson'
def num(v): return int(str(v).replace(',','').strip())
# ---- 2022 governor: candidate-name matching, precinct rows summed ----
wb=openpyxl.load_workbook(RAW+'2022-General-Election-Governor-Results-By-Precinct.xlsx',read_only=True,data_only=True)
v22={}; blank_cells=0
for r in list(wb['Governor'].iter_rows(values_only=True))[1:]:
    if r[0] is None: continue
    k=key(r[0]); d=v22.setdefault(k,{'D':0,'R':0,'O':0}); cand=r[3]
    if r[5] is None: blank_cells+=1; continue   # 28 blank vote cells (no votes recorded), counted as 0
    if cand.startswith('Laura Kelly'): d['D']+=r[5]
    elif cand.startswith('Derek Schmidt'): d['R']+=r[5]
    elif cand.startswith(('Seth Cordell','Dennis Pyle')): d['O']+=r[5]
    else: raise ValueError(cand)
bigcheck={}
for sh in ['JOHNSON','SEDGWICK','SHAWNEE','WYANDOTTE']:
    rows=list(wb[sh].iter_rows(values_only=True)); hdr=rows[1]
    cols={j:('D' if 'Kelly' in str(h) else 'R' if 'Schmidt' in str(h) else 'O') for j,h in enumerate(hdr) if h and any(n in str(h) for n in ('Kelly','Schmidt','Cordell','Pyle'))}
    prec={'D':0,'R':0,'O':0}; tot=None; redacted=0
    for r in rows[2:]:
        if r[1] and 'COUNTY TOTALS' in str(r[1]).upper(): tot={p:sum(r[j] for j,q in cols.items() if q==p) for p in 'DRO'}; continue
        if isinstance(r[0],(int,float)):
            if any(str(r[j]).strip().lower()=='redacted' for j in cols): redacted+=1; continue
            for j,q in cols.items(): prec[q]+=(r[j] or 0)
    bigcheck[sh]=dict(precinct_sum=prec,county_total_row=tot,match=prec==tot,redacted_precinct_rows=redacted)
    v22[key(sh)]=tot
# ---- 2026 governor: regex over re-downloaded SOS county pages; also read hand transcription with csv ----
v26={}; upd=set(); creport={}
for fn in sorted(os.listdir(HT)):
    if not fn.endswith('.html'): continue
    s=open(HT+fn,encoding='utf-8',errors='ignore').read()
    blk=s[s.index('<h3>Governor / Lt. Governor</h3>'):]; blk=blk[:blk.index('end of .race-candidate-list')]
    pr=re.search(r'County Precincts Reporting:\s*(\d+)\s*of\s*(\d+)',blk)
    cands=re.findall(r'<p>([DR])-([^<]+)</p>\s*</div>\s*<div class="col-2">\s*<p>([\d,]+)</p>',blk)
    assert len(cands)==2,(fn,cands)
    v26[key(fn[:-5])]={c[0]:num(c[2]) for c in cands}; v26[key(fn[:-5])]['prec']=(int(pr.group(1)),int(pr.group(2)))
    m=re.search(r'Last Updated:</strong>\s*<span[^>]*>([^<]+)',s); upd.add(m.group(1).strip() if m else '?')
tr={key(r['county']):r for r in csv.DictReader(open(RAW+'ent2026_governor_transcribed.csv'))}
transcription_diffs=[(k,tr[k]['holscher_D'],tr[k]['masterson_R'],v26[k]['D'],v26[k]['R']) for k in v26 if num(tr[k]['holscher_D'])!=v26[k]['D'] or num(tr[k]['masterson_R'])!=v26[k]['R']]
assert set(tr)==set(v26)
# ---- registration ----
def regrows(f,sheet,cname,cdem,ctot):
    ws=openpyxl.load_workbook(RAW+f,read_only=True,data_only=True)[sheet]; rows=list(ws.iter_rows(values_only=True)); h=list(rows[0])
    out={}; gt=None
    for r in rows[1:]:
        if r[h.index(cname)] is None: continue
        rec=(num(r[h.index(cdem)]),num(r[h.index(ctot)]))
        if str(r[h.index(cname)]).strip()=='Grand Total': gt=rec
        else: out[key(r[h.index(cname)])]=rec
    return out,gt
reg22,gt22=regrows('11-2022-Voter-Registration-Numbers-by-County.xlsx','Nov. 2022','Jurisdiction','Democratic','Grand Total')
reg26,gt26=regrows('10-2026-Voter-Registration-Numbers-by-County.xlsx','By County','County','Democratic','Total')
# ---- 2022 turnout file (ballots cast, advance by mail) ----
tw=openpyxl.load_workbook(RAW+'2022-General-Election-Turnout-Information.xlsx',read_only=True,data_only=True)['Sheet1']
tb={}
for r in tw.iter_rows(values_only=True):
    if r[0] and str(r[0]).endswith(' COUNTY'): tb[key(str(r[0])[:-7])]=dict(adv_mail=r[1],ballots=r[3],reg_in_turnout=r[5])
# ---- population (csv module) ----
pop={}
with open(RAW+'co-est2025-alldata.csv',encoding='latin-1') as f:
    for r in csv.DictReader(f):
        if r['STATE']=='20' and r['COUNTY']!='000': pop[key(r['CTYNAME'].replace(' County',''))]=int(r['POPESTIMATE2025'])
ks=set(v22)
for nmd,dct in [('v26',v26),('reg22',reg22),('reg26',reg26),('turnout',tb),('pop',pop)]: assert set(dct)==ks,(nmd,set(dct)^ks)
assert len(ks)==105
rows=[]
for k in sorted(ks,key=lambda k:-pop[k]):
    D22,R22,O22=v22[k]['D'],v22[k]['R'],v22[k]['O']; T22=D22+R22+O22
    D26,R26=v26[k]['D'],v26[k]['R']; T26=D26+R26
    (DR22,TR22),(DR26,TR26)=reg22[k],reg26[k]
    G22=F(100*D22,T22)-F(100*DR22,TR22); G26=F(100*D26,T26)-F(100*DR26,TR26)
    rows.append(dict(key=k,population_2025=pop[k],D_votes_22=D22,R_votes_22=R22,other_votes_22=O22,total_votes_22=T22,D_reg_22=DR22,total_reg_22=TR22,
        D_votes_26=D26,R_votes_26=R26,total_votes_26=T26,D_reg_26=DR26,total_reg_26=TR26,ballots_22=tb[k]['ballots'],adv_mail_22=tb[k]['adv_mail'],
        G22=float(G22),G26=float(G26),dG=float(G26-G22),prec_rep_26=v26[k]['prec'][0],prec_tot_26=v26[k]['prec'][1]))
with open(V+'passB_counties.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); [w.writerow({a:(repr(b) if isinstance(b,float) else b) for a,b in r.items()}) for r in rows]
S={c:sum(r[c] for r in rows) for c in ['D_votes_22','R_votes_22','other_votes_22','total_votes_22','D_reg_22','total_reg_22','D_votes_26','R_votes_26','total_votes_26','D_reg_26','total_reg_26','ballots_22']}
S.update(blank_vote_cells_2022=blank_cells,reg22_grand_total_row=list(gt22),reg26_grand_total_row=list(gt26),big_county_precinct_vs_total_row=bigcheck,
         transcription_vs_refetch_diffs=transcription_diffs,ent_last_updated_values=sorted(upd),
         all_precincts_reported_2026=all(r['prec_rep_26']==r['prec_tot_26'] for r in rows))
json.dump(S,open(V+'passB_statewide.json','w'),indent=1,default=str); print(json.dumps(S,default=str)[:3000])
