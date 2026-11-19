import pandas as pd, numpy as np, json
R='/workspace/kansas-wiki/repo/'; W='/workspace/kansas-wiki/wiki/'
o=pd.read_pickle('/tmp/ks_o.pkl'); J=json.load(open(R+'KS_results_summary.json')); K=J['K']; F=J['fits']; FL=J['neighbor_flag']; NB=J['neighbors']; TX=J['TX']; ABS=J['ABS']
CMP=json.load(open('/workspace/kansas-wiki/verification/compare_report.json'))
RAWIMG='https://raw.githubusercontent.com/mbenson8989/Kansas-Election-Analysis/main/'
CEDAR='https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit'
def sg(x,d=2): v=round(float(x),d); return ('+' if v>0 else '−' if v<0 else '')+f"{abs(v):.{d}f}"
def p2(x,d=2): return f"{float(x):.{d}f}"
def n0(x): return f"{int(x):,}"
def si(x): v=int(round(float(x))); return ('+' if v>0 else '−' if v<0 else '')+f"{abs(v):,}"
def neg(x,d=2): v=round(float(x),d); return ('−' if v<0 else '')+f"{abs(v):.{d}f}"
cap=list(K['top5']); flo=K['floor_counties']; bot=list(K['bot5']); P=K['pooled']
BANNER=("> **\\*2026 figures are UNOFFICIAL.** They are the Kansas Secretary of State (SOS) election-night results ([ent.sos.ks.gov](https://ent.sos.ks.gov/)), "
"county pages last updated 11/08/2026 9:15 PM CST, re-downloaded for all 105 counties on 11/19/2026 and unchanged. They exclude provisional ballots; county canvasses were due Nov 16, 2026 "
"and the State Board of Canvassers certifies the results Dec 1, 2026. 2022 figures are SOS official results. Governor race only. "
"Denominator: total governor votes, all candidates, in both years (never ballots cast; see [Locked Kansas Formula](Locked-Kansas-Formula)). "
"Registration: all registered voters, active + inactive, SOS county reports of Nov 1, 2022 and Oct 1, 2026 (the Nov 2026 report is not posted). "
"These pages measure a pattern; they make no claim about intent, fraud or cause.")
REL=lambda here:"\n---\n**Related:** "+" · ".join(x for x in ["[Home](Home)","[Bottom-Up Reverse Math](Reverse-Math)","[Locked Kansas Formula](Locked-Kansas-Formula)","[Floor and Ceiling Counties](Floor-and-Ceiling)","[Graphs](Graphs)"] if here not in x)+f" · [Cedar County Audit (Nebraska)]({CEDAR})\n"
SIB=("**Other state wikis:** [Nebraska](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki) · [Iowa](https://github.com/mbenson8989/Iowa-Election-Analysis/wiki) · "
"[South Dakota](https://github.com/mbenson8989/South-Dakota-Election-Analysis/wiki) · [Texas](https://github.com/mbenson8989/Texas-Election-Analysis/wiki) · [Michigan](https://github.com/mbenson8989/Michigan-Election-Analysis/wiki)\n")
f22,f26,fp=F['2022'],F['2026'],F['pooled']; yi=F['year_interaction']
def row(c,cols): return "| "+" | ".join(cols(c))+" |"
S=o.loc
UNAF22=int(pd.read_excel('/workspace/kansas/raw/11-2022-Voter-Registration-Numbers-by-County.xlsx').query("Jurisdiction=='Grand Total'").Unaffiliated.astype(int).iloc[0])
# ===================== HOME =====================
H=f"""# Kansas 2022 vs 2026 Governor Race: ΔG Method

{BANNER}

Method developed by Morissa Benson (CD3 Vice Chair, Nebraska GOP). It began with her [Cedar County Audit]({CEDAR}) on the [Nebraska Election Analysis wiki](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki), the origin of the ΔG method. This wiki applies the same county-by-county arithmetic to all 105 Kansas counties, using Kansas SOS numbers only, with one Kansas-specific change: the denominator is total governor votes in both years, because the Kansas ballots-cast data is not usable (see [Locked Kansas Formula](Locked-Kansas-Formula)). Compiled Nov 19 2026.

## Pages

Start with the Cedar County audit in Nebraska. That is where the method began. The Kansas pages then build up from one county (Seward) to the six largest counties, to all 105 counties, and to the formula.

1. [Cedar County Audit]({CEDAR}) (Nebraska wiki): where the method started
2. [Bottom-Up Reverse Math](Reverse-Math): Seward → the six largest counties → all 105 counties, and the Kansas-only constants fitted from Kansas data
3. [Locked Kansas Formula](Locked-Kansas-Formula): the equation, why Kansas uses governor votes, and a blank fill-in template
4. [Floor and Ceiling Counties](Floor-and-Ceiling): the counties at the top and bottom, the floor and ceiling constants, and the ballots-cast (over-ballot) check
5. [Graphs](Graphs): county slope chart, forward-fit scatter, ΔG by population, stacked share bars with registration loss

## Statewide at a glance

| Measure | 2022 (official) | 2026\\* (unofficial) | Change |
|---|---|---|---|
| Democratic registration (active + inactive) | {n0(o.D_reg_22.sum())} | {n0(o.D_reg_26.sum())} | {si(o.D_reg_26.sum()-o.D_reg_22.sum())} |
| Total registration (active + inactive) | {n0(o.total_reg_22.sum())} | {n0(o.total_reg_26.sum())} | +{n0(o.total_reg_26.sum()-o.total_reg_22.sum())} |
| Democratic governor votes | {n0(o.D_votes_22.sum())} (Kelly) | {n0(o.D_votes_26.sum())}\\* (Holscher) | +{n0(o.D_votes_26.sum()-o.D_votes_22.sum())}\\* |
| Total governor votes, all candidates | {n0(o.total_votes_22.sum())} (4 candidates) | {n0(o.total_votes_26.sum())}\\* (2 candidates) | +{n0(o.total_votes_26.sum()-o.total_votes_22.sum())}\\* |
| Democratic share of governor votes | {p2(P['S22'])}% | {p2(P['S26'])}%\\* | {sg(P['S26']-P['S22'])} pts\\* |
| Democratic registration share | {p2(P['D22'])}% | {p2(P['D26'])}% | {sg(P['D26']-P['D22'])} pts |
| G = vote share − registration share | {sg(P['G22'])} | {sg(P['G26'])}\\* | ΔG {sg(P['dG'])}\\* |

## County results in brief

- **ΔG rose in {K['n_G_rose']} counties and fell in {K['n_neg']}.** County median ΔG is {sg(K['median_dG'])}\\* (mean {sg(K['mean_dG'])}\\*), ranging from {sg(K['bot5']['Russell'])}\\* (Russell) to {sg(K['top5']['Seward'])}\\* (Seward). Democratic vote share rose in {K['n_S_rose']} counties; registered Democrats fell in {K['n_Dreg_fell']} of 105.
- **Ceiling counties** (five largest ΔG): Seward {sg(K['top5']['Seward'])}\\*, Ford {sg(K['top5']['Ford'])}\\*, Finney {sg(K['top5']['Finney'])}\\*, Wyandotte {sg(K['top5']['Wyandotte'])}\\*, Montgomery {sg(K['top5']['Montgomery'])}\\*.
- **Floor counties** (most Republican baseline): Wallace has the lowest 2022 Democratic vote share in the state ({p2(K['lowest5_S22']['Wallace'])}%). The ten-county floor cluster is {', '.join(flo)}; its median ΔG, the **floor constant**, is {sg(K['floor_median'])}\\*.
- **Size slope:** ΔG rises {sg(K['slope'])} points for every tenfold increase in population (r = {p2(K['slope_r'])}, p = {K['slope_p']:.1e}). The **ceiling constant** (median ΔG of Johnson, Sedgwick, Wyandotte) is {sg(K['ceiling3_median'])}\\*; with Douglas, Riley and Shawnee added it is {sg(K['ceiling6_median'])}\\*.
- **Kansas-only constants** (least squares, S = m·(D/100) + b, Kansas data only): 2022 m = {p2(f22['m'])}, b = {p2(f22['b'])} (R² {p2(f22['r2'],3)}, residual SD {p2(f22['resid_sd'])} pts); 2026\\* m = {p2(f26['m'])}, b = {p2(f26['b'])} (R² {p2(f26['r2'],3)}, residual SD {p2(f26['resid_sd'])} pts). The Kansas multiplier m sits well above the Nebraska / Iowa / South Dakota range in both years. See [Bottom-Up Reverse Math](Reverse-Math#kansas-only-constants-forward-surplus-fit).

## Read this before using the numbers

- **Kansas moved little overall, and unevenly.** Statewide ΔG is {sg(P['dG'])}\\*, and most counties fell. The largest rises are concentrated in southwest Kansas (Seward, Ford, Finney) and in Wyandotte.
- **The field changed.** 2022 had four governor candidates (Kelly, Schmidt, Pyle, Cordell; {n0(o.other_votes_22.sum())} votes went to Pyle and Cordell). 2026 had two. Because the denominator is all governor votes, some of the change in Democratic share reflects the smaller field.
- **A large ΔG is not evidence of altered votes.** Candidate choice, crossover voting by Republicans and unaffiliated voters, turnout differences, and registration-list maintenance all move these numbers. The arithmetic cannot separate them.
- **2026 is unofficial.** Every 2026 figure is marked \\* and will be re-run after the Dec 1, 2026 state certification.

## Verification

Every county figure on these pages was computed twice, by two independently written programs reading the raw SOS files: pass A (pandas) and pass B (openpyxl/csv with exact fractions, and 2026 votes re-read from the 105 SOS county pages downloaded again on Nov 19). Both passes checked {CMP['counties']} counties × {CMP['fields_per_county']} fields = {n0(CMP['figures_A_vs_B'])} figures, with **0 mismatches** between them and 0 mismatches against the published county CSV. County sums equal the SOS statewide totals in both years (2022: Kelly {n0(o.D_votes_22.sum())}, Schmidt {n0(o.R_votes_22.sum())}; 2026\\*: Holscher {n0(o.D_votes_26.sum())}, Masterson {n0(o.R_votes_26.sum())}). Every number written into these pages was then checked against the pass outputs by script. Reports are in the repo's `verification/` folder.

## Sources

All election and registration numbers come from the Kansas Secretary of State. Population (used only for sort order and the size slope) is from the U.S. Census Bureau. Retrieved Nov 15–19, 2026 (America/Chicago).

| Data | Status | URL |
|---|---|---|
| 2022 general, governor results by precinct (county totals) | OFFICIAL | https://sos.ks.gov/elections/election-results.html (Governor/Lt. Governor 2022 General Election) |
| 2022 general, official vote totals (statewide check) | OFFICIAL | https://sos.ks.gov/elections/election-results.html (2022 Official General Election Results) |
| 2022 general, turnout information (ballots cast, advance ballots returned by mail) | OFFICIAL, but broken in 6 counties (see [Floor and Ceiling](Floor-and-Ceiling#ballots-cast-check-texas-style)) | https://sos.ks.gov/elections/election-results.html (2022 General Election Turnout Information) |
| 2026 general, governor results by county (Holscher D, Masterson R) | **UNOFFICIAL\\*** (last updated 11/08/2026 9:15 PM; all 4,168 precincts reporting) | https://ent.sos.ks.gov/ (county pages, e.g. https://ent.sos.ks.gov/Seward.html) |
| Voter registration by county and party, Nov 1, 2022 | SOS monthly report | https://sos.ks.gov/elections/voter-registration-statistics.html (11-2022-Voter-Registration-Numbers-by-County.xlsx) |
| Voter registration by county and party, Oct 1, 2026 (latest posted) | SOS monthly report | https://sos.ks.gov/elections/voter-registration-statistics.html (10-2026-Voter-Registration-Numbers-by-County.xlsx) |
| County population, July 1, 2025 | U.S. Census Bureau Vintage 2025 | https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv |

Data files, charts and scripts: [mbenson8989/Kansas-Election-Analysis](https://github.com/mbenson8989/Kansas-Election-Analysis).

{SIB}{REL('Home')}"""
# ===================== REVERSE MATH =====================
s=S['Seward']
six=['Johnson','Sedgwick','Shawnee','Wyandotte','Douglas','Leavenworth']
def grp(idx):
    g=o.loc[idx]; S22=100*g.D_votes_22.sum()/g.total_votes_22.sum(); S26=100*g.D_votes_26.sum()/g.total_votes_26.sum(); D22=100*g.D_reg_22.sum()/g.total_reg_22.sum(); D26=100*g.D_reg_26.sum()/g.total_reg_26.sum()
    return S22,S26,D22,D26,(S26-D26)-(S22-D22),g.dG.median(),g.dG.min(),g.dG.max()
