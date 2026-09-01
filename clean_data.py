#!/usr/bin/env python3
"""
Clean and format the scraped operations management providers data
"""

import pandas as pd
import re

def clean_training_options(text):
    """Clean up training options text"""
    if pd.isna(text) or not text:
        return ""
    
    # Split by common patterns and clean
    options = []
    
    # Handle different training option patterns
    patterns = [
        r"At apprentice's workplace",
        r"Day release",
        r"Block release",
        r"Block release at multiple locations",
        r"Day release at multiple locations"
    ]
    
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            if "workplace" in pattern.lower():
                options.append("At apprentice's workplace")
            elif "day release at multiple" in pattern.lower():
                options.append("Day release (multiple locations)")
            elif "block release at multiple" in pattern.lower():
                options.append("Block release (multiple locations)")
            elif "day release" in pattern.lower():
                options.append("Day release")
            elif "block release" in pattern.lower():
                options.append("Block release")
    
    return "; ".join(list(dict.fromkeys(options)))  # Remove duplicates while preserving order

def clean_reviews(text):
    """Clean up review text"""
    if pd.isna(text) or not text:
        return ""
    
    if "No employer reviews" in text or "No apprentice reviews" in text:
        return "No reviews"
    
    # Extract rating and count using regex
    match = re.search(r'(Excellent|Good|Poor|Very poor)\((\d+)\s+(employer|apprentice)\s+review', text)
    if match:
        rating = match.group(1)
        count = match.group(2)
        review_type = match.group(3)
        return f"{rating} ({count} {review_type} review{'s' if int(count) > 1 else ''})"
    
    return text

def main():
    # Load the data
    df = pd.read_csv('operations_management_providers.csv')
    
    # Clean the data
    df['training_options_cleaned'] = df['training_options'].apply(clean_training_options)
    df['employer_reviews_cleaned'] = df['employer_reviews'].apply(clean_reviews)
    df['apprentice_reviews_cleaned'] = df['apprentice_reviews'].apply(clean_reviews)
    
    # Create a clean version with better column names
    clean_df = pd.DataFrame({
        'Provider Name': df['name'],
        'UKPRN': df['ukprn'],
        'Training Options': df['training_options_cleaned'],
        'Employer Reviews': df['employer_reviews_cleaned'],
        'Apprentice Reviews': df['apprentice_reviews_cleaned'],
        'Achievement Rate': df['achievement_rate'],
        'Detail URL': df['detail_url']
    })
    
    # Save cleaned data
    clean_df.to_csv('operations_management_providers_clean.csv', index=False)
    clean_df.to_json('operations_management_providers_clean.json', orient='records', indent=2)
    
    print("Data cleaning completed!")
    print(f"Total providers: {len(clean_df)}")
    print(f"Saved to: operations_management_providers_clean.csv and operations_management_providers_clean.json")
    
    # Show sample of cleaned data
    print("\nSample of cleaned data:")
    print(clean_df.head(3).to_string(index=False))

if __name__ == "__main__":
    main()