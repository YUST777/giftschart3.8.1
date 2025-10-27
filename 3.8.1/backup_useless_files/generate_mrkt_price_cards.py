#!/usr/bin/env python3
"""
Generate Sticker Cards with MRKT API Price Data

This script generates sticker cards for all stickers that have valid prices
in the MRKT API. It filters out stickers without valid prices.
"""

import os
import json
import logging
import argparse
from pathlib import Path
import mrkt_api_improved as api
import subprocess
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('generate_mrkt_cards')

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

def check_sticker_price(collection, sticker):
    """Check if a sticker has a valid price in the MRKT API"""
    # Try collection_sticker format
    sticker_id = f"{collection}_{sticker}"
    price_data = api.get_sticker_price(sticker_id)
    
    if price_data and price_data.get('price_ton', 0) > 0:
        logger.info(f"Found price for {sticker_id}: {price_data.get('price_ton')} TON")
        return price_data
    
    # Try with just the sticker name
    price_data = api.get_sticker_price(sticker)
    if price_data and price_data.get('price_ton', 0) > 0:
        logger.info(f"Found price for {sticker}: {price_data.get('price_ton')} TON")
        return price_data
    
    # Try with just the collection name
    price_data = api.get_sticker_price(collection)
    if price_data and price_data.get('price_ton', 0) > 0:
        logger.info(f"Found price for {collection}: {price_data.get('price_ton')} TON")
        return price_data
    
    logger.warning(f"No valid price found for {collection} - {sticker}")
    return None

def generate_card_with_price_check(collection, sticker, output_dir, debug=False):
    """Generate a card for a sticker if it has a valid price"""
    # Check if the sticker has a valid price
    price_data = check_sticker_price(collection, sticker)
    
    if not price_data:
        logger.warning(f"❌ {collection} - {sticker}: No valid price - Skipping card generation")
        return False, None
    
    # Sticker has a valid price, generate the card
    price = price_data.get('price_ton', 0)
    logger.info(f"✅ {collection} - {sticker}: {price} TON - Generating card")
    
    # Normalize names for file operations
    collection_norm = normalize_name(collection)
    sticker_norm = normalize_name(sticker)
    
    # Define output path
    output_path = os.path.join(output_dir, f"{collection_norm}_{sticker_norm}_card.png")
    
    if debug:
        # In debug mode, just create a placeholder file with price info
        with open(output_path.replace('.png', '.txt'), 'w') as f:
            f.write(f"Collection: {collection}\n")
            f.write(f"Sticker: {sticker}\n")
            f.write(f"Price: {price} TON (${price_data.get('price_usd', 0):.2f})\n")
            f.write(f"Source: {price_data.get('source', 'MRKT API')}\n")
        
        logger.info(f"Created debug info for {collection} - {sticker}")
        return True, output_path.replace('.png', '.txt')
    
    # Generate the card using sticker_card_generator.py
    try:
        cmd = [
            "python3", "sticker_card_generator.py",
            "--collection", collection,
            "--sticker", sticker,
            "--output-dir", output_dir,
            "--include-price",
            "--use-mrkt-api"
        ]
        
        subprocess.run(cmd, check=True)
        
        # Verify the card was created
        if os.path.exists(output_path):
            logger.info(f"Successfully generated card: {output_path}")
            return True, output_path
        else:
            logger.error(f"Card generation command completed but file not found: {output_path}")
            return False, None
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate card for {collection} - {sticker}: {e}")
        return False, None

def process_collections(output_dir='mrkt_cards', debug=False):
    """Process all collections and generate cards for stickers with valid prices"""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create backup directory for cards without prices
    backup_dir = 'no_price_cards'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Initialize results
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
            
            # Check if sticker has a valid price and generate card if it does
            success, output_path = generate_card_with_price_check(collection, sticker, output_dir, debug)
            
            if success:
                results["cards_generated"] += 1
                results["generated_cards"].append({
                    "collection": collection,
                    "sticker": sticker,
                    "output_path": output_path
                })
            else:
                results["cards_skipped"] += 1
                results["skipped_cards"].append({
                    "collection": collection,
                    "sticker": sticker,
                    "reason": "No valid price data from MRKT API"
                })
                
                # Check if a card exists in the sticker_cards directory
                collection_norm = normalize_name(collection)
                sticker_norm = normalize_name(sticker)
                existing_card = os.path.join('sticker_cards', f"{collection_norm}_{sticker_norm}_card.png")
                
                if os.path.exists(existing_card):
                    # Move the card to the backup directory
                    backup_path = os.path.join(backup_dir, f"{collection_norm}_{sticker_norm}_card.png")
                    logger.info(f"Moving existing card to backup: {existing_card} -> {backup_path}")
                    shutil.move(existing_card, backup_path)
    
    # Save results to JSON
    with open('mrkt_card_generation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    logger.info(f"Card generation complete:")
    logger.info(f"- Total stickers checked: {results['total_checked']}")
    logger.info(f"- Cards generated: {results['cards_generated']}")
    logger.info(f"- Cards skipped: {results['cards_skipped']}")
    logger.info(f"Results saved to mrkt_card_generation_results.json")
    
    return results

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Generate sticker cards with MRKT API price check')
    parser.add_argument('--output-dir', default='mrkt_cards',
                        help='Output directory for generated cards')
    parser.add_argument('--debug', action='store_true',
                        help='Run in debug mode without generating actual cards')
    args = parser.parse_args()
    
    logger.info("Starting card generation process with MRKT API price check")
    
    # Clear API cache to ensure fresh data
    api.clear_cache()
    
    # Process collections
    results = process_collections(args.output_dir, args.debug)
    
    # Copy generated cards to the main sticker_cards directory
    if results["cards_generated"] > 0:
        logger.info(f"Copying {results['cards_generated']} cards to sticker_cards directory")
        
        for card_info in results["generated_cards"]:
            output_path = card_info["output_path"]
            if output_path and os.path.exists(output_path):
                # Get the filename
                filename = os.path.basename(output_path)
                
                # Define destination path
                dest_path = os.path.join('sticker_cards', filename)
                
                # Copy the file
                shutil.copy(output_path, dest_path)
                logger.info(f"Copied {filename} to sticker_cards directory")
    
    logger.info("Card generation process completed")

if __name__ == "__main__":
    main() 