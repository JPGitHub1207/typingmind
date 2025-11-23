#!/usr/bin/env python3
"""
Script to add Provider Type column to the processed CSV
"""

import pandas as pd
import sys

def add_provider_type(processed_csv, provider_types_csv, output_csv):
    """
    Add Provider Type column to processed CSV by matching UKPRN
    """
    print(f"Reading processed CSV: {processed_csv}")
    df_processed = pd.read_csv(processed_csv)
    print(f"  Found {len(df_processed)} rows")
    
    print(f"\nReading provider types CSV: {provider_types_csv}")
    df_types = pd.read_csv(provider_types_csv)
    print(f"  Found {len(df_types)} rows")
    print(f"  Columns: {', '.join(df_types.columns)}")
    
    # Normalize UKPRN column names (case-insensitive matching)
    ukprn_col_processed = None
    ukprn_col_types = None
    
    for col in df_processed.columns:
        if 'ukprn' in col.lower():
            ukprn_col_processed = col
            break
    
    for col in df_types.columns:
        if 'ukprn' in col.lower():
            ukprn_col_types = col
            break
    
    if not ukprn_col_processed:
        print("ERROR: Could not find UKPRN column in processed CSV")
        return False
    
    if not ukprn_col_types:
        print("ERROR: Could not find UKPRN column in provider types CSV")
        return False
    
    print(f"\nMatching on UKPRN:")
    print(f"  Processed CSV column: {ukprn_col_processed}")
    print(f"  Provider types CSV column: {ukprn_col_types}")
    
    # Convert UKPRN to string for matching (handle any type differences)
    df_processed[ukprn_col_processed] = df_processed[ukprn_col_processed].astype(str)
    df_types[ukprn_col_types] = df_types[ukprn_col_types].astype(str)
    
    # Find ApplicationType column
    app_type_col = None
    for col in df_types.columns:
        if 'applicationtype' in col.lower() or 'application type' in col.lower() or 'type' in col.lower():
            app_type_col = col
            break
    
    if not app_type_col:
        print("ERROR: Could not find ApplicationType column in provider types CSV")
        print(f"Available columns: {', '.join(df_types.columns)}")
        return False
    
    print(f"  Using ApplicationType column: {app_type_col}")
    
    # Create a mapping dictionary
    provider_type_map = dict(zip(df_types[ukprn_col_types], df_types[app_type_col]))
    
    # Add Provider Type column
    print("\nMatching providers...")
    df_processed['Provider Type'] = df_processed[ukprn_col_processed].map(provider_type_map)
    
    # Count matches
    matched = df_processed['Provider Type'].notna().sum()
    unmatched = df_processed['Provider Type'].isna().sum()
    
    print(f"  Matched: {matched} providers")
    print(f"  Unmatched: {unmatched} providers")
    
    if unmatched > 0:
        print(f"\nUnmatched UKPRNs (first 10):")
        unmatched_ukprns = df_processed[df_processed['Provider Type'].isna()][ukprn_col_processed].head(10).tolist()
        for ukprn in unmatched_ukprns:
            print(f"  {ukprn}")
    
    # Show distribution
    print(f"\nProvider Type distribution:")
    print(df_processed['Provider Type'].value_counts().to_string())
    
    # Save output
    print(f"\nSaving to: {output_csv}")
    df_processed.to_csv(output_csv, index=False)
    
    print("\n✓ Successfully added Provider Type column!")
    return True

if __name__ == "__main__":
    processed_file = "companies_data_processed.csv"
    provider_types_file = "provider_types.csv"
    output_file = "companies_data_processed.csv"  # Overwrite the existing file
    
    if len(sys.argv) > 1:
        processed_file = sys.argv[1]
    if len(sys.argv) > 2:
        provider_types_file = sys.argv[2]
    if len(sys.argv) > 3:
        output_file = sys.argv[3]
    
    add_provider_type(processed_file, provider_types_file, output_file)
