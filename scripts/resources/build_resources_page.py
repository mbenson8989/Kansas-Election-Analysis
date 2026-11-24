import pandas as pd, json, re
W='https://github.com/mbenson8989/Kansas-Election-Analysis/wiki/'; RAWU='https://raw.githubusercontent.com/mbenson8989/Kansas-Election-Analysis/main/'
old=open('/workspace/kansas-wiki/wikiclone/Resources.md').read()
flip=old[old.index('## Ten counties'):old.index('## Did you know? The Guarantee Clause')].rstrip()
gc=old[old.index('## Did you know? The Guarantee Clause'):].rstrip()
flip=flip.replace('## Ten counties','### Ten counties').replace('### The ten graphics','#### The ten graphics')
gc=gc.replace('## Did you know? The Guarantee Clause','### Did you know? The Guarantee Clause').replace("- Morissa Benson's write-up: [A pattern you can't unsee](https://moebenson.substack.com/p/a-pattern-you-cant-unsee).","- Morissa Benson's write-up: [A pattern you can't unsee](https://moebenson.substack.com/p/a-pattern-you-cant-unsee).")
E_=pd.read_csv('/workspace/kansas-resources/out/KS_105_County_Voting_Equipment_VerifiedVoting.csv',keep_default_na=False)
sizes=json.load(open('/workspace/kansas-resources/out/zip_sizes.json'))
D=json.load(open('/workspace/kansas-resources/raw/regions/kdot_districts.json'))
eq=json.load(open('/workspace/kansas-wiki/repo/verification/eqA.json'))
tot=int(E_.Population.sum())
def mb(b): return f"{b/1e6:.1f} MB"
L=[]
a=L.append
a("""# Resources

> **\\*2026 figures are unofficial.** The Kansas Secretary of State's 2026 general-election results are election-night results (last updated 11/08/2026 9:15 PM); state certification is scheduled for December 1, 2026. 2022 figures are the SOS official results. Kansas has party registration, so "registration" on this wiki means registered Democrats (active plus inactive) from the SOS county registration reports.

This page collects the documents, data sources, laws, equipment records, and graphics behind the Kansas Election Analysis in one place. Everything here is offered as analysis and as draft correspondence. Nothing on this page is an accusation against any county, official, or vendor.

## Letter to the Kansas Attorney General

A draft letter to Attorney General Kris W. Kobach asking his office to say publicly whether cast vote records are open to the public under the Kansas Open Records Act (K.S.A. 45-215 et seq.), how K.S.A. 25-2422's limit on disclosing ballot contents applies to a cast vote record that names no voter, and to help make sure 2026 election records are kept for the full 22-month preservation period (K.S.A. 25-2708; 52 U.S.C. § 20701). It cites the Guarantee Clause (U.S. Const. art. IV, § 4), the Article II enforcement-duty language in Executive Order 14399, Attorney General Opinion No. 2025-25, and the Legislative Division of Post Audit's February 2023 election-security report. It is respectful and non-accusatory, and it presents the Kansas analysis as a hypothesis, not proof. It is a draft for Morissa to review and send herself; it has not been sent.

- [Download the Attorney General letter (PDF)]("""+RAWU+"""Kansas_Attorney_General_Letter.pdf)
- [Download the Attorney General letter (Word)]("""+RAWU+"""Kansas_Attorney_General_Letter.docx)

Every quotation in the letter was checked word for word against the official text of the statute, order, opinion, or report it quotes. The addressee and office address are from the [Kansas Attorney General's office](https://www.ag.ks.gov/about-us/contact-us).

## County clerk letters

One letter for each of Kansas's 105 counties, addressed to that county's election officer, in both PDF and Word. In 101 counties the election officer is the elected county clerk; in Johnson, Sedgwick, Shawnee and Wyandotte it is the election commissioner appointed by the Secretary of State ([SOS: County Election Offices](https://sos.ks.gov/elections/county-election-offices.html)). Each ZIP has a `PDF` folder and a `Word` folder. Pick your district, or download everything at once.
""")
allk='Kansas_Clerk_Letters_All_105_Counties'
a(f"- **[Download all 105 Kansas county clerk letters (ZIP, 105 counties, {mb(sizes[allk][1])})]({RAWU}downloads/{allk}.zip)**\n\nBy district:\n")
for k,v in D.items():
    if not k.startswith('District'): continue
    n,name=k.split(' ',2)[1],k.split(' ',2)[2]; zn=f"Kansas_Clerk_Letters_District_{n}_{name.replace(' Kansas','').replace(' ','_')}"
    a(f"- [Download District {n} ({name}) county clerk letters (ZIP, {sizes[zn][0]} counties, {mb(sizes[zn][1])})]({RAWU}downloads/{zn}.zip)")
