#!/usr/bin/env python3
"""
Filter Collection Cards by MRKT API Price

This script filters sticker cards based on the specified collections and
removes any cards that don't have a valid price from the MRKT API.
"""

import os
import json
import shutil
import logging
from pathlib import Path
import mrkt_api_improved as api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('filter_collection_cards')

# Define collections and their stickers
COLLECTIONS = {
    "WAGMI HUB": ["EGG & HAMMER", "WAGMI AI AGENT"],
    "Cattea Life": ["Cattea Chaos"],
    "Doodles": ["Doodles Dark Mode"],
    "Pudgy & Friends": ["Pengu x Baby Shark", "Pengu x NASCAR"],
    "Lil Pudgys": ["Lil Pudgys x Baby Shark"],
    "Lazy & Rich": ["Chill or thrill", "Sloth Capital"],
    "Smeshariki": ["Chamomile Valley", "The Memes"],
    "SUNDOG": ["TO THE SUN"],
    "Kudai": ["GMI", "NGMI"],
    "BabyDoge": ["Mememania"],
    "PUCCA": ["PUCCA Moods"],
    "Not Pixel": ["Vice Pixel", "Pixioznik", "Zompixel", "Pixel phrases", "Films memes", 
                 "Smileface pack", "Tournament S1", "Random memes", "Cute pack", 
                 "Grass Pixel", "MacPixel", "SuperPixel", "DOGS Pixel", 
                 "Diamond Pixel", "Pixanos", "Retro Pixel", "Error Pixel"],
    "Lost Dogs": ["Lost Memeries", "Magic of the Way"],
    "Pudgy Penguins": ["Pengu Valentines", "Pengu CNY", "Blue Pengu", "Cool Blue Pengu"],
    "Blum": ["General", "Cook", "Curly", "No", "Worker", "Bunny", "Cap", "Cat"],
    "Flappy Bird": ["Blue Wings", "Light Glide", "Frost Flap", "Blush Flight", "Ruby Wings"],
    "Bored Stickers": ["CNY 2092", "3151", "3278", "4017", "5824", "6527", "9287", "9765", "9780"],
    "Dogs OG": ["Sheikh", "Not Cap", "King"],
    "Azuki": ["Shao"],
    "Ric Flair": ["Ric Flair"],
    "Notcoin": ["Not Memes", "flags"],
    "Dogs rewards": ["Gold bone", "silver bone", "full dig"]
}

def normalize_name(name):
    """Normalize a sticker name for file operations"""
    return name.replace(' ', '_').replace('&', 'and')

def get_sticker_filename(collection, sticker):
    """Get the expected filename for a sticker card"""
    # Try collection_sticker format
    collection_norm = normalize_name(collection)
    sticker_norm = normalize_name(sticker)
    filename1 = f"{collection_norm}_{sticker_norm}_card.png"
    
    # Try just sticker format
    filename2 = f"{sticker_norm}_card.png"
    
    return filename1, filename2

def process_collections(cards_dir='sticker_cards', backup_dir='sticker_cards_backup'):
    """Process all collections and filter cards based on MRKT API price data"""
    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Initialize counters and results
    results = {
        "total_checked": 0,
        "cards_with_price": 0,
        "cards_without_price": 0,
        "cards_not_found": 0,
        "kept_cards": [],
        "removed_cards": [],
        "missing_cards": []
    }
    
    # Process each collection and sticker
    for collection, stickers in COLLECTIONS.items():
        logger.info(f"Processing collection: {collection}")
        
        for sticker in stickers:
            results["total_checked"] += 1
            
            # Get possible filenames
            filename1, filename2 = get_sticker_filename(collection, sticker)
            
            # Check if either file exists
            file_path1 = os.path.join(cards_dir, filename1)
            file_path2 = os.path.join(cards_dir, filename2)
            
            if os.path.exists(file_path1):
                file_path = file_path1
                filename = filename1
                sticker_id = f"{collection}_{sticker}"
            elif os.path.exists(file_path2):
                file_path = file_path2
                filename = filename2
                sticker_id = sticker
            else:
                # Card not found
                logger.warning(f"❓ Card not found for {collection} - {sticker}")
                results["cards_not_found"] += 1
                results["missing_cards"].append({
                    "collection": collection,
                    "sticker": sticker,
                    "expected_files": [filename1, filename2]
                })
                continue
            
            # Check if the sticker has a price in the MRKT API
            logger.info(f"Checking price for {sticker_id}")
            price_data = api.get_sticker_price(sticker_id)
            
            if not price_data or price_data.get('price_ton', 0) <= 0:
                # Try with just the sticker name
                price_data = api.get_sticker_price(sticker)
            
            if price_data and price_data.get('price_ton', 0) > 0:
                # Card has a valid price, keep it
                results["cards_with_price"] += 1
                price = price_data.get('price_ton', 0)
                logger.info(f"✅ {sticker_id}: {price} TON - Keeping card")
                
                results["kept_cards"].append({
                    "collection": collection,
                    "sticker": sticker,
                    "filename": filename,
                    "price_ton": price,
                    "price_usd": price_data.get('price_usd', 0)
                })
            else:
                # Card doesn't have a valid price, move it to backup
                results["cards_without_price"] += 1
                logger.info(f"❌ {sticker_id}: No valid price - Moving to backup")
                
                # Move the card to backup
                dst_path = os.path.join(backup_dir, filename)
                shutil.move(file_path, dst_path)
                
                results["removed_cards"].append({
                    "collection": collection,
                    "sticker": sticker,
                    "filename": filename,
                    "reason": "No valid price data from MRKT API"
                })
    
    # Save results to JSON
    with open('collection_filtering_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    logger.info(f"Filtering complete:")
    logger.info(f"- Total stickers checked: {results['total_checked']}")
    logger.info(f"- Cards with price: {results['cards_with_price']}")
    logger.info(f"- Cards without price: {results['cards_without_price']}")
    logger.info(f"- Cards not found: {results['cards_not_found']}")
    logger.info(f"Results saved to collection_filtering_results.json")

def main():
    """Main function"""
    logger.info("Starting collection card filtering process")
    
    # Clear API cache to ensure fresh data
    api.clear_cache()
    
    # Process collections
    process_collections()
    
    logger.info("Collection card filtering process completed")

if __name__ == "__main__":
    main() 