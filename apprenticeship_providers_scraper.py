#!/usr/bin/env python3
"""
Apprenticeship Training Providers Scraper

This script scrapes organization details from the UK government's 
Find apprenticeship training website for a specific course.
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import re
from urllib.parse import urljoin, urlparse
import pandas as pd
from typing import List, Dict, Optional

class ApprenticeshipProvidersScraper:
    def __init__(self, base_url: str = "https://findapprenticeshiptraining.apprenticeships.education.gov.uk"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_provider_basic_info(self, card) -> Dict:
        """Extract basic provider information from a summary card"""
        provider_info = {}
        
        # Provider name and link
        title_link = card.find('h2', class_='govuk-summary-card__title').find('a')
        if title_link:
            provider_info['name'] = title_link.get_text().strip()
            provider_info['detail_url'] = urljoin(self.base_url, title_link.get('href'))
            provider_info['provider_id'] = title_link.get('id', '').replace('provider-', '')
        
        # Extract UKPRN from hidden form inputs
        ukprn_input = card.find('input', {'name': 'ukprn'})
        if ukprn_input:
            provider_info['ukprn'] = ukprn_input.get('value')
        
        return provider_info
    
    def extract_provider_details(self, detail_url: str) -> Dict:
        """Extract detailed information from provider detail page"""
        soup = self.get_page(detail_url)
        if not soup:
            return {}
        
        details = {}
        
        # Extract provider information from the detail page
        # Look for summary lists which contain key information
        summary_lists = soup.find_all('dl', class_='govuk-summary-list')
        
        for summary_list in summary_lists:
            rows = summary_list.find_all('div', class_='govuk-summary-list__row')
            for row in rows:
                key_elem = row.find('dt', class_='govuk-summary-list__key')
                value_elem = row.find('dd', class_='govuk-summary-list__value')
                
                if key_elem and value_elem:
                    key = key_elem.get_text().strip()
                    value = value_elem.get_text().strip()
                    
                    # Clean up the key name for consistent field names
                    key_clean = key.lower().replace(' ', '_').replace(':', '')
                    details[key_clean] = value
        
        # Extract contact information
        contact_section = soup.find('section', {'aria-labelledby': lambda x: x and 'contact' in x.lower()})
        if contact_section:
            # Look for address
            address_elem = contact_section.find('address')
            if address_elem:
                details['address'] = address_elem.get_text().strip()
            
            # Look for phone numbers
            phone_links = contact_section.find_all('a', href=lambda x: x and x.startswith('tel:'))
            if phone_links:
                details['phone'] = phone_links[0].get_text().strip()
            
            # Look for email addresses
            email_links = contact_section.find_all('a', href=lambda x: x and x.startswith('mailto:'))
            if email_links:
                details['email'] = email_links[0].get_text().strip()
            
            # Look for website
            website_links = contact_section.find_all('a', href=lambda x: x and x.startswith('http'))
            for link in website_links:
                href = link.get('href')
                if 'apprenticeships.education.gov.uk' not in href:  # Exclude internal links
                    details['website'] = href
                    break
        
        # Extract training information
        training_section = soup.find('section', {'aria-labelledby': lambda x: x and 'training' in x.lower()})
        if training_section:
            # Look for delivery methods
            delivery_elem = training_section.find(text=re.compile(r'delivery', re.I))
            if delivery_elem:
                parent = delivery_elem.parent
                if parent:
                    next_elem = parent.find_next_sibling()
                    if next_elem:
                        details['delivery_method'] = next_elem.get_text().strip()
        
        # Extract ratings and reviews
        ratings_section = soup.find('section', {'aria-labelledby': lambda x: x and ('review' in x.lower() or 'rating' in x.lower())})
        if ratings_section:
            # Look for overall rating
            rating_elem = ratings_section.find('span', class_=lambda x: x and 'rating' in ' '.join(x).lower())
            if rating_elem:
                details['overall_rating'] = rating_elem.get_text().strip()
        
        # Extract achievement rates
        achievement_elem = soup.find(text=re.compile(r'achievement rate', re.I))
        if achievement_elem:
            parent = achievement_elem.parent
            if parent:
                # Look for percentage in nearby elements
                percentage_elem = parent.find_next(text=re.compile(r'\d+%'))
                if percentage_elem:
                    details['achievement_rate'] = percentage_elem.strip()
        
        return details
    
    def scrape_providers_list(self, course_id: str, locations: List[str] = None, max_pages_per_location: int = None) -> List[Dict]:
        """Scrape all providers for a given course from multiple locations"""
        if locations is None:
            # Use major UK cities to get comprehensive coverage
            locations = [
                'London', 'Birmingham', 'Manchester', 'Leeds', 'Glasgow', 
                'Liverpool', 'Newcastle', 'Sheffield', 'Bristol', 'Cardiff',
                'Edinburgh', 'Belfast', 'Nottingham', 'Leicester', 'Coventry',
                'Bradford', 'Stoke-on-Trent', 'Wolverhampton', 'Plymouth', 'Southampton'
            ]
        
        all_providers = []
        seen_providers = set()  # Track by UKPRN to avoid duplicates
        
        for location in locations:
            print(f"\n=== Scraping providers for location: {location} ===")
            location_providers = self.scrape_providers_for_location(course_id, location, max_pages_per_location)
            
            # Add only new providers (avoid duplicates)
            new_providers = 0
            for provider in location_providers:
                ukprn = provider.get('ukprn')
                if ukprn and ukprn not in seen_providers:
                    seen_providers.add(ukprn)
                    provider['discovered_location'] = location  # Track where we found this provider
                    all_providers.append(provider)
                    new_providers += 1
            
            print(f"Added {new_providers} new providers from {location} (total unique: {len(all_providers)})")
            time.sleep(3)  # Be respectful between locations
        
        return all_providers
    
    def scrape_providers_for_location(self, course_id: str, location: str, max_pages: int = None) -> List[Dict]:
        """Scrape providers for a specific location"""
        providers = []
        page = 1
        
        while True:
            if max_pages and page > max_pages:
                break
                
            url = f"{self.base_url}/courses/{course_id}/providers"
            params = {'Location': location}
            if page > 1:
                params['page'] = page
            
            print(f"  Scraping page {page} for {location}")
            
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                print(f"  Error fetching page: {e}")
                break
            
            # Find all provider cards
            summary_cards = soup.find_all('div', class_='govuk-summary-card')
            
            if not summary_cards:
                print(f"  No providers found on page {page}")
                break
            
            print(f"  Found {len(summary_cards)} providers on page {page}")
            
            for card in summary_cards:
                try:
                    # Extract basic info
                    provider_info = self.extract_provider_basic_info(card)
                    
                    if provider_info.get('detail_url'):
                        print(f"    Scraping details for: {provider_info['name']}")
                        
                        # Extract detailed info
                        detailed_info = self.extract_provider_details(provider_info['detail_url'])
                        
                        # Merge the information
                        provider_info.update(detailed_info)
                        
                        providers.append(provider_info)
                        
                        # Be respectful to the server
                        time.sleep(1)
                    
                except Exception as e:
                    print(f"    Error processing provider: {e}")
                    continue
            
            # Check if there's a next page
            next_link = soup.find('a', {'rel': 'next'})
            if not next_link:
                print(f"  No more pages found for {location}")
                break
            
            page += 1
            time.sleep(2)  # Be respectful between pages
        
        return providers
    
    def save_to_json(self, providers: List[Dict], filename: str):
        """Save providers data to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(providers, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(providers)} providers to {filename}")
    
    def save_to_csv(self, providers: List[Dict], filename: str):
        """Save providers data to CSV file"""
        if not providers:
            print("No providers to save")
            return
        
        df = pd.DataFrame(providers)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Saved {len(providers)} providers to {filename}")
    
    def print_summary(self, providers: List[Dict]):
        """Print a summary of scraped data"""
        print(f"\n=== SCRAPING SUMMARY ===")
        print(f"Total providers scraped: {len(providers)}")
        
        if providers:
            # Show available fields
            all_fields = set()
            for provider in providers:
                all_fields.update(provider.keys())
            
            print(f"Available fields: {', '.join(sorted(all_fields))}")
            
            # Show sample data
            print(f"\n=== SAMPLE PROVIDER ===")
            sample = providers[0]
            for key, value in sample.items():
                print(f"{key}: {value}")

def main():
    """Main function to run the scraper"""
    scraper = ApprenticeshipProvidersScraper()
    
    # Course ID 105 is for "Team leader (level 3)" - Operations Management
    course_id = "105"
    
    print(f"Starting to scrape providers for course {course_id}")
    print("This will scrape from multiple UK locations to get comprehensive coverage...")
    print("This may take 30+ minutes as we're being respectful to the server...")
    
    # Scrape all providers from multiple locations
    providers = scraper.scrape_providers_list(course_id, max_pages_per_location=None)
    
    if providers:
        # Save results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        json_filename = f"apprenticeship_providers_{course_id}_{timestamp}.json"
        csv_filename = f"apprenticeship_providers_{course_id}_{timestamp}.csv"
        
        scraper.save_to_json(providers, json_filename)
        scraper.save_to_csv(providers, csv_filename)
        scraper.print_summary(providers)
    else:
        print("No providers were scraped")

if __name__ == "__main__":
    main()