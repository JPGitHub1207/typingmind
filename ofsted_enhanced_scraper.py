#!/usr/bin/env python3
"""
Enhanced Ofsted Website Scraper with BeautifulSoup
More robust HTML parsing and data extraction for Ofsted inspection data
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin, quote, urlparse
import re
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ofsted_enhanced_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedOfstedScraper:
    """Enhanced Ofsted scraper with BeautifulSoup for better HTML parsing"""
    
    def __init__(self, delay: float = 1.0):
        self.base_url = "https://reports.ofsted.gov.uk"
        self.search_api_url = "https://reports.ofsted.gov.uk/search"
        self.provider_api_url = "https://reports.ofsted.gov.uk/provider"
        self.delay = delay
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        self.results = []
        self.processed_urns = set()  # Track processed URNs to avoid duplicates
        
    def search_providers(self, company_name: str, location: str = "", provider_types: List[str] = None) -> List[Dict]:
        """
        Search for providers using Ofsted's search functionality
        
        Args:
            company_name: Name of the company/provider to search for
            location: Location to search in (optional)
            provider_types: List of provider types to filter by
            
        Returns:
            List of provider dictionaries with basic info
        """
        try:
            logger.info(f"Searching for provider: {company_name}")
            
            # Prepare search parameters
            search_params = {
                'q': company_name,
                'location': location,
                'radius': '25',  # 25 mile radius
                'level': 'all',
                'status': 'all',
                'sort': 'relevance'
            }
            
            if provider_types:
                search_params['provider_types'] = ','.join(provider_types)
            
            # Make search request
            response = self.session.get(self.search_api_url, params=search_params, timeout=30)
            response.raise_for_status()
            
            # Parse search results
            soup = BeautifulSoup(response.content, 'html.parser')
            providers = self._parse_search_results(soup, company_name)
            
            logger.info(f"Found {len(providers)} providers for '{company_name}'")
            time.sleep(self.delay)
            
            return providers
            
        except requests.RequestException as e:
            logger.error(f"Network error searching for '{company_name}': {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching for '{company_name}': {e}")
            return []
    
    def _parse_search_results(self, soup: BeautifulSoup, search_term: str) -> List[Dict]:
        """Parse BeautifulSoup object to extract provider information from search results"""
        providers = []
        
        # Look for provider cards/results in the HTML
        # Common selectors for Ofsted search results
        result_selectors = [
            '.search-result',
            '.provider-result', 
            '.inspection-result',
            '[data-provider-urn]',
            'article',
            '.result-item'
        ]
        
        results_found = False
        for selector in result_selectors:
            result_elements = soup.select(selector)
            if result_elements:
                results_found = True
                logger.debug(f"Found {len(result_elements)} results using selector: {selector}")
                
                for element in result_elements:
                    provider_data = self._extract_provider_from_element(element, search_term)
                    if provider_data:
                        providers.append(provider_data)
                break
        
        # If no structured results found, try to find provider links
        if not results_found:
            provider_links = soup.find_all('a', href=re.compile(r'/provider/files/\d+/urn/\d+'))
            for link in provider_links:
                provider_data = self._extract_provider_from_link(link, search_term)
                if provider_data:
                    providers.append(provider_data)
        
        # Remove duplicates based on URN
        unique_providers = []
        seen_urns = set()
        for provider in providers:
            urn = provider.get('urn')
            if urn and urn not in seen_urns:
                seen_urns.add(urn)
                unique_providers.append(provider)
        
        return unique_providers
    
    def _extract_provider_from_element(self, element: BeautifulSoup, search_term: str) -> Optional[Dict]:
        """Extract provider information from a search result element"""
        try:
            # Try to find provider name
            name_selectors = ['h2 a', 'h3 a', '.provider-name', '.result-title', 'a[href*="/provider/"]']
            name = None
            link = None
            
            for selector in name_selectors:
                name_element = element.select_one(selector)
                if name_element:
                    name = name_element.get_text(strip=True)
                    link = name_element.get('href')
                    break
            
            if not name or not link:
                return None
            
            # Extract URN from link
            urn = self._extract_urn_from_link(link)
            if not urn:
                return None
            
            # Extract additional information
            address = self._extract_text_by_selectors(element, ['.address', '.location', '.provider-address'])
            provider_type = self._extract_text_by_selectors(element, ['.provider-type', '.type', '.category'])
            status = self._extract_text_by_selectors(element, ['.status', '.provider-status'])
            
            return {
                'name': name,
                'urn': urn,
                'link': link,
                'address': address,
                'provider_type': provider_type,
                'status': status,
                'search_term': search_term
            }
            
        except Exception as e:
            logger.debug(f"Error extracting provider from element: {e}")
            return None
    
    def _extract_provider_from_link(self, link_element: BeautifulSoup, search_term: str) -> Optional[Dict]:
        """Extract provider information from a simple link element"""
        try:
            name = link_element.get_text(strip=True)
            href = link_element.get('href')
            urn = self._extract_urn_from_link(href)
            
            if name and href and urn:
                return {
                    'name': name,
                    'urn': urn,
                    'link': href,
                    'search_term': search_term
                }
        except Exception as e:
            logger.debug(f"Error extracting provider from link: {e}")
            
        return None
    
    def _extract_text_by_selectors(self, element: BeautifulSoup, selectors: List[str]) -> str:
        """Try multiple selectors to extract text from an element"""
        for selector in selectors:
            found_element = element.select_one(selector)
            if found_element:
                return found_element.get_text(strip=True)
        return ""
    
    def _extract_urn_from_link(self, link: str) -> Optional[str]:
        """Extract URN (Unique Reference Number) from provider link"""
        if not link:
            return None
        
        urn_match = re.search(r'/urn/(\d+)', link)
        return urn_match.group(1) if urn_match else None
    
    def get_provider_details(self, provider: Dict) -> Dict:
        """
        Get detailed information for a specific provider
        
        Args:
            provider: Provider dictionary with basic info
            
        Returns:
            Detailed provider information
        """
        try:
            urn = provider.get('urn')
            if urn in self.processed_urns:
                logger.info(f"Skipping already processed URN: {urn}")
                return provider
            
            logger.info(f"Getting details for provider: {provider['name']} (URN: {urn})")
            
            # Construct full URL
            if provider['link'].startswith('http'):
                provider_url = provider['link']
            else:
                provider_url = urljoin(self.base_url, provider['link'])
            
            # Get provider page
            response = self.session.get(provider_url, timeout=30)
            response.raise_for_status()
            
            # Parse provider details
            soup = BeautifulSoup(response.content, 'html.parser')
            details = self._parse_provider_details(soup, provider)
            
            self.processed_urns.add(urn)
            logger.info(f"Successfully retrieved details for {provider['name']}")
            
            time.sleep(self.delay)
            return details
            
        except requests.RequestException as e:
            logger.error(f"Network error getting details for {provider['name']}: {e}")
            return self._create_error_entry(provider, f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting details for {provider['name']}: {e}")
            return self._create_error_entry(provider, f"Parse error: {str(e)}")
    
    def _parse_provider_details(self, soup: BeautifulSoup, provider: Dict) -> Dict:
        """Parse provider details page using BeautifulSoup"""
        
        details = {
            'name': provider.get('name', ''),
            'urn': provider.get('urn', ''),
            'search_term': provider.get('search_term', ''),
            'scraped_at': datetime.now().isoformat(),
            'data_source': 'Ofsted Reports Website',
            'provider_url': provider.get('link', '')
        }
        
        # Extract basic provider information
        details.update(self._extract_basic_info(soup))
        
        # Extract inspection information
        details.update(self._extract_inspection_info(soup))
        
        # Extract ratings and grades
        details.update(self._extract_ratings(soup))
        
        # Extract contact information
        details.update(self._extract_contact_info(soup))
        
        return details
    
    def _extract_basic_info(self, soup: BeautifulSoup) -> Dict:
        """Extract basic provider information"""
        info = {}
        
        # Provider type
        type_selectors = ['.provider-type', '.establishment-type', '[data-label="Type"]']
        info['provider_type'] = self._get_text_by_selectors(soup, type_selectors)
        
        # Status
        status_selectors = ['.provider-status', '.status', '[data-label="Status"]']
        info['status'] = self._get_text_by_selectors(soup, status_selectors)
        
        # Registration date
        reg_date_selectors = ['.registration-date', '[data-label="Registration date"]']
        info['registration_date'] = self._get_text_by_selectors(soup, reg_date_selectors)
        
        # Age range
        age_range_selectors = ['.age-range', '[data-label="Age range"]']
        info['age_range'] = self._get_text_by_selectors(soup, age_range_selectors)
        
        return info
    
    def _extract_inspection_info(self, soup: BeautifulSoup) -> Dict:
        """Extract inspection-related information"""
        info = {}
        
        # Last inspection date
        inspection_date_selectors = [
            '.inspection-date', 
            '[data-label="Inspection date"]',
            '.last-inspection-date'
        ]
        info['last_inspection_date'] = self._get_text_by_selectors(soup, inspection_date_selectors)
        
        # Report published date
        published_selectors = [
            '.published-date',
            '[data-label="Published"]',
            '.report-published'
        ]
        info['report_published_date'] = self._get_text_by_selectors(soup, published_selectors)
        
        # Next inspection due
        next_inspection_selectors = [
            '.next-inspection',
            '[data-label="Next inspection"]'
        ]
        info['next_inspection_due'] = self._get_text_by_selectors(soup, next_inspection_selectors)
        
        return info
    
    def _extract_ratings(self, soup: BeautifulSoup) -> Dict:
        """Extract inspection ratings and grades"""
        ratings = {}
        
        # Common rating categories
        rating_categories = {
            'overall_effectiveness': ['Overall effectiveness', 'Overall'],
            'quality_of_education': ['Quality of education', 'Quality of teaching'],
            'behaviour_and_attitudes': ['Behaviour and attitudes', 'Behaviour'],
            'personal_development': ['Personal development', 'Personal, social and emotional development'],
            'leadership_and_management': ['Leadership and management', 'Leadership'],
            'safeguarding': ['Safeguarding', 'Safeguarding arrangements']
        }
        
        for key, labels in rating_categories.items():
            rating = self._find_rating_by_labels(soup, labels)
            if rating:
                ratings[key] = rating
        
        return ratings
    
    def _find_rating_by_labels(self, soup: BeautifulSoup, labels: List[str]) -> str:
        """Find rating by searching for specific labels"""
        for label in labels:
            # Try different patterns to find the rating
            patterns = [
                f'//dt[contains(text(), "{label}")]/following-sibling::dd[1]',
                f'//th[contains(text(), "{label}")]/following-sibling::td[1]',
                f'//span[contains(text(), "{label}")]/following-sibling::span[1]'
            ]
            
            # Also try CSS selectors
            css_patterns = [
                f'[data-label*="{label}"]',
                f'.rating-{label.lower().replace(" ", "-")}'
            ]
            
            for pattern in css_patterns:
                element = soup.select_one(pattern)
                if element:
                    return element.get_text(strip=True)
        
        return ""
    
    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict:
        """Extract contact information"""
        contact = {}
        
        # Address
        address_selectors = ['.address', '.provider-address', '[data-label="Address"]']
        contact['address'] = self._get_text_by_selectors(soup, address_selectors)
        
        # Phone
        phone_selectors = ['.phone', '.telephone', '[data-label="Phone"]', 'a[href^="tel:"]']
        contact['phone'] = self._get_text_by_selectors(soup, phone_selectors)
        
        # Website
        website_selectors = ['.website', '[data-label="Website"]', 'a[href^="http"]']
        contact['website'] = self._get_text_by_selectors(soup, website_selectors)
        
        # Email
        email_selectors = ['.email', '[data-label="Email"]', 'a[href^="mailto:"]']
        contact['email'] = self._get_text_by_selectors(soup, email_selectors)
        
        return contact
    
    def _get_text_by_selectors(self, soup: BeautifulSoup, selectors: List[str]) -> str:
        """Try multiple selectors to extract text"""
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return ""
    
    def _create_error_entry(self, provider: Dict, error_msg: str) -> Dict:
        """Create an error entry for failed provider lookups"""
        return {
            **provider,
            'error': error_msg,
            'scraped_at': datetime.now().isoformat(),
            'status': 'Error'
        }
    
    def process_companies(self, company_list: List[str]) -> List[Dict]:
        """
        Process a list of companies to get their Ofsted data
        
        Args:
            company_list: List of company names to search for
            
        Returns:
            List of processed company data
        """
        all_results = []
        
        logger.info(f"Starting to process {len(company_list)} companies")
        
        for i, company in enumerate(company_list, 1):
            logger.info(f"Processing company {i}/{len(company_list)}: {company}")
            
            try:
                # Search for providers matching this company
                providers = self.search_providers(company)
                
                if not providers:
                    logger.warning(f"No providers found for {company}")
                    all_results.append({
                        'name': company,
                        'search_term': company,
                        'status': 'Not Found',
                        'scraped_at': datetime.now().isoformat()
                    })
                    continue
                
                # Get details for each provider found
                for provider in providers:
                    details = self.get_provider_details(provider)
                    all_results.append(details)
                
            except Exception as e:
                logger.error(f"Error processing company {company}: {e}")
                all_results.append({
                    'name': company,
                    'search_term': company,
                    'error': str(e),
                    'status': 'Error',
                    'scraped_at': datetime.now().isoformat()
                })
        
        self.results = all_results
        logger.info(f"Completed processing. Total results: {len(all_results)}")
        return all_results
    
    def save_results_csv(self, filename: str = None) -> str:
        """Save results to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ofsted_enhanced_results_{timestamp}.csv"
        
        if not self.results:
            logger.warning("No results to save")
            return filename
        
        # Get all unique keys from results
        all_keys = set()
        for result in self.results:
            all_keys.update(result.keys())
        
        fieldnames = sorted(list(all_keys))
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)
        
        logger.info(f"Results saved to {filename}")
        return filename
    
    def save_results_json(self, filename: str = None) -> str:
        """Save results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ofsted_enhanced_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.results, jsonfile, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {filename}")
        return filename
    
    def generate_report(self) -> str:
        """Generate a summary report of the scraping results"""
        if not self.results:
            return "No results to report"
        
        total_results = len(self.results)
        successful_results = len([r for r in self.results if 'error' not in r])
        error_results = total_results - successful_results
        
        # Count by status
        status_counts = {}
        for result in self.results:
            status = result.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        report = f"""
