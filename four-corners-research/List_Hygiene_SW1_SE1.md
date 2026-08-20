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

## 29 September implication

Do not mail all 2,331. Core buyer is P1 (maybe P2), then size 250–5,000 and still-in-post.

P1 employers are being sized the same way as LIVE (once per company, UK if known else group). Employment check of the 85 is next, after size.

Kubrick “Head of Learning Operations” is on P1 because the title contains Learning; treat as borderline ops.

Working file (local, PII): `SW1_SE1_title_keep.xlsx` in uploads. Not in this repo.
