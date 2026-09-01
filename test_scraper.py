#!/usr/bin/env python3
"""
Test the scraper on a small sample to verify it works
"""

import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import time

def test_scraper_sample():
    """Test the scraper on a few courses"""
    base_url = "https://findapprenticeshiptraining.apprenticeships.education.gov.uk"
    courses_url = f"{base_url}/courses"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("Testing scraper on sample courses...")
    
    # Get main courses page
    response = requests.get(courses_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract first few course links
    course_links = soup.select('a.das-search-results__link[href^="/courses/"]')
    
    # Filter out provider links
    courses = []
    for link in course_links:
        href = link.get('href', '')
        if '/providers' not in href:
            text = link.get_text(strip=True)
            course_id = href.split('/')[-1]
            courses.append({
                'name': text,
                'url': urljoin(base_url, href),
                'course_id': course_id,
                'providers_url': f"{base_url}/courses/{course_id}/providers"
            })
    
    print(f"Found {len(courses)} courses. Testing first 3...")
    
    # Test first 3 courses
    for i, course in enumerate(courses[:3]):
        print(f"\n=== Testing Course {i+1}: {course['name']} ===")
        print(f"Course URL: {course['url']}")
        print(f"Providers URL: {course['providers_url']}")
        
        try:
            # Get providers page
            response = requests.get(course['providers_url'], headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print(f"Page title: {soup.title.get_text() if soup.title else 'No title'}")
            
            # Look for providers using various selectors
            selectors_to_try = [
                'a[href*="/providers/"]',
                '.provider-name',
                '.training-provider',
                '.govuk-list li a',
                '.das-search-results__link',
                'h2 a',
                'h3 a',
                '.govuk-heading-m a',
                '.govuk-heading-s a'
            ]
            
            providers_found = []
            
            for selector in selectors_to_try:
                elements = soup.select(selector)
                if elements:
                    print(f"  Found {len(elements)} elements with selector '{selector}':")
                    for j, elem in enumerate(elements[:5]):  # Show first 5
                        text = elem.get_text(strip=True)
                        href = elem.get('href', 'No href')
                        print(f"    {j+1}. {text} -> {href}")
                        
                        # Filter for actual providers
                        if (text and len(text) > 2 and len(text) < 100 and
                            not any(skip in text.lower() for skip in ['view', 'back', 'search', 'filter'])):
                            providers_found.append(text)
                    
                    if elements:
                        break  # Use first successful selector
            
            print(f"  Total unique providers found: {len(set(providers_found))}")
            
            # Save sample HTML for manual inspection
            with open(f'sample_providers_page_{i+1}.html', 'w', encoding='utf-8') as f:
                f.write(str(soup.prettify()))
            
            time.sleep(1)  # Be respectful
            
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    test_scraper_sample()