=== OFSTED SCRAPING REPORT ===
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Total Results: {total_results}
Successful: {successful_results}
Errors: {error_results}

Status Breakdown:
"""
        for status, count in sorted(status_counts.items()):
            report += f"  {status}: {count}\n"
        
        return report

def load_company_list(filename: str) -> List[str]:
    """Load company list from a text file (one company per line)"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            companies = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    companies.append(line)
        
        logger.info(f"Loaded {len(companies)} companies from {filename}")
        return companies
    except FileNotFoundError:
        logger.error(f"Company list file {filename} not found")
        return []
    except Exception as e:
        logger.error(f"Error loading company list: {e}")
        return []

def main():
    """Main function to run the enhanced Ofsted scraper"""
    
    print("=== Enhanced Ofsted Website Scraper ===")
    print("This tool scrapes Ofsted inspection data for educational providers")
    print()
    
    # Try to load companies from file
    companies_file = "companies.txt"
    companies = load_company_list(companies_file)
    
    if not companies:
        print(f"No companies loaded from {companies_file}")
        print("Using sample company list for demonstration...")
        companies = [
            "ABC Learning Centre",
            "XYZ Training Academy", 
            "Education Plus Ltd",
            "Skills Development Institute",
            "Future Leaders College"
        ]
    
    print(f"Processing {len(companies)} companies...")
    
    # Create scraper instance with 2 second delay between requests
    scraper = EnhancedOfstedScraper(delay=2.0)
    
    # Process companies
    results = scraper.process_companies(companies)
    
    # Save results
    csv_file = scraper.save_results_csv()
    json_file = scraper.save_results_json()
    
    # Generate and print report
    report = scraper.generate_report()
    print(report)
    
    print(f"\nResults saved to:")
    print(f"  - CSV: {csv_file}")
    print(f"  - JSON: {json_file}")
    
    # Print sample results if available
    if results:
        print(f"\nSample result for '{results[0].get('name', 'Unknown')}':")
        sample = results[0]
        for key, value in sample.items():
            if value:  # Only show non-empty values
                print(f"  {key}: {value}")

if __name__ == "__main__":
    main()