a(f"""
Not sure which district your county is in? [Download the county-to-district lookup (CSV)]({RAWU}downloads/Kansas_County_to_District_Lookup.csv), or use the table below.

**How the counties are grouped.** The Kansas Secretary of State does not divide the state into election regions; each county runs its own elections. So these files use a standard official grouping that covers all 105 counties exactly once: the **[Kansas Department of Transportation's six districts](https://www.ksdot.gov/about/our-organization/districts)**. The grouping is only for convenience. It has nothing to do with how the letters or the analysis were built.

**What each letter contains.** The letters follow Morissa's Nebraska 93-county cast-vote-record request letter, in the same tone and structure as the Texas clerk letters, rewritten for Kansas law: the county's own 2022 and 2026\\* figures for registered Democrats, Democratic governor votes and total governor votes; federal litigation context (no standing claimed); an Open Records Act request for existing records only (cast vote record export, precinct returns under K.S.A. 25-4611(e), the K.S.A. 25-3009 post-election audit records, the K.S.A. 25-4610(b) equipment test records, and hash-verification records); a request, not a demand, for wider hand-count coverage; and blank date, signature, and sender lines. Addressees and mailing addresses come from the [Kansas Secretary of State's list of all county election officers](https://www.sos.ks.gov/elections/county_election_officers_all.aspx), retrieved November 24, 2026. All 105 counties had a name and address on that list, so no addressee is a placeholder. Please confirm each addressee against the county's own website before sending, because officials change. Nothing has been mailed or emailed.

| District | Counties | County list |
|---|---|---|""")
for k,v in D.items():
    if k.startswith('District'): a(f"| {k.replace('District ','').replace(' ', '. ',1)} | {len(v)} | {', '.join(sorted(v))} |")
