#!/usr/bin/env python3
"""
Script to verify company registered addresses
Uses Companies House API and address validation
"""

import pandas as pd
import requests
import time
import re
from typing import Dict, Optional

def normalize_company_name(name: str) -> str:
    """Normalize company name for searching"""
    # Remove common suffixes and T/A parts
    name = name.split(' T/A ')[0]  # Remove "T/A" part
    name = re.sub(r'\s+LIMITED\s*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+PLC\s*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+LTD\s*$', '', name, flags=re.IGNORECASE)
    name = name.strip()
    return name

def check_address_format(address: str) -> Dict[str, any]:
    """
    Check if address format looks correct
    Returns dict with validation results
    """
    issues = []
    warnings = []
    
    if pd.isna(address) or not address:
        return {'valid': False, 'issues': ['Address is empty'], 'warnings': []}
    
    address_lower = str(address).lower()
    address_upper = str(address).upper()
    
    # Check for UK postcode (more comprehensive pattern)
    uk_postcode_pattern = r'\b([A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2})\b'
    has_uk_postcode = bool(re.search(uk_postcode_pattern, address, re.IGNORECASE))
    
    # Check for non-UK countries (be more specific)
    # Only flag if the country name appears as a standalone word/phrase, not as part of another word
    non_uk_countries = {
        r'\bghana\b': 'Ghana',
        r'\baustralia\b': 'Australia', 
        r'\bcanada\b': 'Canada',
        r'\bunited states\b': 'United States',
        r'\busa\b(?!\w)': 'United States',  # USA but not as part of another word
        r'\bmassachusetts\b': 'United States',
        r'\bpennsylvania\b': 'United States',
        r'\bflorida\b': 'United States',
        r'\bontario\b': 'Canada',
        r'\bnew south wales\b': 'Australia',
        r'\boti region\b': 'Ghana'
    }
    
    detected_non_uk_country = None
    for country_pattern, country_name in non_uk_countries.items():
        if re.search(country_pattern, address_lower):
            # Only flag if it's clearly not UK (check for UK postcode or UK indicators)
            detected_non_uk_country = country_name
            break
    
    # Check for UK indicators
    uk_indicators = ['england', 'scotland', 'wales', 'northern ireland', 'united kingdom', 'uk']
    has_uk_indicator = any(indicator in address_lower for indicator in uk_indicators)
    
    # UK postcode areas (first 1-2 letters)
    uk_postcode_areas = ['AB', 'AL', 'B', 'BA', 'BB', 'BD', 'BH', 'BL', 'BN', 'BR', 'BS', 'BT',
                        'CA', 'CB', 'CF', 'CH', 'CM', 'CO', 'CR', 'CT', 'CV', 'CW',
                        'DA', 'DD', 'DE', 'DG', 'DH', 'DL', 'DN', 'DT', 'DY',
                        'E', 'EC', 'EH', 'EN', 'EX',
                        'FK', 'FY',
                        'G', 'GL', 'GU',
                        'HA', 'HD', 'HG', 'HP', 'HR', 'HS', 'HU',
                        'HX',
                        'IG', 'IP', 'IV',
                        'JE',
                        'KA', 'KT', 'KW', 'KY',
                        'L', 'LA', 'LD', 'LE', 'LL', 'LN', 'LS', 'LU',
                        'M', 'ME', 'MK', 'ML',
                        'N', 'NE', 'NG', 'NN', 'NP', 'NR', 'NW',
                        'OL', 'OX',
                        'PA', 'PE', 'PH', 'PL', 'PO', 'PR',
                        'RG', 'RH', 'RM', 'S', 'SA', 'SE', 'SG', 'SK', 'SL', 'SM', 'SN', 'SO', 'SP', 'SR', 'SS', 'ST', 'SW', 'SY',
                        'TA', 'TD', 'TF', 'TN', 'TQ', 'TR', 'TS', 'TW',
                        'UB',
                        'W', 'WA', 'WC', 'WD', 'WF', 'WN', 'WR', 'WS', 'WV',
                        'YO', 'ZE']
    
    # Extract postcode area if postcode exists
    postcode_area = None
    if has_uk_postcode:
        postcode_match = re.search(uk_postcode_pattern, address, re.IGNORECASE)
        if postcode_match:
            postcode = postcode_match.group(1).upper().replace(' ', '')
            # Extract area (first 1-2 letters)
            area_match = re.match(r'^([A-Z]{1,2})', postcode)
            if area_match:
                postcode_area = area_match.group(1)
    
    # Validation logic
    # Flag as invalid if:
    # 1. Has non-UK country AND no UK postcode AND no UK indicator
    # 2. Has non-UK country AND UK postcode area doesn't exist in UK list
    is_likely_uk = has_uk_postcode or has_uk_indicator
    
    if detected_non_uk_country:
        if has_uk_postcode and postcode_area and postcode_area in uk_postcode_areas:
            # Has UK postcode, so might be a false positive (e.g., "Middlesex" contains "Massachusetts")
            # But if it's clearly a foreign country, flag it
            if detected_non_uk_country in ['Ghana', 'Australia', 'Canada', 'United States']:
                issues.append(f'Address appears to be in {detected_non_uk_country} (may be incorrect)')
        elif not is_likely_uk:
            issues.append(f'Address appears to be in {detected_non_uk_country} (not UK)')
    
    # Check for formatting issues
    if ',,' in address:
        issues.append('Double comma in address')
    
    # Check if address seems too short
    if len(address) < 15:
        warnings.append('Address seems very short')
    
    if not has_uk_postcode and not detected_non_uk_country:
        warnings.append('No UK postcode found')
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'has_uk_postcode': has_uk_postcode,
        'has_uk_indicator': has_uk_indicator,
        'postcode_area': postcode_area
    }

