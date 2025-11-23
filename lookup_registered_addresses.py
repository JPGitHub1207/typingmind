#!/usr/bin/env python3
"""
Script to look up registered addresses from Companies House
This requires a Companies House API key
"""

import pandas as pd
import requests
import time
import sys
import os
from typing import Optional, Dict

def normalize_company_name(name: str) -> str:
    """Normalize company name for searching"""
    # Remove common suffixes and T/A parts
    name = name.split(' T/A ')[0]  # Remove "T/A" part
    name = re.sub(r'\s+LIMITED\s*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+PLC\s*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+LTD\s*$', '', name, flags=re.IGNORECASE)
    name = name.strip()
    return name

def lookup_companies_house_address(company_name: str, api_key: str) -> Optional[Dict]:
    """
    Look up company registered address from Companies House API
    Returns dict with company_number and registered_address
    """
    import re
    
    try:
        # Normalize company name
        search_name = normalize_company_name(company_name)
        
        # Companies House search API
        url = "https://api.company-information.service.gov.uk/search/companies"
        headers = {
            'Authorization': f'Basic {api_key}'
        }
        params = {
            'q': search_name,
            'items_per_page': 5  # Get top 5 matches
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('items') and len(data['items']) > 0:
                # Try to find best match
                for item in data['items']:
                    company_title = item.get('title', '').upper()
                    search_upper = search_name.upper()
                    
                    # Check if names match reasonably well
                    if search_upper in company_title or company_title in search_upper:
                        company_number = item.get('company_number', '')
                        
                        # Get company details to get registered address
                        details_url = f"https://api.company-information.service.gov.uk/company/{company_number}"
                        details_response = requests.get(details_url, headers=headers, timeout=10)
                        
                        if details_response.status_code == 200:
                            details = details_response.json()
                            registered_address = details.get('registered_office_address', {})
                            
                            if registered_address:
                                # Format address
                                address_parts = []
                                if registered_address.get('address_line_1'):
                                    address_parts.append(registered_address['address_line_1'])
                                if registered_address.get('address_line_2'):
                                    address_parts.append(registered_address['address_line_2'])
                                if registered_address.get('locality'):
                                    address_parts.append(registered_address['locality'])
                                if registered_address.get('postal_code'):
                                    address_parts.append(registered_address['postal_code'])
                                
                                formatted_address = ', '.join(address_parts)
                                
                                return {
                                    'company_number': company_number,
                                    'registered_address': formatted_address,
                                    'match_confidence': 'high' if search_upper == company_title.upper() else 'medium'
                                }
        
        return None
    except Exception as e:
        print(f"Error looking up {company_name}: {e}")
        return None

def update_addresses_with_companies_house(input_csv: str, output_csv: str, api_key: str, limit: Optional[int] = None):
    """
    Look up registered addresses from Companies House and update the CSV
    """
    import re
    
    print(f"Reading CSV file: {input_csv}")
    df = pd.read_csv(input_csv)
    
    # Add new columns
    if 'Registered Address (Companies House)' not in df.columns:
        df['Registered Address (Companies House)'] = ''
    if 'Companies House Match' not in df.columns:
        df['Companies House Match'] = ''
    if 'Company Number' not in df.columns:
        df['Company Number'] = ''
    
    # Process companies with invalid addresses first
    invalid_df = df[df['Address Valid'] == 'No'].copy()
    
    if limit:
        invalid_df = invalid_df.head(limit)
    
    print(f"\nLooking up {len(invalid_df)} companies with invalid addresses...")
    print("(This may take a while due to API rate limits)\n")
    
    for idx, row in invalid_df.iterrows():
        company_name = row['Provider Name']
        print(f"Looking up: {company_name}")
        
        result = lookup_companies_house_address(company_name, api_key)
        
        if result:
            df.at[idx, 'Registered Address (Companies House)'] = result['registered_address']
            df.at[idx, 'Companies House Match'] = result['match_confidence']
            df.at[idx, 'Company Number'] = result['company_number']
            print(f"  ✓ Found: {result['registered_address']}")
        else:
            print(f"  ✗ Not found")
        
        time.sleep(0.5)  # Rate limiting (2 requests per second max)
    
    # Save results
    print(f"\nSaving updated data to: {output_csv}")
    df.to_csv(output_csv, index=False)
    
    print("\n✓ Address lookup complete!")
    return df

if __name__ == "__main__":
    import re
    
    input_file = "companies_data_verified.csv"
    output_file = "companies_data_with_registered_addresses.csv"
    api_key = None
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    if len(sys.argv) > 3:
        api_key = sys.argv[3]
    elif 'COMPANIES_HOUSE_API_KEY' in os.environ:
        api_key = os.environ['COMPANIES_HOUSE_API_KEY']
    
    if not api_key:
        print("ERROR: Companies House API key required")
        print("\nTo get an API key:")
        print("1. Go to https://developer.company-information.service.gov.uk/")
        print("2. Sign up for a free account")
        print("3. Create an application and get your API key")
        print("\nThen run:")
        print(f"  export COMPANIES_HOUSE_API_KEY='your-api-key'")
        print(f"  python3 {sys.argv[0]} {input_file} {output_file}")
        sys.exit(1)
    
    update_addresses_with_companies_house(input_file, output_file, api_key)
