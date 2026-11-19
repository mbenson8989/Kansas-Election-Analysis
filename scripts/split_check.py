"""Confirm the split tables carry exactly the original cells: rejoin Part A + Part B by row and compare with the pre-split table, cell for cell."""
import re,collections,json,sys
old=open(sys.argv[1]).read().split('\n'); new=open(sys.argv[2]).read().split('\n')
def tables(L):
    out=[];i=0
    while i<len(L):
        if L[i].startswith('|') and i+1<len(L) and L[i+1].startswith('|---'):
            j=i
            while j<len(L) and L[j].startswith('|'): j+=1
            out.append([[c.strip() for c in l.strip().strip('|').split('|')] for k,l in enumerate(L[i:j]) if k!=1]); i=j
        else: i+=1
    return out
TO=[t for t in tables(old) if len(t)==106]; TN=[t for t in tables(new) if len(t)==106]
assert len(TO)==2 and len(TN)==4
rep={}
for k,o in enumerate(TO):
    a,b=TN[2*k],TN[2*k+1]
    ok_rows=all(ra[0]==rb[0] and ra[1]==rb[1] for ra,rb in zip(a,b))
    rejoined=[ra+rb[2:] for ra,rb in zip(a,b)]
    # restore original column order by header
    hdr=o[0]; pos=[rejoined[0].index(h) for h in hdr]
    same=all([r[p] for p in pos]==ro for r,ro in zip(rejoined,o))
    rep[f'table{k+1}']=dict(original_cols=len(o[0]),part_a_cols=len(a[0]),part_b_cols=len(b[0]),rows=len(o)-1,county_pop_aligned=ok_rows,cells_identical=same,original_cells=(len(o)-1)*len(o[0]),new_cells=(len(a)-1)*len(a[0])+(len(b)-1)*len(b[0]))
num=lambda s: collections.Counter(re.findall(r'[−+\-]?\d[\d,]*(?:\.\d+)?%?',re.sub(r'\(https?://[^)]*\)','','\n'.join(s))))
extra=num(new)-num(old); missing=num(old)-num(new)
pops=collections.Counter(r[1] for r in TO[0][1:])+collections.Counter(r[1] for r in TO[1][1:])
rep['tokens_missing']=dict(missing); rep['extra_tokens_minus_repeated_population']=dict(extra-pops); rep['repeated_population_tokens']=sum(pops.values()); rep['extra_equals_population']= not (pops-extra) 
rep['ALL_OK']=all(v['cells_identical'] and v['county_pop_aligned'] for k,v in rep.items() if k.startswith('table')) and not missing
print(json.dumps(rep,indent=1,ensure_ascii=False)); json.dump(rep,open('/workspace/kansas-wiki/verification/split_table_check.json','w'),indent=1,ensure_ascii=False)
