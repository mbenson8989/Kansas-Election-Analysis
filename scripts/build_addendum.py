"""Build the appended section (Reverse-Math) and the Home reference. Writes addendum files; the published page text is never regenerated."""
import pandas as pd, numpy as np, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
V='/workspace/kansas-wiki/verification/'; R='/workspace/kansas-wiki/repo/'; A='/workspace/kansas-wiki/addendum/'
import os; os.makedirs(A,exist_ok=True)
assert json.load(open(V+'resid_compare_report.json'))['CLEAN'] and json.load(open(V+'compare_report.json'))['CLEAN']
o=pd.read_csv(V+'residA_counties.csv',index_col='county'); ST=json.load(open(V+'residA_statewide.json')); CR=json.load(open(V+'resid_compare_report.json'))
K=json.load(open(R+'KS_results_summary.json'))['K']; cap=list(K['top5']); flo=K['floor_counties']
RAWIMG='https://raw.githubusercontent.com/mbenson8989/Kansas-Election-Analysis/main/'
def sg(x,d=2): v=round(float(x),d); return ('+' if v>0 else '−' if v<0 else '')+f"{abs(v):.{d}f}"
def si(x): v=int(round(float(x))); return ('+' if v>0 else '−' if v<0 else '')+f"{abs(v):,}"
def n0(x): return f"{int(round(float(x))):,}"
def p2(x): return f"{float(x):.2f}"
NL=lambda c:'' if o.loc[c,'dem_reg_lost'] else ' †'
# ---- CSV ----
csvcols=['population_2025','dem_reg_lost','D_reg_22','D_reg_26','D22','D26','exp_loss','G22','G26','dG','S22','S26','residual','D_votes_22','D_votes_26','total_votes_26','offset_votes','gap_votes_ne','resid_votes_ne_live']
out=o[csvcols].rename(columns={'D22':'dem_reg_share_22','D26':'dem_reg_share_26','S22':'dem_vote_share_22','S26':'dem_vote_share_26','exp_loss':'expected_loss_pts','residual':'residual_pts',
  'offset_votes':'backward_solved_offset_votes','gap_votes_ne':'NE_gap_in_votes_comparison','resid_votes_ne_live':'NE_live_residual_votes_comparison','dem_reg_lost':'lost_registered_democrats'})
out.insert(0,'status_2026','UNOFFICIAL (SOS election night, last updated 11/08/2026 9:15 PM)')
out.round(6).to_csv(R+'KS_Expected_Loss_Residual_Offset_Votes_by_County.csv')
# ---- chart (Iowa/Nebraska residual-bars style) ----
fig,ax=plt.subplots(figsize=(22,8)); xs=np.arange(len(o))
cols=['#e8590c' if c in cap else '#1f5fbf' if c in flo else '#9a9a9a' for c in o.index]
bars=ax.bar(xs,o.residual,color=cols)
for i,c in enumerate(o.index):
    if not o.loc[c,'dem_reg_lost']: bars[i].set_hatch('//'); bars[i].set_edgecolor('black')
