#!/usr/bin/env python3
"""
Script to find all further education training provider networks in London.
"""

import json
from datetime import datetime

# Known Further Education Training Provider Networks in London
# This list includes major networks and organizations

LONDON_FE_NETWORKS = [
    {
        "name": "Capital City College Group",
        "type": "College Group",
        "description": "One of London's largest further education groups, operating multiple colleges",
        "website": "https://www.capitalccg.ac.uk",
        "colleges": [
            "City and Islington College",
            "Westminster Kingsway College",
            "The College of Haringey, Enfield and North East London"
        ]
    },
    {
        "name": "London South East Colleges",
        "type": "College Group",
        "description": "Large further education group serving South East London",
        "website": "https://www.lsec.ac.uk",
        "colleges": [
            "Bromley College",
            "Bexley College",
            "Greenwich Community College"
        ]
    },
    {
        "name": "New City College",
        "type": "College Group",
        "description": "Further education group operating across East London",
        "website": "https://www.ncclondon.ac.uk",
        "colleges": [
            "Hackney Community College",
            "Redbridge College",
            "Epping Forest College",
            "Havering College",
            "Tower Hamlets College"
        ]
    },
    {
        "name": "West Thames College",
        "type": "College",
        "description": "Further education college in West London",
        "website": "https://www.west-thames.ac.uk"
    },
    {
        "name": "Richmond and Hillcroft Adult Community College",
        "type": "College",
        "description": "Adult and community education provider",
        "website": "https://www.rhacc.ac.uk"
    },
    {
        "name": "Waltham Forest College",
        "type": "College",
        "description": "Further education college in North East London",
        "website": "https://www.waltham.ac.uk"
    },
    {
        "name": "Lambeth College",
        "type": "College",
        "description": "Further education college in South London",
        "website": "https://www.lambethcollege.ac.uk"
    },
    {
        "name": "Croydon College",
        "type": "College",
        "description": "Further education college in South London",
        "website": "https://www.croydon.ac.uk"
    },
    {
        "name": "Kensington and Chelsea College",
        "type": "College",
        "description": "Further education college in West London",
        "website": "https://www.kcc.ac.uk"
    },
    {
        "name": "Hammersmith and West London College",
        "type": "College",
        "description": "Further education college in West London",
        "website": "https://www.wlc.ac.uk"
    },
    {
        "name": "Barnet and Southgate College",
        "type": "College Group",
        "description": "Further education group in North London",
        "website": "https://www.barnetsouthgate.ac.uk"
    },
    {
        "name": "City of Westminster College",
        "type": "College",
        "description": "Further education college in Central London",
        "website": "https://www.cwc.ac.uk"
    },
    {
        "name": "Hackney Community College",
        "type": "College",
        "description": "Further education college in East London (part of New City College)",
        "website": "https://www.ncclondon.ac.uk"
    },
    {
        "name": "Lewisham Southwark College",
        "type": "College Group",
        "description": "Further education group in South London",
        "website": "https://www.lscollege.ac.uk"
    },
    {
        "name": "Ealing, Hammersmith and West London College",
        "type": "College Group",
        "description": "Further education group in West London",
        "website": "https://www.wlc.ac.uk"
    },
    {
        "name": "London Skills for Growth",
        "type": "Training Provider Network",
        "description": "Network of training providers supporting skills development in London",
        "website": "https://www.londonskillsforgrowth.co.uk"
    },
    {
        "name": "Association of Colleges (AoC) London Region",
        "type": "Network/Association",
        "description": "Regional network representing further education colleges in London",
        "website": "https://www.aoc.co.uk"
    },
    {
        "name": "Greater London Authority Skills for Londoners",
        "type": "Network/Partnership",
        "description": "Strategic partnership for skills and training in London",
        "website": "https://www.london.gov.uk/what-we-do/skills-and-employment"
    },
    {
        "name": "London Learning Consortium",
        "type": "Training Provider Network",
        "description": "Consortium of training providers in London",
        "website": "https://www.londonlearningconsortium.co.uk"
    },
    {
        "name": "London Apprenticeship Ambassador Network",
        "type": "Network",
        "description": "Network promoting apprenticeships in London",
        "website": "https://www.gov.uk/government/groups/london-apprenticeship-ambassador-network"
    },
    {
        "name": "London Providers Network",
        "type": "Training Provider Network",
        "description": "Network of independent training providers in London",
        "website": None
    },
    {
        "name": "Skills for Londoners Business Partnership",
        "type": "Partnership Network",
        "description": "Partnership between GLA, colleges, and training providers",
        "website": "https://www.london.gov.uk/what-we-do/skills-and-employment/skills-londoners"
    }
]

def search_additional_networks():
    """
    Function to search for additional networks online.
    This would require web scraping or API access.
    """
    # Placeholder for web search functionality
    # Could use Google Custom Search API, DuckDuckGo API, or web scraping
    pass

def generate_report():
    """Generate a comprehensive report of all networks."""
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_networks": len(LONDON_FE_NETWORKS),
        "networks_by_type": {},
        "networks": LONDON_FE_NETWORKS
    }
    
    # Count by type
    for network in LONDON_FE_NETWORKS:
        net_type = network.get("type", "Unknown")
        report["networks_by_type"][net_type] = report["networks_by_type"].get(net_type, 0) + 1
    
    return report

def save_to_json(filename="london_fe_networks.json"):
    """Save the networks data to a JSON file."""
    report = generate_report()
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved {len(LONDON_FE_NETWORKS)} networks to {filename}")

def save_to_csv(filename="london_fe_networks.csv"):
    """Save the networks data to a CSV file."""
    import csv
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Type', 'Description', 'Website', 'Colleges/Institutions'])
        for network in LONDON_FE_NETWORKS:
            colleges = ', '.join(network.get('colleges', [])) if 'colleges' in network else ''
            website = network.get('website', '') or ''
            writer.writerow([
                network['name'],
                network['type'],
                network['description'],
                website,
                colleges
            ])
    print(f"✓ Saved {len(LONDON_FE_NETWORKS)} networks to {filename}")

def print_summary():
    """Print a summary of all networks."""
    report = generate_report()
    
    print("=" * 80)
    print("LONDON FURTHER EDUCATION TRAINING PROVIDER NETWORKS")
    print("=" * 80)
    print(f"\nTotal Networks Found: {report['total_networks']}\n")
    
    print("Networks by Type:")
    for net_type, count in sorted(report['networks_by_type'].items()):
        print(f"  - {net_type}: {count}")
    
    print("\n" + "=" * 80)
    print("DETAILED LISTING")
    print("=" * 80 + "\n")
    
    for i, network in enumerate(LONDON_FE_NETWORKS, 1):
        print(f"{i}. {network['name']}")
        print(f"   Type: {network['type']}")
        print(f"   Description: {network['description']}")
        if 'website' in network and network['website']:
            print(f"   Website: {network['website']}")
        if 'colleges' in network:
            print(f"   Colleges/Institutions:")
            for college in network['colleges']:
                print(f"     - {college}")
        print()

if __name__ == "__main__":
    print_summary()
    save_to_json()
    save_to_csv()
    
    print("\n" + "=" * 80)
    print("Note: This is a preliminary list. For comprehensive information,")
    print("consider searching official government databases and FE sector directories.")
    print("=" * 80)
