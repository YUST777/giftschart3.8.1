#!/usr/bin/env python3
"""
Telegram Sticker Card Generator

This script generates visual cards for Telegram stickers with price information.
It supports integration with the MRKT API to get real price data.
"""

import os
import sys
import argparse
import logging
from PIL import Image, ImageDraw, ImageFont
import mrkt_api_improved as mrkt_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sticker_card_generator')

# Default output directory
DEFAULT_OUTPUT_DIR = "sticker_cards"

# Card dimensions
CARD_WIDTH = 800
CARD_HEIGHT = 600

# Font settings
FONT_PATH = "fonts/Roboto-Bold.ttf"  # Adjust path as needed
TITLE_FONT_SIZE = 36
SUBTITLE_FONT_SIZE = 28
PRICE_FONT_SIZE = 48

# Colors
BACKGROUND_COLOR = (255, 255, 255)  # White
TEXT_COLOR = (0, 0, 0)  # Black
PRICE_COLOR = (0, 128, 0)  # Green
BORDER_COLOR = (200, 200, 200)  # Light gray

def normalize_name(name):
    """Normalize a name for file operations"""
    return name.replace(' ', '_').replace('&', 'and')

def get_mrkt_price_data(collection_name, pack_name):
    """Get price data for a sticker from the MRKT API."""
    try:
        # Try collection_pack format first
        sticker_id = f"{collection_name}_{pack_name}"
        price_data = mrkt_api.get_sticker_price(sticker_id)
        
        if not price_data or price_data.get('price', 0) <= 0:
            # Try with just the pack name
            price_data = mrkt_api.get_sticker_price(pack_name)
        
        if not price_data or price_data.get('price', 0) <= 0:
            # Try with just the collection name
            price_data = mrkt_api.get_sticker_price(collection_name)
            
        if price_data and price_data.get('price', 0) > 0:
            return price_data
        
            return None
    except Exception as e:
        logger.error(f"Error getting MRKT price data: {e}")
        return None

def generate_sticker_card(collection, sticker, output_dir, include_price=False, use_mrkt_api=False):
    """Generate a visual card for a Telegram sticker"""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a blank card
        card = Image.new('RGB', (CARD_WIDTH, CARD_HEIGHT), BACKGROUND_COLOR)
        draw = ImageDraw.Draw(card)
        
        # Add border
        draw.rectangle([(10, 10), (CARD_WIDTH - 10, CARD_HEIGHT - 10)], outline=BORDER_COLOR, width=5)
        
        # Load fonts
        try:
            title_font = ImageFont.truetype(FONT_PATH, TITLE_FONT_SIZE)
            subtitle_font = ImageFont.truetype(FONT_PATH, SUBTITLE_FONT_SIZE)
            price_font = ImageFont.truetype(FONT_PATH, PRICE_FONT_SIZE)
        except IOError:
            # Fallback to default font if custom font not found
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            price_font = ImageFont.load_default()
        
        # Add collection name
        draw.text((CARD_WIDTH // 2, 50), collection, fill=TEXT_COLOR, font=title_font, anchor="mt")
        
        # Add sticker name
        draw.text((CARD_WIDTH // 2, 120), sticker, fill=TEXT_COLOR, font=subtitle_font, anchor="mt")
        
        # Get price data if requested
        price_data = None
        if include_price and use_mrkt_api:
            price_data = get_mrkt_price_data(collection, sticker)
        
        # Add price information if available
        if price_data:
            price = price_data.get('price', 0)
            price_usd = price_data.get('price_usd', 0)
            
            # Format price string
            price_str = f"{price:.2f} TON"
            usd_str = f"(${price_usd:.2f})"
            
            # Draw price
            draw.text((CARD_WIDTH // 2, CARD_HEIGHT - 150), price_str, fill=PRICE_COLOR, font=price_font, anchor="mt")
            draw.text((CARD_WIDTH // 2, CARD_HEIGHT - 90), usd_str, fill=PRICE_COLOR, font=subtitle_font, anchor="mt")
            
            # Add source note
            source_str = "Price from MRKT API"
            draw.text((CARD_WIDTH // 2, CARD_HEIGHT - 40), source_str, fill=TEXT_COLOR, font=subtitle_font, anchor="mt")
        elif include_price:
            # Show placeholder if price was requested but not available
            draw.text((CARD_WIDTH // 2, CARD_HEIGHT - 150), "Price not available", fill=TEXT_COLOR, font=subtitle_font, anchor="mt")
        
        # Save the card
        output_filename = f"{normalize_name(collection)}_{normalize_name(sticker)}_card.png"
        output_path = os.path.join(output_dir, output_filename)
        card.save(output_path)
        
        logger.info(f"Generated card: {output_path}")
        return output_path
    except Exception as e:
        logger.error(f"Error generating sticker card: {e}")
        return None

def main():
    """Main function to parse arguments and generate sticker cards"""
    parser = argparse.ArgumentParser(description="Generate visual cards for Telegram stickers")
    parser.add_argument("--collection", required=True, help="Collection name")
    parser.add_argument("--sticker", required=True, help="Sticker name")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Output directory for generated cards")
    parser.add_argument("--include-price", action="store_true", help="Include price information on the card")
    parser.add_argument("--use-mrkt-api", action="store_true", help="Use MRKT API to get real price data")
    
    args = parser.parse_args()
    
    # Generate the card
    generate_sticker_card(
        args.collection,
        args.sticker,
        args.output_dir,
        include_price=args.include_price,
        use_mrkt_api=args.use_mrkt_api
    )
        
if __name__ == "__main__":
    main() 