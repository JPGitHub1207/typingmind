#!/usr/bin/env python3
"""
Script to verify if networks are specifically for Further Education providers
(directors/staff from different FE organizations).
"""

# Research notes on the three networks
NETWORKS_ANALYSIS = {
    "London Skills for Growth": {
        "url": "https://www.londonskillsforgrowth.co.uk",
        "description": "Network of training providers supporting skills development in London",
        "verification_needed": True,
        "notes": [
            "Name suggests it's for 'skills for growth' - could be training providers rather than FE colleges",
            "Need to verify if this is specifically for FE college directors/staff",
            "May be a consortium of independent training providers rather than FE colleges"
        ]
    },
    "London Learning Consortium": {
        "url": "https://www.londonlearningconsortium.co.uk",
        "description": "Consortium of training providers in London",
        "verification_needed": True,
        "notes": [
            "Described as 'consortium of training providers' - not specifically FE colleges",
            "Training providers are different from Further Education colleges",
            "FE colleges are institutions like City and Islington College, Westminster Kingsway College",
            "Training providers are often private companies delivering apprenticeships/training",
            "May not be a network for FE college directors/staff"
        ]
    },
    "London Providers Network": {
        "url": None,
        "description": "Network of independent training providers in London",
        "verification_needed": True,
        "notes": [
            "Explicitly described as 'independent training providers'",
            "Training providers ≠ Further Education colleges",
            "FE colleges are public institutions (like Capital City College Group)",
            "Training providers are private companies (like apprenticeship training providers)",
            "This is likely NOT a network for FE college directors/staff"
        ]
    }
}

# Actual FE Provider Networks (where directors/staff from FE colleges meet)
ACTUAL_FE_NETWORKS = [
    {
        "name": "Association of Colleges (AoC) London Region",
        "type": "Network/Association",
        "description": "Regional network representing further education colleges in London",
        "website": "https://www.aoc.co.uk",
        "is_fe_provider_network": True,
        "notes": "This is THE main network for FE college principals, directors, and staff"
    },
    {
        "name": "London Colleges Group",
        "type": "FE Provider Network",
        "description": "Network of London FE colleges (may be informal or through AoC)",
        "website": None,
        "is_fe_provider_network": True,
        "notes": "FE colleges collaborate through AoC London region"
    },
    {
        "name": "Greater London Authority Skills for Londoners",
        "type": "Partnership Network",
        "description": "Strategic partnership including FE colleges, GLA, and training providers",
        "website": "https://www.london.gov.uk/what-we-do/skills-and-employment",
        "is_fe_provider_network": True,
        "notes": "Includes FE colleges but also other stakeholders"
    }
]

def print_analysis():
    print("=" * 80)
    print("VERIFICATION: Are these Further Education Provider Networks?")
    print("=" * 80)
    print("\nKEY DISTINCTION:")
    print("  • Further Education (FE) Colleges = Public institutions like")
    print("    Capital City College Group, New City College, etc.")
    print("  • Training Providers = Private companies delivering apprenticeships/training")
    print("\n" + "=" * 80)
    
    print("\n1. LONDON SKILLS FOR GROWTH")
    print("-" * 80)
    info = NETWORKS_ANALYSIS["London Skills for Growth"]
    print(f"URL: {info['url']}")
    print(f"Description: {info['description']}")
    print("\nAnalysis:")
    for note in info['notes']:
        print(f"  • {note}")
    print("\nVERDICT: Likely NOT specifically for FE college directors/staff")
    print("         (Appears to be for training providers)")
    
    print("\n2. LONDON LEARNING CONSORTIUM")
    print("-" * 80)
    info = NETWORKS_ANALYSIS["London Learning Consortium"]
    print(f"URL: {info['url']}")
    print(f"Description: {info['description']}")
    print("\nAnalysis:")
    for note in info['notes']:
        print(f"  • {note}")
    print("\nVERDICT: Likely NOT specifically for FE college directors/staff")
    print("         (Explicitly described as 'training providers', not FE colleges)")
    
    print("\n3. LONDON PROVIDERS NETWORK")
    print("-" * 80)
    info = NETWORKS_ANALYSIS["London Providers Network"]
    print(f"URL: {info['url'] or 'Not available'}")
    print(f"Description: {info['description']}")
    print("\nAnalysis:")
    for note in info['notes']:
        print(f"  • {note}")
    print("\nVERDICT: NOT a network for FE college directors/staff")
    print("         (Explicitly for 'independent training providers')")
    
    print("\n" + "=" * 80)
    print("ACTUAL FE PROVIDER NETWORKS (where FE college directors/staff meet):")
    print("=" * 80)
    for network in ACTUAL_FE_NETWORKS:
        print(f"\n• {network['name']}")
        print(f"  Type: {network['type']}")
        print(f"  Description: {network['description']}")
        if network['website']:
            print(f"  Website: {network['website']}")
        print(f"  Note: {network['notes']}")
    
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print("""
The three networks you asked about appear to be for TRAINING PROVIDERS 
(independent/private training companies), NOT for Further Education colleges.

For networks where FE college directors/staff from different FE organizations 
come together, the main network is:

  • Association of Colleges (AoC) London Region
     https://www.aoc.co.uk
  
This is the primary network where FE college principals, directors, and staff 
from London's FE colleges collaborate and meet.
    """)

if __name__ == "__main__":
    print_analysis()
