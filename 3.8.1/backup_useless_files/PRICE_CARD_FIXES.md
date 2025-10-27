# Price Card Generation Fixes and Improvements

This document summarizes the issues that were identified and fixed in the sticker price card generation process, as well as design improvements.

## Issue Summary

Several stickers were showing $0 prices on their cards despite having actual prices in the MRKT API. The affected stickers included:

- Dogs rewards - Silver bone (86.0 TON)
- Dogs rewards - Full dig (2.795 TON)
- Notcoin - Flags (182.75 TON)
- Ric Flair - Ric Flair (9.46 TON)

## Root Causes

1. **Case Sensitivity Mismatch**: The primary issue was a case sensitivity mismatch between the API data and local file naming conventions. For example:
   - API returned "Silver bone" with uppercase "S"
   - Template file was named with lowercase "silver_bone"

2. **Inconsistent Naming**: Some stickers had inconsistent naming between the API and local files.

3. **Missing Templates**: Some stickers didn't have corresponding template files in the `sticker_templates` directory.

## Implemented Fixes

### 1. Case-Insensitive Template Matching

Added a robust case-insensitive template matching function that tries multiple variations of the filename:

```python
def find_template_case_insensitive(collection_norm, sticker_norm):
    """Find template file with case-insensitive matching"""
    # Try exact match first
    template_path = os.path.join(TEMPLATES_DIR, f"{collection_norm}_{sticker_norm}_template.png")
    if os.path.exists(template_path):
        return template_path
    
    # Try with lowercase sticker name
    template_path = os.path.join(TEMPLATES_DIR, f"{collection_norm}_{sticker_norm.lower()}_template.png")
    if os.path.exists(template_path):
        return template_path
    
    # Try with lowercase collection and sticker name
    template_path = os.path.join(TEMPLATES_DIR, f"{collection_norm.lower()}_{sticker_norm.lower()}_template.png")
    if os.path.exists(template_path):
        return template_path
    
    # Try to find any matching file by listing directory and comparing case-insensitive
    try:
        for filename in os.listdir(TEMPLATES_DIR):
            expected_name = f"{collection_norm}_{sticker_norm}_template.png".lower()
            if filename.lower() == expected_name:
                return os.path.join(TEMPLATES_DIR, filename)
    except Exception as e:
        logger.error(f"Error searching for template: {e}")
    
    return None
```

### 2. Improved Price Extraction

Fixed the price extraction from the MRKT API to properly handle None values:

```python
# Get price data from floor price already in the sticker data
price_in_nano = sticker.get('floorPriceNanoTons', 0) or 0  # Handle None values
price_in_ton = mrkt_api.convert_nano_ton(price_in_nano)
```

### 3. Date Generation Feature

Added a timestamp to each generated price card showing when it was created:

```python
# Add generation date at the bottom middle of the card
current_date = datetime.datetime.now().strftime("%d %b %Y • %H:%M UTC")
date_text = current_date
date_text_width = draw.textlength(date_text, font=date_font)
date_x = width // 2 - date_text_width // 2
date_y = white_box_y + WHITE_BOX_HEIGHT - 50  # Position at bottom of white card area
draw.text((date_x, date_y), date_text, fill=(100, 100, 100), font=date_font)
```

### 4. Improved Price Positioning

Adjusted the positioning of price information for better visual balance:

```python
# Dollar sign and USD price
dollar_x = collection_x + 20
dollar_y = sticker_y + subtitle_font.getbbox("A")[3] + 50  # Add spacing after sticker name
```

### 5. Modern Card Design

Completely redesigned the price cards with a modern, clean layout:

```python
# Create a new blank image with the dominant color as background
card = Image.new('RGBA', (CARD_WIDTH, CARD_HEIGHT), dominant_color)
draw = ImageDraw.Draw(card)

# Draw white rounded rectangle
create_rounded_rectangle(
    draw, 
    (white_box_x, white_box_y, white_box_x + WHITE_BOX_WIDTH, white_box_y + WHITE_BOX_HEIGHT),
    WHITE_BOX_RADIUS,
    (255, 255, 255, 255)  # White color
)

# Draw collection name
draw.text((collection_x, collection_y), collection, fill=(20, 20, 20), font=title_font)

# Draw sticker name
draw.text((collection_x, sticker_y), sticker, fill=(80, 80, 80), font=subtitle_font)

# Draw dollar sign in lighter color (using dominant color with transparency)
dollar_color = (*dominant_color[:3], 150)  # Use dominant color with transparency
draw.text((dollar_x, dollar_y), "$", fill=dollar_color, font=price_font)
```

## Design Improvements

The new design includes:

1. **Background Color**: Uses the dominant color from the sticker as the background
2. **White Rounded Box**: A clean white box with rounded corners contains the content
3. **Larger Typography**: Collection name and price are displayed in larger fonts
4. **Sticker Image**: Displays the actual sticker image on the right side
5. **Visual Hierarchy**: Clear separation between collection name, sticker name, and price
6. **Horizontal Line**: Separates the price from the TON price information
7. **Triangle Symbol**: Uses a purple triangle symbol before the TON price
8. **House Icon**: Small house icon in the top right corner
9. **Date Stamp**: Date and time of generation at the bottom

## Results

After implementing these fixes and design improvements:

1. **Reduced $0 Price Cards**: The number of stickers showing $0 price was reduced from 41 to just 1 (Doodles - OG Icons, which legitimately can't be sold).

2. **Improved Template Matching**: The system now correctly finds template files regardless of capitalization differences.

3. **Added Generation Date**: Each card now shows when it was generated in the format "DD MMM YYYY • HH:MM UTC" at the bottom of the card.

4. **Modern Design**: The cards now have a clean, modern design that highlights the sticker name and price.

5. **Successful Card Generation**: Successfully generated price cards for 70 stickers, with only 1 showing $0 price (which is correct).

## Remaining Challenges

1. **Missing Templates**: Some stickers still don't have template files. Consider generating templates automatically.

2. **API Rate Limiting**: The MRKT API may impose rate limits during heavy usage. The system should implement better retry logic.

3. **Price Volatility**: Prices can change frequently. Consider implementing a scheduled task to update prices regularly.

## Future Work

1. **Automatic Template Generation**: Develop a system to automatically generate templates for new stickers.

2. **Scheduled Price Updates**: Implement a scheduled task to update prices at regular intervals.

3. **Improved Error Handling**: Enhance error handling for API rate limits and timeouts.

4. **UI for Price Card Management**: Create a user interface for managing price cards.
