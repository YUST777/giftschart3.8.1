#!/usr/bin/env python3
"""
Fetch MRKT Prices

Command-line tool for fetching specific sticker prices from the MRKT API.
"""

import os
import sys
import json
import logging
import argparse
from tabulate import tabulate
from mrkt_api_improved import get_sticker_price, clear_cache, test

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("fetch_mrkt_prices")

def fetch_prices(sticker_names, output_file=None, format_output="table"):
    """
    Fetch prices for specific stickers
    
    Args:
        sticker_names (list): List of sticker names to fetch prices for
        output_file (str): Path to output file (optional)
        format_output (str): Output format (table, json, or csv)
        
    Returns:
        list: Price data for each sticker
    """
    # Clear cache to ensure fresh data
    clear_cache()
    
    results = []
    
    for i, sticker_name in enumerate(sticker_names):
        logger.info(f"Fetching price for {sticker_name} ({i+1}/{len(sticker_names)})")
        
        # Get price data
        price_data = get_sticker_price(sticker_name)
        
        # Add to results
        results.append({
            "sticker_name": sticker_name,
            "api_name": price_data.get("name", "Unknown"),
            "price_ton": price_data.get("price", 0),
            "price_usd": price_data.get("price_usd", 0),
            "supply": price_data.get("supply", 0),
            "collection_id": price_data.get("collection_id"),
            "character_id": price_data.get("character_id"),
            "is_real_data": price_data.get("is_real_data", False),
            "description": price_data.get("description", "")
        })
    
    # Save results if output file specified
    if output_file:
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {output_file}")
    
    # Print results
    if format_output == "table":
        # Format as table
        table_data = []
        for result in results:
            table_data.append([
                result["sticker_name"],
                result["api_name"],
                f"{result['price_ton']:.4f}",
                f"${result['price_usd']:.2f}",
                result["supply"],
                "✓" if result["is_real_data"] else "✗"
            ])
        
        print(tabulate(
            table_data,
            headers=["Sticker Name", "API Name", "Price (TON)", "Price (USD)", "Supply", "Real Data"],
            tablefmt="grid"
        ))
    elif format_output == "json":
        # Format as JSON
        print(json.dumps(results, indent=2))
    elif format_output == "csv":
        # Format as CSV
        print("Sticker Name,API Name,Price (TON),Price (USD),Supply,Real Data")
        for result in results:
            print(f"{result['sticker_name']},{result['api_name']},{result['price_ton']:.4f},{result['price_usd']:.2f},{result['supply']},{result['is_real_data']}")
    
    return results

def run_api_test():
    """Run API test and print results"""
    print("Testing MRKT API integration...")
    test_results = test()
    print(json.dumps(test_results, indent=2))

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Fetch sticker prices from the MRKT API")
    
    # Add arguments
    parser.add_argument("stickers", nargs="*", help="Sticker names to fetch prices for")
    parser.add_argument("-f", "--file", help="File containing sticker names (one per line)")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-t", "--test", action="store_true", help="Run API test")
    parser.add_argument("--format", choices=["table", "json", "csv"], default="table", help="Output format")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run API test if requested
    if args.test:
        run_api_test()
        return
    
    # Get sticker names
    sticker_names = args.stickers
    
    # If file specified, read sticker names from file
    if args.file:
        try:
            with open(args.file, "r") as f:
                file_stickers = [line.strip() for line in f.readlines() if line.strip()]
                sticker_names.extend(file_stickers)
        except Exception as e:
            logger.error(f"Error reading sticker names from file: {e}")
    
    # Check if we have any sticker names
    if not sticker_names:
        parser.print_help()
        print("\nError: No sticker names provided. Please specify sticker names or a file containing sticker names.")
        return
    
    # Fetch prices
    fetch_prices(sticker_names, args.output, args.format)

if __name__ == "__main__":
    main() 