others=[c for c in o.index if c not in six]
G6,GO,GA=grp(six),grp(others),grp(list(o.index))
def grow(name,n,g): return f"| {name} | {n} | {p2(g[0])}% → {p2(g[1])}%\\* | {p2(g[2])}% → {p2(g[3])}% | {sg(g[1]-g[0])} | {sg(g[3]-g[2])} | {sg(g[4])} | {sg(g[5])} ({sg(g[6])} to {sg(g[7])}) |"
full="\n".join(f"| {c} | {n0(r.population_2025)} | {n0(r.D_votes_22)} | {n0(r.total_votes_22)} | {n0(r.D_reg_22)} | {n0(r.total_reg_22)} | {sg(r.G22)} | {n0(r.D_votes_26)} | {n0(r.total_votes_26)} | {n0(r.D_reg_26)} | {n0(r.total_reg_26)} | {sg(r.G26)} | {sg(r.dG)} |" for c,r in o.iterrows())
def nbrow(st,y,den): x=NB[f'{st}_{y}_{den}']; return f"{p2(x['m'])} / {p2(x['b'])}"
RM=f"""# Bottom-Up Reverse Math

{BANNER}

The same arithmetic at three levels, from one county up to the whole state, then the Kansas-only constants fitted across all 105 counties. Denominator: total governor votes, all candidates, both years. The method comes from the [Cedar County Audit]({CEDAR}) in Nebraska.

## Step 1: Seward County (the ceiling county)

| Step | Value |
|---|---|
| Democratic share of governor votes | {p2(s.S22)}% (2022: {n0(s.D_votes_22)} of {n0(s.total_votes_22)}) → {p2(s.S26)}%\\* (2026: {n0(s.D_votes_26)} of {n0(s.total_votes_26)}\\*): **{sg(s.S26-s.S22)} points\\*** |
| Democratic registration share | {p2(s.D22)}% ({n0(s.D_reg_22)} of {n0(s.total_reg_22)}) → {p2(s.D26)}% ({n0(s.D_reg_26)} of {n0(s.total_reg_26)}): **{sg(s.D26-s.D22)} points** |
| G 2022 = vote share − registration share | {p2(s.S22)} − {p2(s.D22)} = **{sg(s.G22)}** |
| G 2026\\* | {p2(s.S26)} − {p2(s.D26)} = **{sg(s.G26)}\\*** |
| ΔG = G 2026 − G 2022 | **{sg(s.dG)} points\\***, the largest in Kansas |
| Registered Democrats | {n0(s.D_reg_22)} → {n0(s.D_reg_26)} ({si(s.D_reg_26-s.D_reg_22)}): Seward is a **non-loss county** (raw numbers only, no registration-loss step) |

## Step 2: the six largest counties

Largest to smallest population.

| County | Population | Dem reg 2022 → 2026 | Dem gov votes 2022 → 2026\\* | Total gov votes 2022 → 2026\\* | G 2022 | G 2026\\* | ΔG\\* |
|---|---|---|---|---|---|---|---|
""" + "\n".join(f"| {c} | {n0(S[c].population_2025)} | {n0(S[c].D_reg_22)} → {n0(S[c].D_reg_26)} | {n0(S[c].D_votes_22)} → {n0(S[c].D_votes_26)} | {n0(S[c].total_votes_22)} → {n0(S[c].total_votes_26)} | {sg(S[c].G22)} | {sg(S[c].G26)} | {sg(S[c].dG)} |" for c in six) + f"""

Wyandotte ({sg(S['Wyandotte'].dG)}\\*) is the only one of the six among the five ceiling counties. Shawnee is the only one of the six where ΔG fell. The six largest counties' median ΔG ({sg(G6[5])}\\*) is above the state median ({sg(K['median_dG'])}\\*), which is the size slope described below.

## Step 3: all 105 counties

| Group | Counties | Dem vote share | Dem registration share | Vote-share change\\* | Reg-share change | Pooled ΔG\\* | County median ΔG\\* (range) |
|---|---|---|---|---|---|---|---|
{grow('Six largest counties',6,G6)}
{grow('Other counties',99,GO)}
{grow('All Kansas counties',105,GA)}

- ΔG rose in {K['n_G_rose']} of 105 counties and fell in {K['n_neg']}. County-level SD of ΔG: {p2(K['sd_dG'])} points.
- **Size slope:** ΔG = {p2(K['slope_intercept'])} + {p2(K['slope'])} × log10(population). That is {sg(K['slope'])} points per tenfold population (r = {p2(K['slope_r'])}, R² = {p2(K['slope_r2'],3)}, p = {K['slope_p']:.1e}). Larger counties moved more toward the Democratic candidate than small ones, but county size explains under a fifth of the spread.

## Kansas-only constants (forward surplus fit)

Kansas's own constants are fitted from Kansas data only; no other state's constant is reused. For each county, S = G (Democratic vote share − Democratic registration share, in points) and D = Democratic registration share (%). Ordinary least squares across the 105 counties fits **S = m × (D/100) + b**.

| Fit | n | m (multiplier) | b (offset, pts) | R² | Residual SD (pts) | Counties within ±2 / ±5 pts of the line |
|---|---|---|---|---|---|---|
| 2022 (official) | {f22['n']} | {p2(f22['m'])} (95% CI {p2(f22['m_ci'][0])} to {p2(f22['m_ci'][1])}) | {p2(f22['b'])} ({p2(f22['b_ci'][0])} to {p2(f22['b_ci'][1])}) | {p2(f22['r2'],3)} | {p2(f22['resid_sd'])} | {f22['within_2']} / {f22['within_5']} |
| 2026\\* (unofficial) | {f26['n']} | {p2(f26['m'])} ({p2(f26['m_ci'][0])} to {p2(f26['m_ci'][1])}) | {p2(f26['b'])} ({p2(f26['b_ci'][0])} to {p2(f26['b_ci'][1])}) | {p2(f26['r2'],3)} | {p2(f26['resid_sd'])} | {f26['within_2']} / {f26['within_5']} |
| Pooled, both years | {fp['n']} | {p2(fp['m'])} ({p2(fp['m_ci'][0])} to {p2(fp['m_ci'][1])}) | {p2(fp['b'])} ({p2(fp['b_ci'][0])} to {p2(fp['b_ci'][1])}) | {p2(fp['r2'],3)} | {p2(fp['resid_sd'])} | {fp['within_2']} / {fp['within_5']} |

**How to read it.** A county with D = 20% registered Democrats is expected to have S = m × 0.20 + b: in 2022 about {p2(f22['m']*0.2+f22['b'])} points, in 2026\\* about {p2(f26['m']*0.2+f26['b'])} points. In both years the Democratic candidate ran further ahead of Democratic registration in counties with more registered Democrats.

**Tightness.** The residual SD (the typical distance of a county from the fitted line) tightened from {p2(f22['resid_sd'])} points in 2022 to {p2(f26['resid_sd'])} in 2026\\*, and R² rose from {p2(f22['r2'],3)} to {p2(f26['r2'],3)}. Testing both years in one model, the 2026 line is steeper (m larger by {p2(yi['d_slope'])}, p = {yi['p_d_slope']:.1e}) with a lower offset (b lower by {p2(abs(yi['d_intercept']))}, p = {yi['p_d_intercept']:.1e}). In 2026\\* county surplus followed registration share more closely than in 2022.

### Compared with neighboring states

Same fit, run on each state's own saved county files (Nebraska and Iowa recomputed here from their wiki CSVs; South Dakota from its saved fit). "Governor votes" is the Kansas-comparable denominator; Nebraska, Iowa and South Dakota's own wikis divide by ballots cast. Shown as m / b.

| State | 2022, governor votes | 2026\\*, governor votes | 2022, ballots | 2026\\*, ballots |
|---|---|---|---|---|
| Nebraska (93) | {nbrow('NE',2022,'govvotes')} | {nbrow('NE',2026,'govvotes')} | {nbrow('NE',2022,'ballots')} | {nbrow('NE',2026,'ballots')} |
| Iowa (99) | {nbrow('IA',2022,'govvotes')} | {nbrow('IA',2026,'govvotes')} | {nbrow('IA',2022,'ballots')} | {nbrow('IA',2026,'ballots')} |
| South Dakota (66) | {nbrow('SD',2022,'govvotes')} | {nbrow('SD',2026,'govvotes')} | {nbrow('SD',2022,'ballots')} | {nbrow('SD',2026,'ballots')} |
| **Kansas (105)** | **{p2(f22['m'])} / {p2(f22['b'])}** | **{p2(f26['m'])} / {p2(f26['b'])}** | not computed (ballots data unusable) | not computed (not posted) |

**Flag: Kansas's multiplier m is far outside the neighbor band in both years.** On the governor-votes basis, the 2022 band for m is {neg(FL['m_2022_govvotes']['band'][0])} to {p2(FL['m_2022_govvotes']['band'][1])}, and Kansas is {p2(FL['m_2022_govvotes']['distance'])} above its top ({p2(FL['m_2022_govvotes']['distance_in_KS_SE'],1)} Kansas standard errors). The 2026\\* band is {p2(FL['m_2026_govvotes']['band'][0])} to {p2(FL['m_2026_govvotes']['band'][1])}, and Kansas is {p2(FL['m_2026_govvotes']['distance'])} above its top ({p2(FL['m_2026_govvotes']['distance_in_KS_SE'],1)} SE). Kansas's 95% confidence interval does not overlap the band in either year. The offset b is outside the band in 2022 ({p2(f22['b'])} vs {neg(FL['b_2022_govvotes']['band'][0])} to {p2(FL['b_2022_govvotes']['band'][1])}) and inside it in 2026\\* ({p2(f26['b'])} vs {p2(FL['b_2026_govvotes']['band'][0])} to {p2(FL['b_2026_govvotes']['band'][1])}). Registration definitions differ by state (South Dakota's fit uses active registration), and several neighbors' 2026 figures are also unofficial, so the comparison is descriptive.

## Not computed here

The locked Kansas method has no expected-loss step, no registration-drop subtraction, and no backward-solved "implied extra votes" layer. ΔG is the reported number.

## What the arithmetic cannot tell you

- **Field size changed.** 2022 had four governor candidates and 2026 had two. With all governor votes as the denominator, a county where third-party voters in 2022 went Democratic in 2026 shows a larger ΔG for that reason alone.
- **Registered Democrats are not the only people who vote for Democrats.** Unaffiliated voters were {p2(100*UNAF22/o.total_reg_22.sum())}% of registrants statewide on Nov 1, 2022 ({n0(UNAF22)} of {n0(o.total_reg_22.sum())}).
- **2026 is unofficial.** These totals come from the SOS election-night site and exclude provisional ballots. They will be re-run after the Dec 1 certification.

## All 105 counties

Largest to smallest population. G = 100 × Dem governor votes ÷ total governor votes − 100 × Dem registered ÷ total registered.

| County | Population | Dem gov votes 2022 | Total gov votes 2022 | Dem reg 2022 | Total reg 2022 | G 2022 | Dem gov votes 2026\\* | Total gov votes 2026\\* | Dem reg 2026 | Total reg 2026 | G 2026\\* | ΔG\\* |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
{full}
{REL('Reverse-Math')}"""
# ===================== LOCKED FORMULA =====================
tx=TX['detail']
LF=f"""# Locked Kansas Formula

{BANNER}

## The equation

- **S** (Democratic vote share) = Democratic governor votes ÷ total governor votes (all candidates) × 100
- **D** (Democratic registration share) = Democratic registered voters ÷ total registered voters (active + inactive) × 100
- **G** = S − D (the Democratic surplus, in points)
- **ΔG** = G(2026) − G(2022). ΔG is the plotted number.

Locked by Morissa Benson on Nov 17, 2026 and confirmed Nov 19, 2026:
1. The denominator is **total governor votes** in both years. Never ballots cast, and never one denominator in 2022 and another in 2026.
2. No turnout adjustment, no expected-loss step, no registration-drop subtraction, no backward-solved layer.
3. Registration is all registered voters (active + inactive). The Kansas SOS does not publish active registration by party.

## Why Kansas uses governor votes, not ballots cast

The Nebraska and Iowa pages divide by ballots cast. Kansas can't, for two reasons.

**1. The 2022 SOS ballots-cast file is broken in six counties.** In the SOS "2022 General Election Turnout Information" file, ballots cast should be at least the governor-race total and no more than registered voters. Statewide, the median county has {p2(TX['undervote_median'])}% of ballots with no governor vote (95th percentile {p2(TX['undervote_p95'])}%). Six counties fall outside any plausible range:

| County | Ballots cast (turnout file) | Governor votes | Registered (Nov 1, 2022) | Problem |
|---|---|---|---|---|
| Stevens | {n0(tx['Stevens']['ballots'])} | {n0(tx['Stevens']['gov'])} | {n0(tx['Stevens']['reg_nov1'])} | Ballots exceed registered voters by {n0(tx['Stevens']['ballots']-tx['Stevens']['reg_nov1'])} |
| Sumner | {n0(tx['Sumner']['ballots'])} | {n0(tx['Sumner']['gov'])} | {n0(tx['Sumner']['reg_nov1'])} | Governor votes are {p2(tx['Sumner']['gov']/tx['Sumner']['ballots'],1)} times ballots cast |
| Washington | {n0(tx['Washington']['ballots'])} | {n0(tx['Washington']['gov'])} | {n0(tx['Washington']['reg_nov1'])} | Governor votes exceed ballots by {n0(tx['Washington']['gov']-tx['Washington']['ballots'])} |
| Wilson | {n0(tx['Wilson']['ballots'])} | {n0(tx['Wilson']['gov'])} | {n0(tx['Wilson']['reg_nov1'])} | Governor votes exceed ballots by {n0(tx['Wilson']['gov']-tx['Wilson']['ballots'])} |
| Rice | {n0(tx['Rice']['ballots'])} | {n0(tx['Rice']['gov'])} | {n0(tx['Rice']['reg_nov1'])} | Governor votes exceed ballots by {n0(tx['Rice']['gov']-tx['Rice']['ballots'])} |
| Montgomery | {n0(tx['Montgomery']['ballots'])} | {n0(tx['Montgomery']['gov'])} | {n0(tx['Montgomery']['reg_nov1'])} | {p2(tx['Montgomery']['undervote_pct'],1)}% of ballots show no governor vote (state median {p2(TX['undervote_median'])}%) |

Sumner's listed ballots ({n0(tx['Sumner']['ballots'])}) are close to Stevens's governor votes ({n0(tx['Stevens']['gov'])}), and Stevens's listed ballots ({n0(tx['Stevens']['ballots'])}) are close to Sumner's governor votes ({n0(tx['Sumner']['gov'])}). That looks like the two counties' ballot figures were swapped in the file. **This is an inference only**; the SOS has not confirmed it, and nothing here has been corrected.

**2. 2026 ballots cast by county are not posted.** The SOS election-night site reports candidate votes only, and the SOS has not published 2026 county turnout. A ballots denominator would therefore mix denominators across years, which the locked method forbids.

## Blank template

| Line | Item | 2022 | 2026\\* |
|---|---|---|---|
| 1 | Democratic governor votes | ______ | ______ |
| 2 | Total governor votes, all candidates | ______ | ______ |
| 3 | S = line 1 ÷ line 2 × 100 | ______ | ______ |
| 4 | Democratic registered voters, active + inactive | ______ | ______ |
| 5 | Total registered voters, active + inactive | ______ | ______ |
| 6 | D = line 4 ÷ line 5 × 100 | ______ | ______ |
| 7 | G = line 3 − line 6 | ______ | ______ |
| 8 | ΔG = G 2026 − G 2022 | | ______ |
| 9 | Fitted surplus for this county: m × (line 6 ÷ 100) + b, Kansas constants for that year | ______ | ______ |
| 10 | Distance from the Kansas line = line 7 − line 9 | ______ | ______ |

Kansas constants for line 9: 2022 m = {p2(f22['m'])}, b = {p2(f22['b'])}; 2026\\* m = {p2(f26['m'])}, b = {p2(f26['b'])}. Residual SD {p2(f22['resid_sd'])} (2022) and {p2(f26['resid_sd'])} (2026\\*).

## Worked example: Seward

| Line | Item | 2022 | 2026\\* |
|---|---|---|---|
| 1 | Democratic governor votes | {n0(s.D_votes_22)} | {n0(s.D_votes_26)}\\* |
| 2 | Total governor votes | {n0(s.total_votes_22)} | {n0(s.total_votes_26)}\\* |
| 3 | S | {p2(s.S22)} | {p2(s.S26)}\\* |
| 4 | Democratic registered | {n0(s.D_reg_22)} | {n0(s.D_reg_26)} |
| 5 | Total registered | {n0(s.total_reg_22)} | {n0(s.total_reg_26)} |
| 6 | D | {p2(s.D22)} | {p2(s.D26)} |
| 7 | G | {sg(s.G22)} | {sg(s.G26)}\\* |
| 8 | ΔG | | {sg(s.dG)}\\* |
| 9 | Fitted surplus | {p2(s.fit22)} | {p2(s.fit26)}\\* |
| 10 | Distance from the Kansas line | {sg(s.res22)} | {sg(s.res26)}\\* |

## Rules for using this formula

1. **Use one denominator in both years.** In Kansas that is total governor votes. If ballots cast are ever published for 2026, and the 2022 file is corrected, run both years on ballots as a separate sensitivity check. Don't mix.
2. **The starting point is different in every state. Don't assume Nebraska's numbers carry over.** Kansas's county median ΔG is {sg(K['median_dG'])}\\*, and its own constants are fitted from Kansas data only.
3. **Always pull out the ceiling and floor counties.** In Kansas the ceiling county is Seward ({sg(s.dG)}\\*), and the most Republican baseline county is Wallace. See [Floor and Ceiling Counties](Floor-and-Ceiling).

**Terms used in this wiki** (full definitions on [Floor and Ceiling Counties](Floor-and-Ceiling#terminology)):
- **Ceiling counties**: the five largest ΔG (Seward, Ford, Finney, Wyandotte, Montgomery).
- **Floor counties**: the most Republican baseline, the ten-county bottom cluster led by Wallace.
- **Non-loss counties**: counties where registered Democrats did not fall ({105-K['n_Dreg_fell']} in Kansas). Raw numbers only.
{REL('Locked-Kansas-Formula')}"""
# ===================== FLOOR & CEILING =====================
def fcrow(c,grp):
    r=S[c]; return f"| {c} | {grp} | {n0(r.population_2025)} | {p2(r.S22)}% | {sg(r.G22)} | {sg(r.G26)} | {sg(r.dG)} | {p2(r.D22)}% → {p2(r.D26)}% | {n0(r.D_reg_22)} → {n0(r.D_reg_26)} ({sg(r.D_reg_pct_change,1)}%) | {n0(r.D_votes_22)} → {n0(r.D_votes_26)} |"
