#!/usr/bin/env python3
"""
Script to upload CSV data to Google Sheets
Requires Google API credentials
"""

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import sys
import os

def upload_csv_to_sheets(csv_file, spreadsheet_id, credentials_file=None):
    """
    Upload CSV file to Google Sheets
    
    Args:
        csv_file: Path to CSV file
        spreadsheet_id: Google Sheets spreadsheet ID
        credentials_file: Path to Google service account JSON file (optional)
    """
    
    # Read CSV
    print(f"Reading CSV file: {csv_file}")
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} rows and {len(df.columns)} columns")
    
    # Authenticate with Google Sheets
    print("\nAuthenticating with Google Sheets...")
    
    if credentials_file and os.path.exists(credentials_file):
        # Use service account credentials
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(credentials_file, scopes=scope)
        gc = gspread.authorize(creds)
    else:
        # Try to use default credentials or OAuth
        try:
            # Try service account from environment
            if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
                creds = Credentials.from_service_account_file(
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'],
                    scopes=['https://spreadsheets.google.com/feeds',
                           'https://www.googleapis.com/auth/drive'])
                gc = gspread.authorize(creds)
            else:
                print("ERROR: No Google API credentials found.")
                print("\nTo upload to Google Sheets, you need to:")
                print("1. Create a Google Cloud project")
                print("2. Enable Google Sheets API")
                print("3. Create a service account and download JSON credentials")
                print("4. Share your Google Sheet with the service account email")
                print("\nAlternatively, you can manually upload the CSV:")
                print(f"   File: {csv_file}")
                print(f"   Google Sheet: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")
                return False
        except Exception as e:
            print(f"Authentication error: {e}")
            print("\nPlease set up Google API credentials or upload manually.")
            return False
    
    try:
        # Open the spreadsheet
        print(f"\nOpening spreadsheet: {spreadsheet_id}")
        spreadsheet = gc.open_by_key(spreadsheet_id)
        
        # Get the first worksheet (or create one)
        try:
            worksheet = spreadsheet.sheet1
            print(f"Using existing worksheet: {worksheet.title}")
        except:
            worksheet = spreadsheet.add_worksheet(title="Processed Data", rows=len(df)+1, cols=len(df.columns))
            print(f"Created new worksheet: {worksheet.title}")
        
        # Clear existing content
        print("Clearing existing content...")
        worksheet.clear()
        
        # Upload data
        print("Uploading data...")
        # Convert DataFrame to list of lists
        values = [df.columns.tolist()] + df.values.tolist()
        
        # Update in batches to avoid API limits
        batch_size = 1000
        for i in range(0, len(values), batch_size):
            batch = values[i:i+batch_size]
            start_row = i + 1
            end_row = i + len(batch)
            print(f"  Uploading rows {start_row}-{end_row}...")
            worksheet.update(f'A{start_row}', batch)
        
        print(f"\n✓ Successfully uploaded {len(df)} rows to Google Sheets!")
        print(f"  Spreadsheet: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")
        return True
        
    except gspread.exceptions.APIError as e:
        print(f"\nERROR: {e}")
        if "PERMISSION_DENIED" in str(e):
            print("\nMake sure you've shared the Google Sheet with the service account email.")
        return False
    except Exception as e:
        print(f"\nERROR: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 upload_to_sheets.py <csv_file> [spreadsheet_id] [credentials_file]")
        print("\nExample:")
        print("  python3 upload_to_sheets.py companies_data_processed.csv 1RwQutEFOjZWJMnZtl2MncGIkarNTLYAG2JJwOMAOGDQ")
        print("\nOr set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    spreadsheet_id = sys.argv[2] if len(sys.argv) > 2 else "1RwQutEFOjZWJMnZtl2MncGIkarNTLYAG2JJwOMAOGDQ"
    credentials_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    upload_csv_to_sheets(csv_file, spreadsheet_id, credentials_file)