def lookup_companies_house(company_name: str, api_key: Optional[str] = None) -> Optional[Dict]:
    """
    Look up company on Companies House API
    Requires API key from https://developer.company-information.service.gov.uk/
    """
    if not api_key:
        return None
    
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
            'items_per_page': 1
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('items') and len(data['items']) > 0:
                return data['items'][0]
        
        return None
    except Exception as e:
        print(f"Error looking up {company_name}: {e}")
        return None

def verify_addresses(input_csv: str, output_csv: str, companies_house_api_key: Optional[str] = None):
    """
    Verify addresses in the CSV file
    """
    print(f"Reading CSV file: {input_csv}")
    df = pd.read_csv(input_csv)
    print(f"Found {len(df)} companies to verify\n")
    
    # Add verification columns
    df['Address Valid'] = ''
    df['Address Issues'] = ''
    df['Address Warnings'] = ''
    df['Verified Source'] = ''
    
    # Process each company
    for idx, row in df.iterrows():
        if (idx + 1) % 100 == 0:
            print(f"Processing {idx + 1}/{len(df)}...")
        
        address = row['Head Office Address']
        company_name = row['Provider Name']
        
        # Check address format
        validation = check_address_format(address)
        
        df.at[idx, 'Address Valid'] = 'Yes' if validation['valid'] else 'No'
        df.at[idx, 'Address Issues'] = '; '.join(validation['issues']) if validation['issues'] else ''
        df.at[idx, 'Address Warnings'] = '; '.join(validation['warnings']) if validation['warnings'] else ''
        
        # Try Companies House lookup if API key provided
        if companies_house_api_key:
            ch_data = lookup_companies_house(company_name, companies_house_api_key)
            if ch_data:
                registered_address = ch_data.get('address_snippet', '')
                df.at[idx, 'Verified Source'] = 'Companies House'
                # Could compare addresses here
                time.sleep(0.5)  # Rate limiting
    
    # Summary
    print(f"\n{'='*60}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*60}")
    
    valid_count = (df['Address Valid'] == 'Yes').sum()
    invalid_count = (df['Address Valid'] == 'No').sum()
    
    print(f"Valid addresses: {valid_count} ({valid_count/len(df)*100:.1f}%)")
    print(f"Invalid addresses: {invalid_count} ({invalid_count/len(df)*100:.1f}%)")
    
    print(f"\nAddress Issues Breakdown:")
    issue_counts = df[df['Address Issues'] != '']['Address Issues'].value_counts()
    print(issue_counts.to_string())
    
    print(f"\nAddresses with issues (first 20):")
    issues_df = df[df['Address Issues'] != ''][['Provider Name', 'Head Office Address', 'Address Issues']].head(20)
    print(issues_df.to_string())
    
    # Save results
    print(f"\nSaving verified data to: {output_csv}")
    df.to_csv(output_csv, index=False)
    
    print("\n✓ Address verification complete!")
    return df

if __name__ == "__main__":
    import sys
    
    input_file = "companies_data_processed.csv"
    output_file = "companies_data_verified.csv"
    api_key = None
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    if len(sys.argv) > 3:
        api_key = sys.argv[3]
    elif 'COMPANIES_HOUSE_API_KEY' in __import__('os').environ:
        api_key = __import__('os').environ['COMPANIES_HOUSE_API_KEY']
    
    verify_addresses(input_file, output_file, api_key)
