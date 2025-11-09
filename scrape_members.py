#!/usr/bin/env python3
"""
Script to search for and extract member information from training provider organizations.
Uses web search to find organization websites, then scrapes member information.
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin, urlparse, quote_plus
import time
import subprocess

# List of organizations to check
ORGANIZATIONS = [
    "Collab Group",
    "HOLEX",
    "Natspec",
    "Independent Training Provider Association",
    "Networks of Providers Community of Practice",
    "ETF Centres for Excellence in SEND",
    "North East Learning Providers",
    "Tees Valley Learning Provider Network",
    "Northumberland Learning Providers Network",
    "Northern Skills Network",
    "Greater Manchester Learning Provider Network",
    "Greater Merseyside Learning Providers Federation",
    "Lancashire Work Based Learning Executive Forum",
    "Cumbria Work Based Learning Provider Forum",
    "Cheshire and Warrington Learning Provider Network",
    "Lancashire Colleges Group",
    "Yorkshire Learning Providers",
    "South Yorkshire Providers Network",
    "Humber Learning Consortium",
    "West Yorkshire Consortium of Colleges",
    "North Yorkshire Provider Network",
    "East Midlands Provider Network",
    "East Midlands Accelerated Apprenticeship Network",
    "D2N2 Provider Network",
    "Leicester and Leicestershire Provider Network",
    "Lincolnshire Provider Network",
    "Birmingham and Solihull Provider Network",
    "Black Country Provider Network",
    "Coventry and Warwickshire Provider Network",
    "Herefordshire and Worcestershire Training Provider Association",
    "Marches Provider Network",
    "Staffordshire and Stoke-on-Trent Provider Network",
    "West Midlands 5G Skills Network",
    "Essex Provider Network",
    "Bedfordshire and Hertfordshire Provider Network",
    "Suffolk Provider Network",
    "Cambridgeshire and Peterborough Provider Network",
    "Norfolk Learning and Skills Provider Network",
    "Eastern Colleges Group",
    "Sussex Council of Training Providers",
    "Kent Association of Training Organisations",
    "ALPS",
    "ALPHI",
    "Thames Valley Berkshire Provider Network",
    "Buckinghamshire Skills Provider Network",
    "Oxfordshire Provider Network",
    "Solent Training Provider Network",
    "Western Training Provider Network",
    "Dorset and Somerset Training Provider Network",
    "Devon and Cornwall Training Provider Network",
    "Gloucestershire and Wiltshire Partnership",
    "Swindon and Wiltshire Provider Network",
    "Somerset Education Business Partnership",
    "Heart of the South West Colleges Partnership",
    "Cornwall and Isles of Scilly Skills Hub",
    "AELP London Strategic Forum",
    "Local London Skills Providers Network",
    "West London Alliance Skills & Employment",
    "South London Partnership Skills",
    "Central London Forward Skills Programmes",
]

def try_common_urls(org_name):
    """Try common URL patterns for UK training provider organizations."""
    # Clean organization name for URL
    org_clean = org_name.lower()
    org_clean = org_clean.replace(' ', '-').replace('&', 'and')
    org_clean = org_clean.replace("'", '').replace(',', '')
    org_clean = re.sub(r'[^a-z0-9-]', '', org_clean)
    
    # Common patterns
    patterns = [
        f"https://www.{org_clean}.org.uk",
        f"https://{org_clean}.org.uk",
        f"https://www.{org_clean}.co.uk",
        f"https://{org_clean}.co.uk",
        f"https://www.{org_clean}.com",
        f"https://{org_clean}.com",
    ]
    
    # Special cases - known URLs or abbreviations
    special_cases = {
        'Collab Group': 'https://www.collabgroup.co.uk',
        'HOLEX': 'https://www.holex.org.uk',
        'Natspec': 'https://www.natspec.org.uk',
        'Independent Training Provider Association': 'https://www.itpa.org.uk',
        'ALPS': 'https://www.alps.org.uk',  # Note: May need verification
        'ALPHI': 'https://www.alphi.org.uk',  # Note: May need verification
        'Yorkshire Learning Providers': 'https://www.ylp.org.uk',
        'Greater Manchester Learning Provider Network': 'https://www.gmlpn.co.uk',
        'Lancashire Colleges Group': 'https://www.lancashirecolleges.ac.uk',
        'West Yorkshire Consortium of Colleges': 'https://www.wycc.ac.uk',
        'Eastern Colleges Group': 'https://www.easterncollegesgroup.ac.uk',
        'Greater Merseyside Learning Providers Federation': 'https://www.gmlpf.org.uk',
        'Northern Skills Network': 'https://www.northernskillsnetwork.co.uk',
        'North East Learning Providers': 'https://www.nelp.org.uk',
        'Tees Valley Learning Provider Network': 'https://www.tvlearningproviders.co.uk',
        'Cheshire and Warrington Learning Provider Network': 'https://www.cwlearningproviders.co.uk',
        'Yorkshire Learning Providers': 'https://www.ylp.org.uk',
        'Humber Learning Consortium': 'https://www.humberlearningconsortium.co.uk',
        'East Midlands Provider Network': 'https://www.empn.org.uk',
        'Birmingham and Solihull Provider Network': 'https://www.bspn.org.uk',
        'Black Country Provider Network': 'https://www.bcpn.org.uk',
        'Essex Provider Network': 'https://www.essexprovidernetwork.co.uk',
        'Sussex Council of Training Providers': 'https://www.sctp.org.uk',
        'Kent Association of Training Organisations': 'https://www.kato.org.uk',
        'Thames Valley Berkshire Provider Network': 'https://www.tvbpnetwork.co.uk',
        'Solent Training Provider Network': 'https://www.solenttrainingproviders.co.uk',
        'Devon and Cornwall Training Provider Network': 'https://www.dctpn.org.uk',
        'AELP London Strategic Forum': 'https://www.aelp.org.uk',
    }
    
    if org_name in special_cases:
        url = special_cases[org_name]
        # Verify URL exists
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code < 400:
                return url
        except:
            pass
    
    # Try common patterns
    for url in patterns:
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code < 400:
                return url
        except:
            continue
    
    return None

def search_duckduckgo(query):
    """Use DuckDuckGo to search and extract first result URL."""
    try:
        # Use DuckDuckGo HTML search
        search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(search_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find result links - DuckDuckGo uses different classes
        results = soup.find_all('a', class_='result__a')
        if not results:
            # Try alternative selectors
            results = soup.find_all('a', href=re.compile(r'^https?://'))
        
        for result in results[:5]:  # Check first 5 results
            href = result.get('href', '')
            if href and ('org.uk' in href or 'co.uk' in href or 'training' in href.lower() or 'provider' in href.lower()):
                # Clean up DuckDuckGo redirect URLs
                if 'duckduckgo.com' in href:
                    continue
                return href
    except Exception as e:
        pass
    
    return None

def find_organization_url(org_name):
    """Find the organization's website URL."""
    # First try common URL patterns
    url = try_common_urls(org_name)
    if url:
        return url
    
    # Then try web search
    queries = [
        f"{org_name} UK",
        f"{org_name} website",
        f'"{org_name}" site:.org.uk',
    ]
    
    for query in queries:
        url = search_duckduckgo(query)
        if url:
            return url
        time.sleep(1)  # Be polite
    
    return None

