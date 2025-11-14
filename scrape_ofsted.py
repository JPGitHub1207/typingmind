#!/usr/bin/env python3
"""
Scrape Outstanding-rated training providers from Ofsted website.
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
from urllib.parse import urljoin
import re

BASE_URL = "https://reports.ofsted.gov.uk"
SEARCH_URL = "https://reports.ofsted.gov.uk/search"

def get_search_results(start=0, rows=10):
    """Fetch search results page."""
    params = {
        'q': '',
        'location': '',
        'radius': '',
        'level_1_types': '1',
        'level_2_types[0]': '3',
        'latest_report_date_start': '',
        'latest_report_date_end': '',
        'rating[0]': '1',  # Outstanding rating
        'status[0]': '1',
        'page': '1',
        'start': str(start),
        'rows': str(rows),
        'sort': 'az',
        'order': 'asc'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(SEARCH_URL, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching results (start={start}): {e}")
        return None

def parse_provider_from_result(result_item):
    """Parse a single provider from search result list item."""
    provider_data = {
        'Name': '',
        'Category': '',
        'Address': '',
        'Rating': 'Outstanding',
        'Latest report': '',
        'URN': '',
        '_provider_url': ''  # Internal field for fetching report URLs
    }
    
    provider_url = None
    
    # Extract name
    title_elem = result_item.find('h3', class_='search-result__title')
    if title_elem:
        link = title_elem.find('a')
        if link:
            provider_data['Name'] = link.get_text(strip=True)
            provider_url = urljoin(BASE_URL, link.get('href', ''))
            provider_data['_provider_url'] = provider_url
    
    # Extract all provider info items
    info_lists = result_item.find_all('ul', class_='search-result__provider-info')
    for info_list in info_lists:
        items = info_list.find_all('li')
        for item in items:
            text = item.get_text(strip=True)
            
            # Extract Category
            if text.startswith('Category:'):
                strong = item.find('strong')
                if strong:
                    provider_data['Category'] = strong.get_text(strip=True)
            
            # Extract Rating
            elif text.startswith('Rating:'):
                strong = item.find('strong')
                if strong:
                    provider_data['Rating'] = strong.get_text(strip=True)
            
            # Extract Latest report date
            elif text.startswith('Latest report:'):
                strong = item.find('strong')
                if strong:
                    time_elem = strong.find('time')
                    if time_elem:
                        provider_data['Latest report'] = time_elem.get_text(strip=True)
                    else:
                        provider_data['Latest report'] = strong.get_text(strip=True)
            
            # Extract URN
            elif text.startswith('URN:'):
                strong = item.find('strong')
                if strong:
                    provider_data['URN'] = strong.get_text(strip=True)
    
    # Extract address
    address_elem = result_item.find('address', class_='search-result__address')
    if address_elem:
        provider_data['Address'] = address_elem.get_text(strip=True)
    
    return provider_data

def enrich_with_report_urls(providers, batch_size=10):
    """Enrich provider data with report URLs in batches."""
    print(f"\nFetching report URLs for {len(providers)} providers...")
    
    for i, provider in enumerate(providers):
        provider_url = provider.get('_provider_url', '')
        if not provider_url and provider.get('URN'):
            # Fallback: try to construct URL (may not always work)
            provider_url = f"{BASE_URL}/provider/46/{provider['URN']}"
        
        if provider_url:
            # Try to get report URL
            report_url = get_latest_report_url(provider_url)
            if report_url:
                if provider['Latest report']:
                    provider['Latest report'] = f"{provider['Latest report']} - {report_url}"
                else:
                    provider['Latest report'] = report_url
        
        if (i + 1) % batch_size == 0:
            print(f"  Processed {i + 1}/{len(providers)} providers...")
            time.sleep(1)  # Be respectful
    
    # Remove internal field before saving
    for provider in providers:
        provider.pop('_provider_url', None)
    
    return providers

def get_latest_report_url(provider_url):
    """Get the URL of the latest report from provider detail page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(provider_url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the first publication link in the timeline
        timeline = soup.find('ol', class_='timeline')
        if timeline:
            first_report = timeline.find('li', class_='timeline__day')
            if first_report:
                report_link = first_report.find('a', class_='publication-link')
                if report_link:
                    return report_link.get('href', '')
        
        time.sleep(0.3)  # Be respectful
    except Exception as e:
        print(f"  Warning: Could not fetch report URL from {provider_url}: {e}")
    
    return None

def scrape_all_providers():
    """Scrape all Outstanding-rated training providers."""
    all_providers = []
    start = 0
    rows = 10
    
    print("Starting to scrape Ofsted Outstanding-rated training providers...")
    
    while True:
        print(f"Fetching results {start+1} to {start+rows}...")
        html = get_search_results(start, rows)
        
        if not html:
            print(f"Failed to fetch results (start={start}), stopping.")
            break
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all result items
        result_items = soup.find_all('li', class_='search-result')
        
        if not result_items:
            print("No more results found.")
            break
        
        print(f"Found {len(result_items)} providers on this page")
        
        # Extract data from each provider
        for i, result_item in enumerate(result_items, 1):
            provider_data = parse_provider_from_result(result_item)
            if provider_data and provider_data['Name']:
                all_providers.append(provider_data)
                print(f"  {start + i}. {provider_data['Name']}")
        
        # Check for next page
        pagination = soup.find('div', class_='pagination')
        if pagination:
            next_link = pagination.find('a', class_='pagination__next')
            if next_link:
                # Extract start parameter from next link
                href = next_link.get('href', '')
                start_match = re.search(r'start=(\d+)', href)
                if start_match:
                    next_start = int(start_match.group(1))
                    if next_start > start:
                        start = next_start
                    else:
                        break
                else:
                    break
            else:
                break
        else:
            break
        
        time.sleep(1)  # Be respectful between pages
    
    return all_providers

def save_to_csv(providers, filename='ofsted_outstanding_providers.csv'):
    """Save providers to CSV file."""
    if not providers:
        print("No providers to save")
        return
    
    # Remove internal fields before saving
    cleaned_providers = []
    for provider in providers:
        cleaned = {k: v for k, v in provider.items() if not k.startswith('_')}
        cleaned_providers.append(cleaned)
    
    fieldnames = ['Name', 'Category', 'Address', 'Rating', 'Latest report', 'URN']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_providers)
    
    print(f"\nSaved {len(providers)} providers to {filename}")

def save_to_json(providers, filename='ofsted_outstanding_providers.json'):
    """Save providers to JSON file."""
    if not providers:
        print("No providers to save")
        return
    
    # Remove internal fields before saving
    cleaned_providers = []
    for provider in providers:
        cleaned = {k: v for k, v in provider.items() if not k.startswith('_')}
        cleaned_providers.append(cleaned)
    
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(cleaned_providers, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(providers)} providers to {filename}")

if __name__ == '__main__':
    providers = scrape_all_providers()
    
    if providers:
        print(f"\nTotal providers scraped: {len(providers)}")
        
        # Optionally enrich with report URLs (commented out as it's slow)
        # Uncomment the next line if you want report URLs:
        # providers = enrich_with_report_urls(providers)
        
        save_to_csv(providers)
        save_to_json(providers)
        print(f"\nData saved to:")
        print(f"  - ofsted_outstanding_providers.csv")
        print(f"  - ofsted_outstanding_providers.json")
    else:
        print("No providers were scraped. Please check the website structure.")
