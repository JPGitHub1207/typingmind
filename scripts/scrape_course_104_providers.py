#!/usr/bin/env python3
import csv
import json
import math
import os
import re
import sys
from dataclasses import dataclass, asdict
from typing import List, Tuple
from urllib.parse import urljoin, urlencode
import time

import requests

BASE_URL = "https://findapprenticeshiptraining.apprenticeships.education.gov.uk"
COURSE_PATH = "/courses/104/providers"
DEFAULT_QUERY = {
    "OrderBy": "AchievementRate",
    "location": "",
    "Distance": "All",
}

DEFAULT_HEADERS = {
    # Mimic a modern browser to avoid basic bot blocks
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp," 
        "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    ),
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}

@dataclass
class Provider:
    ukprn: str
    name: str
    url: str


def fetch_page_html(session: requests.Session, page_number: int) -> str:
    params = dict(DEFAULT_QUERY)
    if page_number > 1:
        params["PageNumber"] = str(page_number)
    url = urljoin(BASE_URL, COURSE_PATH)
    response = session.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.text


def extract_total_results(html: str) -> int:
    # e.g., <p class="govuk-body ...">472 results</p>
    match = re.search(r"(\d+)\s+results", html, flags=re.IGNORECASE)
    return int(match.group(1)) if match else -1


def extract_max_page_number(html: str) -> int:
    # Look for links like /courses/104/providers?PageNumber=6
    page_numbers = [int(n) for n in re.findall(r"/courses/104/providers\?PageNumber=(\d+)", html)]
    return max(page_numbers) if page_numbers else 1


def extract_providers(html: str) -> List[Provider]:
    providers: List[Provider] = []
    # Anchor pattern for providers, e.g. <a class="govuk-link" id="provider-10002917" href="/courses/104/providers/10002917?distance=10">NAME</a>
    for match in re.finditer(r"<a[^>]*id=\"provider-(\d+)\"[^>]*href=\"([^\"]+)\"[^>]*>(.*?)</a>", html, flags=re.DOTALL | re.IGNORECASE):
        ukprn = match.group(1).strip()
        href = match.group(2).strip()
        # Clean the inner text content
        name_html = match.group(3)
        # Remove HTML tags and collapse whitespace
        name_text = re.sub(r"<[^>]+>", " ", name_html)
        name_text = re.sub(r"\s+", " ", name_text).strip()
        absolute_url = urljoin(BASE_URL, href)
        providers.append(Provider(ukprn=ukprn, name=name_text, url=absolute_url))
    return providers


def save_outputs(providers: List[Provider], out_dir: str) -> Tuple[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    csv_path = os.path.join(out_dir, "providers_course_104.csv")
    json_path = os.path.join(out_dir, "providers_course_104.json")

    # CSV
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ukprn", "name", "url"]) 
        for p in providers:
            writer.writerow([p.ukprn, p.name, p.url])

    # JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([asdict(p) for p in providers], f, ensure_ascii=False, indent=2)

    return csv_path, json_path


def main() -> int:
    out_dir = os.environ.get("OUT_DIR", "/workspace/data")
    save_pages = os.environ.get("SAVE_PAGES", "0") == "1"

    with requests.Session() as session:
        # Set default headers to avoid 403s
        session.headers.update(DEFAULT_HEADERS)
        first_html = fetch_page_html(session, page_number=1)
        total_results = extract_total_results(first_html)
        providers_page1 = extract_providers(first_html)
        per_page = len(providers_page1) if providers_page1 else 0

        # Prefer computing max pages via total results if available
        if total_results > 0 and per_page > 0:
            max_page = math.ceil(total_results / per_page)
        else:
            # Fallback to reading pagination links
            max_page = extract_max_page_number(first_html)

        if save_pages:
            os.makedirs("/workspace/tmp/providers_course_104", exist_ok=True)
            with open("/workspace/tmp/providers_course_104/page1.html", "w", encoding="utf-8") as f:
                f.write(first_html)

        all_providers: List[Provider] = []
        all_providers.extend(providers_page1)

        # Fetch remaining pages
        for page in range(2, max_page + 1):
            # Small delay to be polite and avoid rate limiting
            time.sleep(0.2)
            html = fetch_page_html(session, page_number=page)
            if save_pages:
                with open(f"/workspace/tmp/providers_course_104/page{page}.html", "w", encoding="utf-8") as f:
                    f.write(html)
            all_providers.extend(extract_providers(html))

        # Deduplicate by ukprn in case of issues
        deduped: dict[str, Provider] = {}
        for p in all_providers:
            deduped[p.ukprn] = p
        providers_list = list(deduped.values())

        # Validate count if total_results was found
        if total_results != -1 and len(providers_list) != total_results:
            print(
                f"Warning: extracted {len(providers_list)} providers, expected {total_results}.",
                file=sys.stderr,
            )
        else:
            print(f"Extracted providers: {len(providers_list)}")

        csv_path, json_path = save_outputs(providers_list, out_dir)
        print(f"CSV saved to: {csv_path}")
        print(f"JSON saved to: {json_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
