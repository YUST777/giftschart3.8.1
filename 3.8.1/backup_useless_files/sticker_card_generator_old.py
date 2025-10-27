#!/usr/bin/env python3
"""
Sticker Card Generator

This script generates cards for sticker packs similar to the gift cards.
"""

import os
import json
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import colorsys
import numpy as np
import datetime
import sqlite3
import logging
import glob

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sticker_card_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sticker_card_generator")

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Directory paths - use os.path.join to ensure cross-platform compatibility
sticker_dir = os.path.join(script_dir, "sticker_collections")
output_dir = os.path.join(script_dir, "sticker_cards")
assets_dir = os.path.join(script_dir, "assets")
templates_dir = os.path.join(script_dir, "sticker_templates")
metadata_dir = os.path.join(script_dir, "sticker_metadata")
background_path = os.path.join(assets_dir, "Background color this.png")
white_box_path = os.path.join(assets_dir, "white box.png")
ton_logo_path = os.path.join(assets_dir, "TON2.png")
star_logo_path = os.path.join(assets_dir, "star.png")
font_path = os.path.join(script_dir, "Typekiln - EloquiaDisplay-ExtraBold.otf")

# Database path
DB_FILE = "place_stickers.db"

# Create output directories if they don't exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(templates_dir, exist_ok=True)
os.makedirs(metadata_dir, exist_ok=True)

# Context manager for database connections
conn = sqlite3.connect(DB_FILE, timeout=30)
conn.row_factory = sqlite3.Row
try:
    yield conn
finally:
    conn.close()

