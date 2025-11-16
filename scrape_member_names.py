#!/usr/bin/env python3
"""
Script to scrape member names from membership organization websites.
Reads organizations from training-provider-networks-and-organisations.md
and attempts to extract member names from each organization's website.
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import urljoin, urlparse, quote_plus
import time
from typing import List, Dict, Optional

# Headers to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

def parse_organizations_from_markdown(file_path: str) -> List[Dict[str, str]]:
    """Parse organizations and their websites from the markdown file."""
    organizations = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for numbered list items with organization names
        org_match = re.match(r'^\d+\.\s+\*\*(.+?)\*\*(?:\s+\([^)]+\))?', line)
        if org_match:
            org_name = org_match.group(1).strip()
            website = None
            
            # Look ahead for website line
            j = i + 1
            while j < len(lines) and j < i + 10:  # Check next 10 lines
                website_match = re.search(r'^\s+- Website:\s+(https?://[^\s]+)', lines[j])
                if website_match:
                    website = website_match.group(1).strip()
                    break
                # Stop if we hit another numbered item
                if re.match(r'^\d+\.\s+\*\*', lines[j]):
                    break
                j += 1
            
            if website:
                organizations.append({
                    'name': org_name,
                    'website': website
                })
        i += 1
    
    return organizations

def find_member_list_urls(soup: BeautifulSoup, base_url: str) -> List[str]:
    """Find potential URLs that might contain member lists."""
    member_urls = []
    
    # Keywords that might indicate member lists
    member_keywords = [
        'member', 'members', 'membership', 'directory', 'network',
        'colleges', 'providers', 'institutions', 'organizations',
        'partners', 'affiliates', 'who-we-are', 'our-members'
    ]
    
    # Find all links
    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link.get('href', '').lower()
        text = link.get_text().lower().strip()
        
        # Check if link text or href contains member keywords
        if any(keyword in href or keyword in text for keyword in member_keywords):
            # Skip common non-member pages
            skip_keywords = ['contact', 'about-us', 'home', 'index', 'login', 'sign-up', 'join']
            if not any(skip in href for skip in skip_keywords):
                full_url = urljoin(base_url, link.get('href'))
                if full_url not in member_urls:
                    member_urls.append(full_url)
    
    return member_urls[:10]  # Limit to first 10 potential URLs

def extract_member_names_from_page(soup: BeautifulSoup, org_name: str) -> List[str]:
    """Extract member names from a page."""
    members = []
    
    # Remove script and style elements
    for script in soup(["script", "style", "nav", "header", "footer"]):
        script.decompose()
    
    # Strategy 1: Look for lists (ul, ol) with member-like content
    lists = soup.find_all(['ul', 'ol'])
    for list_elem in lists:
        items = list_elem.find_all('li', recursive=False)
        for item in items:
            text = item.get_text().strip()
            # Clean up text
            text = re.sub(r'\s+', ' ', text)
            text = text.replace('\n', ' ').replace('\r', '')
            
            # Filter criteria
            if (text and 
                10 < len(text) < 300 and  # Reasonable length
                not text.lower().startswith(('home', 'about', 'contact', 'login', 'sign', 'join', 'read more', 'learn more')) and
                not re.match(r'^[\d\s\-\(\)]+$', text) and  # Not just numbers/punctuation
                not text.lower() in ['skip to content', 'menu', 'search', 'close']):
                members.append(text)
    
    # Strategy 2: Look for tables with member data
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header
            cells = row.find_all(['td', 'th'])
            for cell in cells:
                text = cell.get_text().strip()
                text = re.sub(r'\s+', ' ', text)
                if (text and 
                    10 < len(text) < 300 and
                    not text.lower().startswith(('home', 'about', 'contact'))):
                    members.append(text)
    
    # Strategy 3: Look for divs with member-related classes
    member_divs = soup.find_all('div', class_=re.compile(r'member|provider|college|institution|organization', re.I))
    for div in member_divs:
        # Get direct text children only
        text = ' '.join([t.strip() for t in div.stripped_strings])
        text = re.sub(r'\s+', ' ', text)
        if (text and 
            10 < len(text) < 300 and
            not text.lower().startswith(('home', 'about', 'contact'))):
            members.append(text)
    
    # Strategy 4: Look for links that might be member names
    links = soup.find_all('a', href=True)
    for link in links:
        text = link.get_text().strip()
        href = link.get('href', '').lower()
        
        # If link looks like it goes to a member page
        if any(kw in href for kw in ['member', 'college', 'provider', 'institution']):
            text = re.sub(r'\s+', ' ', text)
            if (text and 
                10 < len(text) < 300 and
                not text.lower().startswith(('home', 'about', 'contact', 'view', 'read', 'more'))):
                members.append(text)
    
    # Clean and deduplicate
    cleaned_members = []
    seen = set()
    
    for member in members:
        # Remove common prefixes/suffixes
        member_clean = member.strip()
        member_clean = re.sub(r'^(view|read|see|learn|more|about)\s+', '', member_clean, flags=re.I)
        member_clean = re.sub(r'\s+(view|read|see|learn|more|about)$', '', member_clean, flags=re.I)
        
        # Skip if too short or looks like navigation
        if (len(member_clean) < 10 or 
            member_clean.lower() in seen or
            member_clean.lower().startswith(('http', 'www.', 'mailto:'))):
            continue
        
        # Normalize for comparison
        member_lower = member_clean.lower()
        if member_lower not in seen:
            seen.add(member_lower)
            cleaned_members.append(member_clean)
    
    return cleaned_members[:500]  # Limit to 500 members

def scrape_organization_members(org_name: str, website: str) -> Dict:
    """Scrape member names from an organization's website."""
    print(f"\n{'='*70}")
    print(f"Processing: {org_name}")
    print(f"Website: {website}")
    print(f"{'='*70}")
    
    result = {
        'organization': org_name,
        'website': website,
        'members': [],
        'member_count': 0,
        'status': 'pending',
        'pages_scraped': []
    }
    
    try:
        # Fetch main page
        print("  Fetching main page...")
        response = requests.get(website, headers=HEADERS, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        result['pages_scraped'].append(website)
        
        # Try to extract members from main page
        print("  Extracting members from main page...")
        members = extract_member_names_from_page(soup, org_name)
        if members:
            print(f"  Found {len(members)} potential members on main page")
            result['members'].extend(members)
        
        # Try to find member list pages
        print("  Looking for member list pages...")
        member_urls = find_member_list_urls(soup, website)
        
        for url in member_urls[:5]:  # Try up to 5 member list pages
            try:
                print(f"  Fetching: {url}")
                time.sleep(1)  # Be polite
                member_response = requests.get(url, headers=HEADERS, timeout=15)
                member_response.raise_for_status()
                
                member_soup = BeautifulSoup(member_response.content, 'html.parser')
                page_members = extract_member_names_from_page(member_soup, org_name)
                
                if page_members:
                    print(f"  Found {len(page_members)} members on this page")
                    result['members'].extend(page_members)
                    result['pages_scraped'].append(url)
            except Exception as e:
                print(f"  Error fetching {url}: {e}")
                continue
        
        # Remove duplicates while preserving order
        seen = set()
        unique_members = []
        for member in result['members']:
            member_lower = member.lower().strip()
            if member_lower and member_lower not in seen:
                seen.add(member_lower)
                unique_members.append(member)
        
        result['members'] = unique_members
        result['member_count'] = len(unique_members)
        result['status'] = 'success'
        
        print(f"\n  ✓ Successfully scraped {result['member_count']} unique members")
        
    except requests.exceptions.RequestException as e:
        result['status'] = f'error: {str(e)}'
        print(f"  ✗ Error: {e}")
    except Exception as e:
        result['status'] = f'error: {str(e)}'
        print(f"  ✗ Unexpected error: {e}")
    
    return result

def save_member_names_file(org_name: str, members: List[str], output_dir: str = 'member_names'):
    """Save member names to a text file."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a safe filename from organization name
    safe_name = re.sub(r'[^\w\s-]', '', org_name)
    safe_name = re.sub(r'[-\s]+', '_', safe_name)
    filename = f"{safe_name}_MEMBER_NAMES.txt"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"{org_name} - Member Names ({len(members)} members)\n")
        f.write("="*70 + "\n\n")
        
        if members:
            for i, member in enumerate(members, 1):
                f.write(f"{i}. {member}\n")
        else:
            f.write("No member names found.\n")
        
        f.write(f"\n\nSource: Extracted from organization website")
    
    print(f"  Saved to: {filepath}")
    return filepath

def main():
    """Main function."""
    print("="*70)
    print("MEMBERSHIP ORGANIZATION MEMBER NAME SCRAPER")
    print("="*70)
    
    # Parse organizations from markdown file
    md_file = 'training-provider-networks-and-organisations.md'
    if not os.path.exists(md_file):
        print(f"Error: {md_file} not found!")
        return
    
    print(f"\nReading organizations from {md_file}...")
    organizations = parse_organizations_from_markdown(md_file)
    print(f"Found {len(organizations)} organizations with websites")
    
    # Scrape members for each organization
    results = []
    
    for i, org in enumerate(organizations, 1):
        print(f"\n[{i}/{len(organizations)}]")
        result = scrape_organization_members(org['name'], org['website'])
        results.append(result)
        
        # Save individual member names file if members found
        if result['members']:
            save_member_names_file(org['name'], result['members'])
        
        # Be polite - wait between requests
        if i < len(organizations):
            print("\n  Waiting 3 seconds before next organization...")
            time.sleep(3)
    
    # Save JSON results
    json_file = 'member_names_results.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n\nResults saved to: {json_file}")
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    successful = [r for r in results if r['members']]
    print(f"\nOrganizations with members found: {len(successful)}/{len(results)}")
    
    for result in sorted(successful, key=lambda x: x['member_count'], reverse=True):
        print(f"  {result['organization']}: {result['member_count']} members")
    
    print(f"\nTotal organizations processed: {len(results)}")
    print(f"Total members found: {sum(r['member_count'] for r in results)}")

if __name__ == '__main__':
    main()
