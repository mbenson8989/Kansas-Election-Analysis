import json
a=json.load(open('house_pass1.json')); b=json.load(open('house_pass2.json')); bad=[]; n=0
km={'baseline':'base','positive_only|remove':'pos_rm','positive_only|reassign':'pos_ra','all_residuals|remove':'all_rm','all_residuals|reassign':'all_ra'}
for d,v in a['districts'].items():
    w=b['districts'][d]
    for k1,k2 in km.items():
        for i,f in enumerate(['D','R','total','D_share','R_share','margin_pts']):
            n+=1
            if abs(v[k1][f]-w[k2][i])>1e-12: bad.append((d,k1,f))
    for x,y in (('removed_pos','removed'),('net_all','net'),('counties','n'),('candidates','cands')):
        n+=1
        if v[x]!=w[y]: bad.append((d,x))
for c,v in a['county_house'].items():
    for d,r in v.items():
        n+=1
        if r!=b['house'][c][d]: bad.append((c,d))
for c,v in a['split'].items():
    for k in ('pos','all'):
        n+=1
        if {int(d):x for d,x in v[k].items()}!={int(d):x for d,x in b['split'][c][k].items()}: bad.append((c,k))
print('checks',n,'mismatches',len(bad),bad[:5]); json.dump({'checks':n,'mismatches':bad},open('house_compare_report.json','w'))
