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
PAGES_GLOB = "/workspace/providers_104_p*.html"

# Regex patterns
ANCHOR_RE = re.compile(r'<a\s+class="govuk-link"\s+id="provider-(?P<ukprn>\d+)"[^>]*>(?P<name>[^<]+)</a>')
# Find the Registered address dd following a dt that contains "Registered address"
REG_ADDR_BLOCK_RE = re.compile(r"Registered address\s*</dt>\s*<dd[^>]*>(?P<addr>.*?)</dd>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def extract_providers_from_page(html: str) -> list[tuple[str, str]]:
    providers: list[tuple[str, str]] = []
    for m in ANCHOR_RE.finditer(html):
        ukprn = m.group("ukprn").strip()
        name = m.group("name").strip()
        if ukprn and name:
            providers.append((ukprn, ihtml.unescape(name)))
    return providers


def fetch(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
    req = Request(url, headers=headers)
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def extract_registered_address(html: str) -> str | None:
    m = REG_ADDR_BLOCK_RE.search(html)
    if not m:
        return None
    raw = m.group("addr")
    # Strip tags and condense whitespace
    txt = TAG_RE.sub(" ", raw)
    txt = ihtml.unescape(txt)
    txt = WS_RE.sub(" ", txt).strip()
    return txt or None


def main() -> int:
    pages = sorted(Path(p) for p in Path("/workspace").glob("providers_104_p*.html"))
    if not pages:
        print("No pre-downloaded pages found. Exiting.", file=sys.stderr)
        return 2

    # Collect providers
    ukprn_to_name: dict[str, str] = {}
    for page in pages:
        html = read_text(page)
        for ukprn, name in extract_providers_from_page(html):
            ukprn_to_name.setdefault(ukprn, name)

    if not ukprn_to_name:
        print("No providers found in listing pages", file=sys.stderr)
        return 3

    # Fetch details and extract addresses
    rows: list[tuple[str, str]] = []
    for idx, (ukprn, name) in enumerate(sorted(ukprn_to_name.items(), key=lambda x: int(x[0])) , start=1):
        detail_url = f"{BASE_URL}/courses/{COURSE_ID}/providers/{ukprn}?distance=All"
        try:
            detail_html = fetch(detail_url)
        except (URLError, HTTPError) as e:
            addr = None
        else:
            addr = extract_registered_address(detail_html)
        if addr is None:
            # Last resort: try without query string
            try:
                detail_html = fetch(f"{BASE_URL}/courses/{COURSE_ID}/providers/{ukprn}")
                addr = extract_registered_address(detail_html)
            except Exception:
                addr = None
        rows.append((name, addr or ""))
        # Be gentle to the server
        time.sleep(0.2)

    # Write CSV
    with OUTPUT_CSV.open("w", encoding="utf-8") as f:
        f.write("Name,Address\n")
        for name, addr in rows:
            # Escape quotes by doubling
            name_esc = name.replace('"', '""')
            addr_esc = addr.replace('"', '""')
            f.write(f'"{name_esc}","{addr_esc}"\n')

    print(f"Wrote {len(rows)} providers to {OUTPUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