def extract_member_count(text, soup):
    """Try to extract member count from text or HTML."""
    # Look for patterns like "X members", "X member organizations", etc.
    patterns = [
        r'(\d+)\s+members?',
        r'(\d+)\s+member\s+organizations?',
        r'(\d+)\s+providers?',
        r'(\d+)\s+organizations?',
        r'over\s+(\d+)\s+members?',
        r'more\s+than\s+(\d+)\s+members?',
        r'(\d+)\s+training\s+providers?',
        r'(\d+)\s+colleges?',
        r'(\d+)\s+institutions?',
        r'consisting\s+of\s+(\d+)',
        r'comprising\s+(\d+)',
    ]
    
    text_lower = text.lower()
    found_counts = []
    
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            try:
                count = int(match)
                if 1 <= count <= 10000:  # Reasonable range
                    found_counts.append(count)
            except:
                pass
    
    if found_counts:
        # Return the most common or highest reasonable count
        return max(set(found_counts), key=found_counts.count)
    
    return None

def find_member_list(soup, base_url):
    """Try to find a member list page or section."""
    # Look for links that might lead to member lists
    member_keywords = ['member', 'provider', 'organization', 'network', 'college']
    
    links = soup.find_all('a', href=True)
    for link in links:
        link_text = link.get_text().lower()
        href = link.get('href', '').lower()
        
        if any(keyword in link_text or keyword in href for keyword in member_keywords):
            # Skip common non-member pages
            if any(skip in href for skip in ['contact', 'about', 'home', 'index']):
                continue
            full_url = urljoin(base_url, href)
            return full_url
    
    return None

