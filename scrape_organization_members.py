#!/usr/bin/env python3
"""
Enhanced script to scrape member names from training provider membership organizations.
Focuses on extracting actual member names with improved detection and filtering.
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from urllib.parse import urljoin, quote_plus
from typing import List, Dict, Optional
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
        logging.StreamHandler()
    ]
)

# List of 60 organizations to scrape
ORGANIZATIONS = {
    "Collab Group": "https://www.collabgroup.co.uk",
    "HOLEX": "https://www.holex.org.uk",
    "Natspec": "https://www.natspec.org.uk",
    "Independent Training Provider Association": "https://www.itpa.org.uk",
    "Networks of Providers Community of Practice": None,
    "ETF Centres for Excellence in SEND": None,
    "North East Learning Providers": "https://www.nelp.org.uk",
    "Tees Valley Learning Provider Network": None,
    "Northumberland Learning Providers Network": None,
    "Northern Skills Network": None,
    "Greater Manchester Learning Provider Network": None,
    "Greater Merseyside Learning Providers Federation": None,
    "Lancashire Work Based Learning Executive Forum": None,
    "Cumbria Work Based Learning Provider Forum": None,
    "Cheshire and Warrington Learning Provider Network": None,
    "Lancashire Colleges Group": "https://www.lancashirecolleges.ac.uk",
    "Yorkshire Learning Providers": "https://www.ylp.org.uk",
    "South Yorkshire Providers Network": None,
    "Humber Learning Consortium": None,
    "West Yorkshire Consortium of Colleges": "https://www.wycc.ac.uk",
    "North Yorkshire Provider Network": None,
    "East Midlands Provider Network": None,
    "East Midlands Accelerated Apprenticeship Network": None,
    "D2N2 Provider Network": None,
    "Leicester and Leicestershire Provider Network": None,
    "Lincolnshire Provider Network": None,
    "Birmingham and Solihull Provider Network": None,
    "Black Country Provider Network": None,
    "Coventry and Warwickshire Provider Network": None,
    "Herefordshire and Worcestershire Training Provider Association": None,
    "Marches Provider Network": None,
    "Staffordshire and Stoke-on-Trent Provider Network": None,
    "West Midlands 5G Skills Network": None,
    "Essex Provider Network": None,
    "Bedfordshire and Hertfordshire Provider Network": None,
    "Suffolk Provider Network": None,
    "Cambridgeshire and Peterborough Provider Network": None,
    "Norfolk Learning and Skills Provider Network": None,
    "Eastern Colleges Group": "https://www.easterncollegesgroup.ac.uk",
    "Sussex Council of Training Providers": None,
    "Kent Association of Training Organisations": "https://www.kato.org.uk",
    "ALPS": None,
    "ALPHI": None,
    "Thames Valley Berkshire Provider Network": None,
    "Buckinghamshire Skills Provider Network": None,
    "Oxfordshire Provider Network": None,
    "Solent Training Provider Network": None,
    "Western Training Provider Network": None,
    "Dorset and Somerset Training Provider Network": None,
    "Devon and Cornwall Training Provider Network": None,
    "Gloucestershire and Wiltshire Partnership": None,
    "Swindon and Wiltshire Provider Network": None,
    "Somerset Education Business Partnership": None,
    "Heart of the South West Colleges Partnership": None,
    "Cornwall and Isles of Scilly Skills Hub": None,
    "AELP London Strategic Forum": "https://www.aelp.org.uk",
    "Local London Skills Providers Network": None,
    "West London Alliance Skills & Employment": None,
    "South London Partnership Skills": None,
    "Central London Forward Skills Programmes": None,
}

# Navigation and non-member keywords to filter out
NAVIGATION_KEYWORDS = [
    'home', 'about', 'contact', 'login', 'register', 'news', 'events', 'blog',
    'privacy', 'terms', 'cookies', 'sitemap', 'search', 'menu', 'navigation',
    'footer', 'header', 'skip', 'accessibility', 'copyright', 'all rights reserved',
    'who we are', 'what we do', 'our mission', 'our vision', 'policy', 'governance',
    'join us', 'membership benefits', 'member benefits', 'joining', 'subscribe',
    'social media', 'twitter', 'facebook', 'linkedin', 'youtube', 'instagram'
]

def get_headers():
    """Return headers for HTTP requests."""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

def is_navigation_text(text: str) -> bool:
    """Check if text is likely navigation/header/footer text."""
    text_lower = text.lower().strip()
    
    # Check against navigation keywords
    if any(keyword in text_lower for keyword in NAVIGATION_KEYWORDS):
        return True
    
    # Too short or too long
    if len(text) < 10 or len(text) > 300:
        return True
    
    # Contains common navigation patterns
    if text_lower.startswith(('home', 'about', 'contact', 'login', '©', 'copyright')):
        return True
    
    return False

def is_likely_member_name(text: str) -> bool:
    """Check if text is likely an actual member organization name."""
    text = text.strip()
    
    # Filter out empty or too short
    if len(text) < 5:
        return False
    
    # Filter out navigation text
    if is_navigation_text(text):
        return False
    
    # Filter out URLs
    if text.startswith('http') or 'www.' in text:
        return False
    
    # Filter out email addresses
    if '@' in text and '.' in text:
        return False
    
    # Filter out common non-member text patterns
    non_member_patterns = [
        r'^\d+$',  # Just numbers
        r'^[^a-zA-Z]+$',  # No letters
        r'click here',
        r'read more',
        r'find out',
        r'learn more',
        r'view all',
        r'see all',
        r'show more',
    ]
    
    text_lower = text.lower()
    for pattern in non_member_patterns:
        if re.search(pattern, text_lower):
            return False
    
    # Likely member name indicators
    member_indicators = [
        'college', 'council', 'university', 'education', 'learning', 'training',
        'academy', 'institute', 'centre', 'center', 'school', 'borough', 'city',
        'county', 'metropolitan', 'trust', 'group', 'association', 'ltd', 'limited',
        'cic', 'partnership', 'consortium', 'network', 'provider', 'service'
    ]
    
    # If it contains member indicators, it's likely a member
    if any(indicator in text_lower for indicator in member_indicators):
        return True
    
    # If it has a mix of words (not just one word) and looks like an organization name
    words = text.split()
    if len(words) >= 2 and not text_lower.startswith(('the ', 'our ', 'your ')):
        return True
    
    return False

def find_member_pages(soup: BeautifulSoup, base_url: str) -> List[str]:
    """Find links that might contain member lists."""
    member_urls = []
    
    # Look for links with member-related keywords
    member_link_keywords = [
        'member', 'members', 'membership', 'provider', 'providers', 'partner', 'partners',
        'college', 'colleges', 'organisation', 'organization', 'network', 'directory'
    ]
    
    links = soup.find_all('a', href=True)
    for link in links:
        href = link.get('href', '').lower()
        text = link.get_text().lower().strip()
        
        # Skip obvious non-member pages
        skip_keywords = ['login', 'contact', 'about-us', 'news', 'events', 'blog', 'join', 'careers']
        if any(skip in href for skip in skip_keywords):
            continue
        
        # Check if link text or URL contains member keywords
        if any(keyword in text or keyword in href for keyword in member_link_keywords):
            full_url = urljoin(base_url, link.get('href'))
            if full_url not in member_urls and full_url.startswith('http'):
                member_urls.append(full_url)
    
    return member_urls[:10]  # Limit to first 10 potential member pages

def extract_members_from_page(soup: BeautifulSoup, url: str) -> List[str]:
    """Extract member names from a page."""
    members = []
    
    logging.info(f"    Extracting members from: {url}")
    
    # Strategy 1: Look for lists (ul, ol)
    lists = soup.find_all(['ul', 'ol'])
    for list_elem in lists:
        # Skip navigation lists
        if list_elem.find_parent(['nav', 'header', 'footer']):
            continue
        
        items = list_elem.find_all('li', recursive=False)
        for item in items:
            # Get text, but try to get from link first if available
            link = item.find('a')
            if link:
                text = link.get_text().strip()
            else:
                text = item.get_text().strip()
            
            # Clean up text
            text = re.sub(r'\s+', ' ', text)
            text = text.split('\n')[0].strip()  # Take first line only
            
            if is_likely_member_name(text):
                members.append(text)
    
    # Strategy 2: Look for divs/sections with member classes
    member_containers = soup.find_all(['div', 'section', 'article'], 
                                     class_=re.compile(r'member|provider|partner|college', re.I))
    for container in member_containers:
        # Get the main text from the container
        heading = container.find(['h2', 'h3', 'h4', 'h5', 'strong', 'b'])
        if heading:
            text = heading.get_text().strip()
            text = re.sub(r'\s+', ' ', text)
            if is_likely_member_name(text):
                members.append(text)
    
    # Strategy 3: Look for tables
    tables = soup.find_all('table')
    for table in tables:
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header
            cells = row.find_all(['td', 'th'])
            if cells:
                # Usually first cell contains the member name
                text = cells[0].get_text().strip()
                text = re.sub(r'\s+', ' ', text)
                if is_likely_member_name(text):
                    members.append(text)
    
    # Strategy 4: Look for specific member name patterns
    # Some sites have member names in <p> tags or <div> with specific patterns
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        # Skip if inside navigation
        if p.find_parent(['nav', 'header', 'footer']):
            continue
        
        text = p.get_text().strip()
        # If paragraph is short enough to be a single member name
        if 10 < len(text) < 200 and is_likely_member_name(text):
            members.append(text)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_members = []
    for member in members:
        member_lower = member.lower()
        if member_lower not in seen:
            seen.add(member_lower)
            unique_members.append(member)
    
    logging.info(f"    Found {len(unique_members)} potential members")
    return unique_members

def scrape_organization_members(org_name: str, url: Optional[str]) -> Dict:
    """Scrape member names from an organization."""
    logging.info(f"\n{'='*70}")
    logging.info(f"Processing: {org_name}")
    logging.info(f"{'='*70}")
    
    if not url:
        logging.warning(f"  No URL available for {org_name}")
        return {
            'organization': org_name,
            'url': None,
            'members': [],
            'member_count': 0,
            'status': 'no_url'
        }
    
    try:
        logging.info(f"  Fetching: {url}")
        response = requests.get(url, headers=get_headers(), timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # First, try to find member pages
        member_pages = find_member_pages(soup, url)
        logging.info(f"  Found {len(member_pages)} potential member pages")
        
        all_members = []
        
        # Extract from main page
        members = extract_members_from_page(soup, url)
        all_members.extend(members)
        
        # Extract from member pages
        for page_url in member_pages:
            if page_url == url:
                continue  # Skip main page, already processed
            
            try:
                time.sleep(1)  # Be polite
                logging.info(f"  Fetching member page: {page_url}")
                page_response = requests.get(page_url, headers=get_headers(), timeout=20)
                page_response.raise_for_status()
                
                page_soup = BeautifulSoup(page_response.content, 'html.parser')
                page_members = extract_members_from_page(page_soup, page_url)
                all_members.extend(page_members)
                
            except Exception as e:
                logging.error(f"  Error fetching {page_url}: {e}")
                continue
        
        # Remove duplicates
        seen = set()
        unique_members = []
        for member in all_members:
            member_lower = member.lower()
            if member_lower not in seen:
                seen.add(member_lower)
                unique_members.append(member)
        
        logging.info(f"  ✓ Total unique members found: {len(unique_members)}")
        
        return {
            'organization': org_name,
            'url': url,
            'members': unique_members,
            'member_count': len(unique_members),
            'status': 'success' if unique_members else 'no_members_found'
        }
        
    except requests.exceptions.RequestException as e:
        logging.error(f"  Error fetching {url}: {e}")
        return {
            'organization': org_name,
            'url': url,
            'members': [],
            'member_count': 0,
            'status': f'error: {str(e)}'
        }
    except Exception as e:
        logging.error(f"  Unexpected error: {e}")
        return {
            'organization': org_name,
            'url': url,
            'members': [],
            'member_count': 0,
            'status': f'error: {str(e)}'
        }

def main():
    """Main function to scrape all organizations."""
    logging.info("\n" + "="*70)
    logging.info("SCRAPING MEMBERSHIP ORGANIZATION MEMBER NAMES")
    logging.info("="*70)
    logging.info(f"Total organizations: {len(ORGANIZATIONS)}\n")
    
    results = []
    
    for i, (org_name, url) in enumerate(ORGANIZATIONS.items(), 1):
        logging.info(f"\n[{i}/{len(ORGANIZATIONS)}] {org_name}")
        
        result = scrape_organization_members(org_name, url)
        results.append(result)
        
        # Be polite to servers
        time.sleep(2)
    
    # Save results
    output_file = 'organization_members.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logging.info("\n" + "="*70)
    logging.info("SCRAPING COMPLETE")
    logging.info("="*70)
    logging.info(f"Results saved to: {output_file}")
    
    # Print summary
    logging.info("\n" + "="*70)
    logging.info("SUMMARY")
    logging.info("="*70)
    
    total_members = 0
    orgs_with_members = 0
    
    for result in results:
        member_count = result['member_count']
        if member_count > 0:
            logging.info(f"✓ {result['organization']}: {member_count} members")
            orgs_with_members += 1
            total_members += member_count
        else:
            logging.info(f"✗ {result['organization']}: No members found ({result['status']})")
    
    logging.info(f"\n{'='*70}")
    logging.info(f"Organizations with members found: {orgs_with_members}/{len(ORGANIZATIONS)}")
    logging.info(f"Total member names collected: {total_members}")
    logging.info(f"{'='*70}\n")
    
    return results

if __name__ == '__main__':
    main()
