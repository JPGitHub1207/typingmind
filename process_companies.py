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
    'middlesex': 'Greater London',  # Historical county, now part of Greater London
    
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

# City to County mappings (for cases where county isn't explicitly mentioned)
CITY_TO_COUNTY = {
    # Greater London / Middlesex
    'eastcote': 'Greater London',
    'ruislip': 'Greater London',
    'pinner': 'Greater London',
    'northwood': 'Greater London',
    'harrow': 'Greater London',
    'uxbridge': 'Greater London',
    'hillingdon': 'Greater London',
    'ealing': 'Greater London',
    'brentford': 'Greater London',
    'twickenham': 'Greater London',
    'richmond': 'Greater London',
    'kingston': 'Greater London',
    'sutton': 'Greater London',
    'croydon': 'Greater London',
    'bromley': 'Greater London',
    'lewisham': 'Greater London',
    'greenwich': 'Greater London',
    'bexley': 'Greater London',
    'dartford': 'Kent',
    'gravesend': 'Kent',
    'maidstone': 'Kent',
    'canterbury': 'Kent',
    'rochester': 'Kent',
    'tunbridge wells': 'Kent',
    'tonbridge': 'Kent',
    'sevenoaks': 'Kent',
    'herne bay': 'Kent',
    'whitstable': 'Kent',
    'margate': 'Kent',
    'ramsgate': 'Kent',
    'folkestone': 'Kent',
    'dover': 'Kent',
    'guildford': 'Surrey',
    'woking': 'Surrey',
    'epsom': 'Surrey',
    'reigate': 'Surrey',
    'camberley': 'Surrey',
    'farnham': 'Surrey',
    'wokingham': 'Berkshire',
    'slough': 'Berkshire',
    'reading': 'Berkshire',
    'maidenhead': 'Berkshire',
    'windsor': 'Berkshire',
    'bracknell': 'Berkshire',
    'newbury': 'Berkshire',
    'chelmsford': 'Essex',
    'colchester': 'Essex',
    'southend': 'Essex',
    'basildon': 'Essex',
    'harlow': 'Essex',
    'brentwood': 'Essex',
    'bishops stortford': 'Hertfordshire',
    'hertford': 'Hertfordshire',
    'watford': 'Hertfordshire',
    'st albans': 'Hertfordshire',
    'hemel hempstead': 'Hertfordshire',
    'ware': 'Hertfordshire',
    'milton keynes': 'Buckinghamshire',
    'aylesbury': 'Buckinghamshire',
    'high wycombe': 'Buckinghamshire',
    'amersham': 'Buckinghamshire',
    'beaconsfield': 'Buckinghamshire',
    'chesham': 'Buckinghamshire',
    'luton': 'Bedfordshire',
    'bedford': 'Bedfordshire',
    'dunstable': 'Bedfordshire',
    'cambridge': 'Cambridgeshire',
    'ely': 'Cambridgeshire',
    'peterborough': 'Cambridgeshire',
    'wisbech': 'Cambridgeshire',
    'norwich': 'Norfolk',
    'great yarmouth': 'Norfolk',
    'kings lynn': 'Norfolk',
    'thetford': 'Norfolk',
    'ipswich': 'Suffolk',
    'lowestoft': 'Suffolk',
    'bury st edmunds': 'Suffolk',
    'felixstowe': 'Suffolk',
    'oxford': 'Oxfordshire',
    'banbury': 'Oxfordshire',
    'abingdon': 'Oxfordshire',
    'witney': 'Oxfordshire',
    'southampton': 'Hampshire',
    'portsmouth': 'Hampshire',
    'winchester': 'Hampshire',
    'basingstoke': 'Hampshire',
    'eastleigh': 'Hampshire',
    'fareham': 'Hampshire',
    'gosport': 'Hampshire',
    'salisbury': 'Wiltshire',
    'swindon': 'Wiltshire',
    'chippenham': 'Wiltshire',
    'trowbridge': 'Wiltshire',
    'gloucester': 'Gloucestershire',
    'cheltenham': 'Gloucestershire',
    'stroud': 'Gloucestershire',
    'tewkesbury': 'Gloucestershire',
    'bath': 'Somerset',
    'taunton': 'Somerset',
    'yeovil': 'Somerset',
    'bridgwater': 'Somerset',
    'weston super mare': 'Somerset',
    'bristol': 'Bristol',
    'poole': 'Dorset',
    'bournemouth': 'Dorset',
    'weymouth': 'Dorset',
    'dorchester': 'Dorset',
    'exeter': 'Devon',
    'plymouth': 'Devon',
    'torquay': 'Devon',
    'paignton': 'Devon',
    'barnstaple': 'Devon',
    'truro': 'Cornwall',
    'falmouth': 'Cornwall',
    'penzance': 'Cornwall',
    'st austell': 'Cornwall',
    'leeds': 'West Yorkshire',
    'bradford': 'West Yorkshire',
    'wakefield': 'West Yorkshire',
    'huddersfield': 'West Yorkshire',
    'halifax': 'West Yorkshire',
    'sheffield': 'South Yorkshire',
    'rotherham': 'South Yorkshire',
    'doncaster': 'South Yorkshire',
    'barnsley': 'South Yorkshire',
    'york': 'North Yorkshire',
    'harrogate': 'North Yorkshire',
    'scarborough': 'North Yorkshire',
    'hull': 'East Yorkshire',
    'beverley': 'East Yorkshire',
    'manchester': 'Greater Manchester',
    'salford': 'Greater Manchester',
    'bolton': 'Greater Manchester',
    'oldham': 'Greater Manchester',
    'rochdale': 'Greater Manchester',
    'stockport': 'Greater Manchester',
    'wigan': 'Greater Manchester',
    'bury': 'Greater Manchester',
    'tameside': 'Greater Manchester',
    'trafford': 'Greater Manchester',
    'liverpool': 'Merseyside',
    'birkenhead': 'Merseyside',
    'wallasey': 'Merseyside',
    'southport': 'Merseyside',
    'st helens': 'Merseyside',
    'prescot': 'Merseyside',
    'warrington': 'Cheshire',
    'chester': 'Cheshire',
    'macclesfield': 'Cheshire',
    'crewe': 'Cheshire',
    'ellesmere port': 'Cheshire',
    'winsford': 'Cheshire',
    'blackpool': 'Lancashire',
    'preston': 'Lancashire',
    'blackburn': 'Lancashire',
    'burnley': 'Lancashire',
    'chorley': 'Lancashire',
    'lancaster': 'Lancashire',
    'morecambe': 'Lancashire',
    'thornton-cleveleys': 'Lancashire',
    'fleetwood': 'Lancashire',
    'birmingham': 'West Midlands',
    'coventry': 'West Midlands',
    'wolverhampton': 'West Midlands',
    'solihull': 'West Midlands',
    'walsall': 'West Midlands',
    'dudley': 'West Midlands',
    'sandwell': 'West Midlands',
    'nottingham': 'Nottinghamshire',
    'mansfield': 'Nottinghamshire',
    'worksop': 'Nottinghamshire',
    'newark': 'Nottinghamshire',
    'retford': 'Nottinghamshire',
    'long eaton': 'Nottinghamshire',
    'derby': 'Derbyshire',
    'chesterfield': 'Derbyshire',
    'buxton': 'Derbyshire',
    'matlock': 'Derbyshire',
    'leicester': 'Leicestershire',
    'loughborough': 'Leicestershire',
    'hinckley': 'Leicestershire',
    'melton mowbray': 'Leicestershire',
    'warwick': 'Warwickshire',
    'nuneaton': 'Warwickshire',
    'rugby': 'Warwickshire',
    'stratford upon avon': 'Warwickshire',
    'leamington spa': 'Warwickshire',
    'stafford': 'Staffordshire',
    'stoke on trent': 'Staffordshire',
    'burton upon trent': 'Staffordshire',
    'cannock': 'Staffordshire',
    'newcastle under lyme': 'Staffordshire',
    'shrewsbury': 'Shropshire',
    'telford': 'Shropshire',
    'wellington': 'Shropshire',
    'ludlow': 'Shropshire',
    'worcester': 'Worcestershire',
    'redditch': 'Worcestershire',
    'kidderminster': 'Worcestershire',
    'droitwich': 'Worcestershire',
    'malvern': 'Worcestershire',
    'hereford': 'Herefordshire',
    'leominster': 'Herefordshire',
    'ross on wye': 'Herefordshire',
    'northampton': 'Northamptonshire',
    'wellingborough': 'Northamptonshire',
    'kettering': 'Northamptonshire',
    'corby': 'Northamptonshire',
    'rushden': 'Northamptonshire',
    'irthlingborough': 'Northamptonshire',
    'lincoln': 'Lincolnshire',
    'grimsby': 'Lincolnshire',
    'scunthorpe': 'Lincolnshire',
    'boston': 'Lincolnshire',
    'grantham': 'Lincolnshire',
    'skegness': 'Lincolnshire',
    'newcastle upon tyne': 'Tyne and Wear',
    'sunderland': 'Tyne and Wear',
    'gateshead': 'Tyne and Wear',
    'north shields': 'Tyne and Wear',
    'south shields': 'Tyne and Wear',
    'washington': 'Tyne and Wear',
    'durham': 'County Durham',
    'darlington': 'County Durham',
    'hartlepool': 'County Durham',
    'stockton on tees': 'County Durham',
    'middlesbrough': 'County Durham',
    'carlisle': 'Cumbria',
    'barrow in furness': 'Cumbria',
    'kendal': 'Cumbria',
    'whitehaven': 'Cumbria',
    'workington': 'Cumbria',
    'penrith': 'Cumbria',
    'alnwick': 'Northumberland',
    'berwick upon tweed': 'Northumberland',
    'hexham': 'Northumberland',
    'morpeth': 'Northumberland',
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
    # Also include HA (Harrow), UB (Southall), TW (Twickenham), CR (Croydon), BR (Bromley)
    london_postcode_pattern = r'\b([EW]C?|[NS][W]?|SE|SW|HA|UB|TW|CR|BR)\d'
    if re.search(london_postcode_pattern, address_lower):
        return 'Yes'
    
    # Check for Middlesex (historical county, now part of Greater London)
    if 'middlesex' in address_lower:
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
    
    # Check for explicit county mentions first
    for county_key, county_name in COUNTIES.items():
        if county_key in address_lower:
            return county_name
    
    # Check for London postcodes to infer Greater London
    # Include outer London postcodes: HA (Harrow), UB (Southall), TW (Twickenham), CR (Croydon), BR (Bromley)
    london_postcode_pattern = r'\b([EW]C?|[NS][W]?|SE|SW|HA|UB|TW|CR|BR)\d'
    if re.search(london_postcode_pattern, address_lower):
        return 'Greater London'
    
    # Check for common London area indicators
    london_indicators = ['london', 'greater london', 'inner london', 'outer london']
    for indicator in london_indicators:
        if indicator in address_lower:
            return 'Greater London'
    
    # Extract city names and check against city-to-county mapping
    # Look for common address patterns: "City, County" or "City, Postcode"
    # Try to find city names in the address
    address_parts = re.split(r'[,;]', address_lower)
    
    for part in address_parts:
        part = part.strip()
        # Check if this part matches a known city
        for city, county in CITY_TO_COUNTY.items():
            # Use word boundary to avoid partial matches
            if re.search(r'\b' + re.escape(city) + r'\b', part):
                return county
    
    # Try postcode-based detection for some areas
    # Extract postcode pattern (handles both full postcodes and partial ones)
    # Pattern matches: EC1A 1BB, EC1A1BB, SW1A 1AA, M1 1AA, B1 1AA, etc.
    postcode_match = re.search(r'\b([A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}|[A-Z]\d{1,2}\s?\d[A-Z]{2})\b', address, re.IGNORECASE)
    if postcode_match:
        postcode = postcode_match.group(1).upper().replace(' ', '')
        # Extract postcode area (first 1-2 letters before numbers)
        postcode_area_match = re.match(r'^([A-Z]{1,2})', postcode)
        if postcode_area_match:
            postcode_area = postcode_area_match.group(1)
        else:
            postcode_area = postcode[:1] if len(postcode) >= 1 else ''
        
        # Postcode area to county mappings (common ones)
        postcode_to_county = {
            'HA': 'Greater London',  # Harrow
            'UB': 'Greater London',  # Southall
            'TW': 'Greater London',  # Twickenham
            'KT': 'Surrey',  # Kingston upon Thames area
            'GU': 'Surrey',  # Guildford
            'RH': 'Surrey',  # Redhill
            'SM': 'Surrey',  # Sutton
            'CR': 'Greater London',  # Croydon
            'BR': 'Greater London',  # Bromley
            'DA': 'Kent',  # Dartford
            'ME': 'Kent',  # Medway
            'CT': 'Kent',  # Canterbury
            'TN': 'Kent',  # Tunbridge Wells
            'CM': 'Essex',  # Chelmsford
            'SS': 'Essex',  # Southend
            'IG': 'Essex',  # Ilford
            'RM': 'Essex',  # Romford
            'EN': 'Hertfordshire',  # Enfield
            'AL': 'Hertfordshire',  # St Albans
            'SG': 'Hertfordshire',  # Stevenage
            'WD': 'Hertfordshire',  # Watford
            'HP': 'Buckinghamshire',  # Hemel Hempstead
            'MK': 'Buckinghamshire',  # Milton Keynes
            'SL': 'Berkshire',  # Slough
            'RG': 'Berkshire',  # Reading
            'LU': 'Bedfordshire',  # Luton
            'CB': 'Cambridgeshire',  # Cambridge
            'PE': 'Cambridgeshire',  # Peterborough
            'NR': 'Norfolk',  # Norwich
            'IP': 'Suffolk',  # Ipswich
            'OX': 'Oxfordshire',  # Oxford
            'SO': 'Hampshire',  # Southampton
            'PO': 'Hampshire',  # Portsmouth
            'RG': 'Hampshire',  # Reading (also Berkshire)
            'SP': 'Wiltshire',  # Salisbury
            'SN': 'Wiltshire',  # Swindon
            'GL': 'Gloucestershire',  # Gloucester
            'BA': 'Somerset',  # Bath
            'TA': 'Somerset',  # Taunton
            'BS': 'Bristol',  # Bristol
            'BH': 'Dorset',  # Bournemouth
            'DT': 'Dorset',  # Dorchester
            'EX': 'Devon',  # Exeter
            'PL': 'Devon',  # Plymouth
            'TQ': 'Devon',  # Torquay
            'TR': 'Cornwall',  # Truro
            'LS': 'West Yorkshire',  # Leeds
            'BD': 'West Yorkshire',  # Bradford
            'WF': 'West Yorkshire',  # Wakefield
            'HD': 'West Yorkshire',  # Huddersfield
            'HX': 'West Yorkshire',  # Halifax
            'S': 'South Yorkshire',  # Sheffield
            'DN': 'South Yorkshire',  # Doncaster
            'YO': 'North Yorkshire',  # York
            'HG': 'North Yorkshire',  # Harrogate
            'HU': 'East Yorkshire',  # Hull
            'M': 'Greater Manchester',  # Manchester
            'BL': 'Greater Manchester',  # Bolton
            'OL': 'Greater Manchester',  # Oldham
            'SK': 'Greater Manchester',  # Stockport
            'WN': 'Greater Manchester',  # Wigan
            'L': 'Merseyside',  # Liverpool
            'CH': 'Cheshire',  # Chester
            'CW': 'Cheshire',  # Crewe
            'WA': 'Cheshire',  # Warrington
            'SK': 'Cheshire',  # Stockport (also Greater Manchester)
            'FY': 'Lancashire',  # Blackpool
            'PR': 'Lancashire',  # Preston
            'BB': 'Lancashire',  # Blackburn
            'B': 'West Midlands',  # Birmingham
            'CV': 'West Midlands',  # Coventry
            'WV': 'West Midlands',  # Wolverhampton
            'WS': 'West Midlands',  # Walsall
            'DY': 'West Midlands',  # Dudley
            'NG': 'Nottinghamshire',  # Nottingham
            'DE': 'Derbyshire',  # Derby
            'LE': 'Leicestershire',  # Leicester
            'NN': 'Northamptonshire',  # Northampton
            'LN': 'Lincolnshire',  # Lincoln
            'NE': 'Tyne and Wear',  # Newcastle
            'SR': 'Tyne and Wear',  # Sunderland
            'DH': 'County Durham',  # Durham
            'TS': 'County Durham',  # Middlesbrough
            'DL': 'County Durham',  # Darlington
            'CA': 'Cumbria',  # Carlisle
        }
        
        if postcode_area in postcode_to_county:
            return postcode_to_county[postcode_area]
    
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
