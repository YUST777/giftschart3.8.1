#!/usr/bin/env python3
"""
Extract the top 50 stickers by price from the MRKT API
"""

import mrkt_api_improved as mrkt_api
import json
import os
from tabulate import tabulate

def main():
    """Extract the top 50 stickers by price"""
    print("Fetching character data from API...")
    characters = mrkt_api.fetch_characters()
    if not characters:
        print("Failed to fetch characters")
        return
    
    # Extract name and price data
    sticker_data = []
    for char in characters:
        name = char.get('name', 'Unknown')
        collection_id = char.get('stickerCollectionId')
        character_id = char.get('id')
        price_nano_ton = char.get('floorPriceNanoTons', 0)
        price_ton = mrkt_api.convert_nano_ton(price_nano_ton)
        price_usd = price_ton * mrkt_api.TON_TO_USD
        supply = char.get('supply', 'Unknown')
        
        sticker_data.append({
            'name': name,
            'collection_id': collection_id,
            'character_id': character_id,
            'price_ton': price_ton,
            'price_usd': price_usd,
            'supply': supply
        })
    
    # Sort by price (descending)
    sticker_data.sort(key=lambda x: x['price_ton'], reverse=True)
    
    # Take top 50
    top_stickers = sticker_data[:50]
    
    # Print as table
    table_data = []
    for i, sticker in enumerate(top_stickers, 1):
        table_data.append([
            i,
            sticker['name'],
            f"{sticker['price_ton']:.2f} TON",
            f"${sticker['price_usd']:.2f}",
            sticker['supply'],
            f"{sticker['collection_id']}-{sticker['character_id']}"
        ])
    
    print("\n===== Top 50 Stickers by Price =====\n")
    print(tabulate(table_data, headers=['Rank', 'Name', 'Price (TON)', 'Price (USD)', 'Supply', 'ID (Coll-Char)']))
    print(f"\nTotal stickers in API: {len(sticker_data)}")
    
    # Save as JSON
    with open('top_50_stickers.json', 'w') as f:
        json.dump(top_stickers, f, indent=2)
    
    print(f"\nSaved top 50 stickers to top_50_stickers.json")

if __name__ == "__main__":
    main() 