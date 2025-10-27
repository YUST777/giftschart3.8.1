#!/usr/bin/env python3
"""
List all characters available in the MRKT API
"""

import mrkt_api_improved as mrkt_api
from tabulate import tabulate

def main():
    """List all characters available in the MRKT API"""
    print("\n===== All Characters in MRKT API =====\n")
    
    # Get a working token
    token = mrkt_api.get_working_token()
    if not token:
        print("Failed to get a working token")
        return
    
    print("Fetching character data...")
    
    # Fetch all characters
    characters = mrkt_api.fetch_characters()
    if not characters:
        print("Failed to fetch characters")
        return
    
    # Save raw data to file
    with open("all_mrkt_stickers.txt", "w") as f:
        f.write("===== All Characters in MRKT API =====\n\n")
        
        # Group by collection
        collections = {}
        for char in characters:
            collection_name = char.get("collection", {}).get("name", "Unknown")
            if collection_name not in collections:
                collections[collection_name] = []
            collections[collection_name].append(char)
        
        # Print each collection
        for collection_name, chars in collections.items():
            f.write(f"\n== Collection: {collection_name} ==\n")
            
            # Sort characters by name
            chars.sort(key=lambda x: x.get("name", ""))
            
            for char in chars:
                character_name = char.get("name", "Unknown")
                price_nano_ton = char.get("price", 0)
                
                # Convert from nano TON to TON
                price_ton = mrkt_api.convert_nano_ton(price_nano_ton)
                
                f.write(f"\n- Character: {character_name}\n")
                f.write(f"    Price: {price_ton:.6f} TON (${price_ton * mrkt_api.TON_TO_USD:.2f} USD)\n")
                
                # Add other details
                collection_id = char.get("collection", {}).get("id", "Unknown")
                character_id = char.get("id", "Unknown")
                f.write(f"    Collection ID: {collection_id}\n")
                f.write(f"    Character ID: {character_id}\n")
    
    print(f"Saved {len(characters)} characters to all_mrkt_stickers.txt")
    print(f"Found {len(collections)} collections")

if __name__ == "__main__":
    main() 