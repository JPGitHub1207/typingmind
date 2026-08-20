# SW1 / SE1 list cut (20 August 2026 file)

Counts only. Names and emails stay off GitHub.

James uploaded `W1 SE1 Postcodes 20.08.26.xlsx`. The filename says **W1**. Every postcode in the file is **SW1** (Westminster / Victoria) or **SE1** (South Bank / London Bridge). There are **zero W1** (West End) codes.

| | Count |
|---|---:|
| Rows | 2,331 |
| Unique emails | 2,108 (122 blank) |
| Unique companies | 347 |
| SW1 | 1,446 |
| SE1 | 885 |
| Overlap with LIVE (email) | **0** |
| Overlap with BounceBan EC (email) | **0** |

No ChatGPT Audience / Keep columns on this file. Classify from **Position** (`title_classifier.py`).

## Title keep (unique people)

| Priority | Unique people | Employers |
|---|---:|---:|
| P1 L&D / OD | 85 | 63 |
| P2 Talent development | 34 | 30 |
| P3 CPO / People / HR Director | 383 | ~177 |
| **Title keep** | **502** | |
| Kill | rest of 2,331 | CEOs, CFOs, HRBPs, TA, managers, etc. |

P1 split: 50 SW1 / 35 SE1.

This is a **new** London-commutable slice, not a duplicate of the EC file. It does not replace EC; it sits beside it.

## P1 company size (63 employers)

UK employees if known, else group. Same bands as LIVE.

| Size band | P1 employers | P1 people |
|---|---:|---:|
| 250–5,000 | 46 | 54 |
| over 5,000 | 12 | 24 |
| under 250 | 5 | 7 |

Over 5,000 includes EY, Shell, BP, Civil Service, Mitie, G4S, Pret, Cera Care, BAE, DP World, DIT, Dowlais. They fail the 29 September persona even if still in post.

## P1 still in post (Google snippets, no LinkedIn login)

| Still at recorded company | People |
|---|---:|
| Yes | 56 |
| No | 17 |
| Unclear | 12 |

**P1 wave:** still Yes + 250–5,000 + has an email = **30 people / 26 employers** (17 SW1, 13 SE1). No BounceBan column on this extract — emails are un-verified.

Kubrick “Head of Learning Operations” stayed Unclear / borderline ops; not in the 30.

## P2 + P3 size and still-in-role (finished)

Same method as EC: size once per remaining title-keep employer; Google snippets of LinkedIn; no login. **141** leftover keep-employers sized. **417** leftover P2+P3 people role-checked (34 P2 + 383 P3).

New leftover-employer bands: 81 in 250–5,000 / 40 under 250 / 17 over 5,000 / 3 unknown.

New leftover-person still-in-role: **302 Yes / 82 No / 33 Unclear**.

### All 502 title-keep people on this file

| Size band | People |
|---|---:|
| 250–5,000 | 272 |
| over 5,000 | 154 |
| under 250 | 71 |
| unknown | 5 |

| Still at recorded company | People |
|---|---:|
| Yes | 358 |
| No | 99 |
| Unclear | 45 |

### 29 September working band (this file)

Still Yes + 250–5,000 + has an email:

| Priority | People |
|---|---:|
| P1 L&D / OD | 30 |
| P2 Talent development | 11 |
| P3 People / HR Director | 147 |
| **Total** | **188** (115 SW1 / 73 SE1) |

P1 remains the letter for the L&D room. P2 is the same kind of buyer. P3 is a different room. Emails on this file have not been BounceBan-checked.

Unclear names are for James on LinkedIn.

## Working files (local, PII)

Same packaging as EC. Names stay off GitHub.

- `SW1_SE1_full_original_columns.xlsx` — all 502 title-keep people, every original Pearl column (address, phone, website, sector, title) plus size and still-in-role. Sheets: all keep / 188-row wave / unique emails for BounceBan / P1 / P2 / P3.
- `SW1_SE1_bounceban.xlsx` — **188 unique emails** with original columns, for you to BounceBan (this extract had no BounceBan column). Sheets: all / P1 30 / P2 11 / P3 147.
- `SW1_SE1_P1_full_original_columns.xlsx`, `SW1_SE1_P2_full_original_columns.xlsx`, `SW1_SE1_P3_full_original_columns.xlsx` — the three wave slices.

Unclear names are for James on LinkedIn.

## Not in this file

There is still **no true W1** extract. No other non-EC London postcode files (N, E, SW except SW1, etc.) were uploaded. The 4,043 killed titles on EC, and the killed titles on this 2,331-row file, were not sized or googled.
