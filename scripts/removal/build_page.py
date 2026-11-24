import json
A=json.load(open('pass1.json'))
RACES=['Governor','US Senate','Secretary of State','State Treasurer','Commissioner of Insurance']
def nm(r,i): c=A['candidates'][r][i]; return c[2:]
def cm(x): return f"{x:,}"
def sg(x,d=2):
    s=f"{abs(x):,.{d}f}"; return ('−' if x<0 and float(s.replace(',',''))!=0 else '+')+s
def mg(v): # margin label
    p=v['margin_pts']; return (f"D +{p:.2f}" if p>0 else f"R +{-p:.2f}")+f" ({cm(abs(v['margin_votes']))} votes)"
def status(v):
    w='D' if v['margin_votes']>0 else 'R'; return w+(' (competitive)' if abs(v['margin_pts'])<=5 else '')
SC=[('positive_only|remove','Main scenario, variant 1: positive residuals removed (D votes and race total both reduced)'),
    ('positive_only|reassign','Main scenario, variant 2 ("flip"): positive residuals reassigned from D to R (race total unchanged)'),
    ('all_residuals|remove','Secondary scenario, variant 1: all residuals applied (positive removed, negative added back to D; race total moves with them)'),
    ('all_residuals|reassign','Secondary scenario, variant 2 ("flip"): all residuals applied as D↔R reassignment (race total unchanged)')]
C=A['counties']; L=[]
P=L.append
P("# Removal Simulation (hypothetical what-if)\n")
P("> **This page is a hypothetical simulation, not a finding.** A county's residual is its statistical distance from the fitted surplus line on the [Locked Kansas Formula](Locked-Kansas-Formula) page. It is **not evidence of injected votes**. Treating the residual as if it were injected Democratic votes is the stated assumption **for this simulation only**, so the page can show what the statewide results would look like under that assumption. Any manipulation, if it exists at all, would be multifaceted; this is one lens.\n")
P("> **\\*2026 figures are UNOFFICIAL.** Kansas SOS election-night results ([ent.sos.ks.gov](https://ent.sos.ks.gov/)), county pages last updated 11/08/2026 9:15 PM CST, downloaded for all 105 counties on 11/19/2026. Provisional ballots are not included. The State Board of Canvassers certifies the results Dec 1, 2026.\n")
P("> **The Attorney General race is excluded by design** (standing rule for this analysis). It is not computed anywhere on this page.\n")
P("## Assumptions (read first)\n")
P("1. **The residual is treated as the injected amount and removed entirely.** In the main scenario every county with a positive residual (Democratic governor share above the fitted line) has that many Democratic votes taken out. Nothing is scaled down or partially removed.")
P("2. **The equation is the 2026\\* governor surplus fit from the Locked page, unchanged:** S\\* = 67.6004 × (D/100) + 6.3014, where S = Democratic governor votes ÷ total governor votes × 100 − Democratic registered ÷ total registered × 100 (active + inactive), and D = Democratic registration share in percent (Oct 1, 2026 registration).")
P("3. **Residual (points)** = actual S − fitted S. **Residual (votes)** = residual points ÷ 100 × the county's total governor votes, rounded to the nearest whole vote.")
P("4. **Two ways to take the votes out.** Variant 1 (removal): the votes leave the Democratic total and the race's total votes shrink by the same amount, as if the ballots had never been cast. Variant 2 (\"flip\"): the votes are moved from the Democratic candidate to the Republican candidate, so the race total does not change.")
P("5. **Other statewide races are an extrapolation.** The equation was fit only on the governor race. For US Senate, Secretary of State, State Treasurer and Commissioner of Insurance, each county's **governor-derived residual in votes** is applied unchanged to that race's Democratic candidate. Votes, not share points, are used because the hypothesis being simulated is a fixed number of ballots per county, and a ballot carries a vote in every race on it. The alternative (each county's residual in share points × that race's county total) was also run as a check: in the main removal scenario it gives statewide margins within 0.02 points of the vote method in every race, so the choice does not change any conclusion.")
P("6. Margin = Democratic share − Republican share of all votes in that race (third-party candidates stay in the denominator). **Competitive** means a margin within 5 points. Changes in margin are computed from unrounded margins, so they can differ by 0.01 from subtracting the rounded figures.\n")
P("## Constants used\n")
k=A['constants']
P("| Constant | Value on the Locked page | Raw refit today (105 counties) |")
P("|---|---|---|")
P(f"| Multiplier m | 67.6004 | {k['m_refit']:.4f} |")
P(f"| Offset b | 6.3014 | {k['b_refit']:.4f} |\n")
P("The published four-decimal constants are used for every residual below. Because they are rounded, the 105 point residuals sum to "+sg(A['sum_resid_pts'],4)+" instead of exactly 0.\n")
P("## Statewide results before and after\n")
P(f"Positive residuals: {A['n_pos']} counties, {cm(A['sum_pos_votes'])} votes. Negative residuals: {105-A['n_pos']} counties, {cm(-A['sum_neg_votes'])} votes. Net of all residuals: {sg(A['sum_all_votes'],0).replace('+','+')} votes.\n")
P("### Before (2026\\* as reported)\n")
P("| Race | Democrat | Republican | D share | R share | Margin | Status |"); P("|---|---|---|---|---|---|---|")
for r in RACES:
    v=A['races'][r]['baseline']; P(f"| {r} | {nm(r,0)} | {nm(r,1)} | {v['D_share']:.2f}% | {v['R_share']:.2f}% | {mg(v)} | {status(v)} |")
