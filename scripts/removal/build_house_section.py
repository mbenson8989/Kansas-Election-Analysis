import json
A=json.load(open('pass1.json')); H=json.load(open('house_pass1.json'))
base=open('/workspace/kansas-wiki/wikiclone/Removal-Simulation.md').read()
cm=lambda x:f"{x:,}"
def mt(v): p=v['margin_pts']; return f"D +{p:.2f}" if p>0 else f"R +{-p:.2f}"
def mg(v): return mt(v)+f" ({cm(abs(v['margin_votes']))} votes)"
def st(v): return ('D' if v['margin_votes']>0 else 'R')+(' (competitive)' if abs(v['margin_pts'])<=5 else '')
K=['baseline','positive_only|remove','positive_only|reassign','all_residuals|remove','all_residuals|reassign']
pop={c:v['pop'] for c,v in A['counties'].items()}
rows=[('Federal','US Senate',A['races']['US Senate'])]+[('Federal',f'US House KS-{d}',H['districts'][d]) for d in '1234']+[('State',r,A['races'][r]) for r in ['Governor','Secretary of State','State Treasurer','Commissioner of Insurance']]
def win(v): return 'D' if v['margin_votes']>0 else 'R'
L=[]; P=L.append
P("\n## Top-of-ballot races, including the four US House districts\n")
P("> Added Nov 24, 2026. Scope: every top-of-ballot race on the 2026\\* Kansas ballot, federal and state: US Senate, US House KS-1 to KS-4, Governor, Secretary of State, State Treasurer and Commissioner of Insurance. **The Attorney General race is excluded by design** and is not computed. Legislative and State Board of Education races are not included. Same hypothetical what-if, constants and residuals as above; the residual is still a statistical distance from a fitted line, **not evidence of injected votes**. \\*2026 figures are UNOFFICIAL (SOS election night, last updated 11/08/2026 9:15 PM CST; certification Dec 1, 2026).\n")
P("### Assumptions for this section\n")
P("1. Same equation and residuals as the sections above: S\\* = 67.6004 × (D/100) + 6.3014 on the governor race, residual votes = residual points ÷ 100 × county governor votes, rounded to whole votes. The residual is treated as the injected amount and removed entirely.")
P("2. **US House allocation.** A county's residual votes go to the US House district that contains it. Four counties are split between two districts (Douglas, Jackson, Pawnee and Wyandotte). In those, the county's residual votes are divided between the districts in proportion to each district's share of the county's total US House votes, using the SOS county-by-district results, and rounded to whole votes by the largest-remainder method so the pieces add up to the county's residual exactly.")
P("3. Applying a governor-fit residual to US House races is an extrapolation; the equation was fit only on the governor race.")
P("4. Variants are as above: removal (D votes and race total both reduced) and flip (votes moved from D to R, total unchanged). Margin is D share − R share of all votes in the race (Libertarian candidates stay in the denominator). Competitive means within 5 points.")
P("5. The statewide rows (US Senate, Governor, Secretary of State, Treasurer, Insurance) are the same verified figures as in the tables above.\n")
P("### Combined top-of-ballot summary (margins)\n")
P("| Level | Race | Before | Main: removal | Main: flip | All residuals: removal | All residuals: flip | Winner change (main scenario) |")
P("|---|---|---|---|---|---|---|---|")
for lv,r,v in rows:
    ch='Flips D → R' if win(v['baseline'])!=win(v['positive_only|remove']) else 'No'
    P(f"| {lv} | {r} | "+" | ".join(mt(v[k]) for k in K)+f" | {ch} |")
P("")
P("### Seats and offices won, before and after\n")
P("| Group | Before | Main: removal | Main: flip | All residuals: removal | All residuals: flip |"); P("|---|---|---|---|---|---|")
for lab,sel in (('Federal: US Senate + 4 US House seats',[x for x in rows if x[0]=='Federal']),('US House only (4 seats)',[x for x in rows if x[1].startswith('US House')]),('State: 4 statewide offices (AG excluded)',[x for x in rows if x[0]=='State'])):
    P(f"| {lab} | "+" | ".join(f"{sum(win(v[k])=='D' for _,_,v in sel)} D, {sum(win(v[k])=='R' for _,_,v in sel)} R" for k in K)+" |")
