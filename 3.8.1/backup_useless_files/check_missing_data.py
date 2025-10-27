#!/usr/bin/env python3
"""
Check Missing Data

This script checks which stickers are missing sale price data in our hardcoded mapping.
"""

import json
import hardcoded_sticker_data as hsd

def load_price_data():
    """Load price data from the JSON file"""
    try:
        with open("sticker_price_results.json", 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading price data: {e}")
        return None

def main():
    """Main function"""
    # Load price data
    price_data = load_price_data()
    if not price_data:
        print("Failed to load price data")
        return
    
    # Track stickers with missing data
    missing_sale_price = []
    default_sale_price = []
    
    # Check each sticker in price_data
    for item in price_data['stickers_with_prices']:
        collection = item['collection']
        sticker = item['sticker']
        
        # Get hardcoded data
        key = f"{collection}|{sticker}"
        is_explicit = key in hsd.STICKER_DATA
        data = hsd.get_sticker_data(collection, sticker)
        
        # Check if sale price is None
        if data["sale_price"] is None:
            missing_sale_price.append(f"{collection} - {sticker}")
        # Check if sale price is the default value (3888) and not explicitly set
        elif data["sale_price"] == 3888 and not is_explicit:
            default_sale_price.append(f"{collection} - {sticker}")
    
    # Print results
    print(f"Total stickers in price data: {len(price_data['stickers_with_prices'])}")
    
    print(f"\nStickers with missing sale price data: {len(missing_sale_price)}")
    for sticker in missing_sale_price:
        print(f"  - {sticker}")
    
    print(f"\nStickers with default sale price (3888) but not explicitly set: {len(default_sale_price)}")
    for sticker in default_sale_price:
        print(f"  - {sticker}")
    
    # Group by collection
    collections = {}
    for sticker in default_sale_price:
        collection = sticker.split(" - ")[0]
        if collection not in collections:
            collections[collection] = []
        collections[collection].append(sticker.split(" - ")[1])
    
    print("\nStickers with default sale price grouped by collection:")
    for collection, stickers in collections.items():
        print(f"\n{collection} ({len(stickers)} stickers):")
        for sticker in stickers:
            print(f"  - {sticker}")

if __name__ == "__main__":
    main() 