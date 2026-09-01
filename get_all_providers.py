#!/usr/bin/env python3
"""
Get ALL Ofsted Funded Training Providers
This script will scrape all ~2,458 providers
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
from urllib.parse import urljoin
import re

class AllOfstedProvidersScraper:
    def __init__(self):
        self.base_url = "https://reports.ofsted.gov.uk"
        self.search_base_url = "https://reports.ofsted.gov.uk/search?q=&location=&lat=&lon=&radius=&level_1_types=1&level_2_types%5B%5D=3"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_page_content(self, url):
        """Get page content with error handling"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def get_all_provider_links(self):
        """Get all provider links using start parameter pagination"""
        print("Getting ALL provider links...")
        
        all_provider_links = []
        start = 0
        results_per_page = 10
        page_num = 1
        
        while True:
            if start == 0:
                url = self.search_base_url
            else:
                url = f"{self.search_base_url}&start={start}"
            
            print(f"Scraping page {page_num} (start={start})")
            
            html_content = self.get_page_content(url)
            if not html_content:
                print(f"Failed to get page {page_num}")
                break
            
            page_links = self.parse_provider_links_from_page(html_content)
            
            if not page_links:
                print(f"No providers found on page {page_num}, stopping")
                break
            
            # Add new links only
            new_links = [link for link in page_links if link not in all_provider_links]
            all_provider_links.extend(new_links)
            
            print(f"Page {page_num}: Found {len(page_links)} providers, {len(new_links)} new (total: {len(all_provider_links)})")
            
            # If we got fewer than expected results, we might be at the end
            if len(page_links) < results_per_page:
                print(f"Got {len(page_links)} results (less than {results_per_page}), likely at end")
                break
            
            # If no new links were added, we might be getting duplicates
            if len(new_links) == 0:
                print("No new providers found, stopping")
                break
            
            # Move to next page
            start += results_per_page
            page_num += 1
            
            # Be respectful with requests
            time.sleep(0.5)
            
            # Safety limit
            if page_num > 300:
                print("Reached safety limit of 300 pages")
                break
        
        print(f"\nCompleted! Found {len(all_provider_links)} unique provider links")
        return all_provider_links
    
    def parse_provider_links_from_page(self, html_content):
        """Extract provider detail page links from a single search results page"""
        soup = BeautifulSoup(html_content, 'html.parser')
        provider_links = []
        
        # Look for provider links in search results
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link['href']
            if '/provider/' in href:
                full_url = urljoin(self.base_url, href)
                if full_url not in provider_links:
                    provider_links.append(full_url)
        
        return provider_links
    
    def clean_text(self, text):
        """Clean and normalize text"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    def extract_provider_info(self, provider_url):
        """Extract information from a provider's detail page"""
        html_content = self.get_page_content(provider_url)
        if not html_content:
            return None
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        provider_info = {
            'url': provider_url,
            'category': '',
            'address': '',
            'rating': '',
            'latest_report': '',
            'urn': '',
            'provider_name': ''
        }
        
        # Get all text for analysis
        page_text = soup.get_text()
        
        # Extract provider name from title or h1
        title_elem = soup.find('h1')
        if title_elem:
            provider_info['provider_name'] = self.clean_text(title_elem.get_text())
        elif soup.find('title'):
            title_text = soup.find('title').get_text()
            title_text = re.sub(r'\s*-\s*Ofsted.*$', '', title_text)
            provider_info['provider_name'] = self.clean_text(title_text)
        
        # Extract URN from URL
        urn_match = re.search(r'/provider/\d+/(\d+)', provider_url)
        if urn_match:
            provider_info['urn'] = urn_match.group(1)
        
        # Extract category
        training_categories = [
            'Independent learning provider',
            'Further education college', 
            'Training provider',
            'Apprenticeship provider',
            'Adult learning provider',
            'Community learning provider',
            'Skills training provider',
            'Vocational training provider'
        ]
        
        for category in training_categories:
            if category.lower() in page_text.lower():
                provider_info['category'] = category
                break
        
        if not provider_info['category']:
            if 'apprenticeship' in page_text.lower():
                provider_info['category'] = 'Apprenticeship provider'
            elif 'independent' in page_text.lower() and 'learning' in page_text.lower():
                provider_info['category'] = 'Independent learning provider'
            elif 'training' in page_text.lower():
                provider_info['category'] = 'Training provider'
        
        # Extract address
        address_match = re.search(r'Address:\s*([^\n]+(?:\n[^\n]+)*?)(?=\n\s*\n|\n\s*[A-Z][a-z]+:|$)', page_text, re.IGNORECASE | re.MULTILINE)
        if address_match:
            address = address_match.group(1)
            address = re.sub(r'\n+', ', ', address)
            address = re.sub(r'\s+', ' ', address)
            address = address.strip(', ')
            if len(address) > 10:
                provider_info['address'] = address
        
        # Extract rating
        rating_keywords = ['Outstanding', 'Good', 'Requires improvement', 'Requires Improvement', 'Inadequate']
        for keyword in rating_keywords:
            if keyword in page_text:
                provider_info['rating'] = keyword
                break
        
        # Extract latest report date
        date_patterns = [
            r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4}-\d{2}-\d{2})'
        ]
        
        dates_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            dates_found.extend(matches)
        
        if dates_found:
            provider_info['latest_report'] = dates_found[-1]
        
        return provider_info
    
    def scrape_all_providers(self):
        """Main method to scrape ALL provider information"""
        print("Starting to scrape ALL Ofsted funded training providers...")
        
        # Get all provider links
        all_provider_links = self.get_all_provider_links()
        
        if not all_provider_links:
            print("No provider links found")
            return []
        
        print(f"\nFound {len(all_provider_links)} total providers to scrape")
        print(f"Estimated time: {len(all_provider_links) * 1.5 / 60:.1f} minutes")
        
        # Extract information from each provider
        providers_data = []
        failed_count = 0
        
        for i, link in enumerate(all_provider_links):
            if i % 50 == 0:
                print(f"\nProcessing provider {i+1}/{len(all_provider_links)} ({i/len(all_provider_links)*100:.1f}%)")
            
            provider_info = self.extract_provider_info(link)
            
            if provider_info:
                providers_data.append(provider_info)
                if i % 50 == 0:
                    print(f"✓ {provider_info.get('provider_name', 'Unknown')} (URN: {provider_info.get('urn', 'N/A')})")
            else:
                failed_count += 1
                if i % 50 == 0:
                    print(f"✗ Failed to extract info from {link}")
            
            # Be respectful with requests
            time.sleep(0.8)
            
            # Progress checkpoint every 200 providers
            if (i + 1) % 200 == 0:
                print(f"\n--- CHECKPOINT: Processed {i+1} providers, {len(providers_data)} successful, {failed_count} failed ---")
                # Save intermediate results
                self.save_to_csv(providers_data, f'checkpoint_all_providers_{i+1}.csv')
        
        print(f"\nScraping completed! Successfully scraped {len(providers_data)} providers, {failed_count} failed")
        return providers_data
    
    def display_summary(self, providers_data):
        """Display summary statistics"""
        if not providers_data:
            print("No data to summarize")
            return
        
        print(f"\n" + "="*80)
        print(f"COMPLETE OFSTED FUNDED TRAINING PROVIDERS DATASET")
        print(f"="*80)
        print(f"Total Providers Scraped: {len(providers_data)}")
        
        # Category breakdown
        categories = {}
        ratings = {}
        
        for provider in providers_data:
            cat = provider.get('category', 'Unknown')
            rating = provider.get('rating', 'No Rating')
            
            categories[cat] = categories.get(cat, 0) + 1
            ratings[rating] = ratings.get(rating, 0) + 1
        
        print(f"\nCategory Breakdown:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cat}: {count} ({count/len(providers_data)*100:.1f}%)")
        
        print(f"\nRating Breakdown:")
        for rating, count in sorted(ratings.items(), key=lambda x: x[1], reverse=True):
            print(f"  {rating}: {count} ({count/len(providers_data)*100:.1f}%)")
    
    def save_to_csv(self, providers_data, filename='all_ofsted_funded_training_providers.csv'):
        """Save provider data to CSV file"""
        if not providers_data:
            print("No data to save")
            return
        
        fieldnames = ['urn', 'provider_name', 'category', 'address', 'rating', 'latest_report', 'url']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(providers_data)
        
        print(f"Data saved to {filename}")

