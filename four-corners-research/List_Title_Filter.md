# Title filter — ignore the ChatGPT columns

The BounceBan file’s **Audience category**, **Seniority band**, **Keep for Moorgate** and **Moorgate priority** were produced by ChatGPT. They are **not** the source of truth.

Checked against raw **Position** (5,090 rows):

- ChatGPT said Keep=Yes on **1,888 people we would kill** (CEOs, CFOs, HRBPs, talent acquisition, DEI, pensions, change managers, L&D *managers*).
- ChatGPT said Keep=No on **43 people we would keep** (mostly VP People / People Director).

Rules are in [`title_classifier.py`](title_classifier.py). Job title only.

## Keep (29 September)

Senior = Head of / Director / Chief / VP / Associate Director / Group or Global Head.

| Priority | Who | BounceBan count |
|---|---|---|
| P1 | L&D or OD | 178 people, 125 employers |
| P2 | Talent *development* (not acquisition) | 98 |
| P3 | CPO, People Director, HR Director, Head of People / HR | 771 |

Kill: HRBP, recruitment/TA, reward, ER, DEI, HR ops, managers, specialists, **CFO / Finance Director**, CEO/COO, procurement, pensions.

Do not mail CFOs for 29 September. They do not own the learning diagnosis, and they are not peers of Heads of L&D. A later “performance spend” product would be a different room.

LIVE (1,062 “already checked”): only **533** pass the title test. The other 529 stay on LIVE with employment fields untouched; they should not get 29 September letters.

## Company size (done)

Looked up **353 unique LIVE employers**, not 1,062 people. `size_band` uses UK employees if known, else group. Employment and `Outreach readiness` were not changed.

| Size band | LIVE companies | LIVE people |
|---|---:|---:|
| 250–5,000 | 242 | 629 |
| over 5,000 | 51 | 350 |
| under 250 | 60 | 83 |

Leftover BounceBan P1 L&D/OD not on LIVE: **83** people (50 still there / 28 moved / 5 Unclear). **36** of those are still there, deliverable, and 250–5,000.

Phase 3 finished the rest of the **1,047** title-keep people (P2 + P3 leftover). See [`List_Hygiene_Results.md`](List_Hygiene_Results.md). Spreadsheets stay off GitHub.
