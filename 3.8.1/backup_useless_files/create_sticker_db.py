#!/usr/bin/env python3
"""
Create Sticker Database

This script initializes the database for storing sticker price data.
"""

import sqlite3
import os
import logging
import random
import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("create_sticker_db.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("create_sticker_db")

# Database file
DB_FILE = "place_stickers.db"

def create_database():
    """Create the sticker database and tables."""
    try:
        # Remove existing database if it exists
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
            logger.info(f"Removed existing database: {DB_FILE}")
            
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Create collections table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS collections (
            collection_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        ''')
        
        # Create packs table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS packs (
            pack_id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (collection_id) REFERENCES collections(collection_id),
            UNIQUE(collection_id, name)
        )
        ''')
        
        # Create sticker_prices table with references to collections and packs
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sticker_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_id INTEGER NOT NULL,
            pack_id INTEGER NOT NULL,
            name TEXT DEFAULT NULL,
            number TEXT DEFAULT NULL,
            price_ton REAL NOT NULL,
            price_usd REAL NOT NULL,
            timestamp INTEGER NOT NULL,
            message_id INTEGER DEFAULT NULL,
            FOREIGN KEY (collection_id) REFERENCES collections(collection_id),
            FOREIGN KEY (pack_id) REFERENCES packs(pack_id)
        )
        ''')
        
        # Create price_history table for tracking changes (optimized)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_id INTEGER NOT NULL,
            pack_id INTEGER NOT NULL,
            price_ton_new REAL NOT NULL,
            price_usd_new REAL NOT NULL,
            change_percentage REAL,
            timestamp INTEGER NOT NULL,
            FOREIGN KEY (collection_id) REFERENCES collections(collection_id),
            FOREIGN KEY (pack_id) REFERENCES packs(pack_id)
        )
        ''')
        
        # Create last_processed_message table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS last_processed_message (
            channel_id TEXT PRIMARY KEY,
            message_id INTEGER NOT NULL
        )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sticker_prices_collection_id ON sticker_prices(collection_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sticker_prices_pack_id ON sticker_prices(pack_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sticker_prices_timestamp ON sticker_prices(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_history_timestamp ON price_history(timestamp)')
        
        conn.commit()
        conn.close()
        logger.info("Database created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return False

def get_or_create_collection(conn, collection_name):
    """Get collection ID or create if not exists"""
    cursor = conn.cursor()
    cursor.execute('SELECT collection_id FROM collections WHERE name = ?', (collection_name,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    else:
        cursor.execute('INSERT INTO collections (name) VALUES (?)', (collection_name,))
        return cursor.lastrowid

def get_or_create_pack(conn, collection_id, pack_name):
    """Get pack ID or create if not exists"""
    cursor = conn.cursor()
    cursor.execute('SELECT pack_id FROM packs WHERE collection_id = ? AND name = ?', 
                  (collection_id, pack_name))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    else:
        cursor.execute('INSERT INTO packs (collection_id, name) VALUES (?, ?)', 
                      (collection_id, pack_name))
        return cursor.lastrowid

def populate_sample_data():
    """Populate the database with sample sticker price data."""
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        sticker_dir = os.path.join(script_dir, "sticker_collections")
        
        if not os.path.exists(sticker_dir):
            logger.error(f"Sticker collections directory not found: {sticker_dir}")
            return False
        
        conn = sqlite3.connect(DB_FILE)
        
        # Get current timestamp
        current_time = int(datetime.datetime.now().timestamp())
        
        # Iterate through collections and packs
        for collection_dir in os.listdir(sticker_dir):
            collection_path = os.path.join(sticker_dir, collection_dir)
            if os.path.isdir(collection_path):
                # Convert underscores back to spaces for display
                collection_name = collection_dir.replace("_", " ")
                logger.info(f"Processing collection: {collection_name}")
                
                # Get or create collection
                collection_id = get_or_create_collection(conn, collection_name)
                
                for pack_dir in os.listdir(collection_path):
                    pack_path = os.path.join(collection_path, pack_dir)
                    if os.path.isdir(pack_path):
                        # Convert underscores back to spaces for display
                        pack_name = pack_dir.replace("_", " ")
                        logger.info(f"Processing pack: {pack_name}")
                        
                        # Get or create pack
                        pack_id = get_or_create_pack(conn, collection_id, pack_name)
                        
                        # Generate random price data
                        price_usd = random.randint(50, 500)
                        price_ton = price_usd / 3.4  # Approximate TON price
                        
                        # Insert into sticker_prices table
                        cursor = conn.cursor()
                        cursor.execute('''
                        INSERT INTO sticker_prices 
                        (collection_id, pack_id, price_ton, price_usd, timestamp) 
                        VALUES (?, ?, ?, ?, ?)
                        ''', (collection_id, pack_id, price_ton, price_usd, current_time))
                        
                        # Also add a history entry
                        cursor.execute('''
                        INSERT INTO price_history 
                        (collection_id, pack_id, price_ton_new, price_usd_new, change_percentage, timestamp) 
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''', (collection_id, pack_id, price_ton, price_usd, 0.0, current_time))
        
        conn.commit()
        conn.close()
        logger.info("Sample data populated successfully")
        return True
    except Exception as e:
        logger.error(f"Error populating sample data: {e}")
        return False

def main():
    """Main function."""
    if create_database():
        populate_sample_data()

if __name__ == "__main__":
    main() 