a(f"""
## Kansas Secretary of State data sources

Every election number on this wiki comes from the Kansas Secretary of State (SOS):

- **2022 general election (official):** [SOS election results page](https://sos.ks.gov/elections/elections-results.html): 2022 General Election Governor Results by Precinct (xlsx) and the 2022 General Election Official Vote Totals
- **2026 general election (unofficial\\*):** [SOS election-night results, ent.sos.ks.gov](https://ent.sos.ks.gov/), one page per county, last updated 11/08/2026 9:15 PM; all 105 county pages re-downloaded November 19, 2026
- **Voter registration by county and party:** [SOS voter registration statistics](https://sos.ks.gov/elections/voter-registration-statistics.html): November 1, 2022 and October 1, 2026 county reports (active plus inactive)
- **County election officers:** [SOS All County Election Officers Information](https://www.sos.ks.gov/elections/county_election_officers_all.aspx), used for the clerk-letter addressees
- **Post-election audit:** [SOS post-election audit page](https://sos.ks.gov/elections/post-election-audit.html) (K.S.A. 25-3009)

County populations (used only to sort the tables) are [U.S. Census Bureau Vintage 2025 estimates](https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv) (July 1, 2025).

## County-level results

- [Kansas County PDF Information]({W}Kansas-County-PDF-Information): what each column of the county PDF means
- [Download the 105-county PDF]({RAWU}Kansas_105_County_Democratic_Registration_and_Vote_Change.pdf): registered Democrats, Democratic governor votes, and total governor votes for every county, 2022 vs 2026\\*, with changes and statewide totals
- [105-County Data (CSV)]({RAWU}KS_Governor_2022_2026_DeltaG_by_County.csv): the county figures as a spreadsheet
- Choose any county on the [SOS election-night results site](https://ent.sos.ks.gov/) to see its 2026 returns

## Voting equipment by county

This table lists the in-person and mail-ballot equipment Verified Voting records for each of Kansas's 105 counties. It is offered as background on how ballots are marked and counted. **Equipment information is context only. It is not evidence of wrongdoing, and a vendor name does not imply a problem with that county's results.**

**Why Verified Voting.** The Kansas Secretary of State's County Election Offices page links "a list of what voting system each county uses," but that link (`sos.ks.gov/forms/elections/voting systems.pdf`) returned the SOS "Page Not Found" page when checked on November 24, 2026, and an archived copy could not be retrieved. So, as on the Texas wiki, equipment comes from [Verified Voting's Verifier](https://verifiedvoting.org/verifier/): the public CSV download for Kansas (state FIPS 20), years 2026 and 2022, plus the public county API behind each Verifier county page, retrieved November 24, 2026, 8:20 AM CST (America/Chicago). Verified Voting's 2026 Kansas export is labeled *The Verifier - November 2026 / Kansas. Data as of November 24, 2026.* Each county row links to its Verifier county page. Population figures are Census July 1, 2025 estimates, so the list reads in the same largest-to-smallest order as the other Kansas tables.

**Confirmed vs. unconfirmed.** A county is marked *Confirmed* when Verified Voting's 2026 record lists an election-day tabulator for it. All 105 counties meet that test; **0 counties are unconfirmed**. For Johnson County the equipment also matches the county's own page ([Johnson County Election Office: Voting Systems](https://www.jocoelection.org/voting-election-info/voting-systems): ES&S ExpressVote ballot-marking devices and DS200 scanners).

### Statewide vendor summary (2026 election-day tabulators)

Counts below use the election-day tabulator Verified Voting lists for each county (hand-fed or batch-fed optical scanner, or a hybrid ballot-marking device/tabulator). Ballot-marking devices, poll books, and the email and fax channels for military and overseas voters are not counted as the election-day tabulator.
""")
g=E_.groupby('ED tabulator vendor').agg(n=('County','size'),pop=('Population','sum')).sort_values('n',ascending=False)
for v,r in g.iterrows():
    a(f"- **{v}:** {r.n} counties ({100*r.n/105:.1f}% of counties); population {int(r['pop']):,} ({100*r['pop']/tot:.1f}% of the 105-county total of {tot:,})")
mm=E_['Marking method'].value_counts()
a(f"""
No county lists more than one election-day tabulator vendor in the 2026 Verifier data. Marking method: {mm.get('Hand marked paper ballots and BMDs',0)} counties use hand-marked paper ballots with ballot-marking devices (BMDs) available, and {mm.get('Ballot Marking Devices for all voters',0)} use BMDs for all voters.

The downloadable CSV also records each county's poll book, 2022 election-day tabulator equipment, status, source link, and notes.

### Download the full table

- CSV (all 105 counties and all columns): [KS_105_County_Voting_Equipment_VerifiedVoting.csv]({RAWU}KS_105_County_Voting_Equipment_VerifiedVoting.csv) (raw download link)

### All 105 counties, largest to smallest

| County | FIPS | Population | Marking method | ED tabulator vendor | ED tabulator equipment | Mail tabulator equipment | Accessible device | Paper record / VVPAT | Software/firmware | Status | Source | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |""")
for _,r in E_.iterrows():
    a(f"| {r.County} | {r.FIPS} | {r.Population} | {r['Marking method']} | {r['ED tabulator vendor']} | {r['ED tabulator equipment']} | {r['Mail tabulator equipment']} | {r['Accessible device']} | {r['Paper record / VVPAT']} | {r['Software/firmware']} | {'Confirmed' if r.Status.startswith('Confirmed') else 'Unconfirmed'} | [Verifier]({r.Source}) | {r.Notes} |")
