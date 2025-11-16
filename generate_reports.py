#!/usr/bin/env python3
"""
Generate organized reports from scraped membership data.
Creates individual files for each organization and summary reports.
"""

import json
import os
from datetime import datetime

def load_results():
    """Load the scraping results."""
    with open('organization_members.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def create_organization_files(results):
    """Create individual text files for each organization with members."""
    # Create directory for member lists
    os.makedirs('member_lists', exist_ok=True)
    
    org_count = 0
    total_members = 0
    
    for result in results:
        if result['member_count'] > 0:
            org_name = result['organization']
            members = result['members']
            
            # Create safe filename
            filename = org_name.lower()
            filename = filename.replace(' ', '_')
            filename = filename.replace('&', 'and')
            filename = ''.join(c for c in filename if c.isalnum() or c in '_-')
            filename = f"member_lists/{filename}_members.txt"
            
            # Write member list
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"{org_name} - Member Names\n")
                f.write("=" * 70 + "\n\n")
                f.write(f"Total Members: {result['member_count']}\n")
                f.write(f"Source: {result['url']}\n")
                f.write(f"Date Scraped: {datetime.now().strftime('%Y-%m-%d')}\n\n")
                f.write("-" * 70 + "\n\n")
                
                for i, member in enumerate(members, 1):
                    f.write(f"{i}. {member}\n")
            
            print(f"✓ Created: {filename}")
            org_count += 1
            total_members += result['member_count']
    
    return org_count, total_members

def create_summary_report(results):
    """Create a comprehensive summary report."""
    filename = 'MEMBER_SCRAPING_SUMMARY.md'
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Membership Organization Member Names - Scraping Summary\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Overall Statistics
        total_orgs = len(results)
        orgs_with_members = sum(1 for r in results if r['member_count'] > 0)
        orgs_with_urls = sum(1 for r in results if r['url'])
        orgs_no_url = sum(1 for r in results if not r['url'])
        total_members = sum(r['member_count'] for r in results)
        
        f.write("## 📊 Overall Statistics\n\n")
        f.write(f"- **Total Organizations:** {total_orgs}\n")
        f.write(f"- **Organizations with Members Found:** {orgs_with_members}\n")
        f.write(f"- **Organizations with URLs:** {orgs_with_urls}\n")
        f.write(f"- **Organizations without URLs:** {orgs_no_url}\n")
        f.write(f"- **Total Member Names Collected:** {total_members}\n\n")
        
        f.write("---\n\n")
        
        # Successfully Scraped Organizations
        f.write("## ✅ Organizations with Members Found\n\n")
        success_orgs = [r for r in results if r['member_count'] > 0]
        
        if success_orgs:
            for result in sorted(success_orgs, key=lambda x: x['member_count'], reverse=True):
                f.write(f"### {result['organization']}\n\n")
                f.write(f"- **Member Count:** {result['member_count']}\n")
                f.write(f"- **Website:** {result['url']}\n")
                f.write(f"- **Status:** {result['status']}\n")
                
                # Create safe filename for reference
                org_filename = result['organization'].lower()
                org_filename = org_filename.replace(' ', '_').replace('&', 'and')
                org_filename = ''.join(c for c in org_filename if c.isalnum() or c in '_-')
                f.write(f"- **Member List File:** `member_lists/{org_filename}_members.txt`\n\n")
                
                # Show first 10 members as preview
                f.write("**Sample Members (first 10):**\n\n")
                for i, member in enumerate(result['members'][:10], 1):
                    f.write(f"{i}. {member}\n")
                
                if result['member_count'] > 10:
                    f.write(f"\n*...and {result['member_count'] - 10} more members*\n")
                
                f.write("\n---\n\n")
        else:
            f.write("*No organizations with members found.*\n\n")
        
        # Organizations without Members
        f.write("## ⚠️ Organizations without Member Names Found\n\n")
        
        # Group by status
        no_url_orgs = [r for r in results if not r['url']]
        error_orgs = [r for r in results if r['url'] and r['member_count'] == 0]
        
        if no_url_orgs:
            f.write(f"### Missing URLs ({len(no_url_orgs)} organizations)\n\n")
            f.write("These organizations need URLs to be added:\n\n")
            for result in sorted(no_url_orgs, key=lambda x: x['organization']):
                f.write(f"- {result['organization']}\n")
            f.write("\n---\n\n")
        
        if error_orgs:
            f.write(f"### Scraping Failed or No Members Found ({len(error_orgs)} organizations)\n\n")
            for result in sorted(error_orgs, key=lambda x: x['organization']):
                f.write(f"#### {result['organization']}\n\n")
                f.write(f"- **Website:** {result['url']}\n")
                f.write(f"- **Status:** {result['status']}\n\n")
        
        f.write("---\n\n")
        
        # Recommendations
        f.write("## 💡 Next Steps\n\n")
        f.write("1. **Find Missing URLs:** Research and add URLs for the organizations listed above\n")
        f.write("2. **Manual Verification:** Some organizations may require manual member list extraction\n")
        f.write("3. **Alternative Methods:** Consider:\n")
        f.write("   - LinkedIn company searches\n")
        f.write("   - Direct contact with organizations\n")
        f.write("   - Freedom of Information requests (for public bodies)\n")
        f.write("   - Industry directories and databases\n\n")
        
        f.write("---\n\n")
        
        # File Information
        f.write("## 📁 Generated Files\n\n")
        f.write("- `organization_members.json` - Complete raw data from scraping\n")
        f.write("- `member_lists/` - Individual text files for each organization with members\n")
        f.write("- `MEMBER_SCRAPING_SUMMARY.md` - This summary report\n")
        f.write("- `scraping.log` - Detailed scraping logs\n")
    
    print(f"✓ Created: {filename}")