P("")
for key,title in SC:
    P(f"### {title}\n")
    P("| Race | D share before → after | Margin before | Margin after | Change in margin (pts) | Status after |"); P("|---|---|---|---|---|---|")
    for r in RACES:
        b=A['races'][r]['baseline']; v=A['races'][r][key]
        P(f"| {r} | {b['D_share']:.2f}% → {v['D_share']:.2f}% | {mg(b)} | {mg(v)} | {sg(v['margin_pts']-b['margin_pts'])} | {status(v)} |")
    P("")
P("## What flips or becomes competitive\n")
g=A['races']['Governor']; s=A['races']['US Senate']
P(f"- **Governor flips in both main-scenario variants.** Holscher's reported lead of {mg(g['baseline'])} becomes {mg(g['positive_only|remove'])} with removal and {mg(g['positive_only|reassign'])} with the flip assumption.")
P(f"- **US Senate becomes competitive but does not flip.** Hamilton's reported {mg(s['baseline'])} narrows to {mg(s['positive_only|remove'])} with removal and {mg(s['positive_only|reassign'])} with the flip assumption, inside the 5-point line in both.")
for r in ['Secretary of State','Commissioner of Insurance','State Treasurer']:
    v=A['races'][r]
    extra=' Already Republican and competitive; stays competitive.' if abs(v['positive_only|reassign']['margin_pts'])<=5 and abs(v['baseline']['margin_pts'])<=5 else (' Already Republican and not competitive; the gap widens.' if abs(v['baseline']['margin_pts'])>5 else ' Already Republican and competitive; with the flip assumption it moves outside 5 points.')
    P(f"- **{r}:** {mg(v['baseline'])} → {mg(v['positive_only|remove'])} (removal) or {mg(v['positive_only|reassign'])} (flip).{extra}")
