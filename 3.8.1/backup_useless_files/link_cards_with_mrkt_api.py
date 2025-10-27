#!/usr/bin/env python3
"""
Link Sticker Cards with MRKT API

This script links sticker cards with the MRKT API to ensure that only cards
with valid prices are kept. It moves cards without valid prices to a backup directory.
"""

import os
import json
import shutil
import logging
import subprocess
import argparse
from pathlib import Path
import mrkt_api_improved as api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('link_cards_with_mrkt')

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

def get_sticker_price(collection, sticker):
    """Get the price for a sticker from the MRKT API"""
    # First try with collection_sticker format
    sticker_id = f"{collection}_{sticker}"
    price_data = api.get_sticker_price(sticker_id)
    
    # If we found a price, return it
    if price_data and 'price' in price_data and price_data['price'] > 0:
        logger.info(f"Found price for {sticker_id}: {price_data['price']} TON")
        return price_data
    
    # Try with just the sticker name
    price_data = api.get_sticker_price(sticker)
    if price_data and 'price' in price_data and price_data['price'] > 0:
        logger.info(f"Found price for {sticker}: {price_data['price']} TON")
        return price_data
    
    # Try with just the collection name
    price_data = api.get_sticker_price(collection)
    if price_data and 'price' in price_data and price_data['price'] > 0:
        logger.info(f"Found price for {collection}: {price_data['price']} TON")
        return price_data
    
    logger.warning(f"No valid price found for {collection} - {sticker}")
    return None

def process_sticker_card(collection, sticker, cards_dir, backup_dir, regenerate=False):
    """Process a sticker card, checking if it has a valid price"""
    collection_norm = normalize_name(collection)
    sticker_norm = normalize_name(sticker)
    card_filename = f"{collection_norm}_{sticker_norm}_card.png"
    card_path = os.path.join(cards_dir, card_filename)
    
    # Get price data from MRKT API
    price_data = get_sticker_price(collection, sticker)
    
    if price_data and price_data.get('price', 0) > 0:
        # Sticker has a valid price
        price = price_data['price']
        logger.info(f"✅ {collection} - {sticker}: {price} TON - Valid price")
        
        # If regenerate flag is set, regenerate the card with price information
        if regenerate and os.path.exists(card_path):
            logger.info(f"Regenerating card for {collection} - {sticker} with price information")
            
            # Generate a new card with price information
            cmd = [
                "python3", "sticker_card_generator.py",
                "--collection", collection,
                "--sticker", sticker,
                "--output-dir", cards_dir,
                "--include-price",
                "--use-mrkt-api"
            ]
            
            try:
                subprocess.run(cmd, check=True)
                logger.info(f"Successfully regenerated card with price: {card_path}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to regenerate card: {e}")
        
        return True, price
    else:
        # Sticker has no valid price
        logger.warning(f"❌ {collection} - {sticker}: No valid price")
        
        # If the card exists, move it to the backup directory
        if os.path.exists(card_path):
            backup_path = os.path.join(backup_dir, card_filename)
            logger.info(f"Moving card to backup: {card_path} -> {backup_path}")
            
            # Create backup directory if it doesn't exist
            os.makedirs(backup_dir, exist_ok=True)
            
            # Move the card
            shutil.move(card_path, backup_path)
        
        return False, 0

def process_all_stickers(cards_dir="sticker_cards", backup_dir="no_price_cards", regenerate=False):
    """Process all stickers in the collections"""
    # Create directories if they don't exist
    os.makedirs(cards_dir, exist_ok=True)
    os.makedirs(backup_dir, exist_ok=True)
    
    # Initialize results
    results = {
        "total_checked": 0,
        "valid_prices": 0,
        "no_prices": 0,
        "stickers_with_prices": [],
        "stickers_without_prices": []
    }
    
    # Process each collection and sticker
    for collection, stickers in COLLECTIONS.items():
        logger.info(f"Processing collection: {collection}")
        
        for sticker in stickers:
            results["total_checked"] += 1
            
            # Process the sticker card
            has_price, price = process_sticker_card(
                collection, sticker, cards_dir, backup_dir, regenerate
            )
            
            if has_price:
                results["valid_prices"] += 1
                results["stickers_with_prices"].append({
                    "collection": collection,
                    "sticker": sticker,
                    "price": price
                })
            else:
                results["no_prices"] += 1
                results["stickers_without_prices"].append({
                    "collection": collection,
                    "sticker": sticker
                })
    
    # Save results to JSON
    with open('sticker_price_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    logger.info(f"Processing complete:")
    logger.info(f"- Total stickers checked: {results['total_checked']}")
    logger.info(f"- Stickers with valid prices: {results['valid_prices']}")
    logger.info(f"- Stickers without prices: {results['no_prices']}")
    logger.info(f"Results saved to sticker_price_results.json")
    
    return results

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Link sticker cards with MRKT API prices')
    parser.add_argument('--cards-dir', default='sticker_cards',
                      help='Directory containing sticker cards')
    parser.add_argument('--backup-dir', default='no_price_cards',
                      help='Directory to move cards without prices')
    parser.add_argument('--regenerate', action='store_true',
                      help='Regenerate cards with price information')
    args = parser.parse_args()
    
    logger.info("Starting to link sticker cards with MRKT API prices")
    
    # Clear API cache to ensure fresh data
    api.clear_cache()
    
    # Process all stickers
    process_all_stickers(args.cards_dir, args.backup_dir, args.regenerate)
    
    logger.info("Processing completed")

if __name__ == "__main__":
    main() 