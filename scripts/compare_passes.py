"""Compare pass A vs pass B vs the published CSV, figure by figure, and statewide sums vs SOS statewide totals."""
import csv, json, re, sys
V='/workspace/kansas-wiki/verification/'
PUB='/workspace/kansas-elections/charts/kansas_deltaG_spec_by_county_population_sorted.csv'
def key(s): return re.sub(r'[^a-z]','',str(s).lower())
A={key(r['county']):r for r in csv.DictReader(open(V+'passA_counties.csv'))}
B={r['key']:r for r in csv.DictReader(open(V+'passB_counties.csv'))}
P={key(r['county']):r for r in csv.DictReader(open(PUB))}
INT=['population_2025','D_votes_22','R_votes_22','other_votes_22','total_votes_22','D_reg_22','total_reg_22','D_votes_26','R_votes_26','total_votes_26','D_reg_26','total_reg_26','ballots_22']
FLT=['G22','G26','dG']
PUBF=['population_2025','D_votes_22','total_votes_22','D_reg_22','total_reg_22','G22','D_votes_26','total_votes_26','D_reg_26','total_reg_26','G26','dG']
rows=[]; nAB=nAP=0; mAB=[]; mAP=[]
assert set(A)==set(B)==set(P) and len(A)==105
for k in sorted(A,key=lambda k:-int(A[k]['population_2025'])):
    for c in INT+FLT:
        a=float(A[k][c]); b=float(B[k][c]); tol=1e-9 if c in FLT else 0
        ok=abs(a-b)<=tol; nAB+=1
        if not ok: mAB.append((k,c,a,b))
        line=dict(county=A[k]['county'],field=c,passA=A[k][c],passB=B[k][c],AB_match=ok)
        if c in PUBF:
            p=float(P[k][c]); okp=abs(a-p)<=(5.0001e-5 if c in FLT else 0); nAP+=1  # published CSV rounds G to 4 dp
            if not okp: mAP.append((k,c,a,p))
            line.update(published=P[k][c],A_pub_match=okp)
        rows.append(line)
with open(V+'compare_A_B_published_figure_by_figure.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['county','field','passA','passB','AB_match','published','A_pub_match']); w.writeheader(); w.writerows(rows)
SA=json.load(open(V+'passA_statewide.json')); SB=json.load(open(V+'passB_statewide.json'))
SOS=dict(D_votes_22=499849,R_votes_22=477591,other_votes_22=20452+11106,D_votes_26=551243,R_votes_26=543599,total_votes_26=1094842)
st=[]
for k,v in SOS.items(): st.append((k,v,SA[k],SB[k],SA[k]==v==SB[k]))
st.append(('reg22 county sum vs SOS Grand Total row',SA['reg22_grand_total_row'],[SA['D_reg_22'],SA['total_reg_22']],[SB['D_reg_22'],SB['total_reg_22']],SA['reg22_grand_total_row']==[SA['D_reg_22'],SA['total_reg_22']]==[SB['D_reg_22'],SB['total_reg_22']]))
st.append(('reg26 county sum vs SOS Grand Total row',SA['reg26_grand_total_row'],[SA['D_reg_26'],SA['total_reg_26']],[SB['D_reg_26'],SB['total_reg_26']],SA['reg26_grand_total_row']==[SA['D_reg_26'],SA['total_reg_26']]==[SB['D_reg_26'],SB['total_reg_26']]))
rep=dict(counties=len(A),fields_per_county=len(INT+FLT),figures_A_vs_B=nAB,mismatches_A_vs_B=mAB,figures_A_vs_published=nAP,mismatches_A_vs_published=mAP,
  statewide_checks=[dict(item=a,SOS=b,passA=c,passB=d,ok=e) for a,b,c,d,e in st],
  transcription_vs_SOS_refetch_diffs=SB['transcription_vs_refetch_diffs'],ent_last_updated=SB['ent_last_updated_values'],
  wyandotte_2022_note=SB['big_county_precinct_vs_total_row']['WYANDOTTE'],blank_vote_cells_2022=SB['blank_vote_cells_2022'])
rep['CLEAN']=not mAB and not mAP and all(x['ok'] for x in rep['statewide_checks']) and not rep['transcription_vs_SOS_refetch_diffs']
json.dump(rep,open(V+'compare_report.json','w'),indent=1,default=str)
print(json.dumps({k:rep[k] for k in ['counties','figures_A_vs_B','mismatches_A_vs_B','figures_A_vs_published','mismatches_A_vs_published','CLEAN']},default=str))
for x in rep['statewide_checks']: print(x)
sys.exit(0 if rep['CLEAN'] else 1)
