# List hygiene results — size first, leftover L&D second

Counts only. Names, emails and the two working workbooks stay off GitHub.

**Locked rules**

- Size once per employer. Store **UK** and **group** when they differ. `size_band` uses UK employees if known, else group.
- Bands: under 250 / 250–5,000 / over 5,000.
- Do **not** change `Outreach readiness` or any LIVE employment field.
- Phase 2 was leftover senior **L&D / OD** (P1) not already on LIVE. Phase 3 finished leftover P2 talent development and P3 People / HR Directors.
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

Two leftover cuts exist. The **plan as specified** uses ChatGPT Senior + Audience L&D, plus OD in the job title. The **letter wave** still uses title-only P1 (ignore Audience / Seniority / Moorgate). Senior HR / People / Talent were parked for a later pass, except Talent Development titles already handled in Phase 3.

### Plan filter (Senior + Audience L&D, plus OD in title)

BounceBan Senior + Audience L&D = **221**. Senior + OD in title adds **1** person not already in that L&D set. Already on LIVE by email: **113** of the 221 L&D seniors. **Leftover: 105 rows / 102 unique emails.** Every leftover row has a Google still-in-post check and a company size. New employers not on LIVE: AWS (banded over 5,000 on Amazon group 1,576,000; AWS-only split is not published), Argent (UK under 250), Ropes & Gray (group 1,500+ attorneys, 250–5,000), TTEC (group ~51,000, over 5,000).

| Still at recorded company | People |
|---|---:|
| Yes | 61 |
| No | 34 |
| Unclear | 10 |

Of the 61 still there: **41** are deliverable **and** 250–5,000. Fourteen are still there but over 5,000. Three are under 250.

The 19 people who were not on the title-P1 leftover sheet were mostly “Head of Training” / academy / QA-training titles. Two real L&D/OD titles were missed by the title classifier because they say **Head** without **of** (UBS wealth-management L&D — public post says redundant; Standard Chartered OD — still there, group over 5,000).

Unclear names are for James on LinkedIn. This agent does not log in.

### Title-only P1 leftover (letter wave)

BounceBan title P1 L&D/OD = **178**. Already on LIVE by email = **95**. Leftover = **83**. All 83 have a Google still-in-post check and a company size.

| Still at recorded company | People |
|---|---:|
| Yes | 50 |
| No | 28 |
| Unclear | 5 |

Of the 50 still there: 36 are deliverable **and** 250–5,000. Nine are still there but over 5,000. Three are under 250.

Unity on the leftover sheet is **Unity Software Inc** (group 4,412 FT at 31 Dec 2025, 10-K). The BounceBan website `hellounity.com` is a different London PR firm and was ignored.

## Phase 3 — finish the EC keep list (P2 + P3)

The EC BounceBan file is **5,090 people / 665 companies**. Title filter keeps **1,047** (P1 178 / P2 98 / P3 771) and kills **4,043** (CEOs, CFOs, HRBPs, recruiters, managers, etc.). Those 4,043 were not sized or googled.

Phase 3 sized the remaining **70** title-keep employers that were not already on LIVE or leftover P1, and Google-checked still-in-role for the remaining **426** keep people (84 P2 + 342 P3) who were not on LIVE and not in leftover P1. Same rules: UK employees if known else group; Google snippets of LinkedIn; no login.

New leftover-employer bands: 44 in 250–5,000 / 21 under 250 / 3 over 5,000 / 2 unknown.

New leftover-person still-in-role: **255 Yes / 109 No / 62 Unclear**.

### All 1,047 title-keep people (LIVE July + leftover P1 Google + Phase 3 Google)

| Size band | People |
|---|---:|
| 250–5,000 | 633 |
| over 5,000 | 314 |
| under 250 | 96 |
| unknown | 4 |

| Still at recorded company | People |
|---|---:|
| Yes | 833 |
| No | 138 |
| Unclear | 76 |

Unclear names are for James on a logged-in LinkedIn. Four unknown-size employers are P3.

### 29 September working band

Still Yes + 250–5,000 + BounceBan deliverable:

| Priority | People |
|---|---:|
| P1 L&D / OD | 97 (92 unique emails) |
| P2 Talent development | 39 |
| P3 People / HR Director | 345 |
| **Total** | **481** (468 unique emails) |

P1 remains the letter wave for the L&D room. P2 is the same altitude of buyer (talent *development*, not acquisition). P3 is a different room (People / HR Director). Do not mix P3 into the same 29 September posted letter as Heads of L&D unless that is a deliberate second product.

Do not mail the 4,043 killed titles. Do not mail over-5,000 or under-250 as the 29 September kill-test.

## Working files (local only — PII)

- `LIVE_with_company_size.xlsx` — working copy of LIVE with size columns + `size_band`. Employment/outreach untouched.
- `phase2_ld_od_not_on_live.xlsx` — plan leftover L&D/OD (105 rows / 102 emails); title-P1 leftover 83 is the in-plan 75 plus 8 extras. Names stay off GitHub.
- `EC_keep_full_hygiene.xlsx` — all 1,047 title-keep people with size + still-in-role.
- `EC_keep_2500_5000_still_yes.xlsx` — 481 in the 29 September band.
- `EC_P2_wave.xlsx` / `EC_P3_wave.xlsx` — P2 and P3 slices of that band.
- `EC_P2_P3_leftover_checked.xlsx` — the 426 Phase 3 Google checks.

Do not commit these files to `typingmind`.

## Not in this pass

- Do not mail all 1,062 LIVE rows or all 5,090 BounceBan rows.
- Do not treat 353 employers as 353 campaign contacts.
- True **W1** and other non-EC London postcodes were never uploaded; SW1/SE1 P2+P3 size and still-in-role are in `List_Hygiene_SW1_SE1.md`.
- Changing LIVE `Outreach readiness` from size bands.