ax.axhline(0,color='k',lw=0.6); ax.axhline(ST['median_residual'],ls='--',color='gray',lw=1,label=f"County median residual {sg(ST['median_residual'])}")
ax.bar([0],[0],color='#e8590c',label='Ceiling counties (5 largest ΔG)'); ax.bar([0],[0],color='#1f5fbf',label='Floor counties (most Republican baseline)')
ax.bar([0],[0],color='white',edgecolor='black',hatch='//',label='Non-loss county (registered Democrats did not fall): shown for completeness')
ax.set_xticks(xs); ax.set_xticklabels([f"{c} {p:,}" for c,p in zip(o.index,o.population_2025)],rotation=90,fontsize=7); ax.set_xlim(-1,len(o))
ax.set_ylabel('Residual = ΔG − expected loss (points) = change in Dem share of governor votes'); ax.grid(axis='y',alpha=.25); ax.legend(fontsize=9,loc='upper right')
ax.set_title('Kansas governor: per-county residual after subtracting the expected loss from Dem registration-share decline, 2022→2026* (NE/IA/SD method, separate layer)',fontsize=12,fontweight='bold')
fig.text(.01,.005,'Expected loss = Dem registration share 2022 − 2026. Denominator = total governor votes both years. *2026 UNOFFICIAL (Kansas SOS election night, last updated 11/08/2026 9:15 PM; certification Dec 1, 2026). Largest to smallest population.',fontsize=8)
plt.tight_layout(rect=(0,.02,1,1)); plt.savefig(R+'KS_Expected_Loss_Residual_Bars_by_Population.png',dpi=140); plt.close()
# ---- text ----
top=o.residual.sort_values(ascending=False).head(5).index; bot=o.residual.sort_values().head(5).index
topv=o.offset_votes.sort_values(ascending=False).head(5).index; botv=o.offset_votes.sort_values().head(5).index
nonloss=list(o.index[~o.dem_reg_lost]); hi=o.S22>K['pooled']['S22']; P_=pd.read_csv(V+'passA_counties.csv',index_col='county').reindex(o.index); HI22=100*P_.total_votes_22[hi].sum()/P_.total_votes_22.sum(); HI26=100*P_.total_votes_26[hi].sum()/P_.total_votes_26.sum(); w=o.loc['Wyandotte']; ON=ST['offset_need']; FIT=ST['ks_fit_dG_on_exp_loss']
def trow(c): r=o.loc[c]; return f"| {c}{NL(c)} | {n0(r.population_2025)} | {p2(r.D22)}% → {p2(r.D26)}% | {sg(r.exp_loss)} | {sg(r.dG)} | {sg(r.residual)} | {n0(r.total_votes_26)} | {si(r.offset_votes)} |"
TH="| County | Population | Dem reg share 2022 → 2026 | Expected loss (pts) | ΔG\\* | Residual\\* (pts) | Total gov votes 2026\\* | Backward-solved offset votes\\* |\n|---|---|---|---|---|---|---|---|\n"
full="\n".join(f"| {c}{NL(c)} | {n0(r.population_2025)} | {n0(r.D_reg_22)} → {n0(r.D_reg_26)} | {p2(r.D22)}% → {p2(r.D26)}% | {sg(r.exp_loss)} | {sg(r.dG)} | {sg(r.residual)} | {n0(r.total_votes_26)} | {si(r.offset_votes)} | {si(r.gap_votes_ne)} |" for c,r in o.iterrows())
RM=f"""

## Expected-Loss Residual and Backward-Solved Offset Votes (NE/IA/SD method)

> **Separate layer, added Nov 19, 2026 at Morissa Benson's request.** This section applies the reverse-factoring step used on the Nebraska, Iowa and South Dakota wikis. It is a separate layer on top of the locked Kansas formula. **Everything above this section is unchanged**, including G, ΔG, the Kansas-only forward fit and the 105-county table. The earlier note "Not computed here" describes that locked layer; this section adds the reverse step beside it. \\*2026 figures are UNOFFICIAL (SOS election night, last updated 11/08/2026 9:15 PM; certification Dec 1, 2026).

### The formulas, exactly as the other states define them

- **Nebraska** (`nebraska-elections/statewide/scripts/analyze.py`): `regdrop = RD_2022 − RD_2026`; `resid = dG − regdrop` ("= change in D share of ballots"); `unexpl_votes = resid / 100 × ballots_2026`.
- **Iowa** (`iowa-wiki/repo/scripts/resolve.py`): `reg_share_loss = R22 − R26`; `residual = dG − reg_share_loss`; `residual_votes = D26 − S22 / 100 × ballots26`. The statewide offset need is "switched votes = s × N; added votes = s × N ÷ (1 − p + s)", where s is the registration-share decline (plus any cushion), N is 2026 ballots and p is the 2026 Democratic share.
- **South Dakota** (`south-dakota-elections/github_wiki_build_sd.py`): "Residual = ΔG − registration-share drop, where registration-share drop = Dem reg share 2022 − Dem reg share 2026"; "Implied extra (offset) votes = residual × 2026 ballots cast ÷ 100".

All three are the same arithmetic. Applied to Kansas:

- **Expected loss** (points) = Dem registration share 2022 − Dem registration share 2026
- **Residual** (points) = ΔG − expected loss = Dem share of governor votes 2026 − Dem share of governor votes 2022
- **Backward-solved offset votes** = residual ÷ 100 × 2026 total governor votes = 2026 Dem votes − (2022 Dem share × 2026 total governor votes)

### Where Kansas has to differ

1. **Denominator.** Nebraska's script, Iowa and South Dakota divide by ballots cast. Kansas uses **total governor votes** in both years, as locked. The 2022 ballots-cast file is broken in six counties, and 2026 county ballots cast are not posted. (The live Nebraska wiki also uses the governor-race total.) N in every formula here is the 2026 total governor votes, {n0(o.total_votes_26.sum())}\\* statewide.
2. **Candidate field.** 2022 had four governor candidates and 2026 had two. Because the residual equals the change in Democratic share of all governor votes, it includes wherever the {n0(31558)} Pyle and Cordell votes of 2022 went in 2026.
3. **Registration snapshot.** 2026 registration is the Oct 1, 2026 SOS report; the Nov 2026 report is not posted.
4. **Non-loss counties.** South Dakota and Iowa run the residual step only for counties that lost registered Democrats. Kansas has {len(nonloss)} non-loss counties ({', '.join(nonloss)}). They are marked † below and shown for completeness, and statewide totals are given with and without them.
5. **Sign.** In Kansas the residual is negative in {ST['n_resid_neg']} of 105 counties: their Democratic share of governor votes fell. Their backward-solved figure is negative (fewer Democratic votes than the 2022 share would give on 2026 totals). Negative values are reported as computed, not set to zero.

### Kansas-only constants for this layer

Computed from Kansas data only; no other state's constant is used.

- **Statewide pooled:** expected loss {sg(ST['exp_loss'])} points (registration share {p2(K['pooled']['D22'])}% → {p2(K['pooled']['D26'])}%), ΔG {sg(ST['dG'])}\\*, residual {sg(ST['residual'])}\\*.
- **County residual:** median {sg(ST['median_residual'])}\\*, mean {sg(ST['mean_residual'])}\\*, SD {p2(ST['sd_residual'])}. Positive in {ST['n_resid_pos']} counties, negative in {ST['n_resid_neg']}.
- **Registration constant** (South Dakota's check, fitted on Kansas): ΔG = {sg(FIT['a'])} {'+' if FIT['b']>=0 else '−'} {p2(abs(FIT['b']))} × expected loss across 105 counties (slope SE {p2(FIT['b_se'])}, R² {FIT['r2']:.3f}). In Kansas the registration-share decline explains almost none of the county-to-county spread in ΔG; South Dakota's own fit had a slope near 1.

### Statewide backward solve

| Measure | Votes\\* |
|---|---|
| Statewide, pooled: residual {sg(ST['residual'])} pts × {n0(o.total_votes_26.sum())} 2026 governor votes ÷ 100 | {si(ST['offset_votes_pooled'])} |
| Sum of the 105 county figures (net) | {si(ST['offset_votes_county_sum'])} |
| … the {ST['n_loss']} counties that lost registered Democrats | {si(ST['offset_votes_sum_loss_counties'])} |
| … the {len(nonloss)} non-loss counties † | {si(ST['offset_votes_sum_nonloss'])} |
| Raw rise in Democratic governor votes | {si(ST['D_change'])} = {n0(ST['offset_votes_pooled'])} share gain + {n0(ST['turnout_part'])} from more governor votes at the 2022 share |
| Offset need for the {p2(ST['exp_loss'])}-point registration-share decline: switched / added votes | {n0(ON['0']['switched'])} / {n0(ON['0']['added'])} |
| Same, with a 1-point cushion | {n0(ON['1']['switched'])} / {n0(ON['1']['added'])} |
| Same, with a 2-point cushion | {n0(ON['2']['switched'])} / {n0(ON['2']['added'])} |
| Comparison, Nebraska wiki "gap in votes" (2026 Dem votes − 2022 Dem votes × registration ratio), county sum | {si(ST['gap_votes_ne_sum'])} |
| Comparison, Nebraska wiki "residual votes" (governor votes × ΔG ÷ 100), county sum | {si(ST['resid_votes_ne_live_sum'])} |

The pooled figure and the county sum differ because pooling also counts where the votes were cast: counties above the 2022 statewide Democratic share cast {p2(HI22)}% of governor votes in 2022 and {p2(HI26)}%\\* in 2026, while most smaller, more Republican counties lost Democratic share. The offset need uses Iowa's formula with s = the statewide registration-share decline and p = the 2026 Democratic share ({p2(K['pooled']['S26'])}%\\*).

### Worked example: Wyandotte

Registration share {p2(w.D22)}% → {p2(w.D26)}%: expected loss {p2(w.exp_loss)} points. ΔG {sg(w.dG)}\\*. Residual {sg(w.dG)} − {p2(w.exp_loss)} = **{sg(w.residual)}\\*** (Democratic share of governor votes {p2(w.S22)}% → {p2(w.S26)}%\\*; computed from unrounded shares). Backward-solved offset votes {sg(w.residual)} × {n0(w.total_votes_26)} ÷ 100 = **{si(w.offset_votes)}\\***, the same as {n0(w.D_votes_26)} − {p2(w.S22)}% × {n0(w.total_votes_26)}.

### Top and bottom counties

Five highest residuals (population order):

{TH}""" + "\n".join(trow(c) for c in o.index if c in top) + f"""

Five lowest residuals (population order):

{TH}""" + "\n".join(trow(c) for c in o.index if c in bot) + f"""

By backward-solved votes, the largest positive figures are """ + ", ".join(f"{c}{NL(c)} {si(o.loc[c,'offset_votes'])}\\*" for c in topv) + ". The largest negative figures are " + ", ".join(f"{c}{NL(c)} {si(o.loc[c,'offset_votes'])}\\*" for c in botv) + f""". Large counties dominate the vote figures because the residual is multiplied by each county's vote total.

![Residual after the expected loss, by population]({RAWIMG}KS_Expected_Loss_Residual_Bars_by_Population.png)

*Residual (ΔG minus expected loss) for all 105 counties, largest to smallest population. Orange: ceiling counties. Blue: floor counties. Hatched: non-loss counties.*

> **Hypothesis label.** Turning the residual into "backward-solved offset votes" and calling them injected, switched or offset votes is Morissa Benson's hypothesis, which the arithmetic cannot test. The same number reflects candidate choice, the smaller 2026 field, crossover voting, turnout changes and any other cause. Candidate votes are not turnout, and registered Democrats are not the only people who vote for Democrats.

### All 105 counties, expected-loss layer

Largest to smallest population. † = non-loss county (registered Democrats did not fall). "Gap in votes" is the Nebraska wiki's comparison line: 2026 Dem votes − 2022 Dem votes × (Dem reg 2026 ÷ Dem reg 2022).

| County | Population | Dem reg 2022 → 2026 | Dem reg share 2022 → 2026 | Expected loss (pts) | ΔG\\* | Residual\\* (pts) | Total gov votes 2026\\* | Backward-solved offset votes\\* | Gap in votes\\* (NE comparison) |
|---|---|---|---|---|---|---|---|---|---|
{full}

**Verification of this layer:** two independent passes (pandas, and openpyxl/csv with exact fractions plus the re-downloaded SOS county pages), each re-reading the raw SOS files, compared {CR['figures_compared']} figures with 0 mismatches. Data: [KS_Expected_Loss_Residual_Offset_Votes_by_County.csv](https://github.com/mbenson8989/Kansas-Election-Analysis/blob/main/KS_Expected_Loss_Residual_Offset_Votes_by_County.csv).

---
**Related:** [Home](Home) · [Locked Kansas Formula](Locked-Kansas-Formula) · [Floor and Ceiling Counties](Floor-and-Ceiling) · [Graphs](Graphs) · [Cedar County Audit (Nebraska)](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit)
"""
HOME=f"""

## Added Nov 19, 2026: expected-loss residual layer

At Morissa Benson's request, [Bottom-Up Reverse Math](Reverse-Math#expected-loss-residual-and-backward-solved-offset-votes-neiasd-method) now has a separate, labelled section that applies the Nebraska / Iowa / South Dakota reverse step: residual = ΔG − expected loss from the registration-share decline, then solved backward for offset votes, still on the governor-votes denominator. The locked G and ΔG above are unchanged. Statewide, the residual is {sg(ST['residual'])}\\* points ({si(ST['offset_votes_pooled'])}\\* votes pooled); the county median is {sg(ST['median_residual'])}\\*, and the residual is negative in {ST['n_resid_neg']} of 105 counties. 2026 figures are unofficial.
"""
open(A+'Reverse-Math.append.md','w').write(RM); open(A+'Home.append.md','w').write(HOME); print('ok', top.tolist(), bot.tolist(), topv.tolist(), botv.tolist())
