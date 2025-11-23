# Address Verification Report

## Summary
- **Total Companies**: 1,441
- **Valid Addresses**: 1,431 (99.3%)
- **Addresses Requiring Verification**: 10 (0.7%)

## Issues Found

### 1. Formatting Issues (4 addresses)
These addresses have double commas that should be cleaned:
- W @ H SAFETY SOLUTIONS LTD - "The Bailey,, Cumberland Road..."
- NATIONAL FILM AND TELEVISION SCHOOL - "Station Road,, Beaconsfield,, Bucks..."
- TENDEAN LIMITED - "Gloucester,, Gloucestershire..."
- NATIONAL HORSERACING COLLEGE LIMITED - "Great North Road,, Doncaster..."

### 2. Addresses Outside UK (6 addresses)
These addresses appear to be in other countries and may be incorrect:

1. **FORESTRY COMMISSION** (UKPRN: Check CSV)
   - Current: "Forestry Commission, Jasikan, Jasikan District, Oti Region, Ghana"
   - Issue: Address is in Ghana, not UK

2. **THE UNIVERSITY OF READING** (UKPRN: Check CSV)
   - Current: "Christian Science Reading Room, 927, Yonge Street, Rosedale-Moore Park, University—Rosedale, Toronto, Golden Horseshoe, Ontario, M4W 3C7, Canada"
   - Issue: Address is in Canada, not UK

3. **WESTON COLLEGE OF FURTHER AND HIGHER EDUCATION** (UKPRN: Check CSV)
   - Current: "Weston Community Center, Duff Drive, White Course Apartments, State College, Centre County, Pennsylvania, 16802, United States of America"
   - Issue: Address is in USA, not UK

4. **ESSEX COUNTY COUNCIL** (UKPRN: Check CSV)
   - Current: "Council on Aging, Lafayette Road, Salisbury, Essex County, Massachusetts, 01952, United States of America"
   - Issue: Address is in USA (Massachusetts), not UK

5. **ARDEN UNIVERSITY LIMITED** (UKPRN: Check CSV)
   - Current: "Arden Villas Boulevard, University, Orange County, Florida, 32817, United States of America"
   - Issue: Address is in USA (Florida), not UK

6. **FASHION - ENTER LTD** (UKPRN: Check CSV)
   - Current: "Unit 4 Crusader Estate, 167 Hermitage Road, Harringay, London, N4 1LZ"
   - Issue: False positive - this is actually a valid UK address

## Recommendations

1. **Fix Formatting Issues**: Clean up double commas in 4 addresses
2. **Verify Foreign Addresses**: Check if these 5 companies actually have offices outside UK, or if addresses are incorrect
3. **Look Up Registered Addresses**: Use Companies House API to find official registered addresses for companies with incorrect addresses

## Next Steps

To verify registered addresses:
1. Get a Companies House API key from https://developer.company-information.service.gov.uk/
2. Run: `python3 lookup_registered_addresses.py companies_data_verified.csv`
3. Review and update addresses as needed
