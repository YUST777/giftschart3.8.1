#!/usr/bin/env python3
import os
import sys
import time
import requests
import json

# Add the virtual environment path
script_dir = os.path.dirname(os.path.abspath(__file__))

# Update the site_packages path to work on both Linux and Windows
# Try multiple possible locations for the site-packages directory
possible_site_packages = [
    os.path.join(script_dir, "venv", "lib", "python3.12", "site-packages"),  # Linux
    os.path.join(script_dir, "venv", "Lib", "site-packages"),                # Windows
    os.path.join(script_dir, "venv", "lib", "python3.11", "site-packages"),  # Older Python version
    os.path.join(script_dir, "venv", "lib", "python3.10", "site-packages"),  # Older Python version
]

# Try each path and use the first one that exists
for site_packages in possible_site_packages:
    if os.path.exists(site_packages):
        sys.path.append(site_packages)
        print(f"Added site-packages to path: {site_packages}")
        break
else:
    print("Could not find site-packages directory in virtual environment")

# Import the Tonnel API
try:
    from tonnelmp import getGifts
    from bot_config import TONNEL_API_AUTH
    
    # The 5 problematic gifts
    problem_gifts = [
        "Heart Locket",
        "Lush Bouquet",
        "Bow Tie",
        "Heroic Helmet",
        "Snow Globe"
    ]
    
    # Generate variations for each name
    def generate_variations(name):
        variations = []
        # Original name
        variations.append(name)
        
        # Lowercase
        variations.append(name.lower())
        
        # No spaces
        variations.append(name.replace(" ", ""))
        
        # Lowercase no spaces
        variations.append(name.lower().replace(" ", ""))
        
        # Hyphenated
        variations.append(name.replace(" ", "-"))
        
        # Lowercase hyphenated
        variations.append(name.lower().replace(" ", "-"))
        
        # Common spelling variations
        if "Locket" in name:
            variations.append(name.replace("Locket", "Pendant"))
            variations.append(name.replace("Heart Locket", "Heart-Shaped Locket"))
            variations.append("Locket")
            variations.append("Heart Pendant")
            
        if "Bouquet" in name:
            variations.append(name.replace("Bouquet", "Flowers"))
            variations.append("Flower Bouquet")
            variations.append("Bouquet")
            
        if "Bow Tie" in name:
            variations.append("Bowtie")
            variations.append("Bow-Tie")
            variations.append("BowTie")
            variations.append("Tie")
            
        if "Heroic" in name:
            variations.append(name.replace("Heroic", "Hero"))
            variations.append(name.replace("Heroic Helmet", "Hero's Helmet"))
            variations.append(name.replace("Heroic Helmet", "Warrior Helmet"))
            variations.append("Helmet")
            
        if "Snow Globe" in name:
            variations.append("Snowglobe")
            variations.append("Snow-Globe")
            variations.append("Globe")
            
        # Remove duplicates
        return list(set(variations))

    print("=== Testing Name Variations for Problematic Gifts ===")
    print()
    
    # Try each name variation
    for gift_name in problem_gifts:
        print(f"=== Testing variations for {gift_name} ===")
        variations = generate_variations(gift_name)
        
        print(f"Generated {len(variations)} variations to test")
        
        for variation in variations:
            print(f"\nTrying: '{variation}'")
            try:
                result = getGifts(gift_name=variation, limit=1, authData=TONNEL_API_AUTH)
                if result:
                    print(f"✅ SUCCESS! Found with name: {result[0]['name']} (Model: {result[0]['model']})")
                else:
                    print("❌ Not found")
            except Exception as e:
                print(f"❌ Error: {e}")
                
            # Don't send too many requests too quickly
            time.sleep(0.5)
            
        print("\n" + "-"*50 + "\n")

    # Also try using the direct API endpoint
    print("\n=== Testing Direct API Endpoint ===")
    print("Endpoint: https://gifts3.tonnel.network/api/filterStats")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get('https://gifts3.tonnel.network/api/filterStats', headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API call successful!")
            
            # Get all gift names from the API
            gift_names = []
            if data.get('status') == 'success' and 'data' in data:
                gift_names = list(data['data'].keys())
                print(f"Found {len(gift_names)} gift names in API")
                
                # Check for possible matches to our problematic gifts
                print("\nPossible matches for problematic gifts:")
                for problem_gift in problem_gifts:
                    problem_lower = problem_gift.lower()
                    found_matches = False
                    for api_name in gift_names:
                        if problem_lower in api_name.lower() or any(part.lower() in api_name.lower() for part in problem_lower.split()):
                            print(f"- {problem_gift} might match: {api_name}")
                            found_matches = True
                    
                    if not found_matches:
                        print(f"- No possible matches found for {problem_gift}")
            else:
                print("❌ API returned unexpected format")
        else:
            print(f"❌ API call failed with status code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error accessing API endpoint: {e}")

except ImportError as e:
    print(f"Error importing required modules: {e}")
except Exception as e:
    print(f"Unexpected error: {e}") 