def main():
    scraper = AllOfstedProvidersScraper()
    
    # Scrape ALL providers
    providers = scraper.scrape_all_providers()
    
    if providers:
        # Display summary
        scraper.display_summary(providers)
        
        # Save to CSV
        scraper.save_to_csv(providers)
        
        # Also save to JSON
        with open('all_ofsted_funded_training_providers.json', 'w', encoding='utf-8') as jsonfile:
            json.dump(providers, jsonfile, indent=2, ensure_ascii=False)
        print("Data also saved to all_ofsted_funded_training_providers.json")
        
        # Create final summary document
        with open('ALL_PROVIDERS_SUMMARY.md', 'w', encoding='utf-8') as f:
            f.write(f"# Complete UK Funded Training Providers - Ofsted Data\n\n")
            f.write(f"This document contains information about ALL {len(providers)} Funded Training Providers scraped from the Ofsted website.\n\n")
            f.write(f"## Data Source\n")
            f.write(f"- **Website**: https://reports.ofsted.gov.uk/search?q=&location=&lat=&lon=&radius=&level_1_types=1&level_2_types%5B%5D=3\n")
            f.write(f"- **Date Scraped**: October 20, 2025\n")
            f.write(f"- **Total Providers**: {len(providers)}\n\n")
            
            # Category breakdown
            categories = {}
            for provider in providers:
                cat = provider.get('category', 'Unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            f.write(f"## Category Breakdown\n")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{cat}**: {count} providers ({count/len(providers)*100:.1f}%)\n")
            
            f.write(f"\n## Files Generated\n")
            f.write(f"1. `all_ofsted_funded_training_providers.csv` - Complete dataset in CSV format\n")
            f.write(f"2. `all_ofsted_funded_training_providers.json` - Complete dataset in JSON format\n")
            f.write(f"3. `get_all_providers.py` - The scraper script used\n")
            f.write(f"4. `ALL_PROVIDERS_SUMMARY.md` - This summary document\n")
        
        print("Summary document created: ALL_PROVIDERS_SUMMARY.md")
        
    else:
        print("No provider data was successfully scraped")

if __name__ == "__main__":
    main()