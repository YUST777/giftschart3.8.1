#!/usr/bin/env python3
"""
Telegram Sticker Price Bot

This bot provides real-time price information for Telegram stickers
using the MRKT API integration.
"""

import os
import logging
import json
import time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
import mrkt_api_improved as api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("sticker_price_bot")

# Load bot token from environment or config file
try:
    from bot_config import BOT_TOKEN
    TOKEN = BOT_TOKEN
except ImportError:
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("No bot token found. Please set BOT_TOKEN in bot_config.py or as an environment variable.")

# Create output directory if it doesn't exist
os.makedirs("sticker_prices", exist_ok=True)

# Load cached prices if available
def load_cached_prices():
    """Load cached price data from file."""
    try:
        with open("sticker_prices/all_prices.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Cached price data
CACHED_PRICES = load_cached_prices()

def format_price_message(price_data):
    """Format price data into a readable message."""
    if not price_data:
        return "Sorry, I couldn't find price information for that sticker."
    
    if price_data.get("is_mock_data"):
        message = f"📊 *{price_data['name']}*\n"
        message += "⚠️ _Using estimated price (not real market data)_\n\n"
        message += f"💰 Price: *{price_data['price']:.2f} TON* (${price_data['price_usd']:.2f})\n"
    else:
        message = f"📊 *{price_data['name']}*\n\n"
        message += f"💰 Price: *{price_data['price']:.2f} TON* (${price_data['price_usd']:.2f})\n"
        message += f"🔄 Sales: {price_data.get('sales_count', 0)}\n"
        message += f"🕒 Last updated: {price_data.get('last_updated', 'Unknown')}\n"
    
    return message

def get_collection_buttons(collections):
    """Create buttons for collections."""
    keyboard = []
    row = []
    for i, collection in enumerate(sorted(collections)):
        row.append(InlineKeyboardButton(collection, callback_data=f"collection:{collection}"))
        if len(row) == 2 or i == len(collections) - 1:
            keyboard.append(row)
            row = []
    return InlineKeyboardMarkup(keyboard)

def get_character_buttons(collection, characters):
    """Create buttons for characters in a collection."""
    keyboard = []
    row = []
    for i, character in enumerate(sorted(characters)):
        row.append(InlineKeyboardButton(character, callback_data=f"character:{collection}:{character}"))
        if len(row) == 2 or i == len(characters) - 1:
            keyboard.append(row)
            row = []
    keyboard.append([InlineKeyboardButton("« Back to Collections", callback_data="back_to_collections")])
    return InlineKeyboardMarkup(keyboard)

def start_command(update: Update, context: CallbackContext):
    """Handle /start command."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        f"Hello {user.mention_markdown_v2()}\! 👋\n\n"
        f"I'm the Telegram Sticker Price Bot\\. I can tell you the current market prices for Telegram stickers\\.\n\n"
        f"Try these commands:\n"
        f"• /price \\<sticker name\\> \\- Get price for a specific sticker\n"
        f"• /collections \\- Browse available sticker collections\n"
        f"• /popular \\- See popular stickers\n"
        f"• /refresh \\- Update price data from the market\n\n"
        f"Or just send me a sticker name to get its price\\!"
    )

def help_command(update: Update, context: CallbackContext):
    """Handle /help command."""
    update.message.reply_markdown_v2(
        f"*Telegram Sticker Price Bot Help*\n\n"
        f"I can tell you the current market prices for Telegram stickers\\.\n\n"
        f"*Commands:*\n"
        f"• /price \\<sticker name\\> \\- Get price for a specific sticker\n"
        f"• /price \\<sticker name\\> \\-\\-refresh \\- Get fresh price data\n"
        f"• /collections \\- Browse available sticker collections\n"
        f"• /popular \\- See popular stickers\n"
        f"• /refresh \\- Update price data from the market\n\n"
        f"*Examples:*\n"
        f"• /price Pudgy Penguins Blue Pengu\n"
        f"• /price Blum Cat \\-\\-refresh\n\n"
        f"You can also browse collections and select stickers from the menu\\."
    )

def price_command(update: Update, context: CallbackContext):
    """Handle /price command to get price for a specific sticker."""
    args = context.args
    
    if not args:
        update.message.reply_text("Please specify a sticker name. Example: /price Pudgy Penguins Blue Pengu")
        return
    
    # Check if the last argument is --refresh
    force_refresh = False
    if args[-1] == "--refresh":
        force_refresh = True
        args = args[:-1]
    
    sticker_name = " ".join(args)
    
    update.message.reply_text(f"Looking up price for {sticker_name}...")
    
    try:
        # If force_refresh, clear cursor cache
        if force_refresh:
            api.clear_cursor_cache()
        
        # Get price data
        price_data = api.get_sticker_price(sticker_name, update_cache=True, force_refresh=force_refresh)
        
        # Send price message
        message = format_price_message(price_data)
        update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        
        # Log the search
        log_search(update.effective_user.id, sticker_name, price_data)
    except Exception as e:
        logger.error(f"Error in price command: {e}")
        update.message.reply_text("❌ Error getting price data. Please try again later.")

def collections_command(update: Update, context: CallbackContext):
    """Handle /collections command."""
    # Get collections from cached data
    collections = CACHED_PRICES.keys()
    
    if not collections:
        # If no cached data, fetch from API
        api_collections = api.get_all_collections()
        collections = [c["name"] for c in api_collections]
    
    if not collections:
        update.message.reply_text("No collections found. Please try again later.")
        return
    
    update.message.reply_text(
        "Select a sticker collection:",
        reply_markup=get_collection_buttons(collections)
    )

def popular_command(update: Update, context: CallbackContext):
    """Handle /popular command."""
    # Get popular stickers
    popular_stickers = api.get_popular_stickers()
    
    if not popular_stickers:
        update.message.reply_text("No popular stickers found. Please try again later.")
        return
    
    message = "*Popular Stickers*\n\n"
    for sticker in popular_stickers[:10]:  # Show top 10
        message += f"• {sticker['name']} - {sticker['price']:.2f} TON\n"
    
    update.message.reply_markdown(message)

def refresh_command(update: Update, context: CallbackContext):
    """Handle /refresh command to update price data."""
    update.message.reply_text("Refreshing price data from the market. This may take a moment...")
    
    try:
        # Clear any cached cursors to ensure fresh data
        api.clear_cursor_cache()
        
        # Force update cache for popular collections
        popular_collections = [
            "Pudgy Penguins", 
            "Blum", 
            "Not Pixel", 
            "Flappy Bird", 
            "Lost Dogs", 
            "Bored Stickers"
        ]
        
        refreshed = 0
        failed = 0
        
        for collection in popular_collections:
            if collection in CACHED_PRICES:
                for character in CACHED_PRICES[collection]:
                    search_term = f"{collection} {character}"
                    try:
                        price_data = api.get_sticker_price(search_term, update_cache=True, force_refresh=True)
                        if not price_data.get("is_mock_data", True):
                            refreshed += 1
                        else:
                            failed += 1
                    except Exception as e:
                        logger.error(f"Error refreshing {search_term}: {e}")
                        failed += 1
        
        # Update the metadata
        update_metadata({"last_refresh": datetime.now().isoformat()})
        
        # Send summary
        update.message.reply_text(
            f"✅ Refresh complete!\n"
            f"Successfully refreshed {refreshed} sticker prices.\n"
            f"Could not find real data for {failed} stickers."
        )
    except Exception as e:
        logger.error(f"Error in refresh command: {e}")
        update.message.reply_text("❌ Error refreshing price data. Please try again later.")

def text_handler(update: Update, context: CallbackContext):
    """Handle text messages as sticker name searches."""
    sticker_name = update.message.text
    
    # Check if this looks like a sticker name
    if len(sticker_name.split()) >= 1:
        update.message.reply_text(f"Looking up price for: {sticker_name}...")
        
        # Get price data
        price_data = api.get_sticker_price(sticker_name)
        
        # Reply with price info
        update.message.reply_markdown(
            format_price_message(price_data),
            disable_web_page_preview=True
        )
    else:
        update.message.reply_text(
            "I didn't understand that. Try sending a sticker name like 'Pudgy Penguins Blue Pengu' or use /help to see available commands."
        )

def button_handler(update: Update, context: CallbackContext):
    """Handle button clicks."""
    query = update.callback_query
    query.answer()
    
    data = query.data
    
    if data == "back_to_collections":
        collections = CACHED_PRICES.keys()
        query.edit_message_text(
            text="Select a sticker collection:",
            reply_markup=get_collection_buttons(collections)
        )
    elif data.startswith("collection:"):
        collection = data.split(":", 1)[1]
        
        if collection in CACHED_PRICES:
            characters = CACHED_PRICES[collection].keys()
            query.edit_message_text(
                text=f"Select a sticker from {collection}:",
                reply_markup=get_character_buttons(collection, characters)
            )
        else:
            query.edit_message_text(text=f"No stickers found for collection: {collection}")
    
    elif data.startswith("character:"):
        _, collection, character = data.split(":", 2)
        
        if collection in CACHED_PRICES and character in CACHED_PRICES[collection]:
            price_data = CACHED_PRICES[collection][character]
            price_data["name"] = f"{collection} - {character}"
            price_data["price"] = price_data.get("price_ton", 0)
            
            query.edit_message_text(
                text=format_price_message(price_data),
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        else:
            query.edit_message_text(text=f"No price data found for {character} in {collection}")

def main():
    """Run the bot."""
    # Create the Updater and pass it your bot's token
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start_command))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("price", price_command))
    dispatcher.add_handler(CommandHandler("collections", collections_command))
    dispatcher.add_handler(CommandHandler("popular", popular_command))
    dispatcher.add_handler(CommandHandler("refresh", refresh_command))
    
    # Register message handlers
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, text_handler))
    
    # Register callback query handler
    dispatcher.add_handler(CallbackQueryHandler(button_handler))

    # Start the Bot
    updater.start_polling()
    logger.info("Bot started. Press Ctrl+C to stop.")

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == "__main__":
    main() 