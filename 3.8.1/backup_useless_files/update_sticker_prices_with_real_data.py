#!/usr/bin/env python3
"""
Update Sticker Prices with Real Data

This script updates the existing sticker price data with real prices from the MRKT API.
It reads the existing price data from sticker_prices/all_prices.json,
fetches real prices from the MRKT API, and updates the price data.
"""

import os
import json
import logging
import time
from datetime import datetime
from mrkt_api_improved import get_sticker_price, clear_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("update_sticker_prices")

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ALL_PRICES_PATH = os.path.join(SCRIPT_DIR, "sticker_prices", "all_prices.json")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "sticker_prices", "all_prices_real.json")

def load_existing_prices():
    """
    Load existing price data from all_prices.json
    
    Returns:
        dict: Existing price data
    """
    try:
        with open(ALL_PRICES_PATH, "r") as f:
            data = json.load(f)
            logger.info(f"Loaded existing price data from {ALL_PRICES_PATH}")
            return data
    except Exception as e:
        logger.error(f"Error loading existing price data: {e}")
        return {"stickers": []}

def extract_sticker_names(existing_prices):
    """
    Extract sticker names from the existing price data
    
    Args:
        existing_prices (dict): Existing price data
        
    Returns:
        list: List of sticker names
    """
    sticker_names = []
    
    # Check if the data has a "stickers" key (new format)
    if "stickers" in existing_prices and isinstance(existing_prices["stickers"], list):
        for sticker in existing_prices["stickers"]:
            if "name" in sticker:
                sticker_names.append(sticker["name"])
    # Otherwise, assume it's a dict with sticker names as keys (old format)
    elif isinstance(existing_prices, dict):
        for key in existing_prices:
            if key != "metadata" and isinstance(existing_prices[key], dict):
                sticker_names.append(key)
    
    logger.info(f"Extracted {len(sticker_names)} sticker names")
    return sticker_names

def update_prices_with_real_data(existing_prices):
    """
    Update existing price data with real prices from the MRKT API
    
    Args:
        existing_prices (dict): Existing price data
        
    Returns:
        dict: Updated price data
    """
    # Clear cache to ensure fresh data
    clear_cache()
    
    # Extract sticker names
    sticker_names = extract_sticker_names(existing_prices)
    if not sticker_names:
        logger.error("No sticker names found in existing price data")
        return {"metadata": {"error": "No sticker names found"}, "stickers": []}
    
    # Create a new structure for the updated prices
    updated_prices = {
        "metadata": {
            "updated_at": datetime.now().isoformat(),
            "source": "MRKT API (real data)",
            "total_stickers": len(sticker_names),
            "updated_stickers": 0,
            "high_value_stickers": []
        },
        "stickers": []
    }
    
    # Update each sticker with real price data
    for i, sticker_name in enumerate(sticker_names):
        logger.info(f"Updating price for {sticker_name} ({i+1}/{len(sticker_names)})")
        
        # Get real price data
        price_data = get_sticker_price(sticker_name)
        
        # Create sticker entry
        sticker_entry = {
            "name": sticker_name,
            "price": 0,
            "price_usd": 0,
            "is_real_data": False,
            "last_updated": datetime.now().isoformat()
        }
        
        # Check if we got real data
        is_real_data = price_data.get("is_real_data", False)
        
        if is_real_data:
            # Update sticker with real price data
            sticker_entry["price"] = price_data.get("price", 0)
            sticker_entry["price_usd"] = price_data.get("price_usd", 0)
            sticker_entry["supply"] = price_data.get("supply", 0)
            sticker_entry["description"] = price_data.get("description", "")
            sticker_entry["collection_id"] = price_data.get("collection_id", None)
            sticker_entry["character_id"] = price_data.get("character_id", None)
            sticker_entry["is_real_data"] = True
            sticker_entry["last_updated"] = price_data.get("last_updated", datetime.now().isoformat())
            sticker_entry["api_name"] = price_data.get("name", sticker_name)
            
            # Increment counter
            updated_prices["metadata"]["updated_stickers"] += 1
            
            # Check if this is a high-value sticker (>50 TON)
            price = price_data.get("price", 0)
            if price > 50:
                updated_prices["metadata"]["high_value_stickers"].append({
                    "name": sticker_name,
                    "price_ton": price,
                    "price_usd": price_data.get("price_usd", 0)
                })
        
        # Add sticker to the list
        updated_prices["stickers"].append(sticker_entry)
        
        # Add a small delay to avoid rate limiting
        time.sleep(0.1)
    
    # Sort high-value stickers by price (descending)
    updated_prices["metadata"]["high_value_stickers"].sort(key=lambda x: x["price_ton"], reverse=True)
    
    return updated_prices

def save_updated_prices(updated_prices):
    """
    Save updated price data to all_prices_real.json
    
    Args:
        updated_prices (dict): Updated price data
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        
        with open(OUTPUT_PATH, "w") as f:
            json.dump(updated_prices, f, indent=2)
        logger.info(f"Updated price data saved to {OUTPUT_PATH}")
    except Exception as e:
        logger.error(f"Error saving updated price data: {e}")

def main():
    """Main function"""
    logger.info("Starting update of sticker prices with real data")
    
    # Load existing price data
    existing_prices = load_existing_prices()
    
    # Update prices with real data
    updated_prices = update_prices_with_real_data(existing_prices)
    
    # Save updated prices
    save_updated_prices(updated_prices)
    
    # Print summary
    metadata = updated_prices.get("metadata", {})
    total_stickers = metadata.get("total_stickers", 0)
    updated_stickers = metadata.get("updated_stickers", 0)
    
    print(f"\nSummary:")
    print(f"Total stickers: {total_stickers}")
    print(f"Updated stickers: {updated_stickers}")
    
    # Calculate success rate (avoid division by zero)
    if total_stickers > 0:
        success_rate = (updated_stickers / total_stickers) * 100
        print(f"Success rate: {success_rate:.2f}%")
    else:
        print("Success rate: N/A (no stickers found)")
    
    # Print high-value stickers
    high_value_stickers = metadata.get("high_value_stickers", [])
    if high_value_stickers:
        print(f"\nHigh-value stickers (>50 TON):")
        for sticker in high_value_stickers:
            print(f"  {sticker['name']}: {sticker['price_ton']} TON (${sticker['price_usd']:.2f})")
    else:
        print("\nNo high-value stickers found")

if __name__ == "__main__":
    main() 