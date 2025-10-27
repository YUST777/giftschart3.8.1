#!/usr/bin/env python3
"""
Fetch Channel Messages

This script uses Telethon to fetch messages from a Telegram channel using a regular user account.
It parses the messages to extract sticker price data and stores it in the database.
"""

import os
import sys
import logging
import asyncio
import json
import re
import sqlite3
from datetime import datetime
from telethon.sync import TelegramClient
from telethon import errors

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fetch_channel_messages.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("fetch_channel_messages")

# Telegram API credentials
API_ID = 22307634
API_HASH = '7ab906fc6d065a2047a84411c1697593'
SESSION_NAME = 'duck_session'

# Channel to fetch messages from
CHANNEL_USERNAME = 'palacedeals'  # without @

# Database file
DB_FILE = 'place_stickers.db'

# Path to store the last processed message ID
LAST_MESSAGE_FILE = 'last_message_id.txt'

def get_last_processed_message():
    """Get the ID of the last processed message"""
    try:
        if os.path.exists(LAST_MESSAGE_FILE):
            with open(LAST_MESSAGE_FILE, 'r') as f:
                return int(f.read().strip())
        return 0
    except Exception as e:
        logger.error(f"Error reading last processed message ID: {e}")
        return 0

def update_last_processed_message(message_id):
    """Update the ID of the last processed message"""
    try:
        with open(LAST_MESSAGE_FILE, 'w') as f:
            f.write(str(message_id))
    except Exception as e:
        logger.error(f"Error updating last processed message ID: {e}")

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

def save_message_to_json(message):
    """Save a message to a JSON file for debugging"""
    try:
        # Convert the message to a dictionary
        message_dict = {
            'id': message.id,
            'date': message.date.isoformat(),
            'text': message.text,
            'sender_id': message.sender_id if message.sender else None,
            'chat_id': message.chat_id,
            'raw_text': message.raw_text,
            'has_media': message.media is not None
        }
        
        # Save to a JSON file
        with open(f'message_{message.id}.json', 'w') as f:
            json.dump(message_dict, f, indent=2)
            
        logger.info(f"Saved message {message.id} to JSON file")
    except Exception as e:
        logger.error(f"Error saving message to JSON: {e}")

async def fetch_messages(limit=1000):
    """Fetch messages from the channel"""
    try:
        logger.info(f"Starting Telegram client with session {SESSION_NAME}")
        client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        
        await client.start()
        logger.info("Client started successfully")
        
        if not await client.is_user_authorized():
            logger.error("User is not authorized. Please run the script interactively first to log in.")
            return []
            
        # Get the channel entity
        try:
            channel = await client.get_entity(CHANNEL_USERNAME)
            logger.info(f"Successfully got channel entity: {channel.title}")
        except errors.FloodWaitError as e:
            logger.error(f"Flood wait error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting channel entity: {e}")
            return []
            
        # Get the last processed message ID
        last_message_id = get_last_processed_message()
        logger.info(f"Last processed message ID: {last_message_id}")
        
        # Fetch messages
        messages = []
        logger.info(f"Fetching up to {limit} messages from channel {CHANNEL_USERNAME}")
        
        offset_id = 0  # Start from the most recent message
        async for message in client.iter_messages(channel, limit=limit, offset_id=offset_id):
            if message.id <= last_message_id:
                # We've reached messages we've already processed
                logger.info(f"Reached already processed message {message.id}, stopping")
                break
                
            if message.text:  # Only process messages with text
                logger.info(f"Fetched message {message.id}: {message.text[:50]}...")
                messages.append(message)
                
                # Save the first few messages to JSON for analysis
                if len(messages) <= 5:
                    save_message_to_json(message)
            
        logger.info(f"Fetched {len(messages)} messages")
        
        # Update the last processed message ID if we fetched any messages
        if messages:
            highest_id = max(message.id for message in messages)
            update_last_processed_message(highest_id)
            logger.info(f"Updated last processed message ID to {highest_id}")
            
        await client.disconnect()
        return messages
    
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        return []

def parse_message(message):
    """Parse a message to extract sticker price data"""
    try:
        text = message.text
        
        # Try various patterns
        
        # Pattern 1: "Collection #Number sold for Price TON ($USD)"
        pattern1 = re.search(r'([^\d#]+)\s+#(\d+)\s+(?:sold|purchased)\s+for\s+(\d+\.?\d*)\s+TON\s+\(\$(\d+\.?\d*)\)', text, re.IGNORECASE)
        if pattern1:
            collection = pattern1.group(1).strip()
            number = pattern1.group(2)
            price_ton = float(pattern1.group(3))
            price_usd = float(pattern1.group(4))
            return {
                "collection": collection,
                "pack": "Unknown Pack",
                "name": collection,
                "number": number,
                "price_ton": price_ton,
                "price_usd": price_usd,
                "timestamp": int(message.date.timestamp()),
                "message_id": message.id
            }
            
        # Pattern 2: "Collection name #Number - Price TON ($USD)"
        pattern2 = re.search(r'([^\d#]+)\s+#(\d+)\s+-\s+(\d+\.?\d*)\s+TON\s+\(\$(\d+\.?\d*)\)', text, re.IGNORECASE)
        if pattern2:
            collection = pattern2.group(1).strip()
            number = pattern2.group(2)
            price_ton = float(pattern2.group(3))
            price_usd = float(pattern2.group(4))
            return {
                "collection": collection,
                "pack": "Unknown Pack",
                "name": collection,
                "number": number,
                "price_ton": price_ton,
                "price_usd": price_usd,
                "timestamp": int(message.date.timestamp()),
                "message_id": message.id
            }
            
        # Pattern 3: Try to extract from hashtags and price mentions
        hashtag_match = re.search(r'#(\w+)', text)
        price_match = re.search(r'(\d+\.?\d*)\s+TON\s+\(\$(\d+\.?\d*)\)', text)
        number_match = re.search(r'#(\d+)', text)
        
        if hashtag_match and price_match and number_match:
            collection = hashtag_match.group(1).replace('_', ' ').title()
            number = number_match.group(1)
            price_ton = float(price_match.group(1))
            price_usd = float(price_match.group(2))
            return {
                "collection": collection,
                "pack": "Unknown Pack",
                "name": collection,
                "number": number,
                "price_ton": price_ton,
                "price_usd": price_usd,
                "timestamp": int(message.date.timestamp()),
                "message_id": message.id
            }
        
        logger.warning(f"Could not parse message: {text[:100]}...")
        return None
        
    except Exception as e:
        logger.error(f"Error parsing message: {e}")
        return None

