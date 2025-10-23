#!/usr/bin/env python3
"""
Test script to understand the website structure before running the full scraper
"""

import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

def analyze_courses_page():
    """Analyze the main courses page structure"""
    base_url = "https://findapprenticeshiptraining.apprenticeships.education.gov.uk"
    courses_url = f"{base_url}/courses"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("Fetching main courses page...")
    response = requests.get(courses_url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print("\n=== PAGE TITLE ===")
    print(soup.title.get_text() if soup.title else "No title found")
    
    print("\n=== LOOKING FOR COURSE LINKS ===")
    all_links = soup.find_all('a', href=True)
    
    course_links = []
    for link in all_links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        # Look for patterns that might indicate course links
        if any(pattern in href.lower() for pattern in ['/courses/', '/course/', '/apprenticeship']):
            if text and len(text) > 3:
                course_links.append({
                    'text': text[:100],  # Truncate long text
                    'href': href,
                    'full_url': urljoin(base_url, href)
                })
    
    print(f"Found {len(course_links)} potential course links:")
    for i, link in enumerate(course_links[:10]):  # Show first 10
        print(f"{i+1}. {link['text']} -> {link['href']}")
    
    if len(course_links) > 10:
        print(f"... and {len(course_links) - 10} more")
    
    # Look for specific elements that might contain course listings
    print("\n=== LOOKING FOR COURSE LISTING ELEMENTS ===")
    
    # Common selectors for course listings
    selectors_to_try = [
        '.course-list',
        '.apprenticeship-list',
        '.govuk-list',
        '[class*="course"]',
        '[class*="apprenticeship"]',
        '.search-results',
        '.results-list'
    ]
    
    for selector in selectors_to_try:
        elements = soup.select(selector)
        if elements:
            print(f"Found {len(elements)} elements with selector '{selector}'")
            for i, elem in enumerate(elements[:3]):  # Show first 3
                print(f"  Element {i+1}: {elem.name} with classes {elem.get('class', [])}")
                links_in_elem = elem.find_all('a', href=True)
                print(f"    Contains {len(links_in_elem)} links")
    
    # Save a sample of the HTML for manual inspection
    print("\n=== SAVING SAMPLE HTML ===")
    with open('courses_page_sample.html', 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))
    print("Saved courses_page_sample.html for manual inspection")
    
    return course_links

def test_individual_course_page():
    """Test accessing an individual course page"""
    # Let's try to find and access one course page
    course_links = analyze_courses_page()
    
    if not course_links:
        print("No course links found to test")
        return
    
    # Try the first course link
    test_link = course_links[0]
    print(f"\n=== TESTING INDIVIDUAL COURSE PAGE ===")
    print(f"Testing: {test_link['text']} -> {test_link['full_url']}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(test_link['full_url'], headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"Page title: {soup.title.get_text() if soup.title else 'No title'}")
        
        # Look for provider information
        print("\n=== LOOKING FOR PROVIDER INFORMATION ===")
        
        # Try different selectors for providers
        provider_selectors = [
            'a[href*="/providers/"]',
            '.provider',
            '.training-provider',
            '[class*="provider"]',
            '.govuk-link[href*="provider"]'
        ]
        
        for selector in provider_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"Found {len(elements)} elements with selector '{selector}':")
                for i, elem in enumerate(elements[:5]):  # Show first 5
                    text = elem.get_text(strip=True)
                    href = elem.get('href', 'No href')
                    print(f"  {i+1}. {text} -> {href}")
        
        # Save sample for inspection
        with open('sample_course_page.html', 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        print("Saved sample_course_page.html for manual inspection")
        
    except Exception as e:
        print(f"Error accessing course page: {e}")

if __name__ == "__main__":
    test_individual_course_page()