P("")
P("### US House districts in detail\n")
P("| District | Democrat | Republican | Counties | Votes removed (main) | D share before → after (removal) | Margin before | After (removal) | After (flip) | Status after (removal) |")
P("|---|---|---|---|---|---|---|---|---|---|")
for d in '1234':
    v=H['districts'][d]; b=v['baseline']; a=v['positive_only|remove']
    P(f"| KS-{d} | {v['candidates'][0][2:]} | {v['candidates'][1][2:]} | {v['counties']} | {cm(v['removed_pos'])} | {b['D_share']:.2f}% → {a['D_share']:.2f}% | {mg(b)} | {mg(a)} | {mg(v['positive_only|reassign'])} | {st(a)} |")
P(f"\nThe four districts' removed votes add up to {cm(sum(H['districts'][d]['removed_pos'] for d in '1234'))}, the statewide total of positive residual votes.\n")
P("Secondary scenario (all residuals applied):\n")
P("| District | Net votes applied | Margin before | After (removal) | After (flip) | Status after (flip) |"); P("|---|---|---|---|---|---|")
for d in '1234':
    v=H['districts'][d]; n=v['net_all']
    P(f"| KS-{d} | {('−' if n<0 else '+')+cm(abs(n))} | {mg(v['baseline'])} | {mg(v['all_residuals|remove'])} | {mg(v['all_residuals|reassign'])} | {st(v['all_residuals|reassign'])} |")
P("\nA negative net means the district's counties sit below the fitted line on balance, so the secondary scenario adds Democratic votes there.\n")
P("### Split counties: how residual votes were divided (sorted by population)\n")
P("| County | Population (2025) | District | US House votes in county | Share of county's US House votes | County residual votes | Allocated (main) | Allocated (all residuals) |")
P("|---|---|---|---|---|---|---|---|")
for c in sorted(H['split'],key=lambda c:-pop[c]):
    s=H['split'][c]; T=sum(s['tot'].values()); rv=A['counties'][c]['resid_votes']
    for d in sorted(s['tot']):
        a=s['all'][d]
        P(f"| {c} | {cm(pop[c])} | KS-{d} | {cm(s['tot'][d])} | {100*s['tot'][d]/T:.2f}% | {('−' if rv<0 else '+')+cm(abs(rv))} | {cm(s['pos'][d])} | {('−' if a<0 else '+' if a>0 else '')+cm(abs(a))} |")
P("\nDouglas and Wyandotte have negative residuals, so nothing is removed from them in the main scenario.\n")
P("### What flips or becomes competitive (top of ballot)\n")
g=A['races']['Governor']; s=A['races']['US Senate']; k2=H['districts']['2']
P(f"- **Governor** is the only top-of-ballot race that changes winner: {mt(g['baseline'])} becomes {mt(g['positive_only|remove'])} (removal) or {mt(g['positive_only|reassign'])} (flip).")
P(f"- **US Senate** stays Democratic but becomes competitive: {mt(s['baseline'])} → {mt(s['positive_only|remove'])} (removal) or {mt(s['positive_only|reassign'])} (flip).")
P(f"- **US House: no seat changes in any scenario.** KS-3 stays Democratic ({mt(H['districts']['3']['baseline'])} → {mt(H['districts']['3']['positive_only|remove'])} with removal). KS-1, KS-2 and KS-4 stay Republican, and their Republican margins widen in the main scenario. The House delegation stays 1 D, 3 R.")
P(f"- **KS-2** is the only district that moves inside 5 points, and only in the secondary scenario with the flip variant ({mt(k2['baseline'])} → {mt(k2['all_residuals|reassign'])}), because its counties sit below the line on balance.")
P("- **Secretary of State and Insurance** stay Republican and competitive; **Treasurer** stays Republican and not competitive.\n")
P("**Verification for this section:** two independent scripts (HTML parser vs regular expressions, each with its own allocation code) computed every US House figure from the raw SOS county pages and agreed with 0 mismatches; for each district the county figures add up exactly to the statewide district totals on the SOS pages. A separate page check confirmed every number in this section with 0 mismatches. 2026 figures are unofficial until the Dec 1, 2026 certification.")
open('Removal-Simulation_new.md','w').write(base.rstrip('\n')+'\n'+'\n'.join(L)+'\n'); open('base_snapshot.md','w').write(base)
print('\n'.join(L))
