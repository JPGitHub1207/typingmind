#!/usr/bin/env python3
"""
Apprenticeship Training Provider Scraper

This script scrapes the UK government's apprenticeship training website to collect
information about all apprenticeship programmes and their training providers.

URL: https://findapprenticeshiptraining.apprenticeships.education.gov.uk/courses
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import re
from urllib.parse import urljoin, urlparse
import pandas as pd
from typing import List, Dict, Set
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ApprenticeshipScraper:
    def __init__(self):
        self.base_url = "https://findapprenticeshiptraining.apprenticeships.education.gov.uk"
        self.courses_url = f"{self.base_url}/courses"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Programmes to skip (already completed)
        self.skip_programmes = {
            "Team Leading Level 3",
            "Operations Management Level 5"
        }
        
        # Limit for testing - set to None for full scrape
        self.max_pages = 50  # Reasonable limit to avoid very long runs
        
        self.all_programmes = []
        self.programme_providers = {}
        
    def get_page(self, url: str, retries: int = 3) -> BeautifulSoup:
        """Fetch and parse a webpage with retries"""
        for attempt in range(retries):
            try:
                logger.info(f"Fetching: {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    raise
    
    def extract_programme_links(self) -> List[Dict[str, str]]:
        """Extract all apprenticeship programme links from all pages"""
        logger.info("Extracting programme links from all courses pages...")
        
        all_programmes = []
        page_num = 1
        
        while True:
            if self.max_pages and page_num > self.max_pages:
                logger.info(f"Reached maximum page limit ({self.max_pages}). Stopping.")
                break
                
            page_url = f"{self.courses_url}?PageNumber={page_num}"
            logger.info(f"Processing page {page_num}: {page_url}")
            
            try:
                soup = self.get_page(page_url)
                
                # Look for course links in the search results structure
                course_links = soup.select('a.das-search-results__link[href^="/courses/"]')
                
                # Filter out provider links and extract course info
                page_programmes = []
                for link in course_links:
                    href = link.get('href', '')
                    
                    # Skip provider links (they contain '/providers')
                    if '/providers' in href:
                        continue
                        
                    # Extract programme name and level
                    text = link.get_text(strip=True)
                    
                    # Skip if it's already completed
                    if any(skip in text for skip in self.skip_programmes):
                        logger.info(f"Skipping already completed programme: {text}")
                        continue
                    
                    full_url = urljoin(self.base_url, href)
                    page_programmes.append({
                        'name': text,
                        'url': full_url,
                        'path': href,
                        'course_id': href.split('/')[-1]  # Extract course ID
                    })
                
                if not page_programmes:
                    logger.info(f"No more programmes found on page {page_num}. Stopping.")
                    break
                
                logger.info(f"Found {len(page_programmes)} programmes on page {page_num}")
                all_programmes.extend(page_programmes)
                
                # Check if there's a next page
                next_page_link = soup.select('a[href*="PageNumber"]:contains("Next")')
                if not next_page_link:
                    # Also check for numbered pagination
                    next_page_num = page_num + 1
                    next_page_link = soup.select(f'a[href*="PageNumber={next_page_num}"]')
                    
                if not next_page_link:
                    logger.info(f"No next page found after page {page_num}. Stopping.")
                    break
                
                page_num += 1
                
                # Be respectful with requests
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing page {page_num}: {e}")
                break
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_programmes = []
        for prog in all_programmes:
            if prog['url'] not in seen_urls:
                seen_urls.add(prog['url'])
                unique_programmes.append(prog)
        
        logger.info(f"Found {len(unique_programmes)} unique programmes across all pages")
        return unique_programmes
    
    def extract_providers_from_programme(self, programme: Dict[str, str]) -> List[Dict[str, str]]:
        """Extract all training providers for a specific programme"""
        logger.info(f"Extracting providers for: {programme['name']}")
        
        try:
            # Go directly to the providers page for this course
            providers_url = f"{self.base_url}/courses/{programme['course_id']}/providers"
            
            soup = self.get_page(providers_url)
            providers = []
            
            # Look for provider listings on the providers page
            # Based on typical government website patterns, providers might be in:
            # - List items with provider names
            # - Links to individual provider pages
            # - Table rows with provider information
            
            provider_elements = []
            
            # Try different selectors for provider listings
            possible_selectors = [
                'a[href*="/providers/"]',  # Direct provider links
                '.provider-name',          # Provider name elements
                '.training-provider',      # Training provider elements
                '.govuk-list li a',        # Links in government lists
                '.das-search-results__link', # Search results style links
                'h2 a',                    # Heading links (common pattern)
                'h3 a',                    # Sub-heading links
                '.govuk-heading-m a',      # Government heading links
                '.govuk-heading-s a'       # Government sub-heading links
            ]
            
            for selector in possible_selectors:
                elements = soup.select(selector)
                if elements:
                    for elem in elements:
                        href = elem.get('href', '')
                        text = elem.get_text(strip=True)
                        
                        # Filter for actual provider links/names
                        if (('/providers/' in href or 'provider' in text.lower()) and 
                            text and len(text) > 2 and 
                            'view' not in text.lower() and
                            'back' not in text.lower() and
                            'search' not in text.lower()):
                            provider_elements.append(elem)
            
            # If no specific provider elements found, look for any meaningful links
            if not provider_elements:
                all_links = soup.find_all('a', href=True)
                for link in all_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Look for provider-like links
                    if (text and len(text) > 5 and len(text) < 100 and
                        not any(skip_word in text.lower() for skip_word in 
                               ['view', 'back', 'search', 'filter', 'sort', 'page', 'next', 'previous', 'home'])):
                        # This might be a provider name
                        provider_elements.append(link)
            
            # Extract provider information
            seen_providers = set()
            for element in provider_elements:
                provider_name = element.get_text(strip=True)
                provider_url = element.get('href', '')
                
                if provider_name and provider_name not in seen_providers and len(provider_name) > 2:
                    if provider_url:
                        provider_url = urljoin(self.base_url, provider_url)
                    
                    providers.append({
                        'name': provider_name,
                        'url': provider_url,
                        'programme': programme['name']
                    })
                    seen_providers.add(provider_name)
            
            logger.info(f"Found {len(providers)} providers for {programme['name']}")
            return providers
            
        except Exception as e:
            logger.error(f"Error extracting providers for {programme['name']}: {e}")
            return []
    
    def scrape_all_programmes(self):
        """Main method to scrape all programmes and their providers"""
        logger.info("Starting apprenticeship scraping process...")
        
        # Get all programme links
        programmes = self.extract_programme_links()
        
        if not programmes:
            logger.error("No programmes found! Check the website structure.")
            return
        
        logger.info(f"Processing {len(programmes)} programmes...")
        
        all_providers = []
        
        for i, programme in enumerate(programmes, 1):
            logger.info(f"Processing programme {i}/{len(programmes)}: {programme['name']}")
            
            # Extract providers for this programme
            providers = self.extract_providers_from_programme(programme)
            all_providers.extend(providers)
            
            # Store programme info
            self.programme_providers[programme['name']] = providers
            
            # Be respectful with requests
            time.sleep(1)
        
        self.all_programmes = programmes
        logger.info(f"Scraping completed! Found {len(all_providers)} total provider-programme combinations")
        
        return all_providers
    
    def save_results(self, output_format='both'):
        """Save the scraped results to files"""
        logger.info("Saving results...")
        
        # Prepare data for export
        all_data = []
        for programme_name, providers in self.programme_providers.items():
            if providers:
                for provider in providers:
                    all_data.append({
                        'Programme': programme_name,
                        'Provider': provider['name'],
                        'Provider_URL': provider.get('url', ''),
                        'Programme_URL': next((p['url'] for p in self.all_programmes if p['name'] == programme_name), '')
                    })
            else:
                # Programme with no providers found
                all_data.append({
                    'Programme': programme_name,
                    'Provider': 'No providers found',
                    'Provider_URL': '',
                    'Programme_URL': next((p['url'] for p in self.all_programmes if p['name'] == programme_name), '')
                })
        
        # Save as CSV
        if output_format in ['csv', 'both']:
            df = pd.DataFrame(all_data)
            csv_filename = 'apprenticeship_programmes_providers.csv'
            df.to_csv(csv_filename, index=False)
            logger.info(f"Results saved to {csv_filename}")
        
        # Save as JSON
        if output_format in ['json', 'both']:
            json_data = {
                'summary': {
                    'total_programmes': len(self.all_programmes),
                    'total_providers': len(set(item['Provider'] for item in all_data if item['Provider'] != 'No providers found')),
                    'scrape_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                },
                'programmes': self.all_programmes,
                'programme_providers': self.programme_providers,
                'detailed_data': all_data
            }
            
            json_filename = 'apprenticeship_programmes_providers.json'
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {json_filename}")
        
        # Print summary
        logger.info(f"Summary:")
        logger.info(f"- Total programmes processed: {len(self.all_programmes)}")
        logger.info(f"- Total provider-programme combinations: {len(all_data)}")
        logger.info(f"- Programmes with providers: {len([p for p in self.programme_providers.values() if p])}")
        logger.info(f"- Programmes without providers: {len([p for p in self.programme_providers.values() if not p])}")

def main():
    """Main function to run the scraper"""
    scraper = ApprenticeshipScraper()
    
    try:
        # Scrape all programmes and providers
        scraper.scrape_all_programmes()
        
        # Save results
        scraper.save_results('both')
        
        logger.info("Scraping completed successfully!")
        
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise

if __name__ == "__main__":
    main()