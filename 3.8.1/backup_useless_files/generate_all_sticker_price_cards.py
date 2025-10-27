#!/usr/bin/env python3
"""
Generate All Sticker Price Cards

This script generates price cards for all stickers with prices using the updated design
that includes hardcoded sale prices and supply information.
"""

import os
import json
import time
import logging
import argparse
from datetime import datetime
from sticker_price_card_generator import generate_price_card, load_price_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("generate_all_sticker_price_cards")

# Get script directory for cross-platform compatibility
script_dir = os.path.dirname(os.path.abspath(__file__))

# Constants
PRICE_DATA_FILE = os.path.join(script_dir, "sticker_price_results.json")
OUTPUT_DIR = os.path.join(script_dir, "Sticker_Price_Cards")

def check_data_freshness():
    """Check if the price data is fresh or cached"""
    try:
        if not os.path.exists(PRICE_DATA_FILE):
            return "NO DATA", 0
        
        with open(PRICE_DATA_FILE, 'r') as f:
            data = json.load(f)
        
        timestamp = data.get("timestamp", 0)
        current_time = time.time()
        age_seconds = current_time - timestamp
        age_minutes = age_seconds / 60
        
        if age_minutes < 32:
            return "FRESH", age_minutes, data.get("human_timestamp", "unknown")
        else:
            return "STALE", age_minutes, data.get("human_timestamp", "unknown")
    except Exception as e:
        logger.error(f"Error checking data freshness: {e}")
        return "UNKNOWN", 0, "unknown"

def generate_all_price_cards(price_data, output_dir):
    """Generate price cards for all stickers with prices"""
    if not price_data or 'stickers_with_prices' not in price_data:
        logger.error("Invalid price data")
        print("❌ Invalid price data format")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Import cache counters from sticker_price_card_generator
    from sticker_price_card_generator import cached_usage, live_api_usage
    
    # Reset counters
    import sticker_price_card_generator
    sticker_price_card_generator.cached_usage = 0
    sticker_price_card_generator.live_api_usage = 0
    
    # Track results
    successful = 0
    failed = 0
    
    # Get data freshness
    status, age, timestamp = check_data_freshness()
    freshness_indicator = "🟢" if status == "FRESH" else "🔴" if status == "STALE" else "⚪"
    
    # Get stickers
    stickers = price_data['stickers_with_prices']
    total_stickers = len(stickers)
    
    print(f"\n{freshness_indicator} GENERATING PRICE CARDS: Using {status} data ({age:.2f} minutes old)")
    print(f"📅 Data timestamp: {timestamp}")
    print(f"🎯 Generating {total_stickers} price cards...")
    
    # Track start time
    start_time = time.time()
    
    # Generate cards for each sticker with price
    for i, item in enumerate(stickers):
        collection = item['collection']
        sticker = item['sticker']
        price = item['price']
        
        # Calculate progress percentage
        progress = (i + 1) / total_stickers * 100
        
        logger.info(f"Generating price card for {collection} - {sticker}: {price} TON")
        
        card_start_time = time.time()
        result = generate_price_card(collection, sticker, price, output_dir)
        card_time = time.time() - card_start_time
        
        if result:
            successful += 1
            print(f"  ✅ {i+1}/{total_stickers} {collection} - {sticker}: {price} TON ({card_time:.2f}s)")
        else:
            failed += 1
            print(f"  ❌ {i+1}/{total_stickers} {collection} - {sticker}: Failed ({card_time:.2f}s)")
        
        # Create a progress bar (every 5%)
        if (i + 1) % max(1, int(total_stickers / 20)) == 0 or i == total_stickers - 1:
            bar_length = 30
            filled_length = int(bar_length * progress / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            # Calculate ETA
            elapsed_time = time.time() - start_time
            items_per_second = (i + 1) / elapsed_time if elapsed_time > 0 else 0
            remaining_items = total_stickers - (i + 1)
            eta_seconds = remaining_items / items_per_second if items_per_second > 0 else 0
            
            print(f"  [{bar}] {progress:.1f}% Complete - ETA: {int(eta_seconds//60)}m {int(eta_seconds%60)}s")
    
    # Get final cache counts
    from sticker_price_card_generator import cached_usage, live_api_usage
    
    # Calculate total execution time
    execution_time = time.time() - start_time
    
    logger.info(f"Price card generation complete: {successful} successful ({cached_usage} from cache, {live_api_usage} from live API), {failed} failed in {execution_time:.2f} seconds")
    print(f"\n✅ GENERATION COMPLETE: {successful}/{total_stickers} cards generated successfully")
    print(f"📊 Data sources: {cached_usage} from cache, {live_api_usage} from live API")
    print(f"⏱️ Total execution time: {execution_time:.2f} seconds")
    print(f"⚡ Average time per card: {(execution_time/total_stickers):.2f} seconds")
    
    if failed > 0:
        print(f"⚠️ {failed} cards failed to generate")
    
    return successful, failed

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Generate all sticker price cards")
    parser.add_argument("--output-dir", default=OUTPUT_DIR, help="Output directory for generated cards")
    parser.add_argument("--price-file", default=PRICE_DATA_FILE, help="Price data JSON file")
    
    args = parser.parse_args()
    
    # Load price data
    try:
        print(f"📂 Loading price data from {args.price_file}...")
        with open(args.price_file, 'r') as f:
            price_data = json.load(f)
        
        # Check data timestamp
        if "human_timestamp" in price_data:
            print(f"📅 Price data timestamp: {price_data['human_timestamp']}")
    except Exception as e:
        logger.error(f"Failed to load price data: {e}")
        print(f"❌ Failed to load price data: {e}")
        return
    
    # Generate cards
    generate_all_price_cards(price_data, args.output_dir)

if __name__ == "__main__":
    main() 