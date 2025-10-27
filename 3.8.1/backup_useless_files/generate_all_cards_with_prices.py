#!/usr/bin/env python3
"""
Generate All Sticker Cards with Price Information

This script generates cards for all stickers with price information from the MRKT API.
It serves as a convenient wrapper around the link_cards_with_mrkt_api.py script.
"""

import os
import sys
import subprocess
import logging
import argparse
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('generate_all_cards')

def generate_all_cards(output_dir="sticker_cards_with_prices", backup_dir="no_price_cards", force=False):
    """Generate all sticker cards with price information"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create backup directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    
    # Check if output directory is empty or force flag is set
    if os.listdir(output_dir) and not force:
        logger.error(f"Output directory '{output_dir}' is not empty. Use --force to overwrite.")
        return False
    
    logger.info("Generating all sticker cards with price information...")
    
    # Run the link_cards_with_mrkt_api.py script with regenerate flag
    cmd = [
        "python3", "link_cards_with_mrkt_api.py",
        "--regenerate",
        "--cards-dir", output_dir,
        "--backup-dir", backup_dir
    ]
    
    try:
        subprocess.run(cmd, check=True)
        logger.info(f"Successfully generated all sticker cards with price information in '{output_dir}'")
        
        # Check the results
        if os.path.exists("sticker_price_results.json"):
            with open("sticker_price_results.json", "r") as f:
                results = json.load(f)
                
            logger.info(f"Generated {results['valid_prices']} cards with price information")
            logger.info(f"Skipped {results['no_prices']} cards without price information")
            
            # Print top 5 most valuable stickers
            if results['stickers_with_prices']:
                logger.info("Top 5 most valuable stickers:")
                
                # Sort by price (descending)
                sorted_stickers = sorted(
                    results['stickers_with_prices'],
                    key=lambda x: x['price'],
                    reverse=True
                )
                
                for i, sticker in enumerate(sorted_stickers[:5]):
                    logger.info(f"{i+1}. {sticker['collection']} - {sticker['sticker']}: {sticker['price']} TON")
        
        return True
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate cards: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Generate all sticker cards with price information")
    parser.add_argument("--output-dir", default="sticker_cards_with_prices",
                      help="Output directory for generated cards")
    parser.add_argument("--backup-dir", default="no_price_cards",
                      help="Directory to move cards without prices")
    parser.add_argument("--force", action="store_true",
                      help="Force generation even if output directory is not empty")
    
    args = parser.parse_args()
    
    if generate_all_cards(args.output_dir, args.backup_dir, args.force):
        logger.info("Card generation completed successfully")
    else:
        logger.error("Card generation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()