"""PDF table, pass B: csv + exact fractions with half-up rounding, from the pass B county table (openpyxl/csv pipeline over re-downloaded SOS files)."""
import csv, json
from fractions import Fraction as F
from decimal import Decimal, ROUND_HALF_UP
V='/workspace/kansas-wiki/verification/'
name={r['county'].lower().replace(' ',''):r['county'] for r in csv.DictReader(open(V+'passA_counties.csv'))}
R=[]
for r in csv.DictReader(open(V+'passB_counties.csv')):
    d={k:int(r[k]) for k in ('D_reg_22','D_reg_26','D_votes_22','D_votes_26','total_votes_22','total_votes_26','total_reg_26','population_2025')}
    d['county']=name[r['key']]; R.append(d)
assert len(R)==105
T={k:sum(x[k] for x in R) for k in R[0] if k!='county'}; T['county']='Statewide total'
assert (T['D_reg_26'],T['total_reg_26'],T['D_votes_26'])==(521669,2027520,551243)
sh=lambda x:F(100*x['D_reg_26'],x['total_reg_26'])
R.sort(key=lambda x:-sh(x))
def r1(f): return Decimal(f.numerator)/Decimal(f.denominator)
q=lambda f:str(abs(r1(f)).quantize(Decimal('0.1'),rounding=ROUND_HALF_UP))
c=lambda x:f"{x:,}"; s=lambda x:('+' if x>0 else '-' if x<0 else '')+f"{abs(x):,}"
p=lambda f:('+' if f>0 else '-' if f<0 else '')+q(f)+'%'
out=[]
for x in R+[T]:
    row=[x['county'],c(x['population_2025']),q(sh(x))+'%']
    for k in ('D_reg','D_votes','total_votes'):
        a,b=x[k+'_22'],x[k+'_26']; row+=[c(a),c(b),s(b-a),p(F(100*(b-a),a))]
    out.append(row)
json.dump(out,open(V+'pdfB_rows.json','w'),indent=0); print(len(out),out[0],out[-1])
