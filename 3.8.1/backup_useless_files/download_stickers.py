#!/usr/bin/env python3
"""
Sticker Collection Downloader

This script downloads sticker collections and organizes them in a clean folder structure.
"""

import os
import requests
import logging
import time
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("download_stickers.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("download_stickers")

# Base directory for sticker collections
BASE_DIR = "sticker_collections"

# Define collections and their packs
COLLECTIONS = {
    "WAGMI_HUB": {
        "EGG_AND_HAMMER": "https://cdn.stickerdom.store/20/t/1/1.png?v=0",
        "WAGMI_AI_AGENT": "https://cdn.stickerdom.store/20/t/2/1.png?v=0"
    },
    "Cattea_Life": {
        "Cattea_Chaos": "https://cdn.stickerdom.store/19/t/2/1.png?v=1"
    },
    "Doodles": {
        "Doodles_Dark_Mode": "https://cdn.stickerdom.store/18/t/1/1.png?v=0"
    },
    "Pudgy_and_Friends": {
        "Pengu_x_Baby_Shark": "https://cdn.stickerdom.store/16/t/1/1.png?v=0",
        "Pengu_x_NASCAR": "https://cdn.stickerdom.store/16/t/2/1.png?v=0"
    },
    "Lil_Pudgys": {
        "Lil_Pudgys_x_Baby_Shark": "https://cdn.stickerdom.store/17/t/1/1.png?v=0"
    },
    "Lazy_and_Rich": {
        "Chill_or_thrill": "https://cdn.stickerdom.store/15/t/2/1.png?v=1",
        "Sloth_Capital": "https://cdn.stickerdom.store/15/t/3/1.png?v=1"
    },
    "Smeshariki": {
        "Chamomile_Valley": "https://cdn.stickerdom.store/14/t/1/1.png?v=1",
        "The_Memes": "https://cdn.stickerdom.store/14/t/2/1.png?v=1"
    },
    "SUNDOG": {
        "TO_THE_SUN": "https://cdn.stickerdom.store/13/t/1/1.png?v=0"
    },
    "BabyDoge": {
        "Mememania": "https://cdn.stickerdom.store/11/t/1/1.png?v=0"
    },
    "PUCCA": {
        "PUCCA_Moods": "https://cdn.stickerdom.store/10/t/1/1.png?v=4"
    },
    "Not_Pixel": {
        "Pixel_phrases": "https://cdn.stickerdom.store/8/t/15/1.png?v=7",
        "Films_memes": "https://cdn.stickerdom.store/8/t/16/1.png?v=7",
        "Smileface_pack": "https://cdn.stickerdom.store/8/t/17/1.png?v=7",
        "Tournament_S1": "https://cdn.stickerdom.store/8/t/18/1.png?v=7",
        "Random_memes": "https://cdn.stickerdom.store/8/t/2/1.png?v=7",
        "Cute_pack": "https://cdn.stickerdom.store/8/t/3/8.png?v=7",
        "MacPixel": "https://cdn.stickerdom.store/8/t/6/1.png?v=7",
        "Vice_Pixel": "https://cdn.stickerdom.store/8/t/12/1.png?v=7",
        "Pixioznik": "https://cdn.stickerdom.store/8/t/13/1.png?v=7",
        "Zompixel": "https://cdn.stickerdom.store/8/t/14/1.png?v=7",
        "Grass_Pixel": "https://cdn.stickerdom.store/8/t/5/1.png?v=7",
        "SuperPixel": "https://cdn.stickerdom.store/8/t/7/1.png?v=7",
        "DOGS_Pixel": "https://cdn.stickerdom.store/8/t/4/1.png?v=7",
        "Diamond_Pixel": "https://cdn.stickerdom.store/8/t/8/1.png?v=7",
        "Pixanos": "https://cdn.stickerdom.store/8/t/9/1.png?v=7",
        "Retro_Pixel": "https://cdn.stickerdom.store/8/t/10/1.png?v=7",
        "Error_Pixel": "https://cdn.stickerdom.store/8/t/11/1.png?v=7"
    },
    "Lost_Dogs": {
        "Lost_Memeries": "https://cdn.stickerdom.store/7/t/2/1.png?v=2",
        "Magic_of_the_Way": "https://cdn.stickerdom.store/7/t/1/1.png?v=2"
    },
    "Pudgy_Penguins": {
        "Pengu_Valentines": "https://cdn.stickerdom.store/2/t/4/1.png?v=9",
        "Pengu_CNY": "https://cdn.stickerdom.store/2/t/3/1.png?v=9",
        "Blue_Pengu": "https://cdn.stickerdom.store/2/t/1/1.png?v=9",
        "Cool_Blue_Pengu": "https://cdn.stickerdom.store/2/t/2/1.png?v=9"
    },
    "Blum": {
        "General": "https://cdn.stickerdom.store/4/t/9/1.png?v=2",
        "Cook": "https://cdn.stickerdom.store/4/t/1/1.png?v=2",
        "Curly": "https://cdn.stickerdom.store/4/t/3/1.png?v=2",
        "No": "https://cdn.stickerdom.store/4/t/15/1.png?v=2",
        "Worker": "https://cdn.stickerdom.store/4/t/20/1.png?v=2",
        "Bunny": "https://cdn.stickerdom.store/4/t/26/1.png?v=2",
        "Cap": "https://cdn.stickerdom.store/4/t/27/1.png?v=2",
        "Cat": "https://cdn.stickerdom.store/4/t/28/1.png?v=2"
    },
    "Flappy_Bird": {
        "Blue_Wings": "https://cdn.stickerdom.store/5/t/2/1.png?v=4",
        "Light_Glide": "https://cdn.stickerdom.store/5/t/3/1.png?v=4",
        "Frost_Flap": "https://cdn.stickerdom.store/5/t/4/1.png?v=4",
        "Blush_Flight": "https://cdn.stickerdom.store/5/t/5/1.png?v=4",
        "Ruby_Wings": "https://cdn.stickerdom.store/5/t/6/1.png?v=4"
    },
    "Bored_Stickers": {
        "CNY_2092": "https://cdn.stickerdom.store/3/t/11/1.png?v=4",
        "3151": "https://cdn.stickerdom.store/3/t/3/1.png?v=4",
        "3278": "https://cdn.stickerdom.store/3/t/4/1.png?v=4",
        "4017": "https://cdn.stickerdom.store/3/t/5/1.png?v=4",
        "5824": "https://cdn.stickerdom.store/3/t/6/1.png?v=4",
        "6527": "https://cdn.stickerdom.store/3/t/7/1.png?v=4",
        "9287": "https://cdn.stickerdom.store/3/t/8/1.png?v=4",
        "9765": "https://cdn.stickerdom.store/3/t/9/1.png?v=4",
        "9780": "https://cdn.stickerdom.store/3/t/10/1.png?v=4"
    },
    "Kudai": {
        "GMI": "https://cdn.stickerdom.store/12/t/1/1.png?v=1",
        "NGMI": "https://cdn.stickerdom.store/12/t/2/1.png?v=1"
    },
    "Dogs_OG": {
        "Sheikh": "https://cdn.stickerdom.store/1/t/30/1.png?v=3",
        "Not_Cap": "https://cdn.stickerdom.store/1/t/87/1.png?v=3",
        "King": "https://cdn.stickerdom.store/1/t/71/1.png?v=3"
    },
    "Azuki": {
        "Shao": "https://cdn.stickerdom.store/24/t/1/5.png?v=3"
    },
    "Ric_Flair": {
        "Ric_Flair": "https://cdn.stickerdom.store/21/t/1/5.png?v=3"
    },
    "Notcoin": {
        "Not_Memes": "https://cdn.stickerdom.store/6/t/2/1.png?v=0",
        "flags": "https://cdn.stickerdom.store/6/t/1/1.png?v=0"
    },
    "Dogs_rewards": {
        "Gold_bone": "https://cdn.stickerdom.store/9/t/5/1.png?v=1",
        "silver_bone": "https://cdn.stickerdom.store/9/t/6/1.png?v=1",
        "full_dig": "https://cdn.stickerdom.store/9/t/12/1.png?v=1"
    }
}

def create_directory(path):
    """Create directory if it doesn't exist"""
    try:
        os.makedirs(path, exist_ok=True)
        logger.info(f"Created directory: {path}")
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return False
    return True

def download_image(url, save_path):
    """Download image from URL and save to path"""
    if not url:
        logger.warning(f"No URL provided for {save_path}")
        return False
        
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        logger.info(f"Downloaded: {save_path}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Error downloading {url}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error downloading {url}: {e}")
        return False

def download_sticker_set(collection_name, pack_name, url):
    """Download a sticker set and its variations"""
    if not url:
        logger.warning(f"No URL provided for {collection_name}/{pack_name}")
        return 0
        
    # Create directories
    collection_dir = os.path.join(BASE_DIR, collection_name)
    pack_dir = os.path.join(collection_dir, pack_name)
    
    if not create_directory(pack_dir):
        return 0
        
    # Parse the URL to get base parts
    parsed_url = urlparse(url)
    url_parts = parsed_url.path.split('/')
    
    # Extract collection ID, pack ID, and sticker number
    try:
        collection_id = url_parts[1]
        pack_id = url_parts[3]
        sticker_number = url_parts[4].split('.')[0]
        version = parsed_url.query.split('=')[1]
    except (IndexError, ValueError) as e:
        logger.error(f"Error parsing URL {url}: {e}")
        return 0
        
    # Try to download multiple stickers from the set (1-20)
    downloaded_count = 0
    for i in range(1, 21):
        # Construct new URL for each sticker in the set
        sticker_url = f"https://cdn.stickerdom.store/{collection_id}/t/{pack_id}/{i}.png?v={version}"
        sticker_filename = f"{i}.png"
        sticker_path = os.path.join(pack_dir, sticker_filename)
        
        # Skip if file already exists
        if os.path.exists(sticker_path):
            logger.info(f"Skipping existing file: {sticker_path}")
            downloaded_count += 1
            continue
            
        # Download the sticker
        success = download_image(sticker_url, sticker_path)
        if success:
            downloaded_count += 1
        else:
            # If we fail to download, it might mean we've reached the end of the set
            break
            
        # Be nice to the server
        time.sleep(0.5)
        
    logger.info(f"Downloaded {downloaded_count} stickers for {collection_name}/{pack_name}")
    return downloaded_count

def main():
    """Main function"""
    logger.info("Starting sticker collection download")
    
    # Create base directory
    if not create_directory(BASE_DIR):
        logger.error("Failed to create base directory. Exiting.")
        return
        
    # Download all collections
    total_downloaded = 0
    total_packs = 0
    
    for collection_name, packs in COLLECTIONS.items():
        logger.info(f"Processing collection: {collection_name}")
        collection_count = 0
        
        for pack_name, url in packs.items():
            if url:
                total_packs += 1
                pack_count = download_sticker_set(collection_name, pack_name, url)
                collection_count += pack_count
                total_downloaded += pack_count
            else:
                logger.warning(f"No URL for {collection_name}/{pack_name}, skipping")
                
        logger.info(f"Downloaded {collection_count} stickers for collection {collection_name}")
        
    logger.info(f"Download complete. Downloaded {total_downloaded} stickers across {total_packs} packs.")

if __name__ == "__main__":
    main()
