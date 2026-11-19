"""Build the 'Kansas final fitted equation' section for Locked-Kansas-Formula from the exact-arithmetic pass B (eqB.json), after asserting pass A == pass B."""
import json, csv
from fractions import Fraction as F
V='/workspace/kansas-wiki/verification/'
assert json.load(open(V+'eq_compare_report.json'))['CLEAN']
E=json.load(open(V+'eqB.json')); e=E['dG_on_exp_loss']; f22,f26,fp=E['fwd_2022'],E['fwd_2026'],E['fwd_pooled']
sg=lambda x,d=2: ('+' if x>=0 else '−')+f"{abs(x):,.{d}f}"
ab=lambda x,d=2: f"{abs(x):.{d}f}"
neg=lambda x,d=2: ('−' if x<0 else '')+f"{abs(x):.{d}f}"
r={x['key']:x for x in csv.DictReader(open(V+'passB_counties.csv'))}['seward']
D22=100*int(r['D_reg_22'])/int(r['total_reg_22']); D26=100*int(r['D_reg_26'])/int(r['total_reg_26'])
s=E['ex_Seward']; c4,m4=round(e['const'],4),round(e['mult'],4); prod=m4*round(s['exp_loss'],4); fit4=c4+prod
assert abs(fit4-s['fitted_dG'])<0.00015 and f"{s['dG']-fit4:.2f}"==f"{s['distance']:.2f}"
m26,b26=round(f26['mult'],4),round(f26['const'],4); D26r=round(D26,4); fw=m26*D26r/100+b26
assert f"{fw:.2f}"==f"{f26['mult']*D26/100+f26['const']:.2f}"
anchor='Reverse-Math#expected-loss-residual-and-backward-solved-offset-votes-neiasd-method'
T=f"""## Kansas final fitted equation

> Kansas-only least-squares fits on all 105 counties, Kansas SOS data only; no other state's constant is used. \\*2026 figures are UNOFFICIAL (SOS election night, last updated 11/08/2026 9:15 PM; certification Dec 1, 2026). These equations describe the county pattern. They do not change G or ΔG above. The registration-drop fit comes from the separate [expected-loss layer]({anchor}) on Reverse-Math.

### Kansas equation: ΔG on the registration-share drop

**ΔG\\* = {neg(e['const'],4)} + ({neg(e['mult'],4)}) × (registration-share drop)**

Equivalently, ΔG\\* = {neg(e['const'],4)} − {ab(e['mult'],4)} × (D 2022 − D 2026), where D is the Democratic registration share in points (active + inactive), so the drop is positive where the Democratic share of registration fell.

| Term | Value |
|---|---|
| Constant | {neg(e['const'],4)} (SE {ab(e['const_se'],4)}) |
| Multiplier on the registration-share drop | {neg(e['mult'],4)} (SE {ab(e['mult_se'],4)}; t = {neg(e['mult_t'],2)}; p = {ab(e['mult_p'],3)}) |
| R² | {ab(e['r2'],4)} |
| Residual SD | {ab(e['resid_sd'],2)} pts |
| Counties (n) | {e['n']} |

**Plain note: the registration-drop multiplier explains almost none of the variance.** R² = {ab(e['r2'],4)}, so the registration-share drop accounts for about {ab(100*e['r2'],1)}% of the county-to-county spread in ΔG\\*, and the multiplier is not distinguishable from zero (p = {ab(e['mult_p'],3)}). Most of each county's ΔG\\* is the constant plus a county-specific residual (residual SD {ab(e['resid_sd'],2)} pts).

### Kansas forward surplus equations: S = m × (D/100) + b

Here S is the Democratic surplus G (vote share − registration share, points) and D is the Democratic registration share (points).

| Fit | n | Kansas equation | R² | Residual SD (pts) |
|---|---|---|---|---|
| 2022 (official) | {f22['n']} | S = {f22['mult']:.2f} × (D/100) + {f22['const']:.2f} | {f22['r2']:.3f} | {f22['resid_sd']:.2f} |
| 2026\\* (unofficial) | {f26['n']} | S\\* = {f26['mult']:.2f} × (D/100) + {f26['const']:.2f} | {f26['r2']:.3f} | {f26['resid_sd']:.2f} |
| Pooled, both years | {fp['n']} | S = {fp['mult']:.2f} × (D/100) + {fp['const']:.2f} | {fp['r2']:.3f} | {fp['resid_sd']:.2f} |

Multiplier SEs: {f22['mult_se']:.2f} (2022), {f26['mult_se']:.2f} (2026\\*), {fp['mult_se']:.2f} (pooled).

### Worked example: Seward (non-loss county; registered Democrats rose)

| Step | Seward |
|---|---|
| Registration-share drop = D 2022 − D 2026 | {D22:.2f} − {D26:.2f} = {neg(s['exp_loss'],2)} (unrounded {neg(round(s['exp_loss'],4),4)}) |
| Fitted ΔG\\* = constant + multiplier × drop | {neg(c4,4)} + ({neg(m4,4)} × {neg(round(s['exp_loss'],4),4)}) = {neg(c4,4)} + {ab(prod,4)} = {neg(fit4,4)} |
| Actual ΔG\\* (from the worked example below) | {sg(s['dG'])}\\* |
| Distance from the Kansas line = actual − fitted | {sg(s['distance'])}\\* |
| 2026\\* forward check: S\\* = m × (D/100) + b | {m26:.4f} × ({D26r:.4f} ÷ 100) + {b26:.4f} = {fw:.2f}\\*, matching line 9 of the worked example below |

"""
open('/workspace/kansas-wiki/addendum/Locked-final-equation.md','w').write(T); print(T)
