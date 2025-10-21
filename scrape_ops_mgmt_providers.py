#!/usr/bin/env python3
import re
import sys
import time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import html as ihtml

BASE_URL = "https://findapprenticeshiptraining.apprenticeships.education.gov.uk"
COURSE_ID = "104"
OUTPUT_CSV = Path("/workspace/operations_manager_providers.csv")

# Regex patterns
ANCHOR_RE = re.compile(r'<a\s+class="govuk-link"\s+id="provider-(?P<ukprn>\d+)"[^>]*>(?P<name>[^<]+)</a>')
REG_ADDR_BLOCK_RE = re.compile(r"Registered address\s*</dt>\s*<dd[^>]*>(?P<addr>.*?)</dd>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def fetch(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
    req = Request(url, headers=headers)
    with urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def extract_providers_from_list(html: str) -> list[tuple[str, str]]:
    return [(m.group("ukprn").strip(), ihtml.unescape(m.group("name").strip())) for m in ANCHOR_RE.finditer(html)]


def extract_registered_address(html: str) -> str | None:
    m = REG_ADDR_BLOCK_RE.search(html)
    if not m:
        return None
    raw = m.group("addr")
    txt = TAG_RE.sub(" ", raw)
    txt = ihtml.unescape(txt)
    txt = WS_RE.sub(" ", txt).strip()
    return txt or None


def crawl_all_list_pages(course_id: str) -> dict[str, str]:
    ukprn_to_name: dict[str, str] = {}
    page = 1
    while True:
        url = f"{BASE_URL}/courses/{course_id}/providers?PageNumber={page}&Distance=All"
        html = fetch(url)
        providers = extract_providers_from_list(html)
        if not providers:
            # Try without Distance param (site sometimes defaults to 10 miles)
            url2 = f"{BASE_URL}/courses/{course_id}/providers?PageNumber={page}"
            html2 = fetch(url2)
            providers = extract_providers_from_list(html2)
        if not providers:
            break
        for ukprn, name in providers:
            ukprn_to_name.setdefault(ukprn, name)
        page += 1
        time.sleep(0.15)
    return ukprn_to_name


def main() -> int:
    ukprn_to_name = crawl_all_list_pages(COURSE_ID)
    if not ukprn_to_name:
        print("No providers found.", file=sys.stderr)
        return 2

    rows: list[tuple[str, str]] = []
    for ukprn, name in sorted(ukprn_to_name.items(), key=lambda x: int(x[0])):
        detail_urls = [
            f"{BASE_URL}/courses/{COURSE_ID}/providers/{ukprn}?distance=All",
            f"{BASE_URL}/courses/{COURSE_ID}/providers/{ukprn}",
        ]
        addr = None
        for durl in detail_urls:
            try:
                dhtml = fetch(durl)
                addr = extract_registered_address(dhtml)
            except Exception:
                addr = addr or None
            if addr:
                break
        rows.append((name, addr or ""))
        time.sleep(0.2)

    with OUTPUT_CSV.open("w", encoding="utf-8") as f:
        f.write("Name,Address\n")
        for name, addr in rows:
            name_esc = name.replace('"', '""')
            addr_esc = addr.replace('"', '""')
            f.write(f'"{name_esc}","{addr_esc}"\n')

    print(f"Wrote {len(rows)} providers to {OUTPUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
