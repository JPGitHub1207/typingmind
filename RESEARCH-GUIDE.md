# Further Education Networks Research Guide

## Overview

This guide helps you collect comprehensive data on:
1. **Regional Provider Networks** - Networks connecting FE providers within specific regions
2. **Communities of Practice** - Groups focused on sharing knowledge and best practices
3. **Membership Organisations** - Formal organisations with membership structures

## English Regions

1. North East
2. North West
3. Yorkshire and the Humber
4. East Midlands
5. West Midlands
6. East of England
7. London
8. South East
9. South West

## Key Sources to Research

### Government & Official Bodies

1. **Department for Education (DfE)**
   - Website: https://www.gov.uk/government/organisations/department-for-education
   - Look for: Regional contacts, FE provider lists, network directories

2. **Education and Skills Funding Agency (ESFA)**
   - Website: https://www.gov.uk/government/organisations/education-and-skills-funding-agency
   - Look for: Provider networks, regional contacts

3. **Ofsted**
   - Website: https://www.gov.uk/government/organisations/ofsted
   - Look for: FE provider directories by region

### National Membership Organisations

1. **Association of Colleges (AoC)**
   - Website: https://www.aoc.co.uk/
   - Regional branches and networks
   - Membership types: Full members, Associate members

2. **Association of Employment and Learning Providers (AELP)**
   - Website: https://www.aelp.org.uk/
   - Regional networks
   - Membership types: Full members, Associate members

3. **Association of School and College Leaders (ASCL)**
   - Website: https://www.ascl.org.uk/
   - FE branches

4. **NATSPEC (The Association of National Specialist Colleges)**
   - Website: https://www.natspec.org.uk/
   - Membership organisation for specialist FE colleges

5. **Landex (Land Based Colleges Aspiring to Excellence)**
   - Website: https://landex.org.uk/
   - Membership organisation for land-based colleges

6. **Collab Group**
   - Website: https://www.collabgroup.co.uk/
   - Membership organisation for large FE colleges

### Regional Networks (Examples to Verify)

#### North East
- North East Regional Network (verify)
- Tees Valley FE Network (verify)

#### North West
- Greater Manchester FE Network (verify)
- Lancashire FE Network (verify)
- Merseyside FE Network (verify)

#### Yorkshire and the Humber
- Yorkshire and Humber FE Network (verify)
- West Yorkshire FE Network (verify)

#### East Midlands
- East Midlands FE Network (verify)
- Derbyshire FE Network (verify)

#### West Midlands
- West Midlands FE Network (verify)
- Birmingham FE Network (verify)

#### East of England
- East of England FE Network (verify)
- Cambridgeshire FE Network (verify)

#### London
- London FE Network (verify)
- Greater London FE Network (verify)

#### South East
- South East FE Network (verify)
- Kent FE Network (verify)
- Sussex FE Network (verify)

#### South West
- South West FE Network (verify)
- Bristol FE Network (verify)

### Communities of Practice

1. **ETF (Education and Training Foundation)**
   - Website: https://www.et-foundation.co.uk/
   - Various communities of practice
   - Look for: Subject-specific communities, regional groups

2. **JISC**
   - Website: https://www.jisc.ac.uk/
   - Digital communities for FE
   - Regional networks

3. **LSIS (Learning and Skills Improvement Service)** - Now part of ETF
   - Communities of practice archives

4. **FE Research Network**
   - Research-focused communities

5. **FE Leadership Networks**
   - Various leadership-focused communities

### Subject-Specific Networks

1. **STEM Learning Networks**
2. **Digital Skills Networks**
3. **Apprenticeship Networks**
4. **Adult Learning Networks**
5. **ESOL Networks**
6. **Construction Skills Networks**
7. **Health and Social Care Networks**

### Research Strategy

1. **Start with National Bodies**
   - AoC regional pages
   - AELP regional networks
   - ETF communities

2. **Check Government Directories**
   - DfE provider lists
   - ESFA regional contacts
   - Ofsted regional offices

3. **Search Regional Websites**
   - Local Enterprise Partnerships (LEPs)
   - Combined Authorities
   - Regional Skills Partnerships

4. **Use Search Terms**
   - "[Region] further education network"
   - "[Region] FE provider network"
   - "[Region] college network"
   - "[Region] FE community of practice"
   - "[Region] FE membership organisation"

5. **Check Social Media**
   - LinkedIn groups
   - Twitter/X hashtags
   - Facebook groups

6. **Contact Directly**
   - Email regional AoC offices
   - Contact local FE colleges for network information
   - Reach out to ETF regional contacts

## Data Collection Template

For each entry, collect:

```json
{
  "name": "Full official name",
  "region": "English region",
  "memberCount": "Number or 'Unknown'",
  "membershipTypes": ["Type 1", "Type 2"],
  "website": "URL",
  "description": "What they do",
  "contactEmail": "Contact if available",
  "notes": "Additional information"
}
```

## Using the Data Collection Tools

1. **Edit JSON directly**: Open `further-education-networks.json` and add entries
2. **Generate report**: Run `node collect-data.js report`
3. **Export to CSV**: Run `node collect-data.js export`

## Notes

- Member counts may be approximate or unavailable
- Some networks may span multiple regions
- Membership types vary by organisation
- Some may be informal networks without formal membership structures
- Verify all information from official sources
