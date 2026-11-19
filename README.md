# Kansas Election Analysis: 2022 vs 2026 Governor Race, ΔG Method

County-level analysis of the Kansas governor race, 2022 (official) vs 2026 (**UNOFFICIAL**: Kansas SOS election-night results, last updated 11/08/2026 9:15 PM; state certification Dec 1, 2026). Method developed by Morissa Benson; it began with the [Cedar County Audit](https://github.com/mbenson8989/Nebraska-Election-Analysis-/wiki/Cedar-Audit) on the Nebraska wiki.

**Wiki:** https://github.com/mbenson8989/Kansas-Election-Analysis/wiki — Home, Reverse-Math, Locked-Kansas-Formula, Floor-and-Ceiling, Graphs.

**Locked Kansas formula:** G = 100 × Democratic governor votes ÷ total governor votes (all candidates) − 100 × Democratic registered ÷ total registered (active + inactive); ΔG = G2026 − G2022. Governor votes in both years, never ballots cast (the 2022 SOS ballots-cast file is broken in six counties, and 2026 county ballots cast are not posted).

## Contents
- `KS_Governor_2022_2026_DeltaG_by_County.csv`: all 105 counties, largest to smallest population
- `KS_results_summary.json`: fitted Kansas constants, neighbor-state comparison, floor/ceiling constants, ballots-cast check
- `*.png`: charts embedded in the wiki
- `scripts/`: `run_all.sh` runs pass A, pass B, the comparison, analysis, charts, wiki build, and the wiki number check
- `verification/`: double-verification outputs; start with `VERIFICATION.md`
- `sources/`: 2026 hand transcription of the SOS election-night county pages (checked against a fresh download of all 105 pages)

These files measure a pattern; they make no claim about intent, fraud or cause.

Other state analyses: [Nebraska](https://github.com/mbenson8989/Nebraska-Election-Analysis-) · [Iowa](https://github.com/mbenson8989/Iowa-Election-Analysis) · [South Dakota](https://github.com/mbenson8989/South-Dakota-Election-Analysis) · [Texas](https://github.com/mbenson8989/Texas-Election-Analysis) · [Michigan](https://github.com/mbenson8989/Michigan-Election-Analysis)
