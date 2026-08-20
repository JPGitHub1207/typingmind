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

**Wave from this file:** still Yes + 250–5,000 + has an email = **30 people / 26 employers** (17 SW1, 13 SE1). No BounceBan column on this extract — emails are un-verified.

P2 (34) and P3 (383) are parked. Unclear names are for James on LinkedIn.

Kubrick “Head of Learning Operations” stayed Unclear / borderline ops; not in the 30.

Working files (local, PII): `SW1_SE1_title_keep.xlsx`, `SW1_SE1_P1_wave.xlsx`. Not in this repo.