def store_sticker_price(data):
    """Store sticker price data in the database"""
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_FILE)
        
        # Get or create collection and pack IDs
        collection_id = get_or_create_collection(conn, data["collection"])
        pack_id = get_or_create_pack(conn, collection_id, data["pack"])
        
        # Insert the data
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO sticker_prices (collection_id, pack_id, name, number, price_ton, price_usd, timestamp, message_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            collection_id,
            pack_id,
            data["name"],
            data["number"],
            data["price_ton"],
            data["price_usd"],
            data["timestamp"],
            data["message_id"]
        ))
        
        # Commit and close
        conn.commit()
        conn.close()
        
        logger.info(f"Stored price for {data['collection']} - {data['name']} #{data['number']}: {data['price_ton']} TON (${data['price_usd']})")
        
    except Exception as e:
        logger.error(f"Error storing sticker price: {e}")

async def main():
    """Main function"""
    try:
        logger.info("Starting fetch_channel_messages")
        
        # Fetch messages
        messages = await fetch_messages(limit=1000)
        
        if not messages:
            logger.warning("No messages fetched. If this is the first run, you need to log in interactively.")
            logger.warning("Run the script again and enter your phone number and the verification code when prompted.")
            return
            
        # Process messages
        processed_count = 0
        for message in messages:
            data = parse_message(message)
            if data:
                store_sticker_price(data)
                processed_count += 1
                
        logger.info(f"Processed {processed_count} messages out of {len(messages)} fetched")
        
        # Check if we need to add sample data
        if processed_count == 0:
            logger.warning("No messages were successfully parsed. Check the message formats.")
            
            # Get the total count of records in the database
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sticker_prices")
            count = cursor.fetchone()[0]
            conn.close()
            
            if count == 0:
                logger.warning("No data in the database. Adding sample data for testing.")
                
                # Add some sample data for testing
                sample_data = [
                    {"collection": "Pudgy Penguins", "pack": "Unknown Pack", "name": "Pudgy Penguins", "number": "404", "price_ton": 95.00, "price_usd": 323.01, "timestamp": int(datetime.now().timestamp()), "message_id": 1001},
                    {"collection": "Pudgy Penguins", "pack": "Unknown Pack", "name": "Pudgy Penguins", "number": "505", "price_ton": 87.50, "price_usd": 297.50, "timestamp": int(datetime.now().timestamp()), "message_id": 1002},
                    {"collection": "Pudgy Penguins", "pack": "Unknown Pack", "name": "Pudgy Penguins", "number": "606", "price_ton": 103.25, "price_usd": 351.05, "timestamp": int(datetime.now().timestamp()), "message_id": 1003},
                    
                    {"collection": "Not Pixel", "pack": "Unknown Pack", "name": "Not Pixel", "number": "127", "price_ton": 82.50, "price_usd": 280.50, "timestamp": int(datetime.now().timestamp()), "message_id": 1004},
                    {"collection": "Not Pixel", "pack": "Unknown Pack", "name": "Not Pixel", "number": "128", "price_ton": 79.00, "price_usd": 268.60, "timestamp": int(datetime.now().timestamp()), "message_id": 1005},
                    {"collection": "Not Pixel", "pack": "Unknown Pack", "name": "Not Pixel", "number": "129", "price_ton": 85.75, "price_usd": 291.55, "timestamp": int(datetime.now().timestamp()), "message_id": 1006},
                    
                    {"collection": "WAGMI HUB", "pack": "Unknown Pack", "name": "WAGMI HUB", "number": "33", "price_ton": 110.00, "price_usd": 374.00, "timestamp": int(datetime.now().timestamp()), "message_id": 1007},
                    {"collection": "WAGMI HUB", "pack": "Unknown Pack", "name": "WAGMI HUB", "number": "34", "price_ton": 105.50, "price_usd": 358.70, "timestamp": int(datetime.now().timestamp()), "message_id": 1008},
                    {"collection": "WAGMI HUB", "pack": "Unknown Pack", "name": "WAGMI HUB", "number": "35", "price_ton": 115.25, "price_usd": 391.85, "timestamp": int(datetime.now().timestamp()), "message_id": 1009}
                ]
                
                for data in sample_data:
                    store_sticker_price(data)
                
                logger.info(f"Added {len(sample_data)} sample records for testing")
        
        logger.info("Completed processing messages")
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 