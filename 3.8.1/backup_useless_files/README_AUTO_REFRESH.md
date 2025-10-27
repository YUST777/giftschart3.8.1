# Automatic Sticker Price Refresh System

This system automatically fetches the latest sticker prices from the MRKT API and regenerates all sticker price cards every 32 minutes.

## How It Works

The system consists of two main scripts:

1. `fetch_sticker_prices.py`: Fetches the latest prices from the MRKT API
2. `generate_all_sticker_price_cards.py`: Generates price cards using the updated price data

These scripts are orchestrated by the `scheduled_sticker_update.py` script, which runs them automatically every 32 minutes.

## How to Use

### One-Time Setup

1. Make sure all required dependencies are installed:
   ```
   source venv/bin/activate
   pip install schedule fuzzywuzzy
   ```

2. Ensure your MRKT API token is valid in `mrkt_auth_token.txt`

### Running the Automatic Update Service

To start the automatic update service, use the provided shell script:

```bash
./run_price_updater.sh
```

This will:
1. Activate the virtual environment
2. Run the scheduled_sticker_update.py script
3. Immediately fetch the latest prices and generate all cards
4. Schedule automatic updates every 32 minutes
5. Keep running in the background

### Running Forever (Set and Forget)

To run the service indefinitely, even after closing your terminal, use:

```bash
nohup ./run_price_updater.sh > price_update.log 2>&1 &
```

This will:
1. Start the service in the background
2. Redirect all output to `price_update.log`
3. Keep running even if you close your terminal

To check if the service is still running:

```bash
ps aux | grep scheduled_sticker_update.py
```

To stop the service:

```bash
pkill -f scheduled_sticker_update.py
```

## Logs and Monitoring

The system generates detailed logs in two files:

1. `schedule_output.log`: Contains information about the scheduled runs
2. `price_updater.log`: Contains information about the price fetching process

You can monitor these logs in real-time using:

```bash
tail -f price_update.log
```

## Features

The automatic refresh system includes:

1. **Real-time Progress Tracking**:
   - Progress bars showing completion percentage
   - Estimated time remaining for each operation
   - Execution time statistics

2. **Data Freshness Indicators**:
   - 🟢 FRESH: Data is less than 32 minutes old
   - 🔴 STALE: Data is more than 32 minutes old
   - ⚪ UNKNOWN: Data freshness cannot be determined

3. **Detailed Execution Statistics**:
   - Time taken for each operation
   - Number of API calls made
   - Cache vs. live API usage metrics
   - Average processing time per item

4. **Price Change Tracking**:
   - ↗️ Indicates price increases
   - ↘️ Indicates price decreases
   - → Indicates unchanged prices

## Customizing the Update Interval

If you want to change the update interval, edit the `scheduled_sticker_update.py` file and change:

```python
schedule.every(32).minutes.do(run_update_process)
```

to your desired interval, then restart the service. 