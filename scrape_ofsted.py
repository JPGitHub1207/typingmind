#!/usr/bin/env python3
"""
Scrape Outstanding-rated training providers from Ofsted website.
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import re

BASE_URL = "https://reports.ofsted.gov.uk"
SEARCH_URL = "https://reports.ofsted.gov.uk/search"

def get_page(url, params=None):
    """Fetch a page with retries."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    for attempt in range(3):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(2)
            else:
                raise
    return None

def parse_provider_item(item):
    """Extract provider information from a search result item."""
    provider = {
        'Name': '',
        'Category': '',
        'Address': '',
        'Rating': 'Outstanding',
        'Latest report': '',
        'URN': ''
    }
    
    try:
        # Extract name
        title_elem = item.find('h3', class_='search-result__title')
        if title_elem:
            link = title_elem.find('a')
            if link:
                provider['Name'] = link.get_text(strip=True)
        
        # Extract all provider info items
        info_lists = item.find_all('ul', class_='search-result__provider-info')
        for info_list in info_lists:
            items = info_list.find_all('li')
            for li in items:
                text = li.get_text(strip=True)
                
                # Category
                if text.startswith('Category:'):
                    strong = li.find('strong')
                    if strong:
                        provider['Category'] = strong.get_text(strip=True)
                
                # Rating
                elif text.startswith('Rating:'):
                    strong = li.find('strong')
                    if strong:
                        provider['Rating'] = strong.get_text(strip=True)
                
                # Latest report
                elif text.startswith('Latest report:'):
                    strong = li.find('strong')
                    if strong:
                        time_elem = strong.find('time')
                        if time_elem:
                            provider['Latest report'] = time_elem.get_text(strip=True)
                        else:
                            provider['Latest report'] = strong.get_text(strip=True)
                
                # URN
                elif text.startswith('URN:'):
                    strong = li.find('strong')
                    if strong:
                        provider['URN'] = strong.get_text(strip=True)
        
        # Extract address
        address_elem = item.find('address', class_='search-result__address')
        if address_elem:
            provider['Address'] = address_elem.get_text(strip=True).replace('\n', ', ')
        
    except Exception as e:
        print(f"Error parsing provider item: {e}")
    
    return provider

def scrape_ofsted_providers():
    """Scrape all Outstanding-rated Independent Specialist Colleges from Ofsted."""
    all_providers = []
    
    # Initial search parameters
    params = {
        'q': '',
        'location': '',
        'radius': '',
        'level_1_types': '1',
        'level_2_types': '3',
        'latest_report_date_start': '',
        'latest_report_date_end': '',
        'rating[]': '1',  # Outstanding
        'status[]': '1',   # Active
        'start': '0',
        'rows': '50'  # Get more results per page
    }
    
    start = 0
    rows_per_page = 50
    max_results = 200  # Safety limit
    
    print("Starting to scrape Ofsted Outstanding-rated training providers...")
    
    while start < max_results:
        print(f"Fetching results {start} to {start + rows_per_page - 1}...")
        
        current_params = params.copy()
        current_params['start'] = str(start)
        current_params['rows'] = str(rows_per_page)
        
        try:
            response = get_page(SEARCH_URL, params=current_params)
            if not response:
                break
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Find results list
            results_list = soup.find('ul', class_='results-list')
            if not results_list:
                print("No results list found. Stopping.")
                break
            
            # Find all provider items
            provider_items = results_list.find_all('li', class_='search-result')
            
            if not provider_items:
                print("No more providers found. Stopping.")
                break
            
            print(f"  Found {len(provider_items)} providers on this page")
            
            # Parse each provider
            for item in provider_items:
                provider = parse_provider_item(item)
                if provider['Name']:  # Only add if we have a name
                    all_providers.append(provider)
                    print(f"    - {provider['Name']} (URN: {provider['URN']})")
            
            # Check if there are more results
            # Look for result count
            results_count_elem = soup.find('strong', class_='results-count')
            if results_count_elem:
                total_results = int(results_count_elem.get_text(strip=True))
                print(f"  Total results: {total_results}")
                
                if start + len(provider_items) >= total_results:
                    print("Reached end of results.")
                    break
            
            # If we got fewer results than requested, we're done
            if len(provider_items) < rows_per_page:
                print("Reached last page.")
                break
            
            start += rows_per_page
            time.sleep(1)  # Be polite to the server
            
        except Exception as e:
            print(f"Error fetching page: {e}")
            import traceback
            traceback.print_exc()
            break
    
    print(f"\nScraping complete! Found {len(all_providers)} providers.")
    return all_providers

def save_results(providers, format='both'):
    """Save results to JSON and/or CSV."""
    if format in ('json', 'both'):
        with open('ofsted_outstanding_providers.json', 'w', encoding='utf-8') as f:
            json.dump(providers, f, indent=2, ensure_ascii=False)
        print("Saved to ofsted_outstanding_providers.json")
    
    if format in ('csv', 'both'):
        if providers:
            fieldnames = ['Name', 'Category', 'Address', 'Rating', 'Latest report', 'URN']
            with open('ofsted_outstanding_providers.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(providers)
            print("Saved to ofsted_outstanding_providers.csv")

if __name__ == '__main__':
    providers = scrape_ofsted_providers()
    if providers:
        save_results(providers)
        print(f"\nTotal providers scraped: {len(providers)}")
    else:
        print("No providers found. The website structure might have changed.")
