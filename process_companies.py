#!/usr/bin/env python3
"""
Script to process company data and add:
1. Column indicating if head office is in London or surrounding boroughs
2. Column with the county of the head office
"""

import pandas as pd
import re
import sys
import os

# London boroughs and surrounding areas
LONDON_BOROUGHS = {
    # Inner London boroughs
    'city of london', 'westminster', 'kensington and chelsea', 'hammersmith and fulham',
    'wandsworth', 'lambeth', 'southwark', 'tower hamlets', 'hackney', 'islington',
    'camden', 'brent', 'ealing', 'hounslow', 'richmond upon thames', 'kingston upon thames',
    'merton', 'sutton', 'croydon', 'bromley', 'lewisham', 'greenwich', 'bexley',
    'havering', 'barking and dagenham', 'redbridge', 'newham', 'waltham forest',
    'haringey', 'enfield', 'barnet', 'harrow', 'hillingdon',
    # Greater London areas
    'london', 'greater london',
    # Surrounding areas that might be considered part of London region
    'watford', 'slough', 'reading', 'maidenhead', 'windsor', 'egham', 'staines',
    'uxbridge', 'ruislip', 'pinner', 'northwood', 'rickmansworth', 'chorleywood',
    'amersham', 'beaconsfield', 'high wycombe', 'chesham', 'aylesbury',
    'luton', 'dunstable', 'hemel hempstead', 'st albans', 'ware', 'hertford',
    'bishops stortford', 'harlow', 'epsom', 'reigate', 'crawley', 'gatwick',
    'dartford', 'gravesend', 'medway', 'maidstone', 'sevenoaks', 'tonbridge',
    'tunbridge wells', 'east grinstead', 'haywards heath', 'brighton', 'hove'
}

# UK Counties mapping (common patterns)
COUNTIES = {
    # Greater London
    'greater london': 'Greater London',
    'london': 'Greater London',
    
    # Home Counties
    'kent': 'Kent',
    'surrey': 'Surrey',
    'essex': 'Essex',
    'hertfordshire': 'Hertfordshire',
    'buckinghamshire': 'Buckinghamshire',
    'berkshire': 'Berkshire',
    'sussex': 'Sussex',
    'east sussex': 'East Sussex',
    'west sussex': 'West Sussex',
    
    # Other counties
    'bedfordshire': 'Bedfordshire',
    'cambridgeshire': 'Cambridgeshire',
    'norfolk': 'Norfolk',
    'suffolk': 'Suffolk',
    'oxfordshire': 'Oxfordshire',
    'hampshire': 'Hampshire',
    'wiltshire': 'Wiltshire',
    'gloucestershire': 'Gloucestershire',
    'somerset': 'Somerset',
    'dorset': 'Dorset',
    'devon': 'Devon',
    'cornwall': 'Cornwall',
    'yorkshire': 'Yorkshire',
    'lancashire': 'Lancashire',
    'cheshire': 'Cheshire',
    'derbyshire': 'Derbyshire',
    'nottinghamshire': 'Nottinghamshire',
    'leicestershire': 'Leicestershire',
    'warwickshire': 'Warwickshire',
    'staffordshire': 'Staffordshire',
    'shropshire': 'Shropshire',
    'worcestershire': 'Worcestershire',
    'herefordshire': 'Herefordshire',
    'northamptonshire': 'Northamptonshire',
    'rutland': 'Rutland',
    'lincolnshire': 'Lincolnshire',
    'norfolk': 'Norfolk',
    'suffolk': 'Suffolk',
    'cumbria': 'Cumbria',
    'northumberland': 'Northumberland',
    'durham': 'County Durham',
    'north yorkshire': 'North Yorkshire',
    'south yorkshire': 'South Yorkshire',
    'west yorkshire': 'West Yorkshire',
    'east yorkshire': 'East Yorkshire',
    'merseyside': 'Merseyside',
    'greater manchester': 'Greater Manchester',
    'tyne and wear': 'Tyne and Wear',
    'west midlands': 'West Midlands',
    'south gloucestershire': 'South Gloucestershire',
    'bristol': 'Bristol',
    'city of bristol': 'Bristol',
}

