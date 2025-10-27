#!/usr/bin/env python3
"""
Visualize sticker prices from the MRKT API.

This script creates visualizations of the sticker prices fetched from the MRKT API.
"""

import json
import os
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

def visualize_prices():
    """Create visualizations of sticker prices."""
    # Load the price data
    try:
        with open('sticker_prices/all_prices.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Price data file not found. Please run fetch_all_sticker_prices.py first.")
        return
    
    # Collect stickers with prices
    found = []
    collection_counts = defaultdict(lambda: {'found': 0, 'total': 0})
    
    for collection, characters in data.items():
        for character, info in characters.items():
            collection_counts[collection]['total'] += 1
            if info.get('is_real_data'):
                found.append((
                    collection, 
                    character, 
                    info.get('price', 0), 
                    info.get('price_usd', 0)
                ))
                collection_counts[collection]['found'] += 1
    
    # Sort stickers by price
    found.sort(key=lambda x: x[2], reverse=True)
    
    # Create a directory for visualizations
    os.makedirs('visualizations', exist_ok=True)
    
    # 1. Top 10 most expensive stickers
    create_top_stickers_chart(found[:10])
    
    # 2. Collection success rate
    create_collection_success_chart(collection_counts)
    
    # 3. Price distribution
    create_price_distribution_chart(found)
    
    print("Visualizations created in the 'visualizations' directory.")

def create_top_stickers_chart(stickers):
    """Create a chart of the top most expensive stickers."""
    plt.figure(figsize=(12, 8))
    
    # Extract data
    names = [f"{s[0]}: {s[1]}" for s in stickers]
    prices = [s[2] for s in stickers]
    
    # Create horizontal bar chart
    plt.barh(names, prices, color='skyblue')
    plt.xlabel('Price (TON)')
    plt.title('Top 10 Most Expensive Stickers')
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Add price labels
    for i, price in enumerate(prices):
        plt.text(price + 10, i, f"{price:.2f} TON", va='center')
    
    plt.tight_layout()
    plt.savefig('visualizations/top_stickers.png')
    plt.close()

def create_collection_success_chart(collection_counts):
    """Create a chart showing success rate by collection."""
    # Filter collections with at least one sticker
    collections = [c for c, counts in collection_counts.items() if counts['total'] > 0]
    found = [collection_counts[c]['found'] for c in collections]
    total = [collection_counts[c]['total'] for c in collections]
    
    # Sort by success rate
    success_rates = [f/t for f, t in zip(found, total)]
    sorted_indices = np.argsort(success_rates)[::-1]
    
    collections = [collections[i] for i in sorted_indices]
    found = [found[i] for i in sorted_indices]
    total = [total[i] for i in sorted_indices]
    
    # Create chart
    plt.figure(figsize=(12, 10))
    
    x = np.arange(len(collections))
    width = 0.35
    
    plt.bar(x, found, width, label='Found', color='green')
    plt.bar(x, [t-f for t, f in zip(total, found)], width, bottom=found, label='Not Found', color='red')
    
    plt.xlabel('Collection')
    plt.ylabel('Number of Stickers')
    plt.title('Sticker Price Data by Collection')
    plt.xticks(x, collections, rotation=45, ha='right')
    plt.legend()
    
    # Add success rate labels
    for i, (f, t) in enumerate(zip(found, total)):
        success_rate = f/t*100 if t > 0 else 0
        plt.text(i, t + 0.1, f"{success_rate:.0f}%", ha='center')
    
    plt.tight_layout()
    plt.savefig('visualizations/collection_success.png')
    plt.close()

def create_price_distribution_chart(stickers):
    """Create a chart showing the distribution of prices."""
    prices = [s[2] for s in stickers]
    
    plt.figure(figsize=(10, 6))
    
    # Create histogram
    bins = [0, 10, 25, 50, 100, 200, 500, 1100]
    plt.hist(prices, bins=bins, color='skyblue', edgecolor='black')
    
    plt.xlabel('Price Range (TON)')
    plt.ylabel('Number of Stickers')
    plt.title('Price Distribution of Stickers')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add count labels
    hist, bin_edges = np.histogram(prices, bins=bins)
    bin_centers = [(bin_edges[i] + bin_edges[i+1])/2 for i in range(len(bin_edges)-1)]
    
    for count, x in zip(hist, bin_centers):
        if count > 0:
            plt.text(x, count + 0.2, str(count), ha='center')
    
    plt.tight_layout()
    plt.savefig('visualizations/price_distribution.png')
    plt.close()

if __name__ == "__main__":
    visualize_prices() 