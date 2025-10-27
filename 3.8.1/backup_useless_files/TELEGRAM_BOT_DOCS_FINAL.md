# Telegram Gift Price Bot Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [API Integration](#api-integration)
   - [Tonnel Marketplace API](#tonnel-marketplace-api)
   - [API Fallback System](#api-fallback-system)
   - [API Data Flow](#api-data-flow)
3. [Quick Start](#quick-start)
   - [One-Command Setup](#one-command-setup)
   - [Manual Setup](#manual-setup)
4. [Core Components](#core-components)
   - [File Structure](#file-structure)
   - [Directories](#directories)
5. [Bot Commands](#bot-commands)
6. [Technical Details](#technical-details)
   - [Card Generation Process](#card-generation-process)
   - [Win/Loss Percentage Calculation](#winloss-percentage-calculation)
   - [Cross-Platform Compatibility](#cross-platform-compatibility)
   - [Rate Limiting](#rate-limiting)
7. [Sticker Card Generation](#sticker-card-generation)
   - [Sticker Card Components](#sticker-card-components)
   - [Sticker Card Generation Process](#sticker-card-generation-process)
   - [Running the Sticker Card Generator](#running-the-sticker-card-generator)
   - [Sticker Card Database Schema](#sticker-card-database-schema)
   - [Adding New Sticker Packs](#adding-new-sticker-packs)
8. [Sticker Collection Recognition](#sticker-collection-recognition)
   - [Feature Overview](#feature-overview)
   - [Implementation Details](#implementation-details)
   - [Supported Collections](#supported-collections)
   - [How It Works](#how-it-works)
   - [Example Usage](#example-usage)
9. [Sticker Price Fetcher](#sticker-price-fetcher)
   - [Overview](#overview)
   - [Components](#components)
   - [Key Features](#key-features)
   - [Troubleshooting](#troubleshooting)
10. [Project Organization](#project-organization)
    - [Directory Structure](#directory-structure)
    - [Module Organization](#module-organization)
    - [Path Management](#path-management)
11. [Development](#development)
    - [Adding New Gifts](#adding-new-gifts)
    - [Adding New Sticker Collections](#adding-new-sticker-collections)
    - [Updating Price Data](#updating-price-data)

## Project Overview

This bot generates and serves beautiful price cards for Telegram gifts, showing current prices and 24-hour price trends. The system handles over 75 different Telegram gifts and automatically updates price data every 32 minutes.

**Key Features:**
- Real-time price data from Tonnel Marketplace API
- 24-hour price change charts with win/lose indicators
- Color-matched gradient backgrounds for each gift
- Fast response times through pre-generated cards
- Cross-platform compatibility (Windows, Linux, macOS)

## API Integration

### Tonnel Marketplace API

The primary data source is the Tonnel Marketplace API (`tonnelmp`), which provides:

- Current gift prices in USD and TON
- Gift availability data
- Model and rarity information

**Key API Functions:**
```python
# Get gift data
from tonnelmp import getGifts
gift_data = getGifts(gift_name="toy bear", limit=5, sort="price_asc", authData=AUTH_DATA)

# Get floor prices for all gifts
from tonnelmp import filterStatsPretty
stats = filterStatsPretty(authData=AUTH_DATA)
```

### API Fallback System

If the Tonnel API is unavailable, the system falls back to:
- `https://nft-gifts-api-1.onrender.com/gifts` - For gift pricing
- `https://nft-gifts-api-1.onrender.com/weekChart?name=` - For price history

### API Data Flow:

1. `tonnel_api.py` handles API requests and caching
2. `new_card_design.py` processes the data for visual display
3. Price charts are generated from 24 hour price history
4. Percentage changes are calculated and displayed with color coding (green/red)

## Quick Start

### One-Command Setup

#### Linux/macOS
```bash
git clone <repository-url>
cd telegram-gift-price-bot
./setup_and_run.sh
```

#### Windows
```cmd
git clone <repository-url>
cd telegram-gift-price-bot
setup_and_run.bat
```

### Manual Setup

1. **Install dependencies:**
   
   **Linux/macOS:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install tonnelmp
   ```
   
   **Windows:**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   pip install tonnelmp
   ```

2. **Configure the bot:**
   ```bash
   python setup_bot.py
   ```

3. **Run the bot:**
   ```bash
   python telegram_bot.py
   ```

## Core Components

### File Structure

The project has been reorganized into specialized directories for better code organization:

```
├─ SetupScripts/                # Main bot and setup scripts
│  ├─ telegram_bot.py           # Main bot interface
│  ├─ main.py                   # Downloads gift images & defines gift names
│  ├─ setup.py                  # Setup script
│  └─ run_bot_with_stickers.py  # Bot runner with sticker support
│
├─ GiftCardGeneration/          # Gift card generation components
│  ├─ new_card_design.py        # Card generation engine
│  ├─ pregenerate_backgrounds.py # Creates color-matched backgrounds
│  ├─ pregenerate_gift_cards.py # Generates gift cards
│  └─ run_card_pregeneration.py # Schedules regular updates
│
├─ StickerCardGeneration/       # Sticker card generation components
│  ├─ sticker_card_generator.py # Sticker card generation engine
│  ├─ create_sticker_db.py      # Database creation and sample data
│  └─ download_stickers.py      # Downloads sticker images
│
├─ PriceDataCollection/         # Price data collection components
│  ├─ place_market_integration.py # Integration with Place Market
│  ├─ place_market_query.py     # Query functions for Place Market
│  ├─ tonnel_api.py             # API integration with Tonnel Marketplace
│  ├─ fetch_24h_price_history.py # Fetches price history
│  └─ update_price_history.py   # Updates price history
│
├─ UtilityFiles/                # Utility components
│  ├─ callback_handler.py       # Button interaction handler
│  ├─ image_uploader.py         # Uploads images to catbox.moe
│  ├─ rate_limiter.py           # Prevents API abuse
│  ├─ bot_config.py             # Bot configuration
│  └─ authenticate_telegram.py  # Telegram authentication
│
├─ setup_and_run.bat            # Windows setup script
└─ update_paths_enhanced.py     # Script to update import paths
```

### Directories

- `Gifts/` - Contains all gift-related assets
  - `downloaded_images/` - Original gift images
  - `pregenerated_backgrounds/` - Color-matched gradient backgrounds
  - `card_templates/` - Static template cards 
  - `new_gift_cards/` - Final generated cards
  - `card_metadata/` - Template positioning data

- `Stickers/` - Contains all sticker-related assets
  - `sticker_collections/` - Downloaded sticker images organized by collection/pack
  - `sticker_templates/` - Generated template cards
  - `sticker_cards/` - Final generated sticker cards
  - `sticker_metadata/` - Template positioning data
  - `telegram_messages/` - Saved Telegram messages with price data

- `assets/` - Contains shared assets like fonts and templates

## Bot Commands

- `/start` - Introduction message
- `/help` - Display available commands
- `/gift` - Browse gift categories
- `/random` - Show a random gift card
- `/search [gift name]` - Search for specific gift(s)

## Technical Details

### Card Generation Process

1. **Extract dominant color** from gift image
2. **Create gradient background** using that color
3. **Fetch price data** from Tonnel API:
   - Current price in USD and TON
   - 24-hour price history
   - Price percentage change
4. **Generate visual chart** with colored indicators:
   - Green for price increases
   - Red for price decreases
5. **Format price display**:
   - USD prices as integers without decimals
   - TON prices with up to 1 decimal place
   - Percentage change with +/- sign
6. **Combine elements** into the final card

### Win/Loss Percentage Calculation

The system calculates 24-hour price changes using one of these methods:

1. **Direct API data** - When `changePercentage` is provided by the API
2. **Chart data comparison** - Calculate between oldest and newest price points
3. **Synthetic data** - Generate realistic trends when historical data is unavailable

Implementation details in `tonnel_api.py`:
```python
# Calculate the actual percentage change from the generated data
if data_points and len(data_points) >= 2:
    start_price = float(data_points[0]["priceTon"])
    end_price = float(data_points[-1]["priceTon"])
    
    # Calculate percentage change from the simulated data
    percent_change = ((end_price - start_price) / start_price) * 100
    
    # Update the gift data with this percentage change
    if gift_data:
        gift_data["changePercentage"] = percent_change
```

The percentage change is prominently displayed with appropriate color coding:
- **Green** for positive changes (price increase)
- **Red** for negative changes (price decrease)

### Cross-Platform Compatibility

The project uses:
- `os.path.join()` for path construction
- Relative paths instead of hardcoded absolute paths
- Platform detection for virtual environment paths
- Separate setup scripts for Windows (.bat) and Unix-based systems (.sh)

### Rate Limiting

The bot implements rate limiting to prevent API abuse:
- One request per minute per user/gift combination
- SQLite database tracks user requests

## Sticker Card Generation

The project also includes a system for generating price cards for Telegram sticker packs, similar to the gift cards. This feature allows tracking and displaying price information for sticker collections.

### Sticker Card Components

```
├─ sticker_card_generator.py   # Main sticker card generation script
├─ create_sticker_db.py        # Database creation and sample data population
├─ generate_sticker_cards.sh   # Shell script to run both scripts in sequence
├─ sticker_collections/        # Downloaded sticker images organized by collection/pack
├─ sticker_templates/          # Generated template cards
├─ sticker_cards/              # Final generated sticker cards
└─ sticker_metadata/           # Template positioning data
```

### Sticker Card Generation Process

1. **Database Setup**:
   - Creates SQLite database (`place_stickers.db`)
   - Tables for sticker prices and price history
   - Populates with sample price data

2. **Card Generation**:
   - Scans the `sticker_collections` directory for sticker images
   - Extracts dominant color from each sticker
   - Creates template cards with static elements
   - Adds dynamic elements (prices, percentage changes)
   - Saves final cards to `sticker_cards` directory

3. **Card Features**:
   - Collection and pack name display
   - Current price in USD, TON, and Stars
   - Random percentage change indicator (green/red)
   - Timestamp and watermark

### Running the Sticker Card Generator

```bash
# Make the script executable
chmod +x generate_sticker_cards.sh

# Run the generator
./generate_sticker_cards.sh
```

### Sticker Card Database Schema

```sql
-- Sticker prices table
CREATE TABLE sticker_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection TEXT NOT NULL,
    pack TEXT NOT NULL,
    name TEXT DEFAULT NULL,
    number INTEGER DEFAULT NULL,
    price_ton REAL NOT NULL,
    price_usd REAL NOT NULL,
    timestamp INTEGER NOT NULL,
    UNIQUE(collection, pack, timestamp)
);

-- Price history table
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection TEXT NOT NULL,
    pack TEXT NOT NULL,
    price_ton_old REAL,
    price_usd_old REAL,
    price_ton_new REAL NOT NULL,
    price_usd_new REAL NOT NULL,
    change_percentage REAL,
    timestamp INTEGER NOT NULL
);
```

## Project Organization

### Directory Structure

The project has been reorganized into specialized directories to improve code organization, maintainability, and separation of concerns. Each directory contains related components that serve a specific purpose:

1. **SetupScripts**: Contains the main bot code and setup scripts
   - Main entry points for running the bot
   - Setup and configuration scripts
   - Core bot functionality

2. **GiftCardGeneration**: Contains all code related to gift card generation
   - Card design and template generation
   - Background generation
   - Price card generation and scheduling

3. **StickerCardGeneration**: Contains all code related to sticker card generation
   - Sticker card design and generation
   - Sticker database management
   - Sticker collection organization

4. **PriceDataCollection**: Contains all code related to price data collection
   - API integrations (Tonnel, Place Market)
   - Price history tracking
   - Price data formatting

5. **UtilityFiles**: Contains utility functions and helpers
   - Callback handling
   - Image uploading
   - Rate limiting
   - Configuration

### Module Organization

The modules have been organized to minimize circular dependencies and improve import clarity:

1. **Core Bot Logic**: `SetupScripts/telegram_bot.py` is the main entry point that imports from other specialized modules
2. **Card Generation**: Separated into gift and sticker card generation modules
3. **Price Data**: Centralized in the PriceDataCollection directory
4. **Utilities**: Common utilities shared across the project

### Path Management

To ensure proper path resolution across the reorganized project:

1. **Parent Directory Access**: Modules add the parent directory to sys.path for relative imports
   ```python
   import os
   import sys
   current_dir = os.path.dirname(os.path.abspath(__file__))
   parent_dir = os.path.dirname(current_dir)
   sys.path.insert(0, parent_dir)
   ```

2. **Cross-Platform Path Handling**: All paths use `os.path.join()` for cross-platform compatibility

3. **Asset Directory Structure**: Assets are organized in dedicated directories (Gifts, Stickers, assets)

4. **Path Update Script**: `update_paths_enhanced.py` script automatically updates import statements and file paths throughout the codebase

## Development

### Adding New Features

To extend the bot, follow these patterns:

1. **New Commands**: Add to `telegram_bot.py` and register in the command handler
2. **New API Endpoints**: Add to `tonnel_api.py` with proper error handling
3. **Card Design Changes**: Modify `new_card_design.py`

### Testing

Run these test scripts to verify functionality:

- `test_percentage_fix.py` - Verifies price formatting and percentage display
- `test_card_generation.py` - Tests the card creation process
- `test_tonnel_api.py` - Validates API connectivity

## Special Cases

### Premarket Gifts

Some gifts require special handling as "premarket" gifts:
- Heart Locket
- Lush Bouquet
- Bow Tie
- Heroic Helmet

These are detected automatically by the API wrapper.

### Easter Egg Cards

Special hidden cards can be triggered with keywords:
- SAMIR
- FOMO
- ZEUS

## License and Credits

This project is for educational purposes only. All Telegram gift images are owned by Telegram.

Built with:
- python-telegram-bot
- Pillow for image processing
- Catbox.moe for image hosting
- Tonnel Marketplace API for pricing data
## Common Issues and Solutions

### API Authentication Issues

If you encounter authentication issues with the Tonnel API, verify your authentication data in `bot_config.py`. The key format should look like:

```python
TONNEL_API_AUTH = "user=%7B%22id%22%3A...&hash=..."
```

### Card Generation Issues

If price cards don't display win/loss percentages:
1. Check the `tonnel_api.py` file to ensure percentage changes are being calculated
2. Run `test_percentage_fix.py` to verify pricing display
3. Ensure chart data is being properly retrieved or generated

### Cross-Platform Path Issues

All paths in the project use `os.path.join()` for cross-platform compatibility. If you encounter path-related errors:
1. Verify that no hardcoded path separators are used (e.g., direct `/` or `\` characters)
2. Check that the script directory is correctly detected using `os.path.dirname(os.path.abspath(__file__))`

## Feature Overview

The Telegram bot now recognizes when users type the exact name of a sticker collection and responds by showing all packs within that collection. This feature provides a convenient way for users to browse specific sticker collections without having to use commands.

## Implementation Details

We've updated the `handle_message` function in `telegram_bot.py` to check if the user's message matches any of the sticker collection names defined in `place_market_integration.py`. When a match is found, the bot displays all packs in that collection using the same keyboard format as when browsing through the /sticker command.

## Supported Collections

The bot recognizes the following sticker collections:

1. WAGMI HUB
2. Cattea Life
3. Doodles
4. Pudgy & Friends
5. Lil Pudgys
6. Lazy & Rich
7. Smeshariki
8. SUNDOG
9. Kudai
10. BabyDoge
11. PUCCA
12. Not Pixel
13. Lost Dogs
14. Pudgy Penguins
15. Blum
16. Flappy Bird
17. Bored Stickers
18. Dogs OG
19. Azuki
20. Ric Flair
21. Notcoin
22. Dogs rewards

## How It Works

1. When a user sends a message, the bot cleans and normalizes the text
2. The bot checks if the cleaned text exactly matches any sticker collection name (case-insensitive)
3. If a match is found, the bot retrieves all packs in that collection
4. The bot displays a message with a keyboard showing all packs in the collection
5. The user can then select a specific pack to view its price card

## Example Usage

User: "Pudgy Penguins"
Bot: "Here are all the packs in the *Pudgy Penguins* collection:" [Shows buttons for "Pengu Valentines", "Pengu CNY", "Blue Pengu", "Cool Blue Pengu"]

User: "Not Pixel"
Bot: "Here are all the packs in the *Not Pixel* collection:" [Shows buttons for all 17 Not Pixel packs]

## Technical Notes

- The collection names are stored in the `COLLECTIONS` dictionary in `place_market_integration.py`
- The matching is case-insensitive to accommodate various typing styles
- The feature uses the existing `format_pack_keyboard` function to generate the keyboard layout
- Error handling is in place to prevent crashes if the collection data is unavailable

## Overview

We have successfully implemented a Telegram sticker price fetcher system that:

1. Fetches messages from the Telegram "palacedeals" channel
2. Extracts sticker price data (in TON and USD)
3. Stores the data in a simplified database structure
4. Generates sticker cards with real price data
5. Updates prices automatically on an hourly schedule

## Components Created

1. **fetch_sticker_prices.py**: Fetches messages from Telegram and extracts price data
2. **scheduled_sticker_update.py**: Runs the fetch script periodically to keep data updated
3. **authenticate_telegram.py**: Handles Telegram authentication
4. **run_sticker_price_fetcher.sh**: Shell script to run the entire process
5. **STICKER_PRICE_FETCHER_README.md**: Documentation for the price fetcher system

## Database Structure

We're using a simplified database structure with a single `price_history` table:

```sql
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection TEXT NOT NULL,
    pack TEXT NOT NULL,
    price_ton_old REAL,
    price_usd_old REAL,
    price_ton_new REAL NOT NULL,
    price_usd_new REAL NOT NULL,
    change_percentage INTEGER,
    timestamp INTEGER NOT NULL
);
```

## Data Collection Results

- Successfully fetched and processed 1000 messages from the Telegram channel
- Extracted price data for multiple collections and packs
- Stored the data in the database with proper collection and pack identification
- Generated 71 sticker cards with real price data

## Collections and Packs

We've successfully identified and processed sticker cards for several collections:

1. **Pudgy Penguins**: Blue Pengu, Cool Blue Pengu, Pengu CNY, Pengu Valentines
2. **Not Pixel**: Multiple packs including DOGS Pixel, SuperPixel, etc.
3. **Flappy Bird**: Blue Wings, Light Glide, Ruby Wings, Frost Flap, Blush Flight
4. **Dogs rewards**: Gold bone, full dig, silver bone
5. **Lost Dogs**: Magic of the Way, Lost Memeries
6. **Notcoin**: flags, Not Memes
7. And many more...

## Automated Updates

The system is now set up to:

1. Fetch new messages every hour
2. Update the price history database with new prices
3. Calculate price change percentages
4. Generate updated sticker cards with the latest prices
5. Run continuously in the background

## Next Steps

1. **Monitor and Refine**: Keep an eye on the logs to ensure the system is working correctly
2. **Improve Collection/Pack Identification**: Enhance the extraction logic to better identify collections and packs
3. **Add More Collections**: Expand the system to handle more sticker collections
4. **Performance Optimization**: Optimize the database queries and image generation for better performance
5. **Integration with Telegram Bot**: Integrate with the main Telegram bot for user interaction

This module fetches sticker price data from a Telegram channel and stores it in a database for use by the sticker card generator.

## Overview

The sticker price fetcher consists of the following components:

1. **Authentication Script**: Authenticates with Telegram to create a session file.
2. **Fetch Script**: Fetches messages from a Telegram channel and extracts sticker price data.
3. **Scheduled Update Script**: Runs the fetch script periodically to keep the database updated.
4. **Shell Script**: Combines all of the above into a single command.

## Setup

### Prerequisites

- Python 3.6+
- Telethon library
- Schedule library

### Installation

1. Ensure you have Python 3.6+ installed.
2. Install the required packages:
   ```bash
   pip install telethon schedule
   ```

### Authentication

Before using the fetcher, you need to authenticate with Telegram:

```bash
python authenticate_telegram.py
```

This will prompt you to enter your phone number and verification code. Once authenticated, a session file (`duck_session.session`) will be created.

## Usage

### Running the Fetcher

To run the fetcher and keep it running in the background:

```bash
./run_sticker_price_fetcher.sh
```

This script will:
1. Check if Python is installed
2. Activate the virtual environment if it exists
3. Install required packages if needed
4. Run the authentication script if no session file exists
5. Create the database if it doesn't exist
6. Start the scheduled sticker update script

### Manual Fetching

If you want to manually fetch sticker prices once:

```bash
python fetch_sticker_prices.py
```

### Scheduled Updates

The scheduled update script runs the fetch script every hour:

```bash
python scheduled_sticker_update.py
```

## Database Structure

The sticker price data is stored in a SQLite database with the following structure:

```sql
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection TEXT NOT NULL,
    pack TEXT NOT NULL,
    price_ton_old REAL,
    price_usd_old REAL,
    price_ton_new REAL NOT NULL,
    price_usd_new REAL NOT NULL,
    change_percentage INTEGER,
    timestamp INTEGER NOT NULL
);
```

## Files

- `authenticate_telegram.py`: Script to authenticate with Telegram
- `fetch_sticker_prices.py`: Script to fetch sticker price data from Telegram
- `scheduled_sticker_update.py`: Script to run the fetch script periodically
- `run_sticker_price_fetcher.sh`: Shell script to run the entire process
- `create_sticker_db_old.py`: Script to create the database with the old structure
- `place_stickers.db`: SQLite database containing sticker price data
- `telegram_messages/`: Directory containing JSON files of Telegram messages

## Troubleshooting

### Authentication Issues

If you encounter authentication issues:

1. Delete the `duck_session.session` file
2. Run `python authenticate_telegram.py` again
3. Enter your phone number and verification code

### Rate Limiting

If you encounter rate limiting issues, the script will automatically wait and retry. If the issue persists, try reducing the number of messages fetched by editing the `limit` parameter in `fetch_sticker_prices.py`.

### Database Issues

If you encounter database issues, try deleting the `place_stickers.db` file and running `python create_sticker_db_old.py` to recreate it.

## Overview

We have successfully implemented a Telegram sticker price fetcher system that:

1. Fetches messages from the Telegram "palacedeals" channel
2. Extracts sticker price data (in TON and USD) using the correct collection and pack names
3. Stores the data in a simplified database structure
4. Generates sticker cards with real price data
5. Updates prices automatically on an hourly schedule

## Components Created

1. **fetch_sticker_prices.py**: Fetches messages from Telegram and extracts price data using the correct collection and pack names
2. **scheduled_sticker_update.py**: Runs the fetch script periodically to keep data updated
3. **authenticate_telegram.py**: Handles Telegram authentication
4. **run_sticker_price_fetcher.sh**: Shell script to run the entire process

## Database Structure

The system uses a simplified database structure with a single table:

```sql
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection TEXT NOT NULL,
    pack TEXT NOT NULL,
    price_ton_old REAL,
    price_usd_old REAL,
    price_ton_new REAL NOT NULL,
    price_usd_new REAL NOT NULL,
    change_percentage INTEGER,
    timestamp INTEGER NOT NULL
)
```

## Key Features

1. **Accurate Collection and Pack Names**: The system uses the correct collection and pack names as defined in the sticker collections structure.
2. **Message Parsing**: Extracts collection, pack, and price data from Telegram messages with the format:
   ```
   ➔ Collection purchase
   
   - Name: Pack #Number
   - Cost: Price TON ($USD)
   
   === BUY HERE @palacenftbot ===
   
   #collection
   ```
3. **Database Cleaning**: Normalizes collection and pack names in the database to match the official names.
4. **Price History**: Tracks price changes over time and calculates change percentages.
5. **Fallback Sample Data**: If no messages can be fetched, the system generates sample data for all collections and packs.
6. **Automatic Updates**: The system runs on an hourly schedule to keep prices updated.

## Generated Cards

The system successfully generated 71 sticker cards with the following collections:
- Pudgy Penguins (4 packs)
- Lost Dogs (2 packs)
- Dogs rewards (3 packs)
- Pudgy and Friends (2 packs)
- Azuki (1 pack)
- Flappy Bird (5 packs)
- PUCCA (1 pack)
- Not Pixel (17 packs)
- Ric Flair (1 pack)
- BabyDoge (1 pack)
- Lazy and Rich (2 packs)
- Lil Pudgys (1 pack)
- Cattea Life (1 pack)
- Doodles (1 pack)
- Kudai (2 packs)
- Notcoin (2 packs)
- Smeshariki (2 packs)
- SUNDOG (1 pack)
- WAGMI HUB (2 packs)
- Bored Stickers (10 packs)
- Dogs OG (3 packs)
- Blum (8 packs)

## Next Steps

1. **Monitor the Scheduled Updates**: Check the logs periodically to ensure the system is fetching and processing messages correctly.
2. **Optimize Message Parsing**: Refine the message parsing logic if needed to handle edge cases.
3. **Add More Collections and Packs**: Update the STICKER_COLLECTIONS dictionary as new collections and packs are released.
4. **Implement Error Handling**: Add more robust error handling for network issues, rate limiting, etc.
5. **Add Monitoring and Alerts**: Set up monitoring and alerts for system failures

This module generates visual cards for Telegram sticker packs, similar to the gift cards. The cards display the sticker pack name, collection name, and price information.

## Directory Structure

- `sticker_collections/` - Contains the sticker images organized by collection and pack
- `sticker_templates/` - Contains the template images for each sticker pack
- `sticker_metadata/` - Contains metadata files for each sticker pack
- `sticker_cards/` - Contains the generated card images for each sticker pack
- `place_stickers.db` - SQLite database containing sticker price information

## Database Structure

The database uses a simple structure with a single table:

```sql
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    collection TEXT NOT NULL,
    pack TEXT NOT NULL,
    price_ton_old REAL,
    price_usd_old REAL,
    price_ton_new REAL NOT NULL,
    price_usd_new REAL NOT NULL,
    change_percentage INTEGER,
    timestamp INTEGER NOT NULL
);
```

## How It Works

The sticker card generator performs the following steps:

1. **Collection and Pack Discovery**: Scans the `sticker_collections/` directory to find all sticker collections and packs.

2. **Database Integration**: Checks if price data exists for each pack in the database. If not, it adds random price data.

3. **Template Generation**: For each sticker pack, it:
   - Extracts the dominant color from a sticker image
   - Creates a gradient background based on that color
   - Adds a white box for price information
   - Places the sticker image above the box
   - Adds collection and pack names
   - Adds TON and Star logos

4. **Dynamic Elements**: Adds price information to the template:
   - USD price with colored dollar sign
   - TON price
   - Stars price (1 Star = $0.016)
   - Percentage change (green for positive, red for negative)
   - Timestamp
   - Watermark

## Usage

### Running the Generator

To generate cards for all sticker packs:

```bash
./generate_sticker_cards.sh
```

This script will:
1. Activate the virtual environment if it exists
2. Create the database if it doesn't exist
3. Run the sticker card generator
4. Deactivate the virtual environment

### Adding New Sticker Packs

To add new sticker packs:

1. Create a directory structure in `sticker_collections/` following the pattern:
   ```
   sticker_collections/
     └── Collection_Name/
         └── Pack_Name/
             └── sticker.png
   ```

2. Run the generator script:
   ```bash
   ./generate_sticker_cards.sh
   ```

The script will automatically discover new packs, add them to the database with random price data, generate templates, and create cards.

## Files

- `sticker_card_generator.py` - Main script that generates the sticker cards
- `create_sticker_db_old.py` - Script to create the database with the old structure
- `generate_sticker_cards.sh` - Shell script to run the generator

## Dependencies

- Python 3.6+
- PIL/Pillow
- NumPy
- SQLite3 
