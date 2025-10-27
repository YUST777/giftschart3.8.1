#!/usr/bin/env python3
"""
Analyze sticker prices from the MRKT API.

This script analyzes the sticker prices fetched from the MRKT API
and displays which stickers have prices and which don't.
"""

import json
import os

def analyze_prices():
    """Analyze the sticker prices and display results."""
    # Load the price data
    try:
        with open('sticker_prices/all_prices.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Price data file not found. Please run fetch_all_sticker_prices.py first.")
        return
    
    # Separate stickers with and without prices
    found = []
    not_found = []
    
    for collection, characters in data.items():
        for character, info in characters.items():
            if info.get('is_real_data'):
                found.append((
                    collection, 
                    character, 
                    info.get('price', 0), 
                    info.get('price_usd', 0)
                ))
            else:
                not_found.append((collection, character))
    
    # Sort stickers by price (highest first)
    found.sort(key=lambda x: x[2] or 0, reverse=True)
    not_found.sort(key=lambda x: (x[0], x[1]))
    
    # Display stickers with prices
    print(f"\nFound prices for {len(found)} stickers:\n")
    print("Collection                 Character                  Price (TON)    Price (USD)")
    print("="*80)
    
    for collection, character, price, price_usd in found:
        print(f"{collection:<25} {character:<25} {price:>10.2f}    ${price_usd:>10.2f}")
    
    # Display stickers without prices
    print(f"\n\nNo prices found for {len(not_found)} stickers:\n")
    print("Collection                 Character")
    print("="*50)
    
    for collection, character in not_found:
        print(f"{collection:<25} {character}")

if __name__ == "__main__":
    analyze_prices() 