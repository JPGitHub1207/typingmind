# Member Names Files Summary

## Files Containing Member Names:

### 1. **member_results.json** (26KB)
   - **Primary source file** containing ALL member information
   - Contains raw scraping data for all 60 organizations
   - Includes:
     - Member names (where available)
     - Member counts
     - Organization URLs
     - Scraping status
   - **HOLEX section**: Contains 174 items (includes navigation + 140 actual member names)

### 2. **HOLEX_MEMBER_NAMES.txt** (6.1KB)
   - **Clean, extracted list** of 140 HOLEX member names
   - Filtered to show only actual member organizations
   - One member name per line, numbered 1-140
   - This is the easiest file to read for HOLEX members

### 3. **MEMBER_COUNTS_SUMMARY.md** (6.1KB)
   - Summary report with member counts for all organizations
   - Does not include individual member names
   - Contains methodology and notes

### 4. **MEMBER_COUNTS.txt** (480 bytes)
   - Simple text list of organizations with member counts
   - Does not include member names

## Summary:

**For actual member names, use:**
- **HOLEX_MEMBER_NAMES.txt** - Clean list of 140 HOLEX members
- **member_results.json** - Complete raw data for all organizations (includes HOLEX's 140 members plus navigation items)

**Note:** HOLEX is the only organization where we successfully extracted a substantial list of actual member names. Other organizations either:
- Don't publish member lists publicly
- Require login to access member directories
- Only show member counts without names
