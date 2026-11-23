import json
a=json.load(open('pass1.json'));b=json.load(open('pass2.json'));bad=0
assert set(a)==set(b)
for c in a:
    for k in ('reg22','reg26','v22','v26'):
        if a[c][k]!=b[c][k]: bad+=1;print('MISMATCH',c,k,a[c][k],b[c][k])
    if abs(a[c]['gap']-b[c]['gap'])>1e-6: bad+=1;print('GAP',c)
print('counties',len(a),'mismatches',bad)
