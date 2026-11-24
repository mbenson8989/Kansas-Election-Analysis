"""Kansas county clerk letters (105). Figures from pass A county table (raw SOS); officers from SOS county election officer list (retrieved 2026-11-24);
equipment from the Verified Voting table built in build_equipment.py. Writes one markdown per county; md2docx + soffice make Word/PDF."""
import pandas as pd, json, os
A=pd.read_csv('/workspace/kansas-wiki/verification/passA_counties.csv').set_index('county')
O=pd.read_html('/workspace/kansas-resources/raw/sos/county_election_officers_all.html',converters={c:str for c in ['COUNTY','OFFICER','ADDRESS1','ADDRESS2','CITY','STATE','ZIP']})[0].fillna('')
O['COUNTY']=O.COUNTY.str.strip(); O=O.set_index('COUNTY')
E_=pd.read_csv('/workspace/kansas-resources/out/KS_105_County_Voting_Equipment_VerifiedVoting.csv',keep_default_na=False).set_index('County')
COMM={'Johnson','Sedgwick','Shawnee','Wyandotte'}
OUT='/workspace/kansas-resources/letters/clerk/md/'; os.makedirs(OUT,exist_ok=True)
def f(n): return f"{int(n):,}"
def ch(a,b,star=''):
    d=int(b)-int(a); p=100*d/int(a); s='+' if d>0 else ''
    return f"{f(a)} → {f(b)}{star} ({s}{d:,}{star}, {s}{p:.1f}%{star})".replace('+-','-')
