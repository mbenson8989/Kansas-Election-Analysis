"""Build the Kansas 105-county voting-equipment table from Verified Voting raw exports (retrieved 2026-11-24).
Population and FIPS from Census Vintage 2025 (co-est2025-alldata.csv). Pandas-based builder (pass 1)."""
import pandas as pd, json, glob, re
RAW='/workspace/kansas-resources/raw/vv/'; CEN='/workspace/kansas/raw/co-est2025-alldata.csv'
TAB=['Hand-Fed Optical Scanner','Batch-Fed Optical Scanner','Hybrid BMD/Tabulator']
def load(y):
    m=pd.read_csv(RAW+f'vv{y}/verifier-machines.csv',skiprows=1,dtype=str,index_col=False,keep_default_na=False)
    j=pd.read_csv(RAW+f'vv{y}/verifier-jurisdictions.csv',skiprows=1,dtype=str,index_col=False,keep_default_na=False)
    for d in (m,j): d['county']=d.Jurisdiction.str.replace(' County','',regex=False); d['fips']=d['FIPS code'].str[:5]
    return m,j
m26,j26=load(2026); m22,j22=load(2022)
def eq(r): return f"{r.Manufacturer} {r.Model} ({r['Equipment Type']})"
p=pd.read_csv(CEN,encoding='latin-1',dtype={'STATE':str,'COUNTY':str}); p=p[(p.STATE=='20')&(p.COUNTY!='000')]
p['fips']=p.STATE+p.COUNTY; pop=p.set_index('fips').POPESTIMATE2025.astype(int); cname=p.set_index('fips').CTYNAME.str.replace(' County','')
api={}
for f in glob.glob(RAW+'county_api_2026/*.json'):
    d=json.load(open(f)); api[re.search(r'(\d{5})\.json',f).group(1)]=d
rows=[]
for fips,g in m26.groupby('fips'):
    jr=j26[j26.fips==fips].iloc[0]; c=jr.county
    assert cname[fips]==c,(fips,c,cname[fips])
    ed=g[(g['Election Day Standard']=='Yes')&g['Equipment Type'].isin(TAB)]
    mail=g[(g['Mail Ballot/Absentee Equipment']=='Yes')&g['Equipment Type'].isin(TAB)]
    acc=g[(g['Election Day Accessible']=='Yes')&g['Equipment Type'].isin(['Ballot Marking Device','Hybrid BMD/Tabulator','DRE-Touchscreen'])]
    pb=g[g['Equipment Type'].str.contains('Poll Book')]
    g22=m22[m22.fips==fips]; ed22=g22[(g22['Election Day Standard']=='Yes')&g22['Equipment Type'].isin(TAB)]
    vendors=sorted(set(ed.Manufacturer))
    vv=sorted(set(g[g['Equipment Type'].isin(TAB+['Ballot Marking Device'])].VVPAT))
    ms=[x for x in (api.get(fips,{}).get('machines') or []) if x.get('equip_type') in TAB+['Ballot Marking Device']]
    vers=sorted({x['model']+': '+', '.join(f"{lab} {x[k]}" for lab,k in [('hardware','hardware_version'),('firmware','firmware_version'),('software','software_version')] if x.get(k))+' (other version fields blank)' for x in ms if (x.get('hardware_version') or x.get('firmware_version') or x.get('software_version'))})
    notes=[]
    s26=sorted(set(eq(r) for _,r in ed.iterrows())); s22=sorted(set(eq(r) for _,r in ed22.iterrows()))
    k26=sorted(set((r.Model,r['Equipment Type']) for _,r in ed.iterrows())); k22=sorted(set((r.Model,r['Equipment Type']) for _,r in ed22.iterrows()))
    if k26!=k22: notes.append('Election-day tabulator equipment changed from 2022: '+('; '.join(s22) if s22 else '(none listed)')+'.')
    elif s26!=s22: notes.append('Same election-day tabulator model as 2022; the manufacturer name changed in Verified Voting from '+'/'.join(sorted(set(ed22.Manufacturer)))+' to '+'/'.join(sorted(set(ed.Manufacturer)))+'.')
    if (ed['Equipment Type']=='Batch-Fed Optical Scanner').all() and len(ed): notes.append('Election-day ballots are tabulated on a batch-fed (central-count) scanner.')
    if (ed['Equipment Type']=='Hybrid BMD/Tabulator').any(): notes.append('Uses a hybrid ballot-marking device/tabulator on election day.')
    rows.append(dict(County=c,FIPS=fips,Population=int(pop[fips]),
        **{'Marking method':jr['Election Day Marking Method'],'ED tabulator vendor':'; '.join(vendors) if vendors else 'Not listed',
        'ED tabulator equipment':'; '.join(s26) if s26 else 'Not listed','Mail tabulator equipment':'; '.join(sorted(set(eq(r) for _,r in mail.iterrows()))) or 'Not listed',
        'Accessible device':'; '.join(sorted(set(eq(r) for _,r in acc.iterrows()))) or 'Not listed',
        'Paper record / VVPAT':'VVPAT: '+('/'.join(vv) if vv else 'not listed')+(' (Verified Voting does not list a VVPAT for these systems)' if vv==['N/A'] else ''),
        'Software/firmware':'; '.join(vers) if vers else 'Not listed by Verified Voting',
        'Poll book':'; '.join(sorted(set(f"{r.Manufacturer} {r.Model}".strip() if r.Manufacturer not in ('','Not Applicable') else r['Equipment Type'] for _,r in pb.iterrows()))) or 'Not listed',
        'ED tabulator equipment 2022':'; '.join(s22) if s22 else 'Not listed',
        'Status':'Confirmed (Verified Voting 2026 record)' if len(ed) else 'Unconfirmed',
        'Source':f"https://verifiedvoting.org/verifier/#mode/navigate/map/ppEquip/mapType/normal/year/2026/state/20/county/{fips[2:]}",
        'Notes':' '.join(notes)}))
o=pd.DataFrame(rows).sort_values('Population',ascending=False).reset_index(drop=True)
assert len(o)==105 and o.FIPS.is_unique
o.to_csv('/workspace/kansas-resources/out/KS_105_County_Voting_Equipment_VerifiedVoting.csv',index=False)
summ={}
for v,g in o.groupby('ED tabulator vendor'): summ[v]=dict(counties=len(g),population=int(g.Population.sum()))
summ['_total_pop']=int(o.Population.sum()); summ['_n_confirmed']=int((o.Status.str.startswith('Confirmed')).sum())
summ['_api_version_fields_nonempty']=sum(1 for d in api.values() for x in (d.get('machines') or []) if x.get('hardware_version') or x.get('firmware_version') or x.get('software_version'))
summ['_api_audit']=sorted({json.dumps(d['official_audit']) for d in api.values()})
json.dump(summ,open('/workspace/kansas-resources/out/equipment_summary_pass1.json','w'),indent=1); print(json.dumps(summ,indent=1))
print(o[o.Notes!=''][['County','Notes']].to_string())
print(o['Mail tabulator equipment'].eq('Not listed').sum(), o['Accessible device'].eq('Not listed').sum(), o['Poll book'].value_counts().head(8))