grpof=lambda c:'Ceiling' if c in cap else 'Floor' if c in flo else 'Bottom-5 ΔG'
detail=[c for c in o.index if c in cap or c in flo or c in bot]
nonloss=[c for c in o.index if S[c].D_reg_26>=S[c].D_reg_22]
FC=f"""# Floor and Ceiling Counties

{BANNER}

## How to read floor and ceiling counties

Look for the pattern at both ends. The ceiling counties are the ones with the highest ΔG. The floor counties are the most Republican baseline counties, where there were the fewest Democrats to move.

- **The ceiling** is the single county with the highest ΔG in the state. In Kansas that is **Seward, at {sg(K['top5']['Seward'])}\\***.
- **The floor county** (most Republican baseline) is **Wallace**: the lowest 2022 Democratic share of governor votes ({p2(K['lowest5_S22']['Wallace'])}%) and the lowest 2022 surplus G ({sg(K['lowest5_G22']['Wallace'])}). Its ΔG was {sg(S['Wallace'].dG)}\\*.
- **The lowest ΔG** is Russell, at {sg(K['bot5']['Russell'])}\\*.

Every state has its own floor and ceiling. Those extremes set the range the rest of that state's counties fall within.

## Terminology

- **Ceiling counties** are the five largest ΔG: Seward {sg(K['top5']['Seward'])}\\*, Ford {sg(K['top5']['Ford'])}\\*, Finney {sg(K['top5']['Finney'])}\\*, Wyandotte {sg(K['top5']['Wyandotte'])}\\*, Montgomery {sg(K['top5']['Montgomery'])}\\*.
- **Floor counties** are the most Republican baseline. Rule (2022 data only): 2022 Democratic vote share at or below the 10th percentile ({p2(o.S22.quantile(.1))}%) **and** 2022 G at or below the 25th percentile ({p2(o.G22.quantile(.25))}). Ten counties qualify, lowest 2022 Democratic share first: """ + ", ".join(f"{c} {sg(S[c].dG)}\\*" for c in flo) + f""" (ΔG shown).
- **Bottom-5 ΔG** (the largest declines): """ + ", ".join(f"{c} {sg(K['bot5'][c])}\\*" for c in bot) + f""". None of them is a floor county.
- **Non-loss counties** had no loss of registered Democrats. Raw numbers only: """ + ", ".join(f"{c} ({n0(S[c].D_reg_22)} → {n0(S[c].D_reg_26)})" for c in nonloss) + f""".

## Floor and ceiling constants

| Constant | Counties | Median ΔG\\* | Mean ΔG\\* |
|---|---|---|---|
| **Floor constant** | the 10 floor counties | **{sg(K['floor_median'])}** | {sg(K['floor_mean'])} |
| **Ceiling constant** (largest metro counties) | Johnson, Sedgwick, Wyandotte | **{sg(K['ceiling3_median'])}** | {sg(K['ceiling3_mean'])} |
| Ceiling constant, six counties | + Douglas, Riley, Shawnee | **{sg(K['ceiling6_median'])}** | {sg(K['ceiling6_mean'])} |
| Statewide | all 105 counties | {sg(K['median_dG'])} | {sg(K['mean_dG'])} |

The constants are medians, which keeps one county from dominating a small group (Wyandotte's {sg(S['Wyandotte'].dG)}\\* pulls the three-county mean up to {sg(K['ceiling3_mean'])}). Between the floor and the metro ceiling, ΔG climbs with county size: {sg(K['slope'])} points per tenfold population (r = {p2(K['slope_r'])}, p = {K['slope_p']:.1e}).

## Ceiling and floor detail

Largest to smallest population.

| County | Group | Population | Dem share of gov votes 2022 | G 2022 | G 2026\\* | ΔG\\* | Dem reg share 2022 → 2026 | Dem reg 2022 → 2026 | Dem gov votes 2022 → 2026\\* |
|---|---|---|---|---|---|---|---|---|---|
""" + "\n".join(fcrow(c,grpof(c)) for c in detail) + f"""

**Ceiling profile.** Three of the five ceiling counties (Seward, Ford, Finney) are neighbors in southwest Kansas. Wyandotte is the state's most Democratic-registered county. Montgomery's 2022 figure comes from the governor total; its 2022 ballots-cast entry is one of the six flagged below (14% of ballots with no governor vote). Registered Democrats rose in Seward and Ford and fell in the other three.

**Floor profile.** The ten floor counties are small, mostly in western Kansas, and moved little: median ΔG {sg(K['floor_median'])}\\*, with Chautauqua the only one above +1.

## Ballots-cast check (Texas style)

The Texas wiki checks for counties where Democratic plus Republican votes exceed ballots cast. Kansas's 2022 SOS turnout file gives ballots cast by county; 2026 ballots cast by county are **not posted**, so 2026 cannot be checked. These are anomalies in the data file, not findings about the election.

| Check, 2022 | Counties |
|---|---|
| Democratic + Republican governor votes exceed ballots cast | {', '.join(TX['DR_gt_ballots'])} |
| Total governor votes (all candidates) exceed ballots cast | {', '.join(TX['gov_gt_ballots'])} |
| Ballots cast exceed registered voters | {', '.join(TX['ballots_gt_reg'])} |
| Ballots with no governor vote above 5% (state median {p2(TX['undervote_median'])}%) | {', '.join(TX['undervote_gt5'])} |
| 2026 | not checkable: county ballots cast not posted |

| County | Ballots cast 2022 | Dem + Rep gov votes | All gov votes | Registered | Gov votes minus ballots |
|---|---|---|---|---|---|
""" + "\n".join(f"| {c} | {n0(tx[c]['ballots'])} | {n0(tx[c]['DR'])} | {n0(tx[c]['gov'])} | {n0(tx[c]['reg_nov1'])} | {si(tx[c]['gov']-tx[c]['ballots'])} |" for c in ['Stevens','Sumner','Washington','Wilson','Rice','Montgomery']) + f"""

The Sumner and Stevens entries look like a swap of the two counties' ballot figures (inference only; see [Locked Kansas Formula](Locked-Kansas-Formula#why-kansas-uses-governor-votes-not-ballots-cast)). Statewide, the turnout file's ballots ({n0(TX['statewide_ballots_22'])}) exceed governor votes ({n0(TX['statewide_gov_22'])}) as expected.

## Absentee and mail voting

- **2022:** the SOS turnout file lists advance ballots returned by mail for 101 counties ({n0(ABS['adv_mail_sum_101'])} ballots); it shows "N/A" for {', '.join(sorted(ABS['na']))}. These are ballot counts, not votes by candidate. Across 99 counties (Stevens and Sumner excluded), the county's mail-ballot share in 2022 has no relationship with ΔG (Spearman ρ = {p2(ABS['spearman_mailshare22_vs_dG']['rho'])}, p = {p2(ABS['spearman_mailshare22_vs_dG']['p'])}).
- **2026:** no county absentee or mail breakdown is published. The SOS Advance Voting Data page had no 2026 files when checked on Nov 19, 2026, and the election-night pages report candidate totals only.
- **By candidate:** the SOS does not publish absentee versus Election Day votes by candidate for any Kansas county in 2022 or 2026.

![Delta-G by population, ceiling and floor counties marked]({RAWIMG}KS_DeltaG_Bars_by_Population.png)

*All 105 counties, ΔG\\* in population order. Orange: ceiling (5 largest ΔG). Blue: floor (most Republican baseline). Dotted lines: floor and ceiling constants.*

![County slope chart, G 2022 to G 2026]({RAWIMG}KS_Slope_G2022_to_G2026_County_Slope_Chart.png)

*Each line is one county, G 2022 to G 2026\\*. Ceiling counties in orange, floor counties in blue, labeled with ΔG.*
{REL('Floor-and-Ceiling')}"""
# ===================== GRAPHS =====================
GR=f"""# Graphs

{BANNER}

All charts use the governor-votes denominator in both years and list counties largest to smallest population unless the title says otherwise. Images are stored in the [Kansas-Election-Analysis repo](https://github.com/mbenson8989/Kansas-Election-Analysis).

## 1. County slope chart

![County slope chart, G 2022 to G 2026]({RAWIMG}KS_Slope_G2022_to_G2026_County_Slope_Chart.png)

*Each gray line is one county, from its 2022 surplus G to its 2026\\* surplus G. G rose in {K['n_G_rose']} counties and fell in {K['n_neg']}. Orange: the five ceiling counties, the largest upward shifts (Seward {sg(K['top5']['Seward'])}\\*, Ford {sg(K['top5']['Ford'])}\\*, Finney {sg(K['top5']['Finney'])}\\*, Wyandotte {sg(K['top5']['Wyandotte'])}\\*, Montgomery {sg(K['top5']['Montgomery'])}\\*). Blue: the ten floor counties (most Republican baseline). Each highlighted line is labeled with its ΔG.*

## 2. Forward surplus fit: S against D

![Forward surplus fit, S = m(D/100) + b, 2022 and 2026]({RAWIMG}KS_Forward_Surplus_Fit_S_vs_D.png)

*Kansas-only least-squares lines. 2022: S = {p2(f22['m'])}·(D/100) + {p2(f22['b'])}, R² {p2(f22['r2'],3)}, residual SD {p2(f22['resid_sd'])}. 2026\\*: S = {p2(f26['m'])}·(D/100) + {p2(f26['b'])}, R² {p2(f26['r2'],3)}, residual SD {p2(f26['resid_sd'])}. Shaded band: ±1 residual SD.*

## 3. ΔG by population

![Delta-G for all 105 counties in population order, floor and ceiling marked]({RAWIMG}KS_DeltaG_Bars_by_Population.png)

*All 105 counties in population order. Ceiling: Seward is the highest ΔG\\*. Dotted lines: floor constant {sg(K['floor_median'])} and metro ceiling constant {sg(K['ceiling3_median'])}.*

![Delta-G by county with names, trend against log population]({RAWIMG}KS_DeltaG_by_Population_Scatter_Names.png)

*ΔG\\* by county with the trend against log population ({sg(K['slope'])} points per tenfold population). Red: Seward, the ceiling. Orange: the five lowest ΔG (Russell, Jewell, Marshall, Ottawa, Chase).*

## 4. Stacked share bars with registration loss

![Democratic vote share with gain stacked, registered-Democrat loss below, by population]({RAWIMG}KS_Stacked_Share_Reg_Loss_by_Population.png)

*Blue: 2022 Democratic share of governor votes. Amber stacked on top: the 2022 to 2026\\* gain. Dotted outline: where the share fell. Navy below zero (right axis, head count): the drop in registered Democrats. Democratic share rose in {K['n_S_rose']} counties; registered Democrats fell in {K['n_Dreg_fell']}.*

![The same bars sorted by 2022 Democratic share]({RAWIMG}KS_Stacked_Share_Reg_Loss_by_2022_Dem_Share.png)

*The same bars sorted by 2022 Democratic share, highest to lowest. Floor: Wallace (lowest 2022 share). Ceiling: Seward (highest ΔG).*
{REL('Graphs')}"""
for name,txt in (('Home',H),('Reverse-Math',RM),('Locked-Kansas-Formula',LF),('Floor-and-Ceiling',FC),('Graphs',GR)):
    open(W+name+'.md','w').write(txt)
print('built')
