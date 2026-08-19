# List hygiene results — size first, leftover L&D second

Counts only. Names, emails and the two working workbooks stay off GitHub.

**Locked rules**

- Size once per employer. Store **UK** and **group** when they differ. `size_band` uses UK employees if known, else group.
- Bands: under 250 / 250–5,000 / over 5,000.
- Do **not** change `Outreach readiness` or any LIVE employment field.
- Phase 2 is leftover senior **L&D / OD** (title classifier P1) not already on LIVE. Not the extra HR / People / Talent pass.
- Classify from **Position**. Ignore ChatGPT Audience / Seniority / Keep for Moorgate.
- No LinkedIn login. Unclear names are for James on a logged-in profile.

## Phase 1 — LIVE company size

LIVE is **1,062 people / 353 unique employers**. Original size columns were empty (`Company Size Type` = Unknown).

Every LIVE employer now has a size. Geography is UK on 288 employers, group-only on 65.

| Size band (employer) | LIVE companies | LIVE people |
|---|---:|---:|
| 250–5,000 | 242 | 629 |
| over 5,000 | 51 | 350 |
| under 250 | 60 | 83 |
| unknown | 0 | 0 |

Confidence: 253 high / 99 medium / 1 low (Mer UK — directory estimate, no official headcount).

July employment is unchanged: **1,044 still there / 17 Unclear / 1 No**. Outreach readiness is unchanged: 841 Ready / 119 under review / 102 do not contact yet.

Mids inherited size via their employer. They are not a 29 September mail pass.

## Phase 2 — leftover senior L&D / OD

BounceBan P1 L&D/OD = **178**. Already on LIVE by email = **95**. Leftover = **83**. All 83 have a Google still-in-post check and a company size.

| Still at recorded company | People |
|---|---:|
| Yes | 50 |
| No | 28 |
| Unclear | 5 |

Of the 50 still there: 36 are deliverable **and** 250–5,000. Nine are still there but over 5,000. Three are under 250.

The five Unclear are for James on LinkedIn. This agent does not log in.

Unity on the leftover sheet is **Unity Software Inc** (group 4,412 FT at 31 Dec 2025, 10-K). The BounceBan website `hellounity.com` is a different London PR firm and was ignored.

## Working files (local only — PII)

- `LIVE_with_company_size.xlsx` — working copy of LIVE with size columns + `size_band`. Employment/outreach untouched.
- `phase2_ld_od_not_on_live.xlsx` — the 83 leftover L&D/OD names.

Do not commit either file to `typingmind`.

## Not in this pass

- Do not mail all 1,062.
- Do not treat 353 employers as 353 campaign contacts.
- Parked: P3 HR / People Directors; changing Outreach from size bands; Wave A mail-merge file; non-EC London postcodes (the BounceBan file has none).
