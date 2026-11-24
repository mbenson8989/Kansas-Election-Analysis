import json
a=json.load(open('pass1.json')); b=json.load(open('pass2.json')); bad=[]; n=0
mp={'Governor':'Governor / Lt. Governor','US Senate':'United States Senate','Secretary of State':'Secretary of State','State Treasurer':'State Treasurer','Commissioner of Insurance':'Commissioner of Insurance'}
km={'baseline':'base','positive_only|remove':'pos_rm','positive_only|reassign':'pos_ra','all_residuals|remove':'all_rm','all_residuals|reassign':'all_ra'}
def chk(x,y,lab,tol=1e-9):
    global n; n+=1
    if abs(x-y)>tol: bad.append((lab,x,y))
for c,v in a['counties'].items():
    w=b['county'][c]
    for k1,k2 in (('pop','pop'),('D','D'),('S','S'),('fit','fit'),('resid_pts','rp'),('resid_votes','rv'),('gov_total','gov_T')): chk(v[k1],w[k2],c+k1)
    for r1,r2 in mp.items():
        for cand,val in a['county_race'][c][r1].items(): chk(val,b['race_county'][c][r2][cand],c+r1+cand)
for r1,r2 in mp.items():
    for k1,k2 in km.items():
        x=a['races'][r1][k1]; y=b['race'][r2][k2]
        for i,f in enumerate(['D','R','total','D_share','R_share','margin_pts']): chk(x[f],y[i],r1+k1+f)
chk(a['sum_pos_votes'],b['pos'],'pos'); chk(a['sum_neg_votes'],b['neg'],'neg')
chk(a['constants']['m_refit'],b['refit'][0],'m'); chk(a['constants']['b_refit'],b['refit'][1],'b')
print('checks',n,'mismatches',len(bad),bad[:5])
json.dump({'checks':n,'mismatches':bad},open('compare_report.json','w'))
