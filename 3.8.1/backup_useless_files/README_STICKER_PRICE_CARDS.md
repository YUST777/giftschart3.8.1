# Sticker Price Cards

This document explains the process of generating sticker price cards using real-time price data from the MRKT API.

## Overview

The sticker price cards are visual representations of Telegram stickers with their real-time prices displayed. These cards are generated using templates and price data fetched from the MRKT API. The design matches exactly the gift card design.

## Key Components

1. **sticker_price_card_generator.py**: Main script that generates sticker price cards
2. **mrkt_api_improved.py**: Core API integration for fetching real-time price data
3. **sticker_templates/**: Directory containing template images for each sticker
4. **Sticker_Price_Cards/**: Output directory for the generated price cards

## Price Data

All price data is fetched from the MRKT API in real-time. The prices are stored in `sticker_price_results.json` for reference.

## Card Design

Each price card includes:
- Sticker template as the background (which already contains TON and Star logos)
- Price in TON (positioned at the exact same coordinates as gift cards)
- Price in USD (positioned at the exact same coordinates as gift cards)
- Price in Stars (positioned at the exact same coordinates as gift cards)

The design is identical to the gift cards, using the exact same positions for all elements. The script only adds the price text, as the TON and Star logos are already included in the template.

## Top 10 Most Valuable Stickers

1. **Gold bone** (Dogs rewards): 5,375.00 TON ($16,125.00)
2. **Not Cap** (Dogs OG): 477.30 TON ($1,431.90)
3. **Pengu x Baby Shark** (Pudgy & Friends): 299.93 TON ($899.79)
4. **Sheikh** (Dogs OG): 174.80 TON ($524.40)
5. **Flags** (Notcoin): 170.00 TON ($510.00)
6. **Cool Blue Pengu** (Pudgy Penguins): 160.18 TON ($480.54)
7. **Pengu x NASCAR** (Pudgy & Friends): 118.25 TON ($354.75)
8. **Cute pack** (Not Pixel): 96.75 TON ($290.25)
9. **3278** (Bored Stickers): 95.68 TON ($287.04)
10. **Random memes** (Not Pixel): 90.30 TON ($270.90)

## Usage

### Generate All Price Cards

```bash
python3 sticker_price_card_generator.py
```

This will generate price cards for all stickers with valid prices from the MRKT API.

### Generate a Specific Price Card

```bash
python3 sticker_price_card_generator.py --collection "Collection Name" --sticker "Sticker Name"
```

Example:
```bash
python3 sticker_price_card_generator.py --collection "Dogs rewards" --sticker "Gold bone"
```

### Specify Output Directory

```bash
python3 sticker_price_card_generator.py --output-dir "custom_output_directory"
```

## Results

All 71 stickers have valid prices from the MRKT API, ensuring 100% coverage. The price cards are stored in the `Sticker_Price_Cards` directory. 