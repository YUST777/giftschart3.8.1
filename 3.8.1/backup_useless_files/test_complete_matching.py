#!/usr/bin/env python3
"""
Test script for the complete MRKT API matching with all the new data.
This script tests the matching between our sticker names and MRKT API character names.
"""

import os
import json
import logging
from mrkt_api_improved import get_sticker_price, clear_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_complete_matching")

# Test stickers - these should now all match with the improved mapping
TEST_STICKERS = [
    # Collection names
    "Pudgy Penguins",
    "Pudgy & Friends",
    "BabyDoge",
    "PUCCA",
    "Flappy Bird",
    "Lazy & Rich",
    "Smeshariki",
    "SUNDOG",
    "Kudai",
    "Dogs OG",
    "Azuki",
    "Blum",
    "Bored Stickers",
    "Dogs rewards",
    "Not Pixel",
    "Notcoin",
    "Doodles",
    "Lil Pudgys",
    "WAGMI HUB",
    "Cattea Life",
    "Lost Dogs",
    
    # Specific character names
    "Shao",
    "Mememania",
    "Bunny",
    "Cap",
    "Cat",
    "Cook",
    "Curly",
    "General",
    "No",
    "Worker",
    "3151",
    "Blue Wings",
    "Blush Flight",
    "Frost Flap",
    "Light Glide",
    "Ruby Wings",
    "GMI",
    "NGMI",
    "Chill or thrill",
    "Sloth Capital",
    "Lil Pudgys x Baby Shark",
    "Lost Memeries",
    "Magic of the Way",
    "Flags",
    "Not Memes",
    "Cute pack",
    "Diamond Pixel",
    "DOGS Pixel",
    "Error Pixel",
    "Films memes",
    "Grass Pixel",
    "MacPixel",
    "Pixanos",
    "Pixel phrases",
    "Pixioznik",
    "Random memes",
    "Retro Pixel",
    "Smileface pack",
    "SuperPixel",
    "Tournament S1",
    "Vice Pixel",
    "Zompixel",
    "PUCCA Moods",
    "Pengu x Baby Shark",
    "Pengu x NASCAR",
    "Blue Pengu",
    "Cool Blue Pengu",
    "Pengu CNY",
    "Pengu Valentines",
    "Ric Flair",
    "Chamomile Valley",
    "The Memes",
    "TO THE SUN",
    "EGG & HAMMER",
    "WAGMI AI AGENT",
    "Full dig",
    "Gold bone",
    "Silver bone"
]

def test_sticker_matching():
    """
    Test the sticker matching with the MRKT API
    
    Returns:
        dict: Test results
    """
    # Clear cache to ensure fresh data
    clear_cache()
    
    results = {
        "total_stickers": len(TEST_STICKERS),
        "successful_matches": 0,
        "failed_matches": 0,
        "match_details": [],
        "high_value_stickers": []
    }
    
    for sticker in TEST_STICKERS:
        logger.info(f"Testing sticker: {sticker}")
        
        # Get price data
        price_data = get_sticker_price(sticker, update_cache=True)
        
        # Check if we got real data
        is_real_data = price_data.get("is_real_data", False)
        
        if is_real_data:
            results["successful_matches"] += 1
            
            # Add to match details
            match_detail = {
                "sticker_name": sticker,
                "api_name": price_data.get("name", "Unknown"),
                "price_ton": price_data.get("price", 0),
                "price_usd": price_data.get("price_usd", 0),
                "collection_id": price_data.get("collection_id"),
                "character_id": price_data.get("character_id")
            }
            
            results["match_details"].append(match_detail)
            
            # Check if this is a high-value sticker (>50 TON)
            price = price_data.get("price", 0)
            if price > 50:
                results["high_value_stickers"].append({
                    "name": sticker,
                    "price_ton": price,
                    "price_usd": price_data.get("price_usd", 0)
                })
        else:
            results["failed_matches"] += 1
            
            # Add to match details
            results["match_details"].append({
                "sticker_name": sticker,
                "error": price_data.get("message", "Unknown error"),
                "matched": False
            })
    
    # Calculate success rate
    results["success_rate"] = (results["successful_matches"] / results["total_stickers"]) * 100
    
    # Sort high-value stickers by price (descending)
    results["high_value_stickers"].sort(key=lambda x: x["price_ton"], reverse=True)
    
    return results

def save_results(results, filename="complete_matching_results.json"):
    """Save test results to a JSON file"""
    with open(filename, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {filename}")

if __name__ == "__main__":
    print("Testing complete sticker matching with MRKT API...")
    results = test_sticker_matching()
    
    # Print summary
    print(f"\nSummary:")
    print(f"Total stickers tested: {results['total_stickers']}")
    print(f"Successful matches: {results['successful_matches']}")
    print(f"Failed matches: {results['failed_matches']}")
    print(f"Success rate: {results['success_rate']:.2f}%")
    
    # Print high-value stickers
    print(f"\nHigh-value stickers (>50 TON):")
    for sticker in results["high_value_stickers"]:
        print(f"  {sticker['name']}: {sticker['price_ton']} TON (${sticker['price_usd']:.2f})")
    
    # Save results
    save_results(results) 