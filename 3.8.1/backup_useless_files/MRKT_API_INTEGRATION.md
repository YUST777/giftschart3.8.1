# MRKT API Integration and Sticker Price Card Generation

This document provides a comprehensive overview of the integration with the MRKT API for fetching real-time sticker price data and generating price cards for Telegram stickers.

## Table of Contents

1. [Overview](#overview)
2. [MRKT API Integration](#mrkt-api-integration)
3. [Sticker Mapping](#sticker-mapping)
4. [Price Data Collection](#price-data-collection)
5. [Price Card Generation](#price-card-generation)
6. [Troubleshooting](#troubleshooting)
7. [Future Improvements](#future-improvements)

## Overview

The system integrates with the MRKT API to fetch real-time price data for Telegram stickers and generates visually appealing price cards. This involves several steps:

1. Authentication with the MRKT API
2. Mapping between API sticker IDs and local naming conventions
3. Fetching and caching price data
4. Generating price cards using templates

## MRKT API Integration

### Authentication

The system uses an authentication token stored in `mrkt_auth_token.txt` to authenticate with the MRKT API. The token is refreshed automatically when needed.

```python
# From mrkt_api_improved.py
def authenticate():
    """Authenticate with MRKT API and get a token"""
    try:
        # First check if we have a valid token
        token = get_token_from_file()
        if token and not is_token_expired(token):
            return token
            
        # If no valid token, authenticate
        logger.info("Authenticating with MRKT API")
        # Authentication logic...
        
        # Save token to file
        save_token_to_file(token)
        return token
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None
```

### API Endpoints

The main API endpoints used are:

- `/auth` - For authentication
- `/characters` - For fetching sticker data
- `/collections` - For fetching collection data

## Sticker Mapping

One of the key challenges was mapping between the MRKT API's collection/character ID system and the local naming convention used in the codebase.

### Collection ID Mapping

The system maintains a mapping between collection names and their IDs in the MRKT API:

```python
# Collection ID to name mapping
COLLECTION_ID_TO_NAME = {
    2: 'Pudgy Penguins',
    16: 'Pudgy & Friends',
    11: 'BabyDoge',
    # ... more mappings
}
```

### Sticker Mapping

The `update_mrkt_mapping.py` script creates a comprehensive mapping between API sticker IDs and local naming conventions:

```json
{
  "collection_mapping": {
    "24": "Azuki",
    "11": "BabyDoge",
    "4": "Blum"
    // ... more mappings
  },
  "sticker_mapping": {
    "24:1": {
      "collection_name": "Azuki",
      "sticker_name": "Shao",
      "normalized_collection": "Azuki",
      "normalized_sticker": "Shao",
      "local_format": "Azuki - Shao"
    }
    // ... more mappings
  },
  "local_to_api_mapping": {
    "Azuki_Shao": "24:1",
    "BabyDoge_Mememania": "11:1"
    // ... more mappings
  }
}
```

This mapping is stored in `mrkt_sticker_mapping.json` and is used to translate between API identifiers and local file naming conventions.

## Price Data Collection

### Fetching Price Data

The `update_mrkt_mapping.py` script fetches price data from the MRKT API and stores it in a structured format:

```python
def update_sticker_prices():
    """Update sticker prices with real data from MRKT API"""
    # Clear API cache to ensure fresh data
    mrkt_api.clear_cache()
    
    # Fetch all stickers from API
    stickers_data = mrkt_api.fetch_characters(use_cache=False)
    
    # Process each sticker and extract price data
    for sticker in stickers_data:
        collection_id = sticker.get('stickerCollectionId')
        sticker_id = sticker.get('id')
        sticker_name = sticker.get('name', '')
        
        # Get price data from floor price already in the sticker data
        price_in_nano = sticker.get('floorPriceNanoTons', 0) or 0  # Handle None values
        price_in_ton = mrkt_api.convert_nano_ton(price_in_nano)
        
        # Store price data
        updated_stickers.append({
            "collection": collection_name,
            "sticker": sticker_name,
            "price": price_in_ton,
            "supply": sticker.get('supply', 0) or 0,
            "is_real_data": True if price_in_nano > 0 else False
        })
```

### Price Data Storage

The price data is stored in `sticker_price_results.json` with the following structure:

```json
{
  "timestamp": "2025-06-20T19:49:41.112",
  "total_templates": 141,
  "successful": 136,
  "failed": 1,
  "stickers_with_prices": [
    {
      "collection": "Azuki",
      "sticker": "Shao",
      "price": 77.7655,
      "supply": 3333,
      "is_real_data": true
    },
    // ... more stickers
  ]
}
```

## Price Card Generation

### Template-Based Generation

The system uses pre-designed templates to generate price cards. The templates are stored in the `sticker_templates` directory.

### Card Generation Process

The `sticker_price_card_generator.py` script handles the generation of price cards:

1. Load the template for a specific sticker
2. Extract the dominant color from the template for styling
3. Calculate USD price based on TON price
4. Draw price information on the card
5. Add generation date at the bottom middle of the card
6. Save the generated card to the `Sticker_Price_Cards` directory

```python
def generate_price_card(collection, sticker, price, output_dir):
    """Generate a price card for a sticker using the template"""
    # Find template with case-insensitive matching
    template_path = find_template_case_insensitive(collection_norm, sticker_norm)
    
    # Load template image
    template = Image.open(template_path).convert("RGBA")
    
    # Get dominant color from the template
    dominant_color = get_dominant_color(template_path)
    
    # Calculate USD price
    price_usd = price * TON_TO_USD
    
    # Calculate price in Telegram Stars
    stars_price = int(price_usd / 0.016)
    
    # Dollar sign and USD price - use exact positions from gift card
    dollar_x = x_center + 180
    dollar_y = y_center + 300  # Positioned for better visual balance

    # Draw dollar sign with the dominant color
    dollar_color = dominant_color
    price_color = (20, 20, 20)  # Almost black
    draw.text((dollar_x, dollar_y), "$", fill=dollar_color, font=price_font)

    # Draw USD price
    draw.text((dollar_x + 100, dollar_y), f"{price_usd:,.0f}".replace(",", " "), fill=price_color, font=price_font)

    # Position for TON price text
    ton_y = y_center + 490  # Positioned below the USD price
    ton_text_y = ton_y
    
    # Add generation date at the bottom middle of the card
    current_date = datetime.datetime.now().strftime("%d %b %Y • %H:%M UTC")
    date_text = current_date
    date_text_width = draw.textlength(date_text, font=date_font)
    date_x = width // 2 - date_text_width // 2
    date_y = y_center + 850  # Position at bottom of white card area
    draw.text((date_x, date_y), date_text, fill=(100, 100, 100), font=date_font)
    
    # Save the card
    output_filename = f"{collection_norm}_{sticker_norm}_price_card.png"
    output_path = os.path.join(output_dir, output_filename)
    template.save(output_path)
```

### Case-Insensitive Template Matching

To handle differences in capitalization between the API data and local file naming, the system implements case-insensitive template matching:

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

## Troubleshooting

### Common Issues and Solutions

1. **Missing Templates**: If a template is missing, the card generation will fail. Create the missing template in the `sticker_templates` directory.

2. **Capitalization Mismatches**: The system now handles case-insensitive template matching to address capitalization differences between API data and local file naming.

3. **Zero Prices**: If a sticker shows a price of $0, check:
   - If the sticker is actually not for sale (e.g., Doodles - OG Icons)
   - If there's a mapping issue between the API data and local naming

4. **API Authentication Failures**: If API authentication fails, check the token in `mrkt_auth_token.txt` and ensure it's valid.

### Debugging

The system implements comprehensive logging to help with debugging:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sticker_price_card_generator')
```

## Future Improvements

1. **Automatic Template Generation**: Implement automatic generation of templates for new stickers.

2. **Periodic Price Updates**: Set up a scheduled task to update prices regularly.

3. **Improved Error Handling**: Enhance error handling for API rate limits and timeouts.

4. **UI for Price Card Management**: Develop a user interface for managing price cards.

5. **Integration with Telegram Bot**: Integrate the price card generation with the Telegram bot for real-time price queries.
