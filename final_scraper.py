#!/usr/bin/env python3
"""
Final Ofsted Funded Training Providers Scraper
Scrapes complete information about funded training providers from Ofsted website
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
from urllib.parse import urljoin
import re

class FinalOfstedScraper:
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
    
    def parse_provider_links(self, html_content):
        """Extract provider detail page links from search results"""
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
        
        print(f"Found {len(provider_links)} provider links")
        return provider_links[:10]  # Return first 10
    
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
    
    def scrape_providers(self, max_providers=10):
        """Main method to scrape provider information"""
        print("Starting final Ofsted provider scraping...")
        
        # Get search results
        search_html = self.get_page_content(self.search_url)
        if not search_html:
            print("Failed to get search results")
            return []
        
        # Parse provider links
        provider_links = self.parse_provider_links(search_html)
        if not provider_links:
            print("No provider links found")
            return []
        
        # Extract information from each provider
        providers_data = []
        for i, link in enumerate(provider_links[:max_providers]):
            print(f"\nProcessing provider {i+1}/{min(len(provider_links), max_providers)}")
            provider_info = self.extract_provider_info(link)
            if provider_info:
                providers_data.append(provider_info)
            
            # Be respectful with requests
            time.sleep(1)
        
        return providers_data
    
    def display_results(self, providers_data):
        """Display the scraped results in a formatted way"""
        if not providers_data:
            print("No data to display")
            return
        
        print(f"\nSuccessfully scraped {len(providers_data)} providers")
        print("\n" + "="*120)
        print("FUNDED TRAINING PROVIDERS - OFSTED DATA (First 10)")
        print("="*120)
        
        for i, provider in enumerate(providers_data, 1):
            print(f"\n{i}. {provider.get('provider_name', 'N/A')}")
            print(f"   URN: {provider.get('urn', 'N/A')}")
            print(f"   Category: {provider.get('category', 'N/A')}")
            print(f"   Address: {provider.get('address', 'N/A')}")
            print(f"   Rating: {provider.get('rating', 'N/A')}")
            print(f"   Latest Report: {provider.get('latest_report', 'N/A')}")
            print(f"   URL: {provider.get('url', 'N/A')}")
            print("-" * 120)
    
    def save_to_csv(self, providers_data, filename='final_ofsted_providers.csv'):
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
    scraper = FinalOfstedScraper()
    
    # Scrape provider data
    providers = scraper.scrape_providers(max_providers=10)
    
    if providers:
        # Display results
        scraper.display_results(providers)
        
        # Save to CSV
        scraper.save_to_csv(providers)
        
        # Also save to JSON
        with open('final_ofsted_providers.json', 'w', encoding='utf-8') as jsonfile:
            json.dump(providers, jsonfile, indent=2, ensure_ascii=False)
        print("Data also saved to final_ofsted_providers.json")
        
    else:
        print("No provider data was successfully scraped")

if __name__ == "__main__":
    main()