st=A[['D_reg_22','D_reg_26','D_votes_22','D_votes_26','total_votes_22','total_votes_26']].sum()
SW=f"Statewide, registered Democrats changed {ch(st.D_reg_22,st.D_reg_26)} and Democratic votes for governor changed {ch(st.D_votes_22,st.D_votes_26,'*')}."
rows=[]
for c in A.index:
    a=A.loc[c]; o=O.loc[c]; e=E_.loc[c]
    title='Election Commissioner' if c in COMM else 'County Clerk'
    last=o.OFFICER.replace('(Jamie) ','').split()[-1]
    addr=o.ADDRESS1.strip()+(', '+o.ADDRESS2.strip() if o.ADDRESS2.strip() else '')
    dr=int(a.D_reg_26)-int(a.D_reg_22); dv=int(a.D_votes_26)-int(a.D_votes_22)
    if dr<0 and dv>0: pat='In this county, Democratic registration declined while Democratic votes for governor rose.'
    elif dr<0 and dv<0: pat='In this county, Democratic registration and Democratic votes for governor both declined.'
    elif dr>0 and dv>0: pat='In this county, Democratic registration and Democratic votes for governor both rose.'
    elif dr>0 and dv<0: pat='In this county, Democratic registration rose while Democratic votes for governor declined.'
    else: pat='In this county, at least one of these figures did not change.'
    md=f"""# {c.upper()} COUNTY — Clerk letter (records and audit request)

Date: ______________________

{o.OFFICER}
{title}, {c} County
{addr}
{o.CITY}, KS {o.ZIP}

Re: November 3, 2026 general election — Kansas Open Records Act request for existing election records, and request for additional post-election audit coverage, {c} County

Dear {title} {last}:

I am writing as a member of the public concerning election records and the post-election audit for the November 3, 2026 general election in {c} County, where you serve as the county election officer. Using Kansas Secretary of State figures for the governor race, I compared the 2022 and 2026 general elections in {c} County:

- Registered Democrats, Nov. 1, 2022 to Oct. 1, 2026: {ch(a.D_reg_22,a.D_reg_26)}
- Democratic votes for governor, 2022 to 2026: {ch(a.D_votes_22,a.D_votes_26,'*')}
- Total votes for governor (all candidates), 2022 to 2026: {ch(a.total_votes_22,a.total_votes_26,'*')}

2022 votes are the Secretary of State's official results. *2026 votes are the Secretary of State's unofficial election-night results (last updated Nov. 8, 2026, 9:15 PM) and are not final until the state canvass is certified (scheduled for Dec. 1, 2026). Registration counts are the Secretary of State's county registration reports and include active and inactive voters. These are votes for the Democratic candidate, not a count of registered Democrats who voted; that would require the voter-history file.

{pat} {SW} I offer these figures as an observation, not an allegation. Candidate choice, turnout, and voters crossing party lines can all move them, and county totals alone cannot tell those causes apart. The cast vote record, which shows the ballots in their batches, is the record that could.

**Federal litigation context.** Executive Order 14248 (Mar. 25, 2025) was challenged in *California v. Trump*, No. 1:25-cv-10810 (D. Mass.) (summary-judgment order June 24, 2026; judgment and permanent injunction July 13, 2026), and *LULAC v. Executive Office of the President*, No. 1:25-cv-0946 (D.D.C.) (permanent injunction as to Section 2(a), Oct. 31, 2025). This letter does not assert that Kansas was a plaintiff in either case, and it does not rely on that litigation for standing or for any new right to records. I mention it only as context: county records requests and the county's statutory audit duties stand independently, however the litigation resolves.

**Records request.** Under the Kansas Open Records Act, K.S.A. 45-215 et seq. (a "public record" includes "any recorded information, regardless of form, characteristics or location," K.S.A. 45-217(l)(1)), and in light of the preservation requirements of K.S.A. 25-2708 and 52 U.S.C. § 20701, I request copies of the following existing records for the November 3, 2026 general election:

- **Cast vote record export:** the full cast vote record (CVR) export for the election, if the county has generated or retained one, including batch identifiers, ballot sequence or position numbers, and all contests (including down-ballot columns), in electronic form, with any information that could identify a voter removed. Verified Voting lists the county's election-day tabulator as {e['ED tabulator equipment']}; please tell me if that has changed.
- **Precinct returns:** the printed return of the optical scanning equipment for each precinct, which K.S.A. 25-4611(e) makes open to the public upon completion of the count.
- **Post-election audit records:** the audit report submitted under K.S.A. 25-3009(d), the record of how the audited precincts and races were randomly selected, and the public notice given under K.S.A. 25-3009(c).
- **Equipment test records:** the results of the pre-election test and the post-canvass retest of the optical scanning equipment under K.S.A. 25-4610(b).
- **Hash verification:** the hash values for the certified voting system version the county used, and any record of hash verification performed on that system, so they can be compared with the trusted build published for the certified version. If no such record exists, please say so.

**Audit request (a request, not a records demand).** K.S.A. 25-3009(a) requires a manual audit of 1% of precincts, with a minimum of one, before the county canvass, and K.S.A. 25-3009(d) allows the county election officer or the Secretary of State to require audits of additional precincts when a discrepancy cannot be resolved. I ask that the county consider a further hand count covering ballots from precincts representing at least thirty to forty percent of the county's total ballots, prioritizing the precincts with the highest ballot volume, so the sample reflects where most voters actually cast ballots, and that the audited ballots be cross-checked against the cast vote record. This is a request, not a claim of statutory entitlement. Because K.S.A. 25-2422 limits disclosure of ballot contents and K.S.A. 25-3107(a) limits when sealed ballots may be opened, I ask the county to perform or arrange any such count itself, in public, and not to let me inspect ballots. If the county concludes it has no authority to do so, I ask that it say so in writing.

I understand that some Kansas counties have treated cast vote records and ballot images as closed under K.S.A. 45-221(a)(1) and K.S.A. 25-2422, and that the Legislative Division of Post Audit reported in February 2023 that state law does not address cast vote records. This request is limited to records that already exist. If any record is withheld in whole or in part, I ask that you provide the written statement described in K.S.A. 45-218(d), citing the specific provision of law, tell me whether the record exists, and release any portion that can be separated under K.S.A. 45-221(d). If a record is held by another office, please tell me where. I will pay reasonable fees under K.S.A. 45-219; please tell me the estimated cost before proceeding.

Please confirm the addressee and mailing address if your office's information has changed since the Secretary of State's published list of county election officers was retrieved on November 24, 2026.

Thank you for your time and for the work your office does to conduct elections.

Signature: _______________________________________________

Printed name: _______________________________________________

Address: _______________________________________________

Phone / email: _______________________________________________
"""
    open(OUT+f"{c.replace(' ','_')}_County_Clerk_Letter.md",'w').write(md)
    rows.append(dict(county=c,officer=o.OFFICER,title=title,address=addr,city=o.CITY,zip=o.ZIP,D_reg_22=int(a.D_reg_22),D_reg_26=int(a.D_reg_26),D_votes_22=int(a.D_votes_22),D_votes_26=int(a.D_votes_26),total_votes_22=int(a.total_votes_22),total_votes_26=int(a.total_votes_26),pattern=pat,ed_equipment=e['ED tabulator equipment']))
pd.DataFrame(rows).to_csv('/workspace/kansas-resources/out/clerk_letter_merge_fields.csv',index=False)
print(len(rows), SW)
