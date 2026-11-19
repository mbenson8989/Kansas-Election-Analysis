# Kansas wiki verification report

Run: Nov 19, 2026 (America/Chicago). Script: `scripts/run_all.sh`. Nothing was pushed until every check below was clean.

## Pass A and pass B (independent programs)

| | Pass A | Pass B |
|---|---|---|
| Code | `scripts/pass_a.py`, pandas | `scripts/pass_b.py`, openpyxl + csv module, exact fractions, no pandas |
| 2022 governor votes | precinct workbook, pivot by party; 4 large-county sheets by "COUNTY TOTALS" row | same workbook read cell by cell, matched by candidate name; large-county sheets also re-summed precinct by precinct |
| 2026 governor votes | hand transcription `ent2026_governor_transcribed.csv` | the 105 SOS county pages re-downloaded from ent.sos.ks.gov on Nov 19, 2026, parsed from HTML |
| Registration | Nov 1 2022 and Oct 1 2026 SOS workbooks via pandas | same workbooks via openpyxl |
| Counties | 105 | 105 |

- Figures compared, pass A vs pass B: **1680** (105 counties × 16 fields). Mismatches: **0**.
- Figures compared, pass A vs published county CSV (`kansas_deltaG_spec_by_county_population_sorted.csv`, G rounded to 4 dp): **1260**. Mismatches: **0**.
- 2026 hand transcription vs fresh SOS download: **0 differences** in 210 vote figures. SOS "Last Updated" on every county page: 11/08/2026 9:15 PM. All 4,168 precincts reporting.
- Large-county 2022 sheets: precinct sums equal the "COUNTY TOTALS" row for Johnson, Sedgwick, Shawnee. Wyandotte has 4 precinct rows marked "Redacted" in the SOS file, so its precinct sum (D 23768, R 10244) is below the county total row (D 23772, R 10249); the county total row is used, and the 105-county sum then equals the SOS statewide total exactly.
- 2022 statewide precinct file: 28 blank vote cells (no votes recorded), counted as 0 in both passes.

### Statewide totals (county sums vs SOS)

| Item | SOS | Pass A | Pass B | Result |
|---|---|---|---|---|
| D_votes_22 | 499849 | 499849 | 499849 | OK |
| R_votes_22 | 477591 | 477591 | 477591 | OK |
| other_votes_22 | 31558 | 31558 | 31558 | OK |
| D_votes_26 | 551243 | 551243 | 551243 | OK |
| R_votes_26 | 543599 | 543599 | 543599 | OK |
| total_votes_26 | 1094842 | 1094842 | 1094842 | OK |
| reg22 county sum vs SOS Grand Total row | [523317, 1975535] | [523317, 1975535] | [523317, 1975535] | OK |
| reg26 county sum vs SOS Grand Total row | [521669, 2027520] | [521669, 2027520] | [521669, 2027520] | OK |

**A-vs-B discrepancies: none.** During development the first runs failed for parsing reasons, not data reasons (pandas string-dtype handling, "N/A" advance-mail cells in Bourbon, Cherokee, Osage and Rice, blank vote cells, Wyandotte's redacted precinct rows); each was fixed in the parser and both passes were re-run from the raw files. The published-CSV comparison first flagged rounding only (the CSV stores G to 4 decimals); the tolerance was set to half a unit in the 4th decimal.

## Wiki numbers

`scripts/verify_wiki.py` recomputes every statistic from the pass B table with numpy/scipy (independent of the statsmodels code that produced the pages), then:
- checks every county-table cell on all five pages against pass B: **143 rows, 1364 cells, 0 mismatches**;
- checks every numeric token on all five pages (2289 tokens) against recomputed values, allowing a county's own figures only on lines (or under headings) that name that county: **0 unmatched**.
A negative test (changing Seward's 2022 Democratic votes by 1 and two ΔG values by 0.01) was caught by both checks.

## Files
- `passA_counties.csv`, `passB_counties.csv`, `compare_A_B_published_figure_by_figure.csv`, `compare_report.json`, `wiki_number_check.json`
- `ent_refetch_manifest.csv`: SHA-256 of each re-downloaded SOS county page


## Added Nov 19, 2026: expected-loss residual layer (NE/IA/SD method)

- Pass A (`scripts/resid_pass_a.py`, pandas) and pass B (`scripts/resid_pass_b.py`, exact fractions, no pandas) each re-ran their own raw-file parse, then computed expected loss, residual, ΔG, backward-solved offset votes, the Nebraska comparison lines and the statewide offset need. Figures compared: **962** (105 counties × 9 fields, plus 14 statewide figures). Mismatches: **0**. Pass B also asserts, in exact arithmetic, that residual = ΔG − expected loss = S26 − S22 and that residual × N26 ÷ 100 = D26 − S22 × N26 ÷ 100 for every county.
- New-section number check (`scripts/verify_addendum.py`, from pass B outputs): 115 table rows, 1015 cells, 1371 numeric tokens; 0 mismatches, 0 unmatched. Negative test caught.
- Append-only check (`scripts/append_and_diff.py`): for all five pages, the first bytes of the new page equal the published page (commit b31867e) byte for byte, and the rest equals the appended section. Home +664 bytes, Reverse-Math +20554 bytes, other pages unchanged.
