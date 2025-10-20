#!/usr/bin/env python3
"""
Investigate the actual pagination mechanism on Ofsted website
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def investigate_ofsted_pagination():
    base_url = "https://reports.ofsted.gov.uk"
    search_url = "https://reports.ofsted.gov.uk/search?q=&location=&lat=&lon=&radius=&level_1_types=1&level_2_types%5B%5D=3"
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    print("Investigating Ofsted search pagination...")
    print(f"Base URL: {search_url}")
    
    # Get the first page
    response = session.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print("\n1. Looking for pagination elements...")
    
    # Look for pagination-related elements
    pagination_selectors = [
        '.pagination',
        '.pager', 
        '.page-numbers',
        '[class*="page"]',
        '[class*="pagination"]',
        'nav[aria-label*="page"]',
        '.next',
        '.previous'
    ]
    
    found_pagination = False
    for selector in pagination_selectors:
        elements = soup.select(selector)
        if elements:
            print(f"   Found pagination elements with selector '{selector}':")
            for elem in elements[:3]:  # Show first 3
                print(f"     {elem.name}: {elem.get('class', [])} - {elem.get_text(strip=True)[:100]}")
            found_pagination = True
    
    if not found_pagination:
        print("   No standard pagination elements found")
    
    print("\n2. Looking for JavaScript/AJAX pagination...")
    
    # Look for JavaScript that might handle pagination
    scripts = soup.find_all('script')
    pagination_js_found = False
    
    for script in scripts:
        if script.string:
            script_text = script.string
            if any(keyword in script_text.lower() for keyword in ['page', 'pagination', 'ajax', 'load', 'search']):
                print(f"   Found relevant JavaScript (first 200 chars):")
                print(f"     {script_text[:200]}...")
                pagination_js_found = True
                break
    
    if not pagination_js_found:
        print("   No obvious pagination JavaScript found")
    
    print("\n3. Analyzing page structure...")
    
    # Look for the results container
    results_containers = [
        '.search-results',
        '.results',
        '[class*="result"]',
        '.provider-list',
        '.search-list'
    ]
    
    results_found = False
    for selector in results_containers:
        container = soup.select_one(selector)
        if container:
            print(f"   Found results container: {selector}")
            print(f"     Contains {len(container.find_all('a', href=re.compile(r'/provider/')))} provider links")
            results_found = True
            break
    
    if not results_found:
        print("   No obvious results container found")
    
    print("\n4. Looking for 'Load More' or infinite scroll...")
    
    load_more_selectors = [
        '[class*="load"]',
        '[class*="more"]', 
        '[data-load]',
        'button[onclick*="load"]',
        'a[href*="more"]'
    ]
    
    load_more_found = False
    for selector in load_more_selectors:
        elements = soup.select(selector)
        if elements:
            print(f"   Found potential load more elements: {selector}")
            for elem in elements[:2]:
                print(f"     {elem.name}: {elem.get_text(strip=True)}")
            load_more_found = True
    
    if not load_more_found:
        print("   No 'Load More' buttons found")
    
    print("\n5. Checking if results are limited...")
    
    # Count actual provider links on the page
    provider_links = soup.find_all('a', href=re.compile(r'/provider/'))
    print(f"   Found {len(provider_links)} provider links on first page")
    
    # Look for text indicating total results
    page_text = soup.get_text()
    result_patterns = [
        r'(\d+)\s+results?',
        r'showing\s+(\d+)\s+of\s+(\d+)',
        r'(\d{1,3}(?:,\d{3})*)\s+providers?\s+found',
    ]
    
    for pattern in result_patterns:
        matches = re.findall(pattern, page_text, re.IGNORECASE)
        if matches:
            print(f"   Result count pattern found: {matches}")
    
    print("\n6. Testing alternative URL patterns...")
    
    # Test different URL patterns that might work
    test_urls = [
        f"{search_url}&page=2",
        f"{search_url}&p=2", 
        f"{search_url}&offset=10",
        f"{search_url}&start=10",
        f"{search_url}&from=10",
        f"{search_url}&skip=10"
    ]
    
    for test_url in test_urls:
        try:
            print(f"   Testing: {test_url}")
            response = session.get(test_url, timeout=10)
            test_soup = BeautifulSoup(response.text, 'html.parser')
            test_links = test_soup.find_all('a', href=re.compile(r'/provider/'))
            
            # Compare with first page links
            first_page_urls = [link.get('href') for link in provider_links]
            test_page_urls = [link.get('href') for link in test_links]
            
            if test_page_urls != first_page_urls:
                print(f"     SUCCESS! Different providers found: {len(test_links)} links")
                print(f"     Sample URLs: {test_page_urls[:3]}")
                return test_url  # Return the working URL pattern
            else:
                print(f"     Same providers as page 1: {len(test_links)} links")
                
        except Exception as e:
            print(f"     Error: {e}")
    
    print("\n7. Final analysis...")
    print("   The website appears to show only the first 10 results")
    print("   This might be intentional limitation or require special access")
    
    return None

if __name__ == "__main__":
    working_pattern = investigate_ofsted_pagination()
    if working_pattern:
        print(f"\nWorking pagination pattern found: {working_pattern}")
    else:
        print("\nNo working pagination pattern found")
        print("The website may only show the first 10 results publicly")