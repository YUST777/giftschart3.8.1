#!/usr/bin/env python3
"""
Migrate Database

This script migrates the existing sticker database to the new optimized schema.
It creates new tables with foreign keys and indexes for better performance.
"""

import os
import sqlite3
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("migrate_database.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("migrate_database")

# Database file
DB_FILE = "place_stickers.db"
BACKUP_FILE = "place_stickers_backup.db"

def backup_database():
    """Create a backup of the database"""
    try:
        if os.path.exists(DB_FILE):
            import shutil
            shutil.copy2(DB_FILE, BACKUP_FILE)
            logger.info(f"Created backup of database at {BACKUP_FILE}")
            return True
        else:
            logger.error(f"Database file {DB_FILE} not found")
            return False
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return False

def create_new_schema():
    """Create the new database schema"""
    try:
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
        
        # Create new sticker_prices table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sticker_prices_new (
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
        
        # Create new price_history table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history_new (
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
        
        conn.commit()
        conn.close()
        logger.info("Created new schema")
        return True
    except Exception as e:
        logger.error(f"Error creating new schema: {e}")
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
        conn.commit()
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
        conn.commit()
        return cursor.lastrowid

def migrate_sticker_prices():
    """Migrate data from sticker_prices to the new table"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if old table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sticker_prices'")
        if not cursor.fetchone():
            logger.warning("sticker_prices table not found, skipping migration")
            conn.close()
            return True
        
        # Check table schema to determine available columns
        cursor.execute("PRAGMA table_info(sticker_prices)")
        columns = [column[1] for column in cursor.fetchall()]
        logger.info(f"Found columns in sticker_prices: {columns}")
        
        has_message_id = 'message_id' in columns
        
        # Get all records from the old table
        if has_message_id:
            cursor.execute('SELECT collection, pack, name, number, price_ton, price_usd, timestamp, message_id FROM sticker_prices')
        else:
            cursor.execute('SELECT collection, pack, name, number, price_ton, price_usd, timestamp FROM sticker_prices')
            
        records = cursor.fetchall()
        logger.info(f"Found {len(records)} records in sticker_prices")
        
        # Migrate each record
        migrated_count = 0
        for record in records:
            if has_message_id:
                collection, pack, name, number, price_ton, price_usd, timestamp, message_id = record
            else:
                collection, pack, name, number, price_ton, price_usd, timestamp = record
                message_id = None  # Set to None if column doesn't exist
            
            # Get or create collection and pack IDs
            collection_id = get_or_create_collection(conn, collection)
            pack_id = get_or_create_pack(conn, collection_id, pack)
            
            # Insert into new table
            cursor.execute('''
            INSERT INTO sticker_prices_new 
            (collection_id, pack_id, name, number, price_ton, price_usd, timestamp, message_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (collection_id, pack_id, name, number, price_ton, price_usd, timestamp, message_id))
            
            migrated_count += 1
            if migrated_count % 100 == 0:
                logger.info(f"Migrated {migrated_count} records")
                
        conn.commit()
        logger.info(f"Successfully migrated {migrated_count} records from sticker_prices")
        
        # Rename tables
        cursor.execute('DROP TABLE IF EXISTS sticker_prices_old')
        cursor.execute('ALTER TABLE sticker_prices RENAME TO sticker_prices_old')
        cursor.execute('ALTER TABLE sticker_prices_new RENAME TO sticker_prices')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sticker_prices_collection_id ON sticker_prices(collection_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sticker_prices_pack_id ON sticker_prices(pack_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sticker_prices_timestamp ON sticker_prices(timestamp)')
        
        conn.commit()
        conn.close()
        logger.info("Completed sticker_prices migration")
        return True
    except Exception as e:
        logger.error(f"Error migrating sticker_prices: {e}")
        return False

def migrate_price_history():
    """Migrate data from price_history to the new table"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if old table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='price_history'")
        if not cursor.fetchone():
            logger.warning("price_history table not found, skipping migration")
            conn.close()
            return True
            
        # Get all records from the old table
        cursor.execute('SELECT collection, pack, price_ton_new, price_usd_new, change_percentage, timestamp FROM price_history')
        records = cursor.fetchall()
        logger.info(f"Found {len(records)} records in price_history")
        
        # Migrate each record
        migrated_count = 0
        for record in records:
            collection, pack, price_ton_new, price_usd_new, change_percentage, timestamp = record
            
            # Get or create collection and pack IDs
            collection_id = get_or_create_collection(conn, collection)
            pack_id = get_or_create_pack(conn, collection_id, pack)
            
            # Insert into new table
            cursor.execute('''
            INSERT INTO price_history_new 
            (collection_id, pack_id, price_ton_new, price_usd_new, change_percentage, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (collection_id, pack_id, price_ton_new, price_usd_new, change_percentage, timestamp))
            
            migrated_count += 1
            if migrated_count % 100 == 0:
                logger.info(f"Migrated {migrated_count} records")
                
        conn.commit()
        logger.info(f"Successfully migrated {migrated_count} records from price_history")
        
        # Rename tables
        cursor.execute('DROP TABLE IF EXISTS price_history_old')
        cursor.execute('ALTER TABLE price_history RENAME TO price_history_old')
        cursor.execute('ALTER TABLE price_history_new RENAME TO price_history')
        
        # Create index for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_history_timestamp ON price_history(timestamp)')
        
        conn.commit()
        conn.close()
        logger.info("Completed price_history migration")
        return True
    except Exception as e:
        logger.error(f"Error migrating price_history: {e}")
        return False

def create_last_processed_message_table():
    """Create last_processed_message table if it doesn't exist"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Create last_processed_message table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS last_processed_message (
            channel_id TEXT PRIMARY KEY,
            message_id INTEGER NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Created last_processed_message table")
        return True
    except Exception as e:
        logger.error(f"Error creating last_processed_message table: {e}")
        return False

def main():
    """Main function"""
    logger.info("Starting database migration")
    
    # Create backup
    if not backup_database():
        logger.error("Failed to create backup, aborting migration")
        return
    
    # Create new schema
    if not create_new_schema():
        logger.error("Failed to create new schema, aborting migration")
        return
    
    # Migrate data
    if not migrate_sticker_prices():
        logger.error("Failed to migrate sticker_prices, aborting migration")
        return
    
    if not migrate_price_history():
        logger.error("Failed to migrate price_history, aborting migration")
        return
    
    # Create last_processed_message table
    if not create_last_processed_message_table():
        logger.error("Failed to create last_processed_message table")
    
    logger.info("Database migration completed successfully")

if __name__ == "__main__":
    main() 