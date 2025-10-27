#!/usr/bin/env python3
"""
Sticker Template Generator for Telegram

This script generates new templates for sticker price cards using the same layout as shown
in the screenshot. It extracts dominant colors from stickers and applies them to the background.
"""

import os
import json
import logging
import glob
import colorsys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("sticker_template_generator")

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Directory paths
STICKER_DIR = os.path.join(script_dir, "sticker_collections")
OUTPUT_DIR = os.path.join(script_dir, "test", "templates")
METADATA_DIR = os.path.join(script_dir, "test", "metadata")
ASSETS_DIR = os.path.join(script_dir, "assets")
FONT_PATH = os.path.join(script_dir, "Typekiln - EloquiaDisplay-ExtraBold.otf")

# Asset paths
BACKGROUND_PATH = os.path.join(ASSETS_DIR, "Background color this.png")
WHITE_BOX_PATH = os.path.join(ASSETS_DIR, "white box for sticker.png")

# Target dimensions
TARGET_WIDTH = 1600
TARGET_HEIGHT = 1000

# Create output directories if they don't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)

def get_dominant_color(image_path):
    """Extract the dominant color from an image."""
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

def apply_color_to_background(background_img, color):
    """Apply color to the background image with gradient effect."""
    try:
        # Create a new image with the same size and mode
        width, height = background_img.size
        gradient_bg = Image.new('RGBA', background_img.size, (0, 0, 0, 0))
        
        # Extract color components
        r, g, b = color
        
        # Create darker shade for edges and lighter for center
        darker_color = (max(0, int(r * 0.65)), max(0, int(g * 0.65)), max(0, int(b * 0.65)), 255)
        lighter_color = (min(255, int(r * 1.15)), min(255, int(g * 1.15)), min(255, int(b * 1.15)), 255)
        
        # Create a slightly different hue for added depth
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        h = (h + 0.05) % 1.0  # Shift hue slightly
        s = min(1.0, s * 1.2)  # Increase saturation
        accent_r, accent_g, accent_b = colorsys.hsv_to_rgb(h, s, v)
        accent_color = (int(accent_r*255), int(accent_g*255), int(accent_b*255), 255)
        
        # Create radial gradient
        small_size = (200, 200)
        small_gradient = Image.new('RGBA', small_size, (0, 0, 0, 0))
        small_draw = ImageDraw.Draw(small_gradient)
        
        # Draw concentric circles
        center = (small_size[0] // 2, small_size[1] // 2)
        max_radius = int(((small_size[0] // 2) ** 2 + (small_size[1] // 2) ** 2) ** 0.5)
        
        # Draw gradient with more steps for smoother transition
        num_steps = 40
        for i in range(num_steps):
            radius = max_radius * (1 - (i / num_steps))
            factor = i / num_steps
            
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
            bbox = (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius)
            small_draw.ellipse(bbox, fill=current_color)
        
        # Resize the small gradient to full size
        gradient_bg = small_gradient.resize(background_img.size, Image.BICUBIC)
        
        # Use the original background's alpha channel as a mask
        if background_img.mode == 'RGBA':
            r, g, b, a = background_img.split()
            gradient_bg.putalpha(a)
            
        return gradient_bg
    except Exception as e:
        logger.error(f"Error applying color to background: {e}")
        return background_img  # Return original background on error

def find_sticker_image(collection_name, sticker_name):
    """Find a sticker image in the sticker collections directory."""
    try:
        # Try to find any PNG file in the directory
        sticker_dir = os.path.join(STICKER_DIR, collection_name, sticker_name)
        png_files = glob.glob(os.path.join(sticker_dir, "*.png"))
        
        if png_files:
            return png_files[0]
        
        return None
    except Exception as e:
        logger.error(f"Error finding sticker image for {collection_name}/{sticker_name}: {e}")
        return None

def generate_sticker_template(collection_name, sticker_name):
    """Generate a sticker template matching the layout shown in the screenshot."""
    try:
        # Normalize names for filesystem compatibility
        normalized_collection = collection_name.replace(" ", "_").replace("-", "_").replace("'", "")
        normalized_sticker = sticker_name.replace(" ", "_").replace("-", "_").replace("'", "")
        
        # Output paths
        template_path = os.path.join(OUTPUT_DIR, f"{normalized_collection}_{normalized_sticker}_template.png")
        metadata_path = os.path.join(METADATA_DIR, f"{normalized_collection}_{normalized_sticker}_metadata.json")
        
        # Check if template already exists
        if os.path.exists(template_path):
            logger.info(f"Template already exists for {collection_name} - {sticker_name}")
            return template_path
            
        # Find sticker image
        sticker_img_path = find_sticker_image(normalized_collection, normalized_sticker)
        
        if not sticker_img_path:
            logger.error(f"No image found for {collection_name} - {sticker_name}")
            return None
            
        logger.info(f"Using sticker image: {sticker_img_path}")
        
        # Load assets
        background_img = Image.open(BACKGROUND_PATH).convert("RGBA")
        white_box_img = Image.open(WHITE_BOX_PATH).convert("RGBA")
        
        # Resize to target dimensions
        target_size = (TARGET_WIDTH, TARGET_HEIGHT)
        background_img = background_img.resize(target_size)
        white_box_img = white_box_img.resize(target_size)
        
        # Get dominant color from sticker
        dominant_color = get_dominant_color(sticker_img_path)
        logger.info(f"Extracted dominant color: {dominant_color}")
        
        # Apply color to background
        colored_background = apply_color_to_background(background_img, dominant_color)
        
        # Create template canvas
        template = Image.new('RGBA', target_size, (0, 0, 0, 0))
        
        # Paste colored background
        template.paste(colored_background, (0, 0), colored_background)
        
        # Add shadow for white box
        shadow_offset = 5
        shadow_blur = 10
        shadow_opacity = 40
        
        shadow = Image.new('RGBA', target_size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        
        # Calculate center position for white box
        box_width, box_height = white_box_img.size
        x_center = (target_size[0] - box_width) // 2
        y_center = (target_size[1] - box_height) // 2
        
        # Create shadow rectangle
        shadow_rect = (
            x_center + shadow_offset, 
            y_center + shadow_offset, 
            x_center + box_width + shadow_offset, 
            y_center + box_height + shadow_offset
        )
        shadow_draw.rectangle(shadow_rect, fill=(0, 0, 0, shadow_opacity))
        
        # Blur shadow
        shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
        
        # Composite shadow onto template
        template = Image.alpha_composite(template, shadow)
        
        # Paste white box
        template.paste(white_box_img, (x_center, y_center), white_box_img)
        
        # Draw context
        draw = ImageDraw.Draw(template)
        
        # Format display text (replace underscores with spaces)
        display_collection = collection_name.replace("_", " ")
        display_sticker = sticker_name.replace("_", " ")
        
        # Load fonts
        try:
            title_font = ImageFont.truetype(FONT_PATH, 100)  # For collection name
            subtitle_font = ImageFont.truetype(FONT_PATH, 60)  # For sticker name
        except Exception as e:
            logger.error(f"Error loading font: {e}")
            # Fallback to default font
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Draw collection and sticker names (top left of white box)
        name_color = (60, 60, 60)  # Dark gray
        subtitle_color = (100, 100, 100)  # Light gray
        
        # Match positions to screenshot
        name_x = x_center + 155  # Increased from 115 to 155 to move text more to the right
        name_y = y_center + 115
        
        # Draw collection name
        draw.text((name_x, name_y), display_collection, fill=name_color, font=title_font)
        
        # Draw sticker name below collection name
        draw.text((name_x, name_y + 110), display_sticker, fill=subtitle_color, font=subtitle_font)
        
        # Open sticker image
        sticker_img = Image.open(sticker_img_path).convert("RGBA")
        
        # Calculate the right half of the white box width for sticker display
        right_half_width = box_width // 2
        
        # Make the sticker fill the entire right half of the white box
        # Set the width to fill almost the entire right half
        sticker_target_width = int(right_half_width * 0.8)  # Make it 80% of the right half width
        
        # Get original aspect ratio to maintain proportions
        original_width, original_height = sticker_img.size
        aspect_ratio = original_height / original_width
        
        # Calculate the new height based on the target width and original aspect ratio
        sticker_target_height = int(sticker_target_width * aspect_ratio)
        
        # Use resize instead of thumbnail to actually make the image larger
        sticker_img = sticker_img.resize((sticker_target_width, sticker_target_height), Image.BICUBIC)
        
        # Position sticker in the right half of the white box
        sticker_x = x_center + box_width - sticker_target_width - 70  # Increased right margin to center it better
        sticker_y = y_center + (box_height - sticker_target_height) // 2  # Vertically centered
        
        # Paste sticker image
        template.paste(sticker_img, (sticker_x, sticker_y), sticker_img)
        
        # Save template
        template.save(template_path)
        logger.info(f"Generated template for {collection_name} - {sticker_name} at {template_path}")
        
        # Store metadata for this template
        metadata = {
            "collection_name": display_collection,
            "sticker_name": display_sticker,
            "template_path": template_path,
            "dominant_color": dominant_color,
            "x_center": x_center,
            "y_center": y_center,
            "card_width": TARGET_WIDTH,
            "card_height": TARGET_HEIGHT,
            # Price text positions based on screenshot layout
            "dollar_x": name_x,
            "dollar_y": name_y + 170,  # Dollar sign Y position
            "ton_x": name_x,
            "ton_y": name_y + 350,  # TON price Y position
            "star_x": name_x + 300,  # Star price X position
            "star_y": name_y + 350,  # Star price Y position
            "supply_x": sticker_x + sticker_target_width // 2,  # Center below sticker
            "supply_y": sticker_y + sticker_target_height + 40  # Below sticker
        }
        
        # Save metadata
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        return template_path
        
    except Exception as e:
        logger.error(f"Error generating template for {collection_name} - {sticker_name}: {e}")
        return None

def process_all_stickers():
    """Process all sticker collections and generate templates."""
    # Get all collection directories
    collections = [d for d in os.listdir(STICKER_DIR) if os.path.isdir(os.path.join(STICKER_DIR, d))]
    
    success_count = 0
    error_count = 0
    
    for collection in collections:
        # Get all sticker directories in this collection
        collection_path = os.path.join(STICKER_DIR, collection)
        stickers = [d for d in os.listdir(collection_path) if os.path.isdir(os.path.join(collection_path, d))]
        
        logger.info(f"Processing collection {collection} with {len(stickers)} stickers")
        
        for sticker in stickers:
            logger.info(f"Generating template for {collection} - {sticker}")
            result = generate_sticker_template(collection, sticker)
            
            if result:
                success_count += 1
            else:
                error_count += 1
    
    logger.info(f"Template generation complete. Success: {success_count}, Errors: {error_count}")
    return success_count, error_count

def main():
    """Main function."""
    logger.info("Starting sticker template generation")
    
    # Example: Generate template for the sticker shown in screenshot
    result = generate_sticker_template("Pudgy_and_Friends", "Pengu_x_NASCAR")
    
    if result:
        logger.info(f"Successfully generated template at {result}")
    else:
        logger.error("Failed to generate example template")
    
    # Process all stickers
    print("Do you want to process all stickers? (y/n)")
    choice = input().lower()
    
    if choice == 'y':
        success, errors = process_all_stickers()
        print(f"Generated {success} templates with {errors} errors")
    else:
        print("Template generation for all stickers skipped")

if __name__ == "__main__":
    main() 