# Function to get dominant color from an image
def get_dominant_color(image_path):
    try:
        img = Image.open(image_path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create a smaller version of the image to speed up processing
        img.thumbnail((100, 100))
        
        # Get color data
        pixels = np.array(img)
        
        # Remove transparent pixels (alpha < 128)
        pixels = pixels[pixels[:,:,3] > 128]
        
        if len(pixels) == 0:
            return (128, 128, 128)  # Default to gray if all pixels are transparent
        
        # Remove alpha channel for clustering
        pixels = pixels[:,:3]
        
        # Simple average color (mean of all non-transparent pixels)
        avg_color = pixels.mean(axis=0).astype(int)
        
        # Enhance saturation a bit for better visual appeal
        h, s, v = colorsys.rgb_to_hsv(avg_color[0]/255, avg_color[1]/255, avg_color[2]/255)
        s = min(s * 1.5, 1.0)  # Increase saturation by 50%, but not above 1.0
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        
        return (int(r*255), int(g*255), int(b*255))
    except Exception as e:
        logger.error(f"Error getting dominant color from {image_path}: {e}")
        return (128, 128, 128)  # Default to gray on error

# Function to apply color to the background
def apply_color_to_background(background_img, color):
    try:
        # Create a gradient background instead of solid color
        width, height = background_img.size
        
        # Create a new image with the same size and mode
        gradient_bg = Image.new('RGBA', background_img.size, (0, 0, 0, 0))
        
        # Extract the base color components
        r, g, b = color
        
        # Create a darker shade for the edges
        darker_r = max(0, int(r * 0.65))
        darker_g = max(0, int(g * 0.65))
        darker_b = max(0, int(b * 0.65))
        darker_color = (darker_r, darker_g, darker_b, 255)
        
        # Create a lighter shade for the center
        lighter_r = min(255, int(r * 1.15))
        lighter_g = min(255, int(g * 1.15))
        lighter_b = min(255, int(b * 1.15))
        lighter_color = (lighter_r, lighter_g, lighter_b, 255)
        
        # Create a slightly different hue for added depth
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        h = (h + 0.05) % 1.0  # Shift hue slightly
        s = min(1.0, s * 1.2)  # Increase saturation
        accent_r, accent_g, accent_b = colorsys.hsv_to_rgb(h, s, v)
        accent_color = (int(accent_r*255), int(accent_g*255), int(accent_b*255), 255)
        
        # Create a radial gradient using a more efficient method
        # First create a small gradient image and then resize it
        small_size = (200, 200)  # Increased for smoother gradient
        small_gradient = Image.new('RGBA', small_size, (0, 0, 0, 0))
        small_draw = ImageDraw.Draw(small_gradient)
        
        # Draw concentric circles with decreasing radius
        center = (small_size[0] // 2, small_size[1] // 2)
        max_radius = int(((small_size[0] // 2) ** 2 + (small_size[1] // 2) ** 2) ** 0.5)
        
        # Draw from outside in with more gradual transitions
        num_steps = 40  # More steps for smoother gradient
        for i in range(num_steps):
            # Calculate radius for this step
            radius = max_radius * (1 - (i / num_steps))
            
            # Calculate interpolation factor (0 at edge, 1 at center)
            factor = i / num_steps
            
            # Create multi-point gradient with darker outer edges and lighter center
            if factor < 0.25:  # Outer 25% transitions from darker to base
                t = factor / 0.25
                r_val = int(darker_color[0] * (1-t) + color[0] * t)
                g_val = int(darker_color[1] * (1-t) + color[1] * t)
                b_val = int(darker_color[2] * (1-t) + color[2] * t)
            elif factor < 0.5:  # Next 25% transitions from base to accent
                t = (factor - 0.25) / 0.25
                r_val = int(color[0] * (1-t) + accent_color[0] * t)
                g_val = int(color[1] * (1-t) + accent_color[1] * t)
                b_val = int(color[2] * (1-t) + accent_color[2] * t)
            else:  # Inner 50% transitions from accent to lighter
                t = (factor - 0.5) / 0.5
                r_val = int(accent_color[0] * (1-t) + lighter_color[0] * t)
                g_val = int(accent_color[1] * (1-t) + lighter_color[1] * t)
                b_val = int(accent_color[2] * (1-t) + lighter_color[2] * t)
            
            current_color = (r_val, g_val, b_val, 255)
            
            # Draw a filled circle
            bbox = (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius)
            small_draw.ellipse(bbox, fill=current_color)
        
        # Resize the small gradient to the full size
        gradient_bg = small_gradient.resize(background_img.size, Image.BICUBIC)
        
        # Use the original background's alpha channel as a mask
        if background_img.mode == 'RGBA':
            r, g, b, a = background_img.split()
            gradient_bg.putalpha(a)
            
        return gradient_bg
    except Exception as e:
        logger.error(f"Error applying color to background: {e}")
        return background_img  # Return original background on error

# Function to ensure collection and pack exist in the database
def ensure_collection_and_pack(collection_name, pack_name):
    """Ensure that the collection and pack exist in the database."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if collection exists
            cursor.execute("SELECT collection_id FROM collections WHERE name = ?", (collection_name,))
            collection_row = cursor.fetchone()
            
            if collection_row:
                collection_id = collection_row[0]
            else:
                # Insert new collection
                cursor.execute("INSERT INTO collections (name) VALUES (?)", (collection_name,))
                collection_id = cursor.lastrowid
                conn.commit()
                logger.info(f"Added new collection to database: {collection_name}")
            
            # Check if pack exists
            if pack_name:  # Only check if pack_name is not empty
                cursor.execute("SELECT pack_id FROM packs WHERE collection_id = ? AND name = ?", 
                            (collection_id, pack_name))
                pack_row = cursor.fetchone()
                
                if not pack_row:
                    # Insert new pack
                    cursor.execute("INSERT INTO packs (collection_id, name) VALUES (?, ?)", 
                                (collection_id, pack_name))
                    pack_id = cursor.lastrowid
                    conn.commit()
                    logger.info(f"Added new pack to database: {collection_name} - {pack_name}")
                else:
                    pack_id = pack_row[0]
            else:
                pack_id = None
                
            return collection_id, pack_id
    except Exception as e:
        logger.error(f"Error ensuring collection and pack in database: {e}")
        return None, None

# Function to get sticker price data from the database
def get_sticker_price_data(collection_name, pack_name=None):
    """Get price data for a sticker pack or collection from the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        if pack_name:
            # Query for a specific pack
            cursor.execute("""
                SELECT collection, pack, price_ton_old, price_usd_old, price_ton_new, price_usd_new, change_percentage, timestamp 
                FROM price_history 
                WHERE collection = ? AND pack = ? 
                ORDER BY timestamp DESC
            """, (collection_name, pack_name))
        else:
            # Query for all packs in a collection
            cursor.execute("""
                SELECT collection, pack, price_ton_old, price_usd_old, price_ton_new, price_usd_new, change_percentage, timestamp 
                FROM price_history 
                WHERE collection = ? 
                ORDER BY timestamp DESC
            """, (collection_name,))
            
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return None
            
        # Group by pack
        packs = {}
        for row in rows:
            collection, pack, price_ton_old, price_usd_old, price_ton_new, price_usd_new, change_percentage, timestamp = row
            if pack not in packs:
                packs[pack] = []
            packs[pack].append({
                "collection": collection,
                "pack": pack,
                "price_ton_old": price_ton_old,
                "price_usd_old": price_usd_old,
                "price_ton_new": price_ton_new,
                "price_usd_new": price_usd_new,
                "change_percentage": change_percentage,
                "timestamp": timestamp
            })
            
        # If a specific pack was requested, return just that data
        if pack_name and pack_name in packs:
            return packs[pack_name]
        
        return packs
    except Exception as e:
        logger.error(f"Error getting sticker price data: {e}")
        return None

# Function to find any sticker image in the pack directory
def find_sticker_image(collection_name, pack_name):
    """Find any sticker image in the pack directory."""
    try:
        normalized_collection = collection_name.replace(" ", "_").replace("-", "_").replace("'", "")
        normalized_pack = pack_name.replace(" ", "_").replace("-", "_").replace("'", "")
        
        # Path to the pack directory
        pack_dir = os.path.join(sticker_dir, normalized_collection, normalized_pack)
        
        # Find any PNG file in the directory
        png_files = glob.glob(os.path.join(pack_dir, "*.png"))
        
        if png_files:
            return png_files[0]
        
        return None
    except Exception as e:
        logger.error(f"Error finding sticker image for {collection_name} - {pack_name}: {e}")
        return None

# Function to generate a template card for a sticker pack
def generate_template_card(collection_name, pack_name):
    """Generate a template card with all static elements for a sticker pack."""
    try:
        # Normalize names for file system compatibility
        normalized_collection = collection_name.replace(" ", "_").replace("-", "_").replace("'", "")
        normalized_pack = pack_name.replace(" ", "_").replace("-", "_").replace("'", "")
        
        # Define the template path
        template_path = os.path.join(templates_dir, f"{normalized_collection}_{normalized_pack}_template.png")
        
        # Check if the template already exists
        if os.path.exists(template_path):
            logger.info(f"Template already exists for {collection_name} - {pack_name}")
            return template_path
        
        # Find the sticker image file
        sticker_img_path = find_sticker_image(collection_name, pack_name)
        
        if not sticker_img_path:
            logger.error(f"Error: No image file found for {collection_name} - {pack_name}")
            return None
        
        logger.info(f"Using sticker image: {sticker_img_path}")
        
        # Load background and white box images
        background_img = Image.open(background_path).convert("RGBA")
        white_box_img = Image.open(white_box_path).convert("RGBA")
        
        # Make sure both images are the same size (1600x1000)
        target_size = (1600, 1000)
        background_img = background_img.resize(target_size)
        white_box_img = white_box_img.resize(target_size)
        
        # Get dominant color from sticker image
        dominant_color = get_dominant_color(sticker_img_path)
        
        # Apply color to the background
        colored_background = apply_color_to_background(background_img, dominant_color)
        
        # Create a new blank canvas with the same size
        template = Image.new('RGBA', background_img.size, (0, 0, 0, 0))
        
        # Paste the colored background
        template.paste(colored_background, (0, 0), colored_background if colored_background.mode == 'RGBA' else None)
        
        # Create shadow for white box
        shadow_offset = 5
        shadow_blur = 10
        shadow_opacity = 40
        
        # Create a shadow layer
        shadow = Image.new('RGBA', background_img.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        
        # Calculate center position for white box
        box_width, box_height = white_box_img.size
        x_center = (background_img.width - box_width) // 2
        y_center = (background_img.height - box_height) // 2
        
        # Create a blurred black rectangle for the shadow
        shadow_rect = (
            x_center + shadow_offset, 
            y_center + shadow_offset, 
            x_center + box_width + shadow_offset, 
            y_center + box_height + shadow_offset
        )
        shadow_draw.rectangle(shadow_rect, fill=(0, 0, 0, shadow_opacity))
        
        # Apply blur to the shadow
        shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
        
        # Composite the shadow onto the template
        template = Image.alpha_composite(template, shadow)
        
        # Paste the white box on top at the center position
        template.paste(white_box_img, (x_center, y_center), white_box_img if white_box_img.mode == 'RGBA' else None)
        
        # Open the sticker image
        sticker_img = Image.open(sticker_img_path)
        
        # Convert to RGBA if needed
        if sticker_img.mode != 'RGBA':
            sticker_img = sticker_img.convert('RGBA')
            
        # Resize sticker image to match reference
        sticker_img.thumbnail((150, 150))
        
        # Position for the sticker image
        sticker_x = x_center + 150
        sticker_y = y_center + 130
        
        # Apply a subtle highlight effect to the sticker image
        enhancer = ImageEnhance.Brightness(sticker_img)
        sticker_img = enhancer.enhance(1.05)
        
        # Paste the sticker image onto the template
        template.paste(sticker_img, (sticker_x, sticker_y), sticker_img)
        
        # Prepare for drawing text
        draw = ImageDraw.Draw(template)
        
        # Draw collection and pack name
        name_font = ImageFont.truetype(font_path, 100)
        name_color = (60, 60, 60)
        name_x = x_center + 310
        name_y = y_center + 120
        
        # Draw collection name
        draw.text((name_x, name_y), collection_name, fill=name_color, font=name_font)
        
        # Draw pack name in smaller font below collection name
        pack_font = ImageFont.truetype(font_path, 60)
        pack_color = (100, 100, 100)
        pack_x = name_x
        pack_y = name_y + 100
        draw.text((pack_x, pack_y), pack_name, fill=pack_color, font=pack_font)
        
        # Load and colorize TON logo
        ton_logo = Image.open(ton_logo_path)
        if ton_logo.mode != 'RGBA':
            ton_logo = ton_logo.convert('RGBA')
        
        # Resize TON logo
        ton_logo.thumbnail((70, 70))
        
        # Colorize TON logo with sticker's dominant color
        ton_logo_colored = Image.new('RGBA', ton_logo.size, (0, 0, 0, 0))
        for y in range(ton_logo.height):
            for x in range(ton_logo.width):
                r, g, b, a = ton_logo.getpixel((x, y))
                if a > 0:
                    ton_logo_colored.putpixel((x, y), dominant_color + (a,))
        
        # Load and colorize Star logo
        star_logo = Image.open(star_logo_path)
        if star_logo.mode != 'RGBA':
            star_logo = star_logo.convert('RGBA')
        
        # Resize Star logo
        star_logo.thumbnail((70, 70))
        
        # Colorize Star logo with sticker's dominant color
        star_logo_colored = Image.new('RGBA', star_logo.size, (0, 0, 0, 0))
        for y in range(star_logo.height):
            for x in range(star_logo.width):
                r, g, b, a = star_logo.getpixel((x, y))
                if a > 0:
                    star_logo_colored.putpixel((x, y), dominant_color + (a,))
        
        # Position for TON logo
        ton_y = y_center + 480
        dollar_x = x_center + 180
        
        # Paste TON logo
        template.paste(ton_logo_colored, (dollar_x, ton_y - 15), ton_logo_colored)
        
        # Position for Star logo
        dot_y = (ton_y - 15) + (ton_logo.height // 2)
        ton_text_x = dollar_x + 80
        ton_price_font = ImageFont.truetype(font_path, 50)
        dummy_ton_text = "999.9"  # Placeholder for width calculation
        ton_text_width = draw.textlength(dummy_ton_text, font=ton_price_font)
        dot_x = int(ton_text_x + ton_text_width + 30)
        star_x = int(dot_x + 20)
        
        # Paste Star logo
        template.paste(star_logo_colored, (star_x, ton_y - 15), star_logo_colored)
        
        # Save the template
        template.save(template_path)
        logger.info(f"Generated template for {collection_name} - {pack_name} at {template_path}")
        
        # Store metadata about the template
        metadata = {
            "collection_name": collection_name,
            "pack_name": pack_name,
            "x_center": x_center,
            "y_center": y_center,
            "box_width": box_width,
            "box_height": box_height,
            "dominant_color": dominant_color,
            "dollar_x": dollar_x,
            "dollar_y": y_center + 280,
            "ton_logo_pos": (dollar_x, ton_y - 15),
            "ton_text_pos": (ton_text_x, (ton_y - 15) + (ton_logo.height // 2) - ton_price_font.size // 2),
            "star_logo_pos": (star_x, ton_y - 15),
            "star_text_pos": (star_x + 80, (ton_y - 15) + (ton_logo.height // 2) - ton_price_font.size // 2)
        }
        
        # Save metadata
        metadata_path = os.path.join(metadata_dir, f"{normalized_collection}_{normalized_pack}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
            
        return template_path
    except Exception as e:
        logger.error(f"Error generating template for {collection_name} - {pack_name}: {e}")
        return None

# Function to add dynamic elements (prices) to a template
def add_dynamic_elements(collection_name, pack_name, template_path=None, output_path=None):
    """Add dynamic elements (prices) to a template card."""
    try:
        # Normalize names for file system compatibility
        normalized_collection = collection_name.replace(" ", "_").replace("-", "_").replace("'", "")
        normalized_pack = pack_name.replace(" ", "_").replace("-", "_").replace("'", "")
        
        # If no template path provided, use the default one
        if not template_path:
            template_path = os.path.join(templates_dir, f"{normalized_collection}_{normalized_pack}_template.png")
        
        # If template doesn't exist, generate it
        if not os.path.exists(template_path):
            template_path = generate_template_card(collection_name, pack_name)
            if not template_path:
                return None
        
        # Load the template
        card = Image.open(template_path).convert("RGBA")
        
        # Load metadata
        metadata_path = os.path.join(metadata_dir, f"{normalized_collection}_{normalized_pack}_metadata.json")
        if not os.path.exists(metadata_path):
            logger.error(f"Error: Metadata not found for {collection_name} - {pack_name}")
            return None
            
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        # Extract needed values
        x_center = metadata["x_center"]
        y_center = metadata["y_center"]
        box_width = metadata["box_width"]
        box_height = metadata["box_height"]
        dominant_color = tuple(metadata["dominant_color"])
        dollar_x = metadata["dollar_x"]
        dollar_y = metadata["dollar_y"]
        
        # Fetch price data for the sticker pack
        price_data = get_sticker_price_data(collection_name, pack_name)
        
        # Get price from database or generate random if not available
        current_price_usd = 0
        current_price_ton = 0
        change_pct = 0
        
        if price_data and len(price_data) > 0:
            # Use the most recent price
            current_price_usd = float(price_data[0]["price_usd_new"])
            current_price_ton = float(price_data[0]["price_ton_new"])
            change_pct = price_data[0]["change_percentage"] if price_data[0]["change_percentage"] is not None else 0
        else:
            # Generate random price if no data available
            current_price_usd = random.randint(50, 500)
            current_price_ton = current_price_usd / 3.4  # Approximate TON price
            
            # Add the random price to the database
            add_random_price_data(collection_name, pack_name)
            
            # Calculate percentage change (random for now)
            change_pct = random.uniform(-20, 40)
        
        # Calculate price in Telegram Stars (1 Star = $0.016)
        stars_price = int(current_price_usd / 0.016)
        
        # Determine color based on percentage change
        change_sign = "+" if change_pct >= 0 else ""
        if change_pct >= 0:
            change_color = (46, 204, 113)  # Vibrant green
        else:
            change_color = (231, 76, 60)  # Vibrant red
        
        # Prepare for drawing
        draw = ImageDraw.Draw(card)
        
        # Draw percentage change
        pct_font = ImageFont.truetype(font_path, 70)
        pct_text = f"{change_sign}{int(change_pct)}%"
        pct_width = draw.textlength(pct_text, font=pct_font)
        pct_x = x_center + box_width - pct_width - 140
        pct_y = y_center + 155
        draw.text((pct_x, pct_y), pct_text, fill=change_color, font=pct_font)
        
        # Draw dollar sign and USD price
        price_font = ImageFont.truetype(font_path, 140)
        draw.text((dollar_x, dollar_y), "$", fill=dominant_color, font=price_font)
        draw.text((dollar_x + 100, dollar_y), f"{current_price_usd:,.0f}".replace(",", " "), fill=(20, 20, 20), font=price_font)
        
        # Draw TON and Stars prices
        ton_price_font = ImageFont.truetype(font_path, 50)
        draw.text(metadata["ton_text_pos"], f"{current_price_ton:.1f}".replace(".", ",").replace(",0", ""), fill=(20, 20, 20), font=ton_price_font)
        
        # Draw dot separator
        dot_y = metadata["ton_logo_pos"][1] + 35  # Center of logo
        ton_text_width = draw.textlength(f"{current_price_ton:.1f}".replace(".", ",").replace(",0", ""), font=ton_price_font)
        dot_x = int(metadata["ton_text_pos"][0] + ton_text_width + 30)
        draw.ellipse((dot_x - 7, dot_y - 7, dot_x + 8, dot_y + 8), fill=(100, 100, 100))
        
        # Draw Stars price
        draw.text(metadata["star_text_pos"], f"{stars_price:,}".replace(",", " "), fill=(20, 20, 20), font=ton_price_font)
        
        # Add timestamp
        current_time = datetime.datetime.now().strftime("%d %b %Y • %H:%M UTC")
        timestamp_font = ImageFont.truetype(font_path, 24)
        timestamp_color = (120, 120, 120)
        timestamp_width = draw.textlength(current_time, font=timestamp_font)
        timestamp_x = x_center + (box_width - timestamp_width) // 2
        timestamp_y = y_center + box_height - 40
        draw.text((timestamp_x, timestamp_y), current_time, fill=timestamp_color, font=timestamp_font)
        
        # Add watermark at top center
        watermark_text = "@PlaceMarketBot"
        watermark_font = ImageFont.truetype(font_path, 26)
        watermark_color = (255, 255, 255, 180)  # Semi-transparent white
        watermark_width = draw.textlength(watermark_text, font=watermark_font)
        watermark_x = card.width // 2 - watermark_width // 2  # Centered horizontally
        watermark_y = 40  # 40px from top edge
        draw.text((watermark_x, watermark_y), watermark_text, fill=watermark_color, font=watermark_font)
        
        # Save the final card
        if not output_path:
            output_path = os.path.join(output_dir, f"{normalized_collection}_{normalized_pack}_card.png")
            
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        card.save(output_path)
        logger.info(f"Generated card for {collection_name} - {pack_name} at {output_path}")
            
        return card
        
    except Exception as e:
        logger.error(f"Error adding dynamic elements for {collection_name} - {pack_name}: {e}")
        return None

# Function to add random price data for a collection and pack
def add_random_price_data(collection_name, pack_name):
    """Add random price data for a collection and pack."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Generate random prices
        price_usd_new = random.randint(50, 500)
        price_ton_new = round(price_usd_new / 3.4, 12)  # Approximate TON price
        
        # No old prices for initial data
        price_ton_old = None
        price_usd_old = None
        
        # Change percentage (0 for initial data)
        change_percentage = 0
        
        # Current timestamp
        timestamp = int(datetime.datetime.now().timestamp())
        
        # Insert into price_history
        cursor.execute("""
            INSERT INTO price_history 
            (collection, pack, price_ton_old, price_usd_old, price_ton_new, price_usd_new, change_percentage, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (collection_name, pack_name, price_ton_old, price_usd_old, price_ton_new, price_usd_new, change_percentage, timestamp))
        
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        logger.error(f"Error adding random price data: {e}")
        return False

def main():
    """Main function to generate sticker cards for all collections."""
    try:
        logger.info("Starting sticker card generation")
        
        # Get all collections and packs
        collections = {}
        for collection_dir in os.listdir(sticker_dir):
            collection_path = os.path.join(sticker_dir, collection_dir)
            if os.path.isdir(collection_path):
                collections[collection_dir] = []
                for pack_dir in os.listdir(collection_path):
                    pack_path = os.path.join(collection_path, pack_dir)
                    if os.path.isdir(pack_path):
                        # Check if there are any PNG files in the pack directory
                        png_files = glob.glob(os.path.join(pack_path, "*.png"))
                        if png_files:
                            collections[collection_dir].append(pack_dir)
                        else:
                            logger.warning(f"No PNG files found in {pack_path}, skipping")
        
        # Generate cards for all collections and packs
        total_cards = 0
        
        for collection, packs in collections.items():
            # Convert underscores back to spaces for display
            collection_name = collection.replace("_", " ")
            logger.info(f"Processing collection: {collection_name}")
            
            for pack in packs:
                # Convert underscores back to spaces for display
                pack_name = pack.replace("_", " ")
                logger.info(f"Processing pack: {pack_name}")
                
                # Check if price data exists for this pack
                price_data = get_sticker_price_data(collection_name, pack_name)
                
                # If no price data exists, add some random price data
                if not price_data:
                    try:
                        # Add random price data
                        add_random_price_data(collection_name, pack_name)
                        logger.info(f"Added random price data for {collection_name} - {pack_name}")
                    except Exception as e:
                        logger.error(f"Error adding random price data: {e}")
                
                # Generate card
                card = add_dynamic_elements(collection_name, pack_name)
                if card:
                    total_cards += 1
        
        logger.info(f"Generated {total_cards} sticker cards")
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")

if __name__ == "__main__":
    main() 
