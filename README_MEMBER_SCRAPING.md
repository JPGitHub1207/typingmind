# Membership Organization Member Names Scraping

## Overview

This repository contains scripts and data for scraping member names from 60 training provider membership organizations across England. The data collection focused on identifying individual member organizations within each network.

## Summary

**Date:** 2025-11-16

### Results
- **Total Organizations:** 60
- **Organizations with Members Found:** 3
- **Total Member Names Collected:** 404

### Successfully Scraped Organizations

1. **Natspec** - 178 members
   - National Association of Specialist Colleges
   - Website: https://www.natspec.org.uk
   
2. **HOLEX** - 160 members  
   - Association of Adult and Community Learning
   - Website: https://www.holex.org.uk
   
3. **AELP London Strategic Forum** - 66 members
   - Association of Employment and Learning Providers
   - Website: https://www.aelp.org.uk

## Files Generated

### Data Files
- **`organization_members.json`** - Complete raw JSON data from scraping (34KB)
- **`all_members.csv`** - CSV export of all 404 members across organizations (405 rows)

### Individual Member Lists
Located in `member_lists/` directory:
- `holex_members.txt` - 160 HOLEX members
- `natspec_members.txt` - 178 Natspec members  
- `aelp_london_strategic_forum_members.txt` - 66 AELP members

### Reports
- **`MEMBER_SCRAPING_SUMMARY.md`** - Comprehensive summary with statistics and sample data
- **`ORGANIZATION_MEMBER_COUNTS.txt`** - Simple list of all organizations and member counts
- **`scraping.log`** - Detailed scraping logs (46KB)

### Scripts
- **`scrape_organization_members.py`** - Main web scraping script
- **`generate_reports.py`** - Report generation script

## Technical Details

### Scraping Strategy

The scraper uses multiple strategies to extract member names:

1. **List Detection** - Identifies `<ul>` and `<ol>` elements containing member lists
2. **Table Parsing** - Extracts names from HTML tables
3. **Container Analysis** - Finds divs/sections with member-related classes
4. **Link Following** - Discovers and scrapes dedicated member list pages

### Filtering

The scraper filters out:
- Navigation elements
- Header/footer content
- Common non-member text (login, contact, etc.)
- Duplicate entries

### Member Name Validation

Text is considered a likely member name if it:
- Contains 10-300 characters
- Includes education-related keywords (college, council, university, etc.)
- Has multiple words forming an organization name
- Doesn't match navigation patterns

## Organizations Without Members Found

### Missing URLs (49 organizations)

Many organizations lack publicly available websites. These include:
- Regional provider networks (e.g., "D2N2 Provider Network", "Humber Learning Consortium")
- Local skills forums (e.g., "Thames Valley Berkshire Provider Network")
- Communities of practice

### Failed Scraping (8 organizations)

These organizations have URLs but scraping failed due to:
- Network restrictions in the remote environment
- Password-protected member directories
- JavaScript-rendered content
- Different website structures

Organizations that failed:
- Collab Group
- Independent Training Provider Association
- Yorkshire Learning Providers
- Lancashire Colleges Group
- West Yorkshire Consortium of Colleges
- North East Learning Providers
- Kent Association of Training Organisations
- Eastern Colleges Group

## Next Steps

### To Complete This Task

1. **Find Missing URLs**
   - Research the 49 organizations without URLs
   - Check for LinkedIn pages, social media profiles
   - Contact organizations directly

2. **Manual Verification**
   - Some scraped data contains non-member text that should be filtered
   - Example: HOLEX list includes some policy text
   - Example: Natspec includes cookie notices
   
3. **Alternative Data Sources**
   - LinkedIn company searches
   - Freedom of Information requests (for public bodies)
   - Industry directories
   - Direct contact with organization administrators

4. **Improve Scraping**
   - Add JavaScript rendering support (Selenium/Playwright)
   - Handle login-protected directories
   - Add more URL guessing patterns
   - Implement retry logic for network errors

## Usage

### Run the Scraper

```bash
# Install dependencies
pip3 install requests beautifulsoup4 lxml

# Run the scraper (takes ~5 minutes)
python3 scrape_organization_members.py

# Generate reports
python3 generate_reports.py
```

### Access the Data

**View all members in CSV:**
```bash
cat all_members.csv
```

**View specific organization members:**
```bash
cat member_lists/holex_members.txt
```

**View summary:**
```bash
cat MEMBER_SCRAPING_SUMMARY.md
```

## Data Quality Notes

### Known Issues

1. **HOLEX data includes some non-member text** (policy announcements)
   - First 8 entries are from homepage content
   - Actual member names start from entry 9

2. **Natspec data includes some UI elements**
   - Cookie notices and login prompts captured
   - Actual college names are mixed in

3. **AELP data has promotional content**
   - News headlines and marketing text included
   - Actual member names are sparse

### Recommended Cleanup

Manual review and filtering recommended for:
- Removing policy text and announcements
- Filtering out cookie notices and UI elements  
- Validating organization names against official sources
- Removing duplicate entries with slight variations

## Contact

For questions or issues with this data collection, please refer to the scraping logs at `scraping.log`.

---

**Generated:** 2025-11-16  
**Branch:** cursor/scrape-membership-organization-member-names-8066
