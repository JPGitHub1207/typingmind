#!/usr/bin/env python3
"""
Operations Management Training Providers Scraper

This script scrapes all 472 training providers for Operations Manager (Level 5) 
from the UK government's apprenticeship training website.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import re
from urllib.parse import urljoin
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OperationsManagementProvidersScraper:
    def __init__(self):
        self.base_url = "https://findapprenticeshiptraining.apprenticeships.education.gov.uk"
        self.providers_url = "/courses/104/providers"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.providers = []
        
    def get_page(self, page_number=1):
        """Fetch a specific page of providers"""
        params = {
            'OrderBy': 'AchievementRate',
            'location': '',
            'Distance': 'All',
            'PageNumber': page_number
        }
        
        url = self.base_url + self.providers_url
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching page {page_number}: {e}")
            return None
    
    def extract_provider_info(self, provider_element):
        """Extract information from a single provider element"""
        provider_info = {}
        
        try:
            # Provider name and link
            title_element = provider_element.find('h2', class_='govuk-summary-card__title')
            if title_element:
                link_element = title_element.find('a')
                if link_element:
                    provider_info['name'] = link_element.get_text(strip=True)
                    provider_info['detail_url'] = urljoin(self.base_url, link_element.get('href', ''))
                    
                    # Extract UKPRN from the URL or ID
                    provider_id_match = re.search(r'provider-(\d+)', link_element.get('id', ''))
                    if provider_id_match:
                        provider_info['ukprn'] = provider_id_match.group(1)
            
            # Training options
            training_options = []
            training_dd = provider_element.find('dd', class_='govuk-summary-list__value')
            if training_dd:
                training_paragraphs = training_dd.find_all('p', class_='govuk-body')
                for p in training_paragraphs:
                    option_text = p.get_text(strip=True)
                    if option_text and not option_text.startswith('One day') and not option_text.startswith('Blocks of') and not option_text.startswith('Training at'):
                        training_options.append(option_text)
            provider_info['training_options'] = ', '.join(training_options) if training_options else ''
            
            # Reviews and ratings
            review_sections = provider_element.find_all('p', class_='govuk-!-margin-0')
            employer_reviews = ''
            apprentice_reviews = ''
            
            for review_section in review_sections:
                rating_span = review_section.find('span', class_='das-rating')
                if rating_span:
                    rating_text = rating_span.get_text(strip=True)
                    if 'employer review' in rating_text:
                        employer_reviews = rating_text
                    elif 'apprentice review' in rating_text:
                        apprentice_reviews = rating_text
                else:
                    # Check for "No reviews" text
                    no_review_span = review_section.find('span', class_='govuk-body')
                    if no_review_span:
                        review_text = no_review_span.get_text(strip=True)
                        if 'No employer reviews' in review_text:
                            employer_reviews = 'No employer reviews'
                        elif 'No apprentice reviews' in review_text:
                            apprentice_reviews = 'No apprentice reviews'
            
            provider_info['employer_reviews'] = employer_reviews
            provider_info['apprentice_reviews'] = apprentice_reviews
            
            # Achievement rate
            achievement_elements = provider_element.find_all('dd', class_='govuk-summary-list__value')
            for dd in achievement_elements:
                text = dd.get_text(strip=True)
                if '%' in text and 'apprentices' in text:
                    provider_info['achievement_rate'] = text
                    break
            
            if 'achievement_rate' not in provider_info:
                provider_info['achievement_rate'] = ''
                
        except Exception as e:
            logger.error(f"Error extracting provider info: {e}")
            
        return provider_info
    
    def scrape_page(self, page_number):
        """Scrape all providers from a single page"""
        logger.info(f"Scraping page {page_number}...")
        
        html_content = self.get_page(page_number)
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all provider cards
        provider_cards = soup.find_all('div', class_='govuk-summary-card')
        
        page_providers = []
        for card in provider_cards:
            provider_info = self.extract_provider_info(card)
            if provider_info.get('name'):  # Only add if we got a name
                page_providers.append(provider_info)
        
        logger.info(f"Found {len(page_providers)} providers on page {page_number}")
        return page_providers
    
    def scrape_all_pages(self, max_pages=48):
        """Scrape all pages of providers"""
        logger.info(f"Starting to scrape all {max_pages} pages...")
        
        for page_num in range(1, max_pages + 1):
            try:
                page_providers = self.scrape_page(page_num)
                
                if not page_providers:
                    logger.info(f"No providers found on page {page_num}, stopping...")
                    break
                    
                self.providers.extend(page_providers)
                
                # Add a small delay to be respectful to the server
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error scraping page {page_num}: {e}")
                continue
        
        logger.info(f"Scraping completed. Total providers found: {len(self.providers)}")
        return self.providers
    
    def save_to_csv(self, filename='operations_management_providers.csv'):
        """Save providers data to CSV file"""
        if not self.providers:
            logger.warning("No providers data to save")
            return
        
        df = pd.DataFrame(self.providers)
        df.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"Data saved to {filename}")
        
    def save_to_json(self, filename='operations_management_providers.json'):
        """Save providers data to JSON file"""
        if not self.providers:
            logger.warning("No providers data to save")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.providers, f, indent=2, ensure_ascii=False)
        logger.info(f"Data saved to {filename}")
    
    def get_summary(self):
        """Get summary statistics of scraped data"""
        if not self.providers:
            return "No data scraped yet"
        
        total_providers = len(self.providers)
        providers_with_reviews = len([p for p in self.providers if p.get('employer_reviews') and 'No employer reviews' not in p.get('employer_reviews', '')])
        providers_with_achievement_rate = len([p for p in self.providers if p.get('achievement_rate')])
        
        return f"""
Scraping Summary:
- Total providers scraped: {total_providers}
- Providers with employer reviews: {providers_with_reviews}
- Providers with achievement rate data: {providers_with_achievement_rate}
- Expected total: 472
"""

def main():
    """Main function to run the scraper"""
    scraper = OperationsManagementProvidersScraper()
    
    # Scrape all providers
    providers = scraper.scrape_all_pages()
    
    # Save results
    scraper.save_to_csv()
    scraper.save_to_json()
    
    # Print summary
    print(scraper.get_summary())
    
    # Show first few providers as sample
    if providers:
        print("\nSample of scraped data:")
        for i, provider in enumerate(providers[:3]):
            print(f"\n{i+1}. {provider.get('name', 'Unknown')}")
            print(f"   UKPRN: {provider.get('ukprn', 'N/A')}")
            print(f"   Training Options: {provider.get('training_options', 'N/A')}")
            print(f"   Achievement Rate: {provider.get('achievement_rate', 'N/A')}")

if __name__ == "__main__":
    main()