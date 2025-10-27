#!/usr/bin/env python3
"""
Update sticker prices with real data from the MRKT API

This script:
1. Reads existing price data from sticker_price_results.json
2. Updates prices with real data from the MRKT API where available
3. Saves the updated price data back to the file
"""

import os
import json
import time
import logging
from datetime import datetime
import mrkt_api_improved as mrkt_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("update_prices")

# Get script directory for cross-platform compatibility
script_dir = os.path.dirname(os.path.abspath(__file__))
# Path to the sticker price results file
PRICE_DATA_FILE = "sticker_price_results.json"

def load_existing_prices():
    """
    Load existing price data from sticker_price_results.json
    
    Returns:
        dict: Existing price data or empty dict if file doesn't exist
    """
    try:
        if os.path.exists(PRICE_DATA_FILE):
            with open(PRICE_DATA_FILE, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded existing price data with {len(data.get('stickers_with_prices', []))} entries")
                return data
        else:
            logger.warning(f"Price file not found: {PRICE_DATA_FILE}")
            return {"stickers_with_prices": [], "timestamp": time.time()}
    except Exception as e:
        logger.error(f"Error loading price data: {e}")
        return {"stickers_with_prices": [], "timestamp": time.time()}

def save_updated_prices(price_data):
    """
    Save updated price data to sticker_price_results.json
    
    Args:
        price_data (dict): Updated price data
    """
    try:
        # Update timestamp
        price_data["timestamp"] = time.time()
        
        # Save data with pretty formatting
        with open(PRICE_DATA_FILE, 'w') as f:
            json.dump(price_data, f, indent=2)
            
        logger.info(f"Updated price data saved to {PRICE_DATA_FILE}")
    except Exception as e:
        logger.error(f"Error saving price data: {e}")

def update_sticker_prices():
    """
    Update sticker prices with real data from the MRKT API
    """
    # Load existing prices
    existing_data = load_existing_prices()
    
    # Initialize counters
    updated_count = 0
    failed_count = 0
    skipped_count = 0
    
    # Get all stickers
    stickers = existing_data.get("stickers_with_prices", [])
    total_stickers = len(stickers)
    
    logger.info(f"Starting price update for {total_stickers} stickers")
    print(f"🔄 UPDATING: Refreshing prices for {total_stickers} stickers...")
    
    # Update prices for each sticker
    for i, sticker_data in enumerate(stickers):
        collection = sticker_data.get("collection", "")
        sticker = sticker_data.get("sticker", "")
        search_term = f"{collection} {sticker}"
        
        logger.info(f"Processing {i+1}/{total_stickers}: {search_term}")
        
        try:
            # Get price data from MRKT API
            price_data = mrkt_api.get_sticker_price(search_term, use_cache=False)
            
            # Check if we got price data
            if price_data and "price" in price_data:
                # Update the price data
                sticker_data["price"] = price_data.get("price", 0)
                
                logger.info(f"✅ Updated price for {search_term}: {price_data.get('price', 0)} TON")
                print(f"  ✅ Updated: {collection} - {sticker}: {price_data.get('price', 0)} TON")
                updated_count += 1
            else:
                logger.info(f"ℹ️ No price data for {search_term}")
                print(f"  ⚠️ No data: {collection} - {sticker}")
                skipped_count += 1
        except Exception as e:
            logger.error(f"Error updating price for {search_term}: {e}")
            print(f"  ❌ Failed: {collection} - {sticker}: {str(e)}")
            failed_count += 1
        
        # Add a small delay to avoid rate limiting
        time.sleep(0.5)
    
    # Save the updated prices
    save_updated_prices(existing_data)
    
    # Print summary
    summary = f"Price update complete: {updated_count} updated, {skipped_count} skipped, {failed_count} failed"
    logger.info(summary)
    print(f"📊 {summary}")
    
    return updated_count > 0

if __name__ == "__main__":
    # Test API connection first
    logger.info("Testing MRKT API connection...")
    token = mrkt_api.get_working_token()
    
    if token:
        logger.info(f"API authentication successful, token: {token[:10]}...")
        update_sticker_prices()
    else:
        logger.error("API authentication failed, cannot update prices") 