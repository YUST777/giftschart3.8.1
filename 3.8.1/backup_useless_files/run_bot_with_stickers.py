#!/usr/bin/env python3
"""
Run Bot With Stickers

This script launches both the main Telegram bot and the sticker update process
in separate threads, enabling the bot to provide real-time sticker price data
alongside its gift price functionality.
"""

import os
import sys
import time
import logging
import threading
import subprocess
import signal
import atexit

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("run_bot_with_stickers.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("run_bot_with_stickers")

# Get the script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Processes to track for cleanup
processes = []

def clean_exit(sig=None, frame=None):
    """Clean up processes on exit"""
    logger.info("Shutting down all processes...")
    for process in processes:
        try:
            if process.poll() is None:  # If the process is still running
                process.terminate()
                logger.info(f"Terminated process {process.pid}")
        except Exception as e:
            logger.error(f"Error terminating process: {e}")
    
    logger.info("All processes terminated")
    sys.exit(0)

# Register the clean_exit function to be called on regular exit and signals
atexit.register(clean_exit)
signal.signal(signal.SIGINT, clean_exit)
signal.signal(signal.SIGTERM, clean_exit)

def run_bot():
    """Run the main Telegram bot"""
    try:
        logger.info("Starting main Telegram bot...")
        bot_script = os.path.join(script_dir, "telegram_bot.py")
        process = subprocess.Popen([sys.executable, bot_script], 
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  text=True)
        processes.append(process)
        
        # Log output from the process
        for line in process.stdout:
            logger.info(f"TELEGRAM_BOT: {line.strip()}")
            
        if process.poll() is not None:
            logger.error(f"Main bot process exited with code {process.returncode}")
    except Exception as e:
        logger.error(f"Error running main bot: {e}")

def run_sticker_updater():
    """Run the sticker update process"""
    try:
        logger.info("Starting sticker update process...")
        updater_script = os.path.join(script_dir, "scheduled_sticker_update.py")
        process = subprocess.Popen([sys.executable, updater_script],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  text=True)
        processes.append(process)
        
        # Log output from the process
        for line in process.stdout:
            logger.info(f"STICKER_UPDATER: {line.strip()}")
            
        if process.poll() is not None:
            logger.error(f"Sticker updater process exited with code {process.returncode}")
    except Exception as e:
        logger.error(f"Error running sticker updater: {e}")

def main():
    """Main function to start all components"""
    try:
        logger.info("Starting all components...")
        
        # Start the bot in a separate thread
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.daemon = True
        bot_thread.start()
        
        # Start the sticker updater in a separate thread
        sticker_thread = threading.Thread(target=run_sticker_updater)
        sticker_thread.daemon = True
        sticker_thread.start()
        
        logger.info("All components started")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
            # Check if any thread has died
            if not bot_thread.is_alive():
                logger.error("Bot thread died, restarting...")
                bot_thread = threading.Thread(target=run_bot)
                bot_thread.daemon = True
                bot_thread.start()
                
            if not sticker_thread.is_alive():
                logger.error("Sticker updater thread died, restarting...")
                sticker_thread = threading.Thread(target=run_sticker_updater)
                sticker_thread.daemon = True
                sticker_thread.start()
    
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
        clean_exit()
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        clean_exit()

if __name__ == "__main__":
    main() 