#!/usr/bin/env python3

import os
import sqlite3
import logging
import glob
import random
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("create_sticker_db_old.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("create_sticker_db")

# Database file
DB_FILE = "place_stickers.db"

# Directory paths
script_dir = os.path.dirname(os.path.abspath(__file__))
sticker_dir = os.path.join(script_dir, "sticker_collections")

def create_database():
    """Create the sticker database with the old structure."""
    try:
        # Check if the database file exists and delete it
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            logger.info(f"Deleted existing database file: {DB_FILE}")
        
        # Connect to the database (this will create a new file)
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Create the price_history table with the old structure
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS "price_history" (
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
        """)
        
        # Create indices for faster queries
        cursor.execute("CREATE INDEX idx_price_history_collection ON price_history(collection)")
        cursor.execute("CREATE INDEX idx_price_history_pack ON price_history(pack)")
        cursor.execute("CREATE INDEX idx_price_history_timestamp ON price_history(timestamp)")
        
        conn.commit()
        conn.close()
        
        logger.info(f"Created database {DB_FILE} with the old structure")
        return True
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return False

def populate_sample_data():
    """Populate the database with sample price data for each sticker pack."""
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
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
        
        # Current timestamp
        current_timestamp = int(time.time())
        
        # Insert sample data for each collection and pack
        for collection, packs in collections.items():
            # Convert underscores back to spaces for display
            collection_name = collection.replace("_", " ")
            
            for pack in packs:
                # Convert underscores back to spaces for display
                pack_name = pack.replace("_", " ")
                
                # Generate random prices
                price_usd_new = random.randint(50, 500)
                price_ton_new = round(price_usd_new / 3.4, 12)  # Approximate TON price
                
                # No old prices for initial data
                price_ton_old = None
                price_usd_old = None
                
                # Change percentage (0 for initial data)
                change_percentage = 0
                
                # Insert into price_history
                cursor.execute("""
                INSERT INTO price_history 
                (collection, pack, price_ton_old, price_usd_old, price_ton_new, price_usd_new, change_percentage, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (collection_name, pack_name, price_ton_old, price_usd_old, price_ton_new, price_usd_new, change_percentage, current_timestamp))
                
                logger.info(f"Added sample data for {collection_name} - {pack_name}")
        
        conn.commit()
        conn.close()
        
        logger.info("Sample data population complete")
        return True
    except Exception as e:
        logger.error(f"Error populating sample data: {e}")
        return False

def main():
    """Main function to create the database and populate it with sample data."""
    if create_database():
        populate_sample_data()
        logger.info("Database setup complete")
    else:
        logger.error("Failed to create database")

if __name__ == "__main__":
    main() 