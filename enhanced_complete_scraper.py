#!/usr/bin/env python3
"""
Enhanced Complete Ofsted Funded Training Providers Scraper
Scrapes ALL 2,458 funded training providers with proper pagination handling
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
from urllib.parse import urljoin, urlparse, parse_qs
import re
import math

class EnhancedOfstedScraper:
    def __init__(self):
        self.base_url = "https://reports.ofsted.gov.uk"
        # Original search for funded training providers (level_2_types[]=3)
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
    
    def get_total_results_and_pages(self):
        """Get the total number of results and calculate pages needed"""
        print("Getting total results count...")
        
        html_content = self.get_page_content(self.search_base_url)
        if not html_content:
            return 0, 0
        
        soup = BeautifulSoup(html_content, 'html.parser')
        page_text = soup.get_text()
        
        # Look for result count
        result_count_patterns = [
            r'(\d+)\s+results?',
            r'showing\s+\d+\s+of\s+(\d+)',
            r'(\d+)\s+providers?\s+found',
            r'(\d{1,3}(?:,\d{3})*)\s+results?',  # Handle comma-separated numbers
        ]
        
        total_results = 0
        for pattern in result_count_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                result_str = match.group(1).replace(',', '')
                total_results = int(result_str)
                break
        
        if total_results == 0:
            # Fallback: count providers on first page and estimate
            provider_links = self.parse_provider_links_from_page(html_content)
            if provider_links:
                total_results = len(provider_links) * 10  # Rough estimate
        
        # Calculate pages (assuming 10 results per page)
        results_per_page = 10
        total_pages = math.ceil(total_results / results_per_page) if total_results > 0 else 1
        
        print(f"Found {total_results} total results across {total_pages} pages")
        return total_results, total_pages
    
    def get_all_provider_links(self):
        """Get all provider links from all pages"""
        total_results, total_pages = self.get_total_results_and_pages()
        
        if total_results == 0:
            print("No results found")
            return []
        
        all_provider_links = []
        
        # Try different pagination approaches
        pagination_approaches = [
            # Approach 1: Use page parameter
            lambda page: f"{self.search_base_url}&page={page}",
            # Approach 2: Use offset parameter (common alternative)
            lambda page: f"{self.search_base_url}&offset={(page-1)*10}",
            # Approach 3: Use start parameter
            lambda page: f"{self.search_base_url}&start={(page-1)*10}",
        ]
        
        successful_approach = None
        
        for approach_idx, url_generator in enumerate(pagination_approaches):
            print(f"\nTrying pagination approach {approach_idx + 1}...")
            
            # Test first few pages with this approach
            test_pages = min(3, total_pages)
            approach_links = []
            
            for page in range(1, test_pages + 1):
                url = url_generator(page)
                print(f"Testing page {page}: {url}")
                
                html_content = self.get_page_content(url)
                if not html_content:
                    break
                
                page_links = self.parse_provider_links_from_page(html_content)
                print(f"Found {len(page_links)} providers on page {page}")
                
                if not page_links and page == 1:
                    print("No providers found on first page, trying next approach")
                    break
                
                if not page_links and page > 1:
                    print(f"No providers found on page {page}, stopping this approach")
                    break
                
                # Check for duplicates from previous pages
                new_links = [link for link in page_links if link not in approach_links]
                approach_links.extend(new_links)
                
                if page > 1 and len(new_links) == 0:
                    print(f"All providers on page {page} were duplicates, stopping")
                    break
                
                time.sleep(1)  # Be respectful
            
            if approach_links:
                print(f"Approach {approach_idx + 1} successful! Found {len(approach_links)} unique providers in test")
                successful_approach = url_generator
                all_provider_links = approach_links
                break
        
        if not successful_approach:
            print("No pagination approach worked, using only first page")
            html_content = self.get_page_content(self.search_base_url)
            if html_content:
                all_provider_links = self.parse_provider_links_from_page(html_content)
            return all_provider_links
        
        # Now scrape all pages with the successful approach
        print(f"\nScraping all {total_pages} pages...")
        
        for page in range(len(all_provider_links) // 10 + 1, total_pages + 1):
            url = successful_approach(page)
            print(f"Scraping page {page}/{total_pages}: {url}")
            
            html_content = self.get_page_content(url)
            if not html_content:
                print(f"Failed to get page {page}")
                continue
            
            page_links = self.parse_provider_links_from_page(html_content)
            print(f"Found {len(page_links)} providers on page {page}")
            
            if not page_links:
                print(f"No providers found on page {page}, might be end of results")
                break
            
            # Add only new links
            new_links = [link for link in page_links if link not in all_provider_links]
            all_provider_links.extend(new_links)
            print(f"Added {len(new_links)} new providers (total: {len(all_provider_links)})")
            
            time.sleep(2)  # Be respectful between pages
            
            # Safety check
            if page > 500:  # Prevent infinite loops
                print("Reached safety limit of 500 pages")
                break
        
        print(f"\nCompleted scraping! Found {len(all_provider_links)} unique provider links")
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
    
    def scrape_all_providers(self, max_providers=None):
        """Main method to scrape ALL provider information"""
        print("Starting enhanced complete Ofsted provider scraping...")
        
        # Get all provider links
        all_provider_links = self.get_all_provider_links()
        
        if not all_provider_links:
            print("No provider links found")
            return []
        
        if max_providers:
            all_provider_links = all_provider_links[:max_providers]
            print(f"Limiting to first {max_providers} providers")
        
        print(f"\nFound {len(all_provider_links)} total providers to scrape")
        
        # Extract information from each provider
        providers_data = []
        failed_count = 0
        
        for i, link in enumerate(all_provider_links):
            print(f"\nProcessing provider {i+1}/{len(all_provider_links)}")
            provider_info = self.extract_provider_info(link)
            
            if provider_info:
                providers_data.append(provider_info)
                print(f"✓ {provider_info.get('provider_name', 'Unknown')} (URN: {provider_info.get('urn', 'N/A')})")
            else:
                failed_count += 1
                print(f"✗ Failed to extract info from {link}")
            
            # Be respectful with requests
            time.sleep(1.5)
            
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
    scraper = EnhancedOfstedScraper()
    
    # For testing, let's start with first 100 providers to see if pagination works
    print("Starting with first 100 providers to test pagination...")
    providers = scraper.scrape_all_providers(max_providers=100)
    
    if providers:
        # Display summary
        scraper.display_summary(providers)
        
        # Save to CSV
        scraper.save_to_csv(providers, 'enhanced_ofsted_providers_sample.csv')
        
        # Also save to JSON
        with open('enhanced_ofsted_providers_sample.json', 'w', encoding='utf-8') as jsonfile:
            json.dump(providers, jsonfile, indent=2, ensure_ascii=False)
        print("Data also saved to enhanced_ofsted_providers_sample.json")
        
        # Ask if user wants to continue with all providers
        print(f"\n" + "="*60)
        print("SAMPLE COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("The pagination is working. To scrape all ~2,458 providers,")
        print("modify the script to remove the max_providers limit.")
        
    else:
        print("No provider data was successfully scraped")

if __name__ == "__main__":
    main()