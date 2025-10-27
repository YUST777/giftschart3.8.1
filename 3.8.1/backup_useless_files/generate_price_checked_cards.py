#!/usr/bin/env python3
"""
Generate Sticker Cards with MRKT API Price Check

This script generates sticker cards only for stickers that have valid prices
in the MRKT API. It integrates the card generation process with the price check.
"""

import os
import json
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
logger = logging.getLogger('generate_cards')

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

def check_price(sticker_name):
    """Check if a sticker has a valid price in the MRKT API"""
    price_data = api.get_sticker_price(sticker_name)
    
    if price_data and price_data.get('price_ton', 0) > 0:
        return price_data
    
    return None

def generate_card(collection, sticker, output_dir='sticker_cards'):
    """Generate a card for the specified sticker if it has a valid price"""
    # Check if the sticker has a price
    sticker_id = f"{collection}_{sticker}"
    price_data = check_price(sticker_id)
    
    if not price_data:
        # Try with just the sticker name
        price_data = check_price(sticker)
    
    if not price_data:
        logger.warning(f"❌ {sticker_id}: No valid price - Skipping card generation")
        return False
    
    # Sticker has a valid price, generate the card
    price = price_data.get('price_ton', 0)
    logger.info(f"✅ {sticker_id}: {price} TON - Generating card")
    
    # Normalize names for file operations
    collection_norm = normalize_name(collection)
    sticker_norm = normalize_name(sticker)
    
    # Determine the card generation command
    # This depends on your existing card generation script
    # Adjust this to match your actual card generation process
    try:
        # Assuming your card generation script is called sticker_card_generator.py
        # and it takes collection and sticker name as arguments
        cmd = [
            "python3", "sticker_card_generator.py",
            "--collection", collection,
            "--sticker", sticker,
            "--output-dir", output_dir,
            "--include-price"  # Assuming your script has this option
        ]
        
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate card for {sticker_id}: {e}")
        return False

def process_collections(output_dir='sticker_cards'):
    """Process all collections and generate cards for stickers with valid prices"""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Initialize counters and results
    results = {
        "total_checked": 0,
        "cards_generated": 0,
        "cards_skipped": 0,
        "generated_cards": [],
        "skipped_cards": []
    }
    
    # Process each collection and sticker
    for collection, stickers in COLLECTIONS.items():
        logger.info(f"Processing collection: {collection}")
        
        for sticker in stickers:
            results["total_checked"] += 1
            
            # Generate card if it has a valid price
            if generate_card(collection, sticker, output_dir):
                results["cards_generated"] += 1
                results["generated_cards"].append({
                    "collection": collection,
                    "sticker": sticker
                })
            else:
                results["cards_skipped"] += 1
                results["skipped_cards"].append({
                    "collection": collection,
                    "sticker": sticker,
                    "reason": "No valid price data from MRKT API"
                })
    
    # Save results to JSON
    with open('card_generation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    logger.info(f"Card generation complete:")
    logger.info(f"- Total stickers checked: {results['total_checked']}")
    logger.info(f"- Cards generated: {results['cards_generated']}")
    logger.info(f"- Cards skipped: {results['cards_skipped']}")
    logger.info(f"Results saved to card_generation_results.json")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Generate sticker cards with MRKT API price check')
    parser.add_argument('--output-dir', default='sticker_cards',
                        help='Output directory for generated cards')
    args = parser.parse_args()
    
    logger.info("Starting card generation process with price check")
    
    # Clear API cache to ensure fresh data
    api.clear_cache()
    
    # Process collections
    process_collections(args.output_dir)
    
    logger.info("Card generation process completed")

if __name__ == "__main__":
    main() 