ver=E_[E_['Software/firmware']!='Not listed by Verified Voting']
ch=E_[E_.Notes.str.contains('changed from 2022')]; ren=E_[E_.Notes.str.contains('manufacturer name changed')]; cen=E_[E_.Notes.str.contains('central-count')]; hyb=E_[E_.Notes.str.contains('hybrid')]
pb=E_[E_['Poll book']=='Paper Poll Book']
a(f"""
### Gaps and what Verified Voting does not list

- **Kansas SOS county equipment list:** the SOS link to its county-by-county voting-system list returned "Page Not Found" on November 24, 2026 (see above). If the SOS restores it, this table should be cross-checked against it.
- **Software and firmware versions:** Verified Voting's county API has hardware, firmware and software version fields, but firmware and software are empty for every machine in all 105 counties. Hardware version is filled in only for the ES&S ExpressVote in {len(ver)} counties ({', '.join(ver.County)}: "HW 3.0"). Everything else shows "Not listed by Verified Voting." Versions were not inferred from anywhere else.
- **Post-election audit codes:** the county API's audit fields (comprehensiveness, binding, audit type) are blank for every Kansas county in this retrieval. Kansas's audit rule is K.S.A. 25-3009 (see the laws table below).
- **Missing election-day tabulator:** none. **Missing mail-ballot tabulator:** none. **No accessible device listed:** none.
- **Multiple tabulator vendors in one county:** none.
- **Election-day ballots counted on a central (batch-fed) scanner:** {len(cen)} counties ({', '.join(cen.County)}).
- **Hybrid ballot-marking device/tabulator on election day:** {', '.join(hyb.County)}.
- **Election-day tabulator model changed from 2022 to 2026 in Verified Voting:** {len(ch)} counties ({', '.join(ch.County)}). The 2022 model is in each county's Notes.
- **Vendor renamed, same model:** in {len(ren)} counties the 2022 record lists "Dominion" and the 2026 record lists "Liberty Vote (Dominion)" for the same tabulator model. That is a change in how the vendor is named, not a change in equipment.
- **Paper poll books:** {len(pb)} counties list a paper poll book rather than an electronic one.
- Every county also lists email and fax options for military and overseas voters. Those are special-purpose channels, not the county's ordinary in-person or mail tabulator, and are omitted from the vendor counts above.

Please treat this as a snapshot of Verified Voting's records as of the retrieval date. County equipment can change, and official questions about a county's system should be confirmed with the county election officer or the Kansas Secretary of State.

## Graphics

Charts and shareable graphics built from this wiki's data. Tap an image to open it full size. The full chart set, with captions, is on [Graphs]({W}Graphs).

### Vote-share change bars sorted by 2022 Democratic share

[![2022 Democratic share and 2026 change, sorted by 2022 share]({RAWU}KS_governor_2022_Dem_share_vs_gain_bar_chart.png)]({RAWU}KS_governor_2022_Dem_share_vs_gain_bar_chart.png)
""")
cj=json.load(open('/workspace/kansas-resources/out/charts_pass1.json'))
a(f"*All 105 counties sorted by 2022 Democratic share of governor votes. Blue is the 2022 share; orange is the 2022 to 2026\\* gain; red below zero is a decline. The Democratic share rose in {cj['gain_up']} counties and fell in {cj['gain_down']}\\*.*\n")
a(f"### Ceiling counties\n\n[![Ceiling counties Delta-G by population]({RAWU}KS_Ceiling_Counties_DeltaG_by_Population.png)]({RAWU}KS_Ceiling_Counties_DeltaG_by_Population.png)\n")
a("*Ceiling counties (the five highest ΔG): "+', '.join(f"{c} {v:+.2f}\\*" for c,v in cj['ceiling'])+".*\n")
a(f"""### Charts from the Graphs page

- [County slope chart, G 2022 to G 2026\\*]({RAWU}KS_Slope_G2022_to_G2026_County_Slope_Chart.png)
- [Forward surplus fit, S against D]({RAWU}KS_Forward_Surplus_Fit_S_vs_D.png)
- [ΔG bars by population]({RAWU}KS_DeltaG_Bars_by_Population.png) and [ΔG scatter with county names]({RAWU}KS_DeltaG_by_Population_Scatter_Names.png)
- [Stacked share bars with registration loss, by population]({RAWU}KS_Stacked_Share_Reg_Loss_by_Population.png) and [sorted by 2022 Democratic share]({RAWU}KS_Stacked_Share_Reg_Loss_by_2022_Dem_Share.png)
- [Expected-loss residual bars by population]({RAWU}KS_Expected_Loss_Residual_Bars_by_Population.png)
""")
a(flip+"\n")
a(gc+"\n")
f22,f26=eq['fwd_2022'],eq['fwd_2026']
a(f"""## Where the method began: the Cedar County audit

The method was first worked out in Morissa Benson's [Cedar County Audit](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit) in her Nebraska Election Analysis wiki. This Kansas wiki applies the same approach using Kansas's own numbers only.

## The reverse-factoring method in brief

1. **Two shares per county, per year.** For each of the 105 counties, in 2022 and in 2026\\*, take (a) the Democratic share of all governor votes (all candidates) and (b) **D**, the Democratic share of all registered voters (active plus inactive). Kansas has party registration, so D is real registration, not a stand-in.
2. **The surplus.** The surplus is (a) − D, in percentage points: the Democratic share of governor votes minus the Democratic share of registration. The wiki's other pages call this G.
3. **The Kansas line.** Graph every county's surplus against its D and fit one straight line: **S = multiplier × (D/100) + offset**. Kansas's own 105 counties, weighted equally, give:
   - **2022:** S = {f22['mult']:.2f} × (D/100) + {f22['const']:.2f}, R² {f22['r2']:.3f}
   - **2026\\* (unofficial):** S = {f26['mult']:.2f} × (D/100) + {f26['const']:.2f}, R² {f26['r2']:.3f}. The 2026 line uses unofficial figures and will be refit after certification.
4. **Residuals, floor and ceiling.** A county's residual is its actual surplus minus the surplus the line predicts. See [Floor and Ceiling Counties]({W}Floor-and-Ceiling) and [Locked Kansas Formula]({W}Locked-Kansas-Formula).
5. **Checked against the source.** Two independent programs rebuilt every county figure from the raw SOS files and agreed, with 0 mismatches.

The [README]({W}README) explains it all in plain language. This is an analytical model, with evidence for and against. It is not proof of anything.

## Kansas laws cited in the Attorney General letter

| Law | What it covers | Official text |
|---|---|---|
| K.S.A. 45-216 | Kansas Open Records Act policy: public records are open to any person, and the act is liberally construed | [K.S.A. 45-216](https://www.kslegislature.gov/b2025_26/laws/045_000_0000_chapter/045_002_0000_article/045_002_0016_section/045_002_0016_k/) |
| K.S.A. 45-217(l) | "Public record" means any recorded information, regardless of form | [K.S.A. 45-217](https://www.kslegislature.gov/b2025_26/laws/045_000_0000_chapter/045_002_0000_article/045_002_0017_section/045_002_0017_k/) |
| K.S.A. 45-218(c), (d) | Requests acted on within three business days; on request, a written denial citing the specific law; referral to the right custodian | [K.S.A. 45-218](https://www.kslegislature.gov/b2025_26/laws/045_000_0000_chapter/045_002_0000_article/045_002_0018_section/045_002_0018_k/) |
| K.S.A. 45-219 | Copies and fees | [K.S.A. 45-219](https://www.kslegislature.gov/b2025_26/laws/045_000_0000_chapter/045_002_0000_article/045_002_0019_section/045_002_0019_k/) |
| K.S.A. 45-221(a)(1), (d) | Exception for records closed by statute; open material must be separated and released. No exception names ballots or cast vote records | [K.S.A. 45-221](https://www.kslegislature.gov/b2025_26/laws/045_000_0000_chapter/045_002_0000_article/045_002_0021_section/045_002_0021_k/) |
| K.S.A. 45-228 | Attorney General and county or district attorney investigations of Open Records Act violations | [K.S.A. 45-228](https://www.kslegislature.gov/b2025_26/laws/045_000_0000_chapter/045_002_0000_article/045_002_0028_section/045_002_0028_k/) |
| K.S.A. 25-2422 | Crime for an election official to disclose the contents of any ballot, except as a court orders in an election contest | [K.S.A. 25-2422](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_024_0000_article/025_024_0022_section/025_024_0022_k/) |
| K.S.A. 25-1122(i) | Records made by the county election officer are open to inspection, except voter identification information and ballot numbers | [K.S.A. 25-1122](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_011_0000_article/025_011_0022_section/025_011_0022_k/) |
| K.S.A. 25-2708 | State and national ballots preserved 22 months; county and local ballots six months | [K.S.A. 25-2708](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_027_0000_article/025_027_0008_section/025_027_0008_k/) |
| K.S.A. 25-3009 | Post-election manual audit of 1% of precincts (minimum one) before the canvass, in public; additional precincts when a discrepancy cannot be resolved | [K.S.A. 25-3009](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_030_0000_article/025_030_0009_section/025_030_0009_k/) |
| K.S.A. 25-3107(a) | County canvass; limits on opening sealed ballots | [K.S.A. 25-3107](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_031_0000_article/025_031_0007_section/025_031_0007_k/) |
| K.S.A. 25-4404 | Secretary of State certification of voting systems, including firmware and software | [K.S.A. 25-4404](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_044_0000_article/025_044_0004_section/025_044_0004_k/) |
| K.S.A. 25-4610(b) | Optical-scan equipment tested before the election and retested within five business days after the canvass; programs and ballots retained like paper ballots | [K.S.A. 25-4610](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_046_0000_article/025_046_0010_section/025_046_0010_k/) |
| K.S.A. 25-4611(e) | The scanner's printed return is the official precinct return and is open to the public once the count is complete | [K.S.A. 25-4611](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_046_0000_article/025_046_0011_section/025_046_0011_k/) |
| K.S.A. 75-704 | Officials who may request a formal Attorney General opinion | [K.S.A. 75-704](https://www.kslegislature.gov/b2025_26/laws/075_000_0000_chapter/075_007_0000_article/075_007_0004_section/075_007_0004_k/) |
| Attorney General Opinion No. 2025-25 (Dec. 16, 2025) | The duty to destroy ballots under K.S.A. 25-2708(b) is directory and gives way to a search warrant or subpoena | [Opinion 2025-25 (PDF)](https://ksag.washburnlaw.edu/opinions/2025/2025-025.pdf) |
| Legislative Division of Post Audit (Feb. 2023) | Kansas counties held ballot images as closed records; state law does not address cast vote records | [Reviewing Kansas's Procedures for Election Security, Part 1](https://www.kslpa.gov/audit-report-library/review/) |

## Federal sources cited

- [U.S. Constitution](https://www.archives.gov/founding-docs/constitution-transcript): Article IV, § 4 (Guarantee Clause) and Article II, § 3 (Take Care)
- Executive Order 14399, "Ensuring Citizenship Verification and Integrity in Federal Elections," signed March 31, 2026, 91 Fed. Reg. 17125: [Federal Register](https://www.federalregister.gov/documents/2026/04/03/2026-06601/ensuring-citizenship-verification-and-integrity-in-federal-elections) · [official PDF](https://www.govinfo.gov/content/pkg/FR-2026-04-03/pdf/2026-06601.pdf)
- 52 U.S.C. § 20701 (22-month retention of federal election records): [Cornell LII](https://www.law.cornell.edu/uscode/text/52/20701)
- Clerk letters, litigation context: *California v. Trump*, No. 1:25-cv-10810 (D. Mass.) [judgment and permanent injunction, July 13, 2026 (PDF)](https://storage.courtlistener.com/recap/gov.uscourts.mad.282905/gov.uscourts.mad.282905.194.0.pdf); *LULAC v. Executive Office of the President*, No. 1:25-cv-0946 (D.D.C.) [order of Oct. 31, 2025 (PDF)](https://storage.courtlistener.com/recap/gov.uscourts.dcd.279032/gov.uscourts.dcd.279032.217.0.pdf)

## Morissa Benson on Substack

- [Morissa Benson's Substack](https://moebenson.substack.com/)
- [A pattern you can't unsee](https://moebenson.substack.com/p/a-pattern-you-cant-unsee)

---
*2026 figures are unofficial until the Kansas state canvass is certified (scheduled for December 1, 2026).*
""")
open('/workspace/kansas-resources/out/Resources.md','w').write('\n'.join(L))
print(len('\n'.join(L)))