def create_csv_export(results):
    """Create a CSV export of all members."""
    filename = 'all_members.csv'
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Organization,Member Name,Website,Member Count\n")
        
        for result in results:
            if result['member_count'] > 0:
                org_name = result['organization'].replace('"', '""')
                url = result['url'] or ''
                
                for member in result['members']:
                    member_clean = member.replace('"', '""')
                    f.write(f'"{org_name}","{member_clean}","{url}",{result["member_count"]}\n')
    
    print(f"✓ Created: {filename}")

def create_organization_list(results):
    """Create a simple list of all organizations and their member counts."""
    filename = 'ORGANIZATION_MEMBER_COUNTS.txt'
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("MEMBERSHIP ORGANIZATIONS - MEMBER COUNTS\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Organizations with members
        f.write("ORGANIZATIONS WITH MEMBER NAMES FOUND:\n")
        f.write("-" * 70 + "\n\n")
        
        success_orgs = [r for r in results if r['member_count'] > 0]
        for result in sorted(success_orgs, key=lambda x: x['member_count'], reverse=True):
            f.write(f"{result['organization']}: {result['member_count']} members\n")
        
        f.write(f"\nTotal: {len(success_orgs)} organizations, {sum(r['member_count'] for r in success_orgs)} members\n\n")
        
        # Organizations without members
        f.write("=" * 70 + "\n")
        f.write("ORGANIZATIONS WITHOUT MEMBER NAMES:\n")
        f.write("-" * 70 + "\n\n")
        
        no_member_orgs = [r for r in results if r['member_count'] == 0]
        for result in sorted(no_member_orgs, key=lambda x: x['organization']):
            status = "No URL" if not result['url'] else "No members found"
            f.write(f"{result['organization']}: {status}\n")
        
        f.write(f"\nTotal: {len(no_member_orgs)} organizations\n")
    
    print(f"✓ Created: {filename}")

def main():
    """Main function to generate all reports."""
    print("\n" + "=" * 70)
    print("GENERATING REPORTS")
    print("=" * 70 + "\n")
    
    results = load_results()
    
    # Create individual organization files
    print("Creating individual member list files...")
    org_count, total_members = create_organization_files(results)
    print(f"✓ Created {org_count} member list files with {total_members} total members\n")
    
    # Create summary report
    print("Creating summary report...")
    create_summary_report(results)
    
    # Create CSV export
    print("\nCreating CSV export...")
    create_csv_export(results)
    
    # Create simple organization list
    print("\nCreating organization member counts...")
    create_organization_list(results)
    
    print("\n" + "=" * 70)
    print("REPORT GENERATION COMPLETE")
    print("=" * 70 + "\n")

if __name__ == '__main__':
    main()