def normalize_text(text):
    """Normalize text for comparison"""
    if pd.isna(text):
        return ''
    return str(text).lower().strip()

def is_london_or_surrounding(address):
    """
    Check if address is in London or surrounding boroughs
    Returns: 'Yes' or 'No'
    """
    if pd.isna(address):
        return 'No'
    
    address_lower = normalize_text(address)
    
    # Check for London boroughs
    for borough in LONDON_BOROUGHS:
        if borough in address_lower:
            return 'Yes'
    
    # Check for postcodes (London postcodes typically start with E, EC, N, NW, SE, SW, W, WC)
    london_postcode_pattern = r'\b([EW]C?|[NS][W]?|SE|SW)\d'
    if re.search(london_postcode_pattern, address_lower):
        return 'Yes'
    
    return 'No'

def extract_county(address):
    """
    Extract county from address
    Returns: County name or 'Unknown'
    """
    if pd.isna(address):
        return 'Unknown'
    
    address_lower = normalize_text(address)
    
    # Check for explicit county mentions
    for county_key, county_name in COUNTIES.items():
        if county_key in address_lower:
            return county_name
    
    # Check for London postcodes to infer Greater London
    london_postcode_pattern = r'\b([EW]C?|[NS][W]?|SE|SW)\d'
    if re.search(london_postcode_pattern, address_lower):
        return 'Greater London'
    
    # Check for common London area indicators
    london_indicators = ['london', 'greater london', 'inner london', 'outer london']
    for indicator in london_indicators:
        if indicator in address_lower:
            return 'Greater London'
    
    return 'Unknown'

def process_csv(input_file, output_file=None):
    """
    Process CSV file and add new columns
    """
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return
    
    print(f"Reading CSV file: {input_file}")
    try:
        df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    print(f"Found {len(df)} rows and {len(df.columns)} columns")
    print(f"Columns: {', '.join(df.columns)}")
    
    # Try to identify the address column
    address_column = None
    possible_address_columns = [
        'head office', 'head_office', 'address', 'head office address',
        'head_office_address', 'location', 'registered address', 'registered_address',
        'office address', 'office_address', 'company address', 'company_address'
    ]
    
    for col in df.columns:
        col_lower = normalize_text(col)
        if any(possible in col_lower for possible in possible_address_columns):
            address_column = col
            break
    
    # If not found, try to find any column that might contain addresses
    if address_column is None:
        for col in df.columns:
            # Check if column contains addresses (has common address keywords)
            sample_values = df[col].dropna().astype(str).head(10)
            if any(keyword in ' '.join(sample_values).lower() for keyword in 
                   ['street', 'road', 'avenue', 'london', 'postcode', 'uk', 'england']):
                address_column = col
                print(f"Auto-detected address column: {col}")
                break
    
    if address_column is None:
        print("\nCould not automatically detect address column.")
        print("Available columns:", ', '.join(df.columns))
        print("\nPlease specify which column contains the head office address.")
        return
    
    print(f"Using address column: {address_column}")
    
    # Add new columns
    print("\nProcessing addresses...")
    df['In London or Surrounding Boroughs'] = df[address_column].apply(is_london_or_surrounding)
    df['County'] = df[address_column].apply(extract_county)
    
    # Save output
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_processed.csv"
    
    print(f"\nSaving processed file to: {output_file}")
    df.to_csv(output_file, index=False)
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    london_count = (df['In London or Surrounding Boroughs'] == 'Yes').sum()
    print(f"Companies in London or surrounding boroughs: {london_count} ({london_count/len(df)*100:.1f}%)")
    print(f"\nCounty distribution:")
    print(df['County'].value_counts().to_string())
    print("\n" + "="*60)
    print(f"Processed file saved: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 process_companies.py <input_csv_file> [output_csv_file]")
        print("\nExample: python3 process_companies.py companies.csv companies_processed.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    process_csv(input_file, output_file)
