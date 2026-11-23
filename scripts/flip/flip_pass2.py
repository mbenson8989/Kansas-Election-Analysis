"""PASS 2: openpyxl + csv + regex over SOS county HTML re-downloaded 11/19/2026; exact Fractions. Independent of pass 1."""
import openpyxl,csv,re,os,json
from fractions import Fraction as F
R='/workspace/kansas/raw/'; HT='/workspace/kansas-wiki/verification/ent_refetch_20261119/'
key=lambda s:re.sub(r'[^a-z]','',str(s).lower())
wb=openpyxl.load_workbook(R+'2022-General-Election-Governor-Results-By-Precinct.xlsx',read_only=True,data_only=True)
v22={}
for r in list(wb['Governor'].iter_rows(values_only=True))[1:]:
    if r[0] is None or r[5] is None: continue
    v22.setdefault(key(r[0]),0)
    if str(r[3]).startswith('Laura Kelly'): v22[key(r[0])]+=r[5]
for sh in ['JOHNSON','SEDGWICK','SHAWNEE','WYANDOTTE']:
    rows=list(wb[sh].iter_rows(values_only=True)); hdr=rows[1]; cols=[j for j,h in enumerate(hdr) if h and 'Kelly' in str(h)]
    for r in rows[2:]:
        if r[1] and 'COUNTY TOTALS' in str(r[1]).upper(): v22[key(sh)]=sum(r[j] for j in cols)
v26={}
for fn in os.listdir(HT):
    if not fn.endswith('.html'): continue
    s=open(HT+fn,encoding='utf-8',errors='ignore').read(); blk=s[s.index('<h3>Governor / Lt. Governor</h3>'):]; blk=blk[:blk.index('end of .race-candidate-list')]
    c=re.findall(r'<p>([DR])-([^<]+)</p>\s*</div>\s*<div class="col-2">\s*<p>([\d,]+)</p>',blk)
    v26[key(fn[:-5])]={a:int(n.replace(',','')) for a,_,n in c}
def reg(f,sh,cn):
    rows=list(openpyxl.load_workbook(R+f,read_only=True,data_only=True)[sh].iter_rows(values_only=True)); h=list(rows[0]); out={}
    for r in rows[1:]:
        if r[h.index(cn)] and r[h.index(cn)]!='Grand Total': out[key(r[h.index(cn)])]=int(r[h.index('Democratic')])
    return out
g22=reg('11-2022-Voter-Registration-Numbers-by-County.xlsx',openpyxl.load_workbook(R+'11-2022-Voter-Registration-Numbers-by-County.xlsx',read_only=True).sheetnames[0],'Jurisdiction')
g26=reg('10-2026-Voter-Registration-Numbers-by-County.xlsx','By County','County')
names={key(r['county']):r['county'] for r in csv.DictReader(open(R+'ent2026_governor_transcribed.csv'))}
out={}
for k,n in names.items():
    gap=F(v26[k]['D'])-F(v22[k])*F(g26[k],g22[k])
    out[n]=dict(reg22=g22[k],reg26=g26[k],v22=v22[k],v26=v26[k]['D'],gap_num=gap.numerator,gap_den=gap.denominator,gap=float(gap))
assert len(out)==105
json.dump(out,open('pass2.json','w'),indent=1)
