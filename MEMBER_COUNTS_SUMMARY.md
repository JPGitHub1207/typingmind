# Organization Member Counts - Summary Report

This document provides member counts for UK training provider organizations as found through web scraping of their public websites.

## Summary

Out of 60 organizations searched, **6 organizations** had publicly available member counts or member lists:

## Organizations with Member Counts Found

| Organization | Member Count | Source | URL |
|-------------|--------------|--------|-----|
| **Northern Skills Network** | **400 members** | Website states member count | https://www.northernskillsnetwork.co.uk |
| **HOLEX** | **174 members** | Member list extracted | https://www.holex.org.uk |
| **Greater Manchester Learning Provider Network** | **140 members** | Website states member count | https://www.gmlpn.co.uk |
| **Sussex Council of Training Providers** | **80 members** | Website states member count | https://www.sctp.org.uk |
| **Natspec** | **40 members** | Member list extracted | https://www.natspec.org.uk |
| **AELP London Strategic Forum** | **34 members** | Member list extracted | https://www.aelp.org.uk |

## Detailed Findings

### Northern Skills Network
- **Member Count**: 400 members
- **Website**: https://www.northernskillsnetwork.co.uk
- **Notes**: Website explicitly states "400 members"

### HOLEX
- **Member Count**: 174 members
- **Website**: https://www.holex.org.uk
- **Notes**: Full member list found and extracted from member directory page

### Greater Manchester Learning Provider Network (GMLPN)
- **Member Count**: 140 members
- **Website**: https://www.gmlpn.co.uk
- **Notes**: Website states "140 members"

### Sussex Council of Training Providers (SCTP)
- **Member Count**: 80 members
- **Website**: https://www.sctp.org.uk
- **Notes**: Website states "80 members"

### Natspec
- **Member Count**: 40 members
- **Website**: https://www.natspec.org.uk
- **Notes**: Member list extracted from website (member directory requires login, but some information available on main pages)

### AELP London Strategic Forum
- **Member Count**: 34 members
- **Website**: https://www.aelp.org.uk
- **Notes**: Member information found on website

## Organizations Where No Public Member Information Was Found

The following 54 organizations either:
- Do not have publicly accessible websites
- Have websites but do not publish member counts or member lists publicly
- Require membership login to access member information
- Could not be located through web search
- May have changed names or merged with other organizations

1. Collab Group
2. Independent Training Provider Association
3. Networks of Providers Community of Practice
4. ETF Centres for Excellence in SEND
5. North East Learning Providers
6. Tees Valley Learning Provider Network
7. Northumberland Learning Providers Network
8. Greater Merseyside Learning Providers Federation
9. Lancashire Work Based Learning Executive Forum
10. Cumbria Work Based Learning Provider Forum
11. Cheshire and Warrington Learning Provider Network
12. Lancashire Colleges Group
13. Yorkshire Learning Providers
14. South Yorkshire Providers Network
15. Humber Learning Consortium
16. West Yorkshire Consortium of Colleges
17. North Yorkshire Provider Network
18. East Midlands Provider Network
19. East Midlands Accelerated Apprenticeship Network
20. D2N2 Provider Network
21. Leicester and Leicestershire Provider Network
22. Lincolnshire Provider Network
23. Birmingham and Solihull Provider Network
24. Black Country Provider Network
25. Coventry and Warwickshire Provider Network
26. Herefordshire and Worcestershire Training Provider Association
27. Marches Provider Network
28. Staffordshire and Stoke-on-Trent Provider Network
29. West Midlands 5G Skills Network
30. Essex Provider Network
31. Bedfordshire and Hertfordshire Provider Network
32. Suffolk Provider Network
33. Cambridgeshire and Peterborough Provider Network
34. Norfolk Learning and Skills Provider Network
35. Eastern Colleges Group
36. Kent Association of Training Organisations
37. ALPS
38. ALPHI
39. Thames Valley Berkshire Provider Network
40. Buckinghamshire Skills Provider Network
41. Oxfordshire Provider Network
42. Solent Training Provider Network
43. Western Training Provider Network
44. Dorset and Somerset Training Provider Network
45. Devon and Cornwall Training Provider Network
46. Gloucestershire and Wiltshire Partnership
47. Swindon and Wiltshire Provider Network
48. Somerset Education Business Partnership
49. Heart of the South West Colleges Partnership
50. Cornwall and Isles of Scilly Skills Hub
51. Local London Skills Providers Network
52. West London Alliance Skills & Employment
53. South London Partnership Skills
54. Central London Forward Skills Programmes

## Methodology

1. **URL Discovery**: Attempted to find organization websites using:
   - Known URL patterns (org.uk, co.uk domains)
   - Web search via DuckDuckGo
   - Manual URL verification

2. **Data Extraction**: For each found website:
   - Searched for explicit member counts in text
   - Looked for member directory/list pages
   - Extracted member names where available
   - Used pattern matching to find numbers associated with membership

3. **Limitations**:
   - Some organizations require login to access member information
   - Some organizations may not publish member counts publicly
   - Web scraping may miss dynamically loaded content
   - Some organizations may have changed names or merged

## Data Files

- **Full Results**: `member_results.json` - Contains detailed scraping results for all organizations
- **Scraping Script**: `scrape_members.py` - Python script used for web scraping
- **Output Log**: `scrape_output.log` - Console output from scraping process

## Notes

- This data was collected through automated web scraping
- Member counts are as stated on organization websites or calculated from member lists
- Some organizations may have updated their member counts since scraping
- Organizations without public member information may still have members, but this information is not publicly available
- For organizations requiring login, member information may be available to members only

---

*Report generated through automated web scraping*