P(f"- **Secondary scenario (all residuals):** no race changes winner. The Governor stays {mg(g['all_residuals|remove'])} (removal). The US Senate moves from {mg(s['baseline'])} to {mg(s['all_residuals|remove'])}, just inside the 5-point line.\n")
P("### Why the all-residuals scenario nets near zero\n")
P(f"This is built into the method. A least-squares line is placed so that the residuals above it and below it cancel: the 105 point residuals sum to zero (to {sg(A['sum_resid_pts'],4)} with the rounded constants). Removing every positive residual and adding back every negative one therefore takes back almost nothing. In votes the net is {sg(A['sum_all_votes'],0)} rather than exactly 0, only because each county's points are multiplied by its own vote total, so larger counties weigh more. The all-residuals scenario is shown for completeness; it cannot produce a large statewide change by construction.\n")
P("## Top ten residual counties, before and after (governor)\n")
P("Ranked by residual votes, largest first (not by population; Lyon and McPherson both round to 470 and are ordered by the unrounded value). Main scenario. The county margin columns show both variants.\n")
P("| Rank | County | Population (2025) | D reg share | Actual S | Fitted S | Residual (pts) | Residual (votes removed) | Holscher votes before → after | Governor total before → after (removal) | Holscher share before → after (removal) | County margin before | Margin after (removal) | Margin after (flip) |")
P("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
top=sorted(C,key=lambda c:(-C[c]['resid_votes'],-C[c]['resid_votes_exact']))[:10]
for i,c in enumerate(top,1):
    v=C[c]; gv=A['county_race'][c]['Governor']; d=[x for kk,x in gv.items() if kk.startswith('D-')][0]; rr=[x for kk,x in gv.items() if kk.startswith('R-')][0]; T=v['gov_total']; k_=v['resid_votes']
    def m(dd,rv,tt): p=100*(dd-rv)/tt; return f"D +{p:.2f}" if p>0 else f"R +{-p:.2f}"
    P(f"| {i} | {c} | {cm(v['pop'])} | {v['D']:.2f}% | {v['S']:.2f} | {v['fit']:.2f} | {sg(v['resid_pts'])} | {cm(k_)} | {cm(d)} → {cm(d-k_)} | {cm(T)} → {cm(T-k_)} | {100*d/T:.2f}% → {100*(d-k_)/(T-k_):.2f}% | {m(d,rr,T)} | {m(d-k_,rr,T-k_)} | {m(d-k_,rr+k_,T)} |")
tv=sum(C[c]['resid_votes'] for c in top)
P(f"\nThese ten counties hold {cm(tv)} of the {cm(A['sum_pos_votes'])} removed votes.\n")
P("## All 105 counties (sorted by population, largest first)\n")
P("Residual votes are removed only where positive (main scenario). Negative residuals are used only in the secondary scenario.\n")
P("| County | Population (2025) | D reg share | Actual S | Fitted S | Residual (pts) | Residual (votes) | Removed in main scenario |")
P("|---|---|---|---|---|---|---|---|")
for c in sorted(C,key=lambda c:-C[c]['pop']):
    v=C[c]; P(f"| {c} | {cm(v['pop'])} | {v['D']:.2f}% | {v['S']:.2f} | {v['fit']:.2f} | {sg(v['resid_pts'])} | {sg(v['resid_votes'],0)} | {cm(max(v['resid_votes'],0))} |")
P("\n## Sources and verification\n")
P("- **2026\\* results (unofficial):** Kansas SOS election-night county pages, [ent.sos.ks.gov](https://ent.sos.ks.gov/), all 105 counties, last updated 11/08/2026 9:15 PM CST, downloaded 11/19/2026. For every race used here the 105 county figures add up exactly to the statewide figures on the same pages.")
P("- **Registration:** Kansas SOS, Voter Registration Numbers by County, Oct 1, 2026 (all registered voters, active + inactive).")
P("- **Population:** US Census Bureau county estimates, July 1, 2025 (co-est2025-alldata).")
P("- **Races included:** Governor / Lt. Governor, US Senate (on the 2026 Kansas ballot: Hamilton D, Marshall R, Graham L), Secretary of State, State Treasurer and Commissioner of Insurance, which are all the partisan statewide contests in the 2026\\* data apart from the excluded Attorney General race. The constitutional amendment and Supreme Court retention questions have no Democratic candidate and are not used.")
P("- **Verification:** two independent scripts (one parsing the raw SOS pages with an HTML parser and pandas, one with regular expressions, openpyxl and the csv module) computed every figure from the raw files and agreed with 0 mismatches. A third script then checked every number on this page against the second script, with 0 mismatches.\n")
P("*Prepared for Morissa Benson. Analytical observations only; no accusation is made against any person, county or official. 2026 figures are unofficial until the Dec 1, 2026 certification.*")
open('Removal-Simulation.md','w').write('\n'.join(L)+'\n'); print(len(L))
