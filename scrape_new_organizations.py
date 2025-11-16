#!/usr/bin/env python3
"""
Scrape member names from newly discovered organizations.
"""

import json
import sys
import os

# Add the scraper functions
sys.path.insert(0, os.path.dirname(__file__))

# Import the scraper
from scrape_organization_members import scrape_organization_members
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping_new.log'),
        logging.StreamHandler()
    ]
)

def main():
    """Scrape the newly found organizations."""
    # Load found URLs
    with open('found_urls.json', 'r', encoding='utf-8') as f:
        new_urls = json.load(f)
    
    # Load existing results
    with open('organization_members.json', 'r', encoding='utf-8') as f:
        existing_results = json.load(f)
    
    logging.info("\n" + "="*70)
    logging.info("SCRAPING NEWLY DISCOVERED ORGANIZATIONS")
    logging.info("="*70)
    logging.info(f"New organizations to scrape: {len(new_urls)}\n")
    
    new_results = []
    
    for i, (org_name, url) in enumerate(new_urls.items(), 1):
        logging.info(f"\n[{i}/{len(new_urls)}] {org_name}")
        
        result = scrape_organization_members(org_name, url)
        new_results.append(result)
        
        # Be polite
        time.sleep(2)
    
    # Merge with existing results
    # Create a map of existing results by organization name
    existing_map = {r['organization']: r for r in existing_results}
    
    # Update with new results
    for new_result in new_results:
        org_name = new_result['organization']
        existing_map[org_name] = new_result
    
    # Convert back to list
    updated_results = list(existing_map.values())
    
    # Save updated results
    with open('organization_members.json', 'w', encoding='utf-8') as f:
        json.dump(updated_results, f, indent=2, ensure_ascii=False)
    
    logging.info("\n" + "="*70)
    logging.info("SCRAPING COMPLETE")
    logging.info("="*70)
    
    # Print summary
    total_members = sum(r['member_count'] for r in new_results)
    orgs_with_members = sum(1 for r in new_results if r['member_count'] > 0)
    
    logging.info(f"\nNew organizations with members found: {orgs_with_members}/{len(new_results)}")
    logging.info(f"New member names collected: {total_members}")
    
    if orgs_with_members > 0:
        logging.info("\nSuccessful organizations:")
        for result in new_results:
            if result['member_count'] > 0:
                logging.info(f"  ✓ {result['organization']}: {result['member_count']} members")
    
    logging.info(f"\nUpdated results saved to: organization_members.json\n")

if __name__ == '__main__':
    main()