def extract_member_names(soup):
    """Try to extract member names from HTML."""
    members = []
    
    # Try to find lists
    lists = soup.find_all(['ul', 'ol'])
    for list_elem in lists:
        items = list_elem.find_all('li')
        for item in items:
            text = item.get_text().strip()
            # Filter out navigation items and very short/long text
            if (text and 5 < len(text) < 200 and 
                not text.lower().startswith(('home', 'about', 'contact', 'login'))):
                members.append(text)
    
    # Try to find tables
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header row
            cells = row.find_all(['td', 'th'])
            for cell in cells:
                text = cell.get_text().strip()
                if text and 5 < len(text) < 200:
                    members.append(text)
    
    # Try to find divs with member-like content
    divs = soup.find_all('div', class_=re.compile(r'member|provider|college', re.I))
    for div in divs:
        text = div.get_text().strip()
        if text and 5 < len(text) < 200:
            members.append(text)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_members = []
    for member in members:
        if member.lower() not in seen:
            seen.add(member.lower())
            unique_members.append(member)
    
    return unique_members[:200]  # Limit to first 200

def scrape_organization(org_name, url=None):
    """Scrape member information from an organization's website."""
    if not url:
        print(f"  Searching for {org_name} website...")
        url = find_organization_url(org_name)
        if not url:
            return {
                'organization': org_name,
                'url': None,
                'member_count': None,
                'members': [],
                'status': 'no_url_found'
            }
    
    print(f"  Found URL: {url}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        
        # Try to extract member count from main page
        member_count = extract_member_count(text, soup)
        
        # Try to find and scrape member list page
        members = []
        member_list_url = find_member_list(soup, url)
        
        if member_list_url:
            print(f"  Found member list page: {member_list_url}")
            try:
                member_response = requests.get(member_list_url, headers=headers, timeout=15)
                member_soup = BeautifulSoup(member_response.content, 'html.parser')
                members = extract_member_names(member_soup)
                if members:
                    print(f"  Extracted {len(members)} member names")
            except Exception as e:
                print(f"  Could not scrape member list: {e}")
        
        # If no member list found, try to extract from main page
        if not members:
            members = extract_member_names(soup)
            if members:
                print(f"  Extracted {len(members)} member names from main page")
        
        return {
            'organization': org_name,
            'url': url,
            'member_count': member_count,
            'members': members,
            'status': 'success'
        }
        
    except Exception as e:
        return {
            'organization': org_name,
            'url': url,
            'member_count': None,
            'members': [],
            'status': f'error: {str(e)}'
        }

def main():
    """Main function to scrape all organizations."""
    results = []
    
    print("="*70)
    print("SCRAPING ORGANIZATION MEMBER INFORMATION")
    print("="*70)
    print(f"Total organizations: {len(ORGANIZATIONS)}\n")
    
    for i, org in enumerate(ORGANIZATIONS, 1):
        print(f"\n[{i}/{len(ORGANIZATIONS)}] Processing: {org}")
        result = scrape_organization(org)
        results.append(result)
        
        if result['member_count']:
            print(f"  ✓ Member count: {result['member_count']}")
        if result['members']:
            print(f"  ✓ Found {len(result['members'])} member names")
        if result['status'] != 'success':
            print(f"  ⚠ Status: {result['status']}")
        
        time.sleep(2)  # Be polite to servers
    
    # Save results
    with open('member_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    for result in results:
        org = result['organization']
        if result['member_count']:
            print(f"{org}: {result['member_count']} members")
        elif result['members']:
            print(f"{org}: {len(result['members'])} members (list found)")
        else:
            print(f"{org}: No member information found")
    
    print(f"\nDetailed results saved to: member_results.json")

if __name__ == '__main__':
    main()
