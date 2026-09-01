#!/usr/bin/env python3
"""
Complete Ofsted Funded Training Providers Scraper
Scrapes ALL funded training providers from Ofsted website with pagination support
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
from urllib.parse import urljoin, urlparse, parse_qs
import re

class CompleteOfstedScraper:
    def __init__(self):
        self.base_url = "https://reports.ofsted.gov.uk"
        self.search_url = "https://reports.ofsted.gov.uk/search?q=&location=&lat=&lon=&radius=&level_1_types=1&level_2_types%5B%5D=3"
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
    
    def get_all_search_pages(self):
        """Get all search result pages with pagination"""
        all_provider_links = []
        page = 1
        
        while True:
            # Construct URL for current page
            if page == 1:
                url = self.search_url
            else:
                url = f"{self.search_url}&page={page}"
            
            print(f"Fetching search results page {page}: {url}")
            html_content = self.get_page_content(url)
            
            if not html_content:
                print(f"Failed to get page {page}")
                break
            
            # Parse provider links from current page
            page_links = self.parse_provider_links_from_page(html_content)
            
            if not page_links:
                print(f"No more providers found on page {page}")
                break
            
            print(f"Found {len(page_links)} providers on page {page}")
            all_provider_links.extend(page_links)
            
            # Check if there's a next page
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for pagination indicators
            has_next = False
            
            # Common pagination patterns
            next_links = soup.find_all('a', string=re.compile(r'Next|>|→', re.IGNORECASE))
            if next_links:
                has_next = True
            
            # Look for page numbers
            page_links_found = soup.find_all('a', href=re.compile(r'page=\d+'))
            if page_links_found:
                # Check if there's a page number higher than current
                max_page = page
                for link in page_links_found:
                    href = link.get('href', '')
                    page_match = re.search(r'page=(\d+)', href)
                    if page_match:
                        page_num = int(page_match.group(1))
                        max_page = max(max_page, page_num)
                
                if max_page > page:
                    has_next = True
            
            # Also check if current page has fewer results than expected (indicating last page)
            if len(page_links) < 10:  # Assuming 10 results per page typically
                has_next = False
            
            if not has_next:
                print(f"Reached last page at page {page}")
                break
            
            page += 1
            time.sleep(1)  # Be respectful between page requests
            
            # Safety limit to prevent infinite loops
            if page > 100:
                print("Reached safety limit of 100 pages")
                break
        
        print(f"Total providers found across all pages: {len(all_provider_links)}")
        return all_provider_links
    
    def parse_provider_links_from_page(self, html_content):
        """Extract provider detail page links from a single search results page"""
        soup = BeautifulSoup(html_content, 'html.parser')
        provider_links = []
        
        # Look for provider links in search results
        all_links = soup.find_all('a', href=True)
        for link in all_links:
            href = link['href']
            if '/provider/' in href and href not in [l for l in provider_links]:
                full_url = urljoin(self.base_url, href)
                provider_links.append(full_url)
        
        return provider_links
    
    def clean_text(self, text):
        """Clean and normalize text"""
        if not text:
            return ""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        return text
    
    def extract_provider_info(self, provider_url):
        """Extract information from a provider's detail page"""
        print(f"Extracting info from: {provider_url}")
        
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
            # Remove "Ofsted" and other common suffixes
            title_text = re.sub(r'\s*-\s*Ofsted.*$', '', title_text)
            provider_info['provider_name'] = self.clean_text(title_text)
        
        # Extract URN from URL
        urn_match = re.search(r'/provider/\d+/(\d+)', provider_url)
        if urn_match:
            provider_info['urn'] = urn_match.group(1)
        
        # Extract category - look for training provider types
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
        
        # Fallback category detection
        if not provider_info['category']:
            if 'apprenticeship' in page_text.lower():
                provider_info['category'] = 'Apprenticeship provider'
            elif 'independent' in page_text.lower() and 'learning' in page_text.lower():
                provider_info['category'] = 'Independent learning provider'
            elif 'training' in page_text.lower():
                provider_info['category'] = 'Training provider'
        
        # Extract address with multiple strategies
        address_found = False
        
        # Strategy 1: Look for "Address:" followed by address
        address_match = re.search(r'Address:\s*([^\n]+(?:\n[^\n]+)*?)(?=\n\s*\n|\n\s*[A-Z][a-z]+:|$)', page_text, re.IGNORECASE | re.MULTILINE)
        if address_match:
            address = address_match.group(1)
            # Clean up the address
            address = re.sub(r'\n+', ', ', address)
            address = re.sub(r'\s+', ' ', address)
            address = address.strip(', ')
            if len(address) > 10:  # Ensure it's a meaningful address
                provider_info['address'] = address
                address_found = True
        
        # Strategy 2: Look for postal code patterns if address not found
        if not address_found:
            # UK postal code pattern
            postcode_pattern = r'([A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2})'
            postcode_matches = re.findall(postcode_pattern, page_text)
            if postcode_matches:
                # Find text before the postcode that might be the address
                for postcode in postcode_matches:
                    pattern = r'([^\n]*(?:\n[^\n]*)*?)\s*' + re.escape(postcode)
                    match = re.search(pattern, page_text, re.IGNORECASE)
                    if match:
                        potential_address = match.group(1)
                        # Clean and validate
                        lines = [line.strip() for line in potential_address.split('\n') if line.strip()]
                        if len(lines) >= 2:  # At least 2 lines for a valid address
                            address = ', '.join(lines[-3:]) + ', ' + postcode  # Take last 3 lines + postcode
                            provider_info['address'] = self.clean_text(address)
                            address_found = True
                            break
        
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
            # Take the most recent looking date
            provider_info['latest_report'] = dates_found[-1]
        
        return provider_info
    
    def scrape_all_providers(self):
        """Main method to scrape ALL provider information"""
        print("Starting complete Ofsted provider scraping...")
        
        # Get all provider links from all pages
        all_provider_links = self.get_all_search_pages()
        
        if not all_provider_links:
            print("No provider links found")
            return []
        
        print(f"\nFound {len(all_provider_links)} total providers to scrape")
        
        # Extract information from each provider
        providers_data = []
        failed_count = 0
        
        for i, link in enumerate(all_provider_links):
            print(f"\nProcessing provider {i+1}/{len(all_provider_links)}")
            provider_info = self.extract_provider_info(link)
            
            if provider_info:
                providers_data.append(provider_info)
            else:
                failed_count += 1
                print(f"Failed to extract info from {link}")
            
            # Be respectful with requests - longer delay for large scraping
            time.sleep(2)
            
            # Progress checkpoint every 50 providers
            if (i + 1) % 50 == 0:
                print(f"\n--- CHECKPOINT: Processed {i+1} providers, {len(providers_data)} successful, {failed_count} failed ---")
                # Save intermediate results
                self.save_to_csv(providers_data, f'checkpoint_providers_{i+1}.csv')
        
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
        
        print(f"\nFirst 5 Providers:")
        for i, provider in enumerate(providers_data[:5]):
            print(f"  {i+1}. {provider.get('provider_name', 'N/A')} (URN: {provider.get('urn', 'N/A')})")
        
        if len(providers_data) > 5:
            print(f"  ... and {len(providers_data) - 5} more")
    
    def save_to_csv(self, providers_data, filename='complete_ofsted_providers.csv'):
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
    scraper = CompleteOfstedScraper()
    
    # Scrape ALL provider data
    providers = scraper.scrape_all_providers()
    
    if providers:
        # Display summary
        scraper.display_summary(providers)
        
        # Save to CSV
        scraper.save_to_csv(providers)
        
        # Also save to JSON
        with open('complete_ofsted_providers.json', 'w', encoding='utf-8') as jsonfile:
            json.dump(providers, jsonfile, indent=2, ensure_ascii=False)
        print("Data also saved to complete_ofsted_providers.json")
        
    else:
        print("No provider data was successfully scraped")

if __name__ == "__main__":
    main()