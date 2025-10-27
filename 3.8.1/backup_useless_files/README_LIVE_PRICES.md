# Live Price Data Integration

This document explains the changes made to the sticker price card generation system to support live price data from the MRKT API.

## Understanding the Caching System

The project uses two separate caching mechanisms:

1. **MRKT API Cache** (in `mrkt_api_improved.py`):
   - Contains real-time market prices that change frequently
   - Reflects current trading prices after the initial sale
   - These are dynamic values that need to be refreshed regularly

2. **Supply Data Cache** (in `sticker_price_results.json`):
   - Contains information about the initial sale and total supply
   - Includes fixed values like total supply that don't change
   - This data is relatively static and doesn't need frequent updates

## New Scripts

### 1. `generate_live_price_card.py`

This script generates a price card using live data from the MRKT API:

```bash
python generate_live_price_card.py --collection "Pudgy Penguins" --sticker "Blue Pengu"
```

Features:
- Clears the API cache to ensure fresh data
- Fetches real-time price information from the MRKT API
- Generates a price card with the original design but using live price data
- Shows cache usage statistics in the output

### 2. `compare_prices.py`

This script compares cached prices with live prices:

```bash
python compare_prices.py --limit 5
```

Features:
- Loads cached price data from `sticker_price_results.json`
- Fetches live price data from the MRKT API
- Compares the two and calculates price differences and percentage changes
- Saves the results to `price_comparison_results.json`
- Shows a summary of successful and failed comparisons

### 3. `update_sticker_price_results.py`

This script updates the `sticker_price_results.json` file with fresh data from the MRKT API:

```bash
python update_sticker_price_results.py
```

Features:
- Loads existing price data from the JSON file
- Updates the prices with live data from the MRKT API
- Keeps the existing supply data
- Saves the updated data back to the JSON file

## Terminal Output

The scripts now show more detailed information in the terminal:

- `🌐 LIVE API: Fetching fresh price data for [sticker] from MRKT API`
- `📦 CACHE: Using cached supply data for [collection] - [sticker]`
- `✅ Generated price card for [collection] - [sticker] using [data_source] data: [file_path]`
- `💾 SUMMARY: Generated [successful] cards - [cached] from cache, [live] from live API, [failed] failed`

## Authentication

The MRKT API authentication token has been updated to:
```
{"data":"user=%7B%22id%22%3A7660176383%2C%22first_name%22%3A%22Afsado%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22Afsado%22%2C%22language_code%22%3A%22en%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2F42a5aspTdutRS8KbBc1zWKx5ZYpgjr2PXp5bKEDI91diLJxdTzXtvUussQcWf6g0.svg%22%7D&chat_instance=-6007791381635729774&chat_type=sender&auth_date=1750674849&signature=CDISSs-YDzfpoMgecsazM_9OVMnS0jpRH1Ad-47BXB4Jwh98T3PmrjlKPUzhqTbRA6JXHSNPznbxkkN80sboBQ&hash=97a53412aba54fd0830fcc6d6fc5e470808b9d61b3aa949cf5ce4d92d90223f3","photo":"https://t.me/i/userpic/320/42a5aspTdutRS8KbBc1zWKx5ZYpgjr2PXp5bKEDI91diLJxdTzXtvUussQcWf6g0.svg","appId":null}
``` 