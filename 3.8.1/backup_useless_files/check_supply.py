#!/usr/bin/env python3
"""
Check Supply Information

This script checks the supply information for a specific sticker.
"""

import json
import sys

def main():
    # Load price data
    with open('sticker_price_results.json', 'r') as f:
        data = json.load(f)
    
    # Check if collection and sticker are provided
    if len(sys.argv) < 3:
        print("Usage: python check_supply.py <collection> <sticker>")
        print("Example: python check_supply.py 'Pudgy & Friends' 'Pengu x NASCAR'")
        
        # Print all available stickers
        print("\nAvailable stickers:")
        for item in data['stickers_with_prices']:
            print(f"Collection: {item['collection']}, Sticker: {item['sticker']}, Price: {item['price']} TON, Supply: {item.get('supply', 'N/A')}")
        return
    
    # Get collection and sticker from command line arguments
    collection = sys.argv[1]
    sticker = sys.argv[2]
    
    # Find the sticker
    found = False
    for item in data['stickers_with_prices']:
        if item['collection'] == collection and item['sticker'] == sticker:
            print(f"Collection: {item['collection']}")
            print(f"Sticker: {item['sticker']}")
            print(f"Price: {item['price']} TON")
            print(f"Supply: {item.get('supply', 'N/A')}")
            found = True
            break
    
    if not found:
        print(f"Sticker '{sticker}' in collection '{collection}' not found.")

if __name__ == "__main__":
    main() 