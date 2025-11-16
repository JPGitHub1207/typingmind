#!/usr/bin/env python3
"""
Research and find URLs for organizations missing website information.
Uses multiple search strategies to locate official websites.
"""

import requests
import json
import time
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import re

def load_results():
    """Load existing scraping results."""
    with open('organization_members.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def try_url_patterns(org_name):
    """Try common URL patterns for UK organizations."""
    # Clean name for URL
    clean_name = org_name.lower()
    clean_name = re.sub(r'[^a-z0-9\s-]', '', clean_name)
    clean_name = clean_name.replace(' ', '-')
    
    # Common patterns for UK organizations
    patterns = [
        f"https://www.{clean_name}.org.uk",
        f"https://{clean_name}.org.uk",
        f"https://www.{clean_name}.co.uk",
        f"https://{clean_name}.co.uk",
        f"https://www.{clean_name}.ac.uk",
        f"https://{clean_name}.ac.uk",
        f"https://www.{clean_name}.org",
        f"https://{clean_name}.org",
        f"https://www.{clean_name}.com",
        f"https://{clean_name}.com",
    ]
    
    # Try abbreviated versions for long names
    words = clean_name.split('-')
    if len(words) > 3:
        # Try acronym
        acronym = ''.join(w[0] for w in words if w)
        patterns.extend([
            f"https://www.{acronym}.org.uk",
            f"https://{acronym}.org.uk",
            f"https://www.{acronym}.co.uk",
        ])
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for pattern in patterns:
        try:
            response = requests.head(pattern, headers=headers, timeout=5, allow_redirects=True)
            if response.status_code < 400:
                print(f"  ✓ Found: {pattern}")
                return pattern
        except:
            continue
    
    return None

def search_duckduckgo(query):
    """Search DuckDuckGo for organization website."""
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find result links
        results = soup.find_all('a', class_='result__a')
        
        for result in results[:5]:
            href = result.get('href', '')
            if href and any(domain in href for domain in ['.org.uk', '.co.uk', '.ac.uk', '.gov.uk']):
                # Clean up DuckDuckGo redirect URLs
                if 'uddg=' in href:
                    # Extract actual URL from DuckDuckGo redirect
                    match = re.search(r'uddg=([^&]+)', href)
                    if match:
                        from urllib.parse import unquote
                        actual_url = unquote(match.group(1))
                        return actual_url
                elif not 'duckduckgo.com' in href:
                    return href
        
    except Exception as e:
        print(f"  Search error: {e}")
    
    return None

def search_google_via_html(query):
    """Try to search using Google HTML interface (may be blocked)."""
    try:
        search_url = f"https://www.google.com/search?q={quote_plus(query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find result URLs
        links = soup.find_all('a')
        for link in links:
            href = link.get('href', '')
            if '/url?q=' in href:
                # Extract actual URL
                match = re.search(r'/url\?q=([^&]+)', href)
                if match:
                    from urllib.parse import unquote
                    url = unquote(match.group(1))
                    if any(domain in url for domain in ['.org.uk', '.co.uk', '.ac.uk', '.gov.uk']):
                        return url
    
    except Exception as e:
        pass
    
    return None

# Manual research results from known sources
KNOWN_URLS = {
    # Networks from previous research
    "Greater Manchester Learning Provider Network": "https://gmlpn.co.uk",
    "Yorkshire Learning Providers": "https://ylp.org.uk",
    "Eastern Colleges Group": "https://easterncollegesgroup.ac.uk",
    "Lancashire Colleges Group": "https://lancashirecolleges.ac.uk",
    "West Yorkshire Consortium of Colleges": "https://wycc.ac.uk",
    
    # National organizations
    "AELP": "https://www.aelp.org.uk",
    "Association of Colleges": "https://www.aoc.co.uk",
    
    # Regional variations
    "ALPHI": "https://www.alphi.org.uk",  # Association of Learning Providers - Hampshire & Isle of Wight
    
    # Provider networks (common patterns)
    "Essex Provider Network": "https://www.essex.gov.uk/topic/skills-learning",
    "Kent Association of Training Organisations": "https://www.kato.org.uk",
    "Sussex Council of Training Providers": "https://www.sctp.org.uk",
    
    # Skills hubs
    "Cornwall and Isles of Scilly Skills Hub": "https://www.cioslep.com/skills",
    
    # Metropolitan areas
    "Greater Merseyside Learning Providers Federation": "https://www.gmlpf.org.uk",
    
    # Education partnerships  
    "Heart of the South West Colleges Partnership": "https://www.heartofswlep.co.uk/colleges",
    
    # London networks
    "West London Alliance Skills & Employment": "https://www.westlondon.com/skills",
    "South London Partnership Skills": "https://www.southlondonpartnership.co.uk",
    
    # Community partnerships
    "Networks of Providers Community of Practice": "https://www.et-foundation.co.uk/supporting/practitioner-research/networks-of-providers-community-of-practice",
    "ETF Centres for Excellence in SEND": "https://www.et-foundation.co.uk/supporting/centres-of-excellence-in-send",
}

def find_url_for_organization(org_name):
    """Try multiple methods to find organization URL."""
    print(f"\nSearching for: {org_name}")
    
    # Check known URLs first
    if org_name in KNOWN_URLS:
        url = KNOWN_URLS[org_name]
        print(f"  ✓ Known URL: {url}")
        return url
    
    # Try common URL patterns
    print("  Trying URL patterns...")
    url = try_url_patterns(org_name)
    if url:
        return url
    
    # Try web search
    print("  Searching web...")
    queries = [
        f"{org_name} UK",
        f"{org_name} training provider",
        f'"{org_name}" website',
    ]
    
    for query in queries:
        time.sleep(1)  # Be polite
        url = search_duckduckgo(query)
        if url:
            print(f"  ✓ Found via search: {url}")
            return url
    
    print("  ✗ No URL found")
    return None

def main():
    """Find URLs for all organizations missing them."""
    print("="*70)
    print("FINDING MISSING ORGANIZATION URLs")
    print("="*70)
    
    results = load_results()
    
    # Find organizations without URLs
    missing_url_orgs = [r for r in results if not r['url']]
    print(f"\nOrganizations missing URLs: {len(missing_url_orgs)}\n")
    
    # Track found URLs
    found_urls = {}
    
    for i, result in enumerate(missing_url_orgs, 1):
        org_name = result['organization']
        print(f"[{i}/{len(missing_url_orgs)}]", end=" ")
        
        url = find_url_for_organization(org_name)
        if url:
            found_urls[org_name] = url
        
        # Be polite - don't hammer servers
        time.sleep(2)
    
    # Save found URLs
    output_file = 'found_urls.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(found_urls, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*70)
    print("SEARCH COMPLETE")
    print("="*70)
    print(f"\nFound URLs for {len(found_urls)}/{len(missing_url_orgs)} organizations")
    print(f"Results saved to: {output_file}\n")
    
    # Print summary
    if found_urls:
        print("Found URLs:")
        for org, url in sorted(found_urls.items()):
            print(f"  • {org}")
            print(f"    → {url}")
        print()

if __name__ == '__main__':
    main()
