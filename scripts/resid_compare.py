import csv, json, re, sys
V='/workspace/kansas-wiki/verification/'
key=lambda s:re.sub(r'[^a-z]','',s.lower())
A={key(r['county']):r for r in csv.DictReader(open(V+'residA_counties.csv'))}; B={r['key']:r for r in csv.DictReader(open(V+'residB_counties.csv'))}
assert set(A)==set(B) and len(A)==105
F=['population_2025','exp_loss','residual','dG','offset_votes','gap_votes_ne','resid_votes_ne_live','total_votes_26']; mm=[]; n=0; rows=[]
for k in A:
    for f in F:
        a,b=float(A[k][f]),float(B[k][f]); tol=1e-6 if 'votes' in f else 1e-9; n+=1; ok=abs(a-b)<=tol
        if not ok: mm.append((k,f,a,b))
        rows.append(dict(county=A[k]['county'],field=f,passA=A[k][f],passB=B[k][f],match=ok))
    n+=1; ok=(A[k]['dem_reg_lost']=='True')==(B[k]['dem_reg_lost']=='True'); rows.append(dict(county=A[k]['county'],field='dem_reg_lost',passA=A[k]['dem_reg_lost'],passB=B[k]['dem_reg_lost'],match=ok))
    if not ok: mm.append((k,'dem_reg_lost'))
SA=json.load(open(V+'residA_statewide.json')); SB=json.load(open(V+'residB_statewide.json')); smm=[]
for k,v in SB.items():
    if k=='offset_need':
        for c in v:
            for t in v[c]:
                n+=1
                if abs(v[c][t]-SA[k][c][t])>1e-6: smm.append((k,c,t))
    else:
        n+=1
        if abs(float(v)-float(SA[k]))>1e-6: smm.append(k)
with open(V+'resid_compare_A_B_figure_by_figure.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
rep=dict(counties=105,figures_compared=n,county_mismatches=mm,statewide_mismatches=smm,CLEAN=not mm and not smm)
json.dump(rep,open(V+'resid_compare_report.json','w'),indent=1,default=str); print(rep); sys.exit(0 if rep['CLEAN'] else 1)
