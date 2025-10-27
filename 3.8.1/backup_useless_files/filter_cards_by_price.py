#!/usr/bin/env python3
"""
Filter Sticker Cards by MRKT API Price

This script checks all sticker cards against the MRKT API and removes any cards
that don't have a valid price from the API. Only cards with real price data are kept.
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
logger = logging.getLogger('filter_cards')

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

def get_all_sticker_names():
    """Get a flat list of all sticker names from the collections"""
    all_stickers = []
    for collection, stickers in COLLECTIONS.items():
        for sticker in stickers:
            all_stickers.append(sticker)
            # Also add collection_sticker format
            all_stickers.append(f"{collection}_{sticker}")
    return all_stickers

def check_card_exists(sticker_name, cards_dir='sticker_cards'):
    """Check if a card exists for the given sticker name"""
    normalized = normalize_name(sticker_name)
    card_path = os.path.join(cards_dir, f"{normalized}_card.png")
    return os.path.exists(card_path)

def filter_cards_by_price():
    """
    Filter sticker cards based on MRKT API price data.
    Remove cards that don't have valid price data.
    """
    # Directory containing sticker cards
    cards_dir = 'sticker_cards'
    backup_dir = 'sticker_cards_backup'
    
    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Get all sticker names
    all_stickers = get_all_sticker_names()
    
    # Initialize counters
    total_cards = 0
    cards_with_price = 0
    cards_without_price = 0
    
    # Get all card files
    card_files = [f for f in os.listdir(cards_dir) if f.endswith('_card.png')]
    total_cards = len(card_files)
    
    logger.info(f"Found {total_cards} card files in {cards_dir}")
    
    # Create a results file
    results = {
        "total_cards": total_cards,
        "cards_with_price": 0,
        "cards_without_price": 0,
        "kept_cards": [],
        "removed_cards": []
    }
    
    # Process each card
    for card_file in card_files:
        # Extract sticker name from filename
        sticker_name = card_file.replace('_card.png', '')
        
        # Check if the sticker has a price in the MRKT API
        logger.info(f"Checking price for {sticker_name}")
        price_data = api.get_sticker_price(sticker_name)
        
        if price_data and price_data.get('price_ton', 0) > 0:
            # Card has a valid price, keep it
            cards_with_price += 1
            price = price_data.get('price_ton', 0)
            logger.info(f"✅ {sticker_name}: {price} TON - Keeping card")
            
            results["kept_cards"].append({
                "name": sticker_name,
                "price_ton": price,
                "price_usd": price_data.get('price_usd', 0)
            })
        else:
            # Card doesn't have a valid price, move it to backup
            cards_without_price += 1
            logger.info(f"❌ {sticker_name}: No valid price - Moving to backup")
            
            # Move the card to backup
            src_path = os.path.join(cards_dir, card_file)
            dst_path = os.path.join(backup_dir, card_file)
            shutil.move(src_path, dst_path)
            
            results["removed_cards"].append({
                "name": sticker_name,
                "reason": "No valid price data from MRKT API"
            })
    
    # Update results
    results["cards_with_price"] = cards_with_price
    results["cards_without_price"] = cards_without_price
    
    # Save results to JSON
    with open('card_filtering_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Filtering complete:")
    logger.info(f"- Total cards: {total_cards}")
    logger.info(f"- Cards with price: {cards_with_price}")
    logger.info(f"- Cards without price: {cards_without_price}")
    logger.info(f"Results saved to card_filtering_results.json")

def main():
    """Main function"""
    logger.info("Starting card filtering process")
    
    # Clear API cache to ensure fresh data
    api.clear_cache()
    
    # Filter cards by price
    filter_cards_by_price()
    
    logger.info("Card filtering process completed")

if __name__ == "__main__":
    main() 