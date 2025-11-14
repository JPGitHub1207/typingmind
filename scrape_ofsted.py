#!/usr/bin/env python3
"""
Scrape Outstanding training providers from Ofsted website
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
from urllib.parse import urljoin

def scrape_ofsted_providers(base_url):
    """
    Scrape training providers with Outstanding rating from Ofsted
    """
    providers = []
    page = 1
    url = base_url
    
    # Set up headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    while True:
        print(f"Scraping page {page}...")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all provider results
            results = soup.find_all('li', class_='search-result')
            
            if not results:
                print(f"No results found on page {page}. Stopping.")
                break
            
            print(f"Found {len(results)} results on page {page}")
            
            for result in results:
                provider = {}
                
                # Extract provider name and link
                title_elem = result.find('h3', class_='search-result__title')
                if title_elem:
                    link = title_elem.find('a')
                    if link:
                        provider['Name'] = link.get_text(strip=True)
                        provider['URL'] = urljoin('https://reports.ofsted.gov.uk', link['href'])
                
                # Extract all provider info items (Category, Rating, Latest report, URN)
                info_lists = result.find_all('ul', class_='search-result__provider-info')
                
                for info_list in info_lists:
                    items = info_list.find_all('li')
                    for item in items:
                        text = item.get_text(strip=True)
                        if ':' in text:
                            label, value = text.split(':', 1)
                            label = label.strip()
                            value = value.strip()
                            provider[label] = value
                
                # Extract address
                address_elem = result.find('address', class_='search-result__address')
                if address_elem:
                    provider['Address'] = address_elem.get_text(strip=True)
                
                providers.append(provider)
            
            # Check if there's a next page
            pagination = soup.find('div', class_='pagination')
            if pagination:
                next_button = pagination.find('a', class_='pagination__next')
                if next_button and next_button.get('href'):
                    url = urljoin('https://reports.ofsted.gov.uk', next_button['href'])
                    page += 1
                    time.sleep(1)  # Be polite and wait between requests
                else:
                    print("No more pages. Stopping.")
                    break
            else:
                print("No pagination found. Stopping.")
                break
            
        except Exception as e:
            print(f"Error scraping page {page}: {e}")
            break
    
    return providers

def save_to_csv(providers, filename='ofsted_outstanding_providers.csv'):
    """
    Save providers data to CSV file
    """
    if not providers:
        print("No providers to save")
        return
    
    # Get all unique keys from all providers
    fieldnames = set()
    for provider in providers:
        fieldnames.update(provider.keys())
    
    # Sort fieldnames for consistency, but put important ones first
    priority_fields = ['Name', 'Category', 'Address', 'Rating', 'Latest report', 'URN', 'URL']
    fieldnames = [f for f in priority_fields if f in fieldnames] + sorted(list(fieldnames - set(priority_fields)))
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(providers)
    
    print(f"\nSaved {len(providers)} providers to {filename}")

def main():
    # URL for Outstanding Independent Specialist Colleges
    url = "https://reports.ofsted.gov.uk/search?q=&location=&radius=&level_1_types=1&level_2_types=3&latest_report_date_start=&latest_report_date_end=&rating%5B%5D=1&status%5B%5D=1"
    
    print("Starting Ofsted scraper...")
    print(f"URL: {url}\n")
    
    providers = scrape_ofsted_providers(url)
    
    print(f"\nTotal providers scraped: {len(providers)}")
    
    if providers:
        save_to_csv(providers)
        
        # Print first few providers as sample
        print("\nSample of scraped data:")
        for i, provider in enumerate(providers[:3], 1):
            print(f"\n{i}. {provider.get('Name', 'N/A')}")
            print(f"   Category: {provider.get('Category', 'N/A')}")
            print(f"   Address: {provider.get('Address', 'N/A')}")
            print(f"   Rating: {provider.get('Rating', 'N/A')}")
            print(f"   URN: {provider.get('URN', 'N/A')}")

if __name__ == "__main__":
    main()
