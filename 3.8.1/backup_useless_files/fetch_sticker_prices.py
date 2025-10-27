#!/usr/bin/env python3
"""
Fetch Sticker Prices

This script fetches the latest prices for all stickers from the MRKT API
and updates the sticker_price_results.json file.

It's designed to be run periodically by the scheduled_sticker_update.py script.
"""

import os
import sys
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
logger = logging.getLogger('fetch_sticker_prices')

# Get script directory for cross-platform compatibility
script_dir = os.path.dirname(os.path.abspath(__file__))

# Constants - use os.path.join for cross-platform compatibility
PRICE_DATA_FILE = os.path.join(script_dir, "sticker_price_results.json")

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
                
                # Check if we have timestamp data
                timestamp = data.get("timestamp", 0)
                current_time = time.time()
                age_seconds = current_time - timestamp
                age_minutes = age_seconds / 60
                
                if "human_timestamp" in data:
                    logger.info(f"Loaded existing price data from {data['human_timestamp']} ({age_minutes:.2f} minutes old)")
                    print(f"📂 Loaded price data from {data['human_timestamp']} ({age_minutes:.2f} minutes old)")
                else:
                    logger.info(f"Loaded existing price data with {len(data.get('stickers_with_prices', []))} entries")
                    print(f"📂 Loaded price data with {len(data.get('stickers_with_prices', []))} entries")
                
                return data
        else:
            logger.warning(f"Price file not found: {PRICE_DATA_FILE}")
            print(f"⚠️ Price file not found: {PRICE_DATA_FILE}")
            return {"stickers_with_prices": [], "timestamp": time.time()}
    except Exception as e:
        logger.error(f"Error loading price data: {e}")
        print(f"❌ Error loading price data: {e}")
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
        human_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        price_data["human_timestamp"] = human_timestamp
        
        # Save data with pretty formatting
        with open(PRICE_DATA_FILE, 'w') as f:
            json.dump(price_data, f, indent=2)
            
        logger.info(f"Updated price data saved to {PRICE_DATA_FILE} at {human_timestamp}")
        print(f"💾 Saved price data at {human_timestamp}")
    except Exception as e:
        logger.error(f"Error saving price data: {e}")
        print(f"❌ Error saving price data: {e}")

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
    api_calls = 0
    
    # Get all stickers
    stickers = existing_data.get("stickers_with_prices", [])
    total_stickers = len(stickers)
    
    logger.info(f"Starting price update for {total_stickers} stickers")
    print(f"🔄 UPDATING: Refreshing prices for {total_stickers} stickers...")
    
    # Track start time
    start_time = time.time()
    
    # Update prices for each sticker
    for i, sticker_data in enumerate(stickers):
        collection = sticker_data.get("collection", "")
        sticker = sticker_data.get("sticker", "")
        search_term = f"{collection} {sticker}"
        
        logger.info(f"Processing {i+1}/{total_stickers}: {search_term}")
        
        try:
            # Get price data from MRKT API
            price_data = mrkt_api.get_sticker_price(search_term, use_cache=False)
            api_calls += 1
            
            # Check if we got price data
            if price_data and "price" in price_data:
                # Update the price data
                old_price = sticker_data.get("price", 0)
                new_price = price_data.get("price", 0)
                price_change = new_price - old_price
                
                sticker_data["price"] = new_price
                sticker_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Add price change indicator
                if price_change > 0:
                    change_indicator = f"↗️ +{price_change:.4f}"
                elif price_change < 0:
                    change_indicator = f"↘️ {price_change:.4f}"
                else:
                    change_indicator = "→ 0.0000"
                
                logger.info(f"✅ Updated price for {search_term}: {new_price} TON ({change_indicator})")
                print(f"  ✅ {i+1}/{total_stickers} {collection} - {sticker}: {new_price} TON {change_indicator}")
                updated_count += 1
            else:
                logger.info(f"ℹ️ No price data for {search_term}")
                print(f"  ⚠️ {i+1}/{total_stickers} {collection} - {sticker}: No price data")
                skipped_count += 1
        except Exception as e:
            logger.error(f"Error updating price for {search_term}: {e}")
            print(f"  ❌ {i+1}/{total_stickers} {collection} - {sticker}: {str(e)}")
            failed_count += 1
        
        # Calculate progress percentage
        progress = (i + 1) / total_stickers * 100
        
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
        
        # Add a small delay to avoid rate limiting
        time.sleep(0.5)
    
    # Calculate total execution time
    execution_time = time.time() - start_time
    
    # Save the updated prices
    save_updated_prices(existing_data)
    
    # Print summary
    summary = f"Price update complete: {updated_count} updated, {skipped_count} skipped, {failed_count} failed"
    logger.info(f"{summary} in {execution_time:.2f} seconds ({api_calls} API calls)")
    print(f"📊 {summary}")
    print(f"⏱️ Total execution time: {execution_time:.2f} seconds ({api_calls} API calls)")
    print(f"⚡ Average time per sticker: {(execution_time/total_stickers):.2f} seconds")
    
    return updated_count > 0

if __name__ == "__main__":
    # Test API connection first
    logger.info("Testing MRKT API connection...")
    print("🔑 Testing MRKT API connection...")
    
    token = mrkt_api.get_working_token()
    
    if token:
        logger.info(f"API authentication successful, token: {token[:10]}...")
        print(f"✅ API authentication successful")
        update_sticker_prices()
    else:
        logger.error("API authentication failed, cannot update prices")
        print("❌ API authentication failed, cannot update prices") 