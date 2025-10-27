#!/usr/bin/env python3
"""
Simplified Telegram Gift Price Bot

This bot provides price information for Telegram gift cards and stickers.
"""

import os
import sys
import logging
from typing import Dict, List, Optional

# Telegram Bot API
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, 
    CallbackContext, CallbackQueryHandler
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get script directory for cross-platform compatibility
script_dir = os.path.dirname(os.path.abspath(__file__))

# Constants - use os.path.join for cross-platform compatibility
GIFT_CARDS_DIR = os.path.join(script_dir, "new_gift_cards")
STICKER_CARDS_DIR = os.path.join(script_dir, "Sticker_Price_Cards")

def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    
    # Create keyboard with options
    keyboard = [
        [
            InlineKeyboardButton("🎁 Browse Gift Cards", callback_data="browse_gifts"),
            InlineKeyboardButton("🔍 Search Gift Cards", callback_data="search_gifts")
        ],
        [
            InlineKeyboardButton("📊 Browse Sticker Collections", callback_data="browse_stickers"),
            InlineKeyboardButton("🔍 Search Stickers", callback_data="search_stickers")
        ],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        f"Hello {user.first_name}! I'm the Telegram Gift Price Bot.\n\n"
        f"I can show you the current prices of Telegram gifts and stickers.",
        reply_markup=reply_markup
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Send a help message when the command /help is issued."""
    help_text = (
        "🎁 *Gift Price Bot Help*\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/gift <name> - Show price for a specific gift\n"
        "/search <query> - Search for gifts\n"
        "/browse - Browse all gift categories\n\n"
        "You can also send me the name of a gift, and I'll show you its price!\n\n"
        "📊 *Sticker Commands:*\n"
        "/sticker - Browse sticker collections\n"
        "/stickersearch <query> - Search for stickers\n"
        "/stickercollection <collection> - Show packs in a collection\n"
        "/stickerpack <collection> <pack> - Show a specific sticker pack"
    )
    
    update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

def gift_command(update: Update, context: CallbackContext) -> None:
    """Handle the /gift command."""
    if not context.args:
        update.message.reply_text("Please specify a gift name. Example: /gift Star")
        return
    
    gift_name = " ".join(context.args)
    
    # Try to find the gift card
    gift_card_path = None
    for filename in os.listdir(GIFT_CARDS_DIR):
        if filename.endswith("_card.png"):
            name = filename[:-9]  # Remove "_card.png"
            if gift_name.lower() in name.lower():
                gift_card_path = os.path.join(GIFT_CARDS_DIR, filename)
                gift_name = name
                break
    
    if not gift_card_path:
        update.message.reply_text(f"Sorry, I couldn't find a price card for '{gift_name}'.")
        return
    
    # Send the gift price card
    with open(gift_card_path, 'rb') as photo:
        update.message.reply_photo(
            photo=photo,
            caption=f"🎁 *{gift_name}* price card",
            parse_mode=ParseMode.MARKDOWN
        )

def sticker_command(update: Update, context: CallbackContext) -> None:
    """Handle the /sticker command."""
    # Create keyboard with collection options
    keyboard = []
    collections = []
    
    # Get all collections
    for filename in os.listdir(STICKER_CARDS_DIR):
        if filename.endswith("_price_card.png"):
            parts = filename.split("_")
            if len(parts) >= 2:
                collection = parts[0]
                if collection not in collections:
                    collections.append(collection)
    
    # Create keyboard
    for collection in sorted(collections):
        keyboard.append([InlineKeyboardButton(collection, callback_data=f"sticker_collection_{collection}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "Browse sticker collections:",
        reply_markup=reply_markup
    )

def stickersearch_command(update: Update, context: CallbackContext) -> None:
    """Handle the /stickersearch command."""
    if not context.args:
        update.message.reply_text("Please specify a search term. Example: /stickersearch dogs")
        return
    
    query = " ".join(context.args).lower()
    
    # Search for matching sticker cards
    matches = []
    for filename in os.listdir(STICKER_CARDS_DIR):
        if filename.endswith("_price_card.png"):
            if query in filename.lower():
                matches.append(filename)
    
    if not matches:
        update.message.reply_text(f"No stickers found matching '{query}'.")
        return
    
    if len(matches) == 1:
        # Only one match, send the price card directly
        filepath = os.path.join(STICKER_CARDS_DIR, matches[0])
        with open(filepath, 'rb') as photo:
            update.message.reply_photo(
                photo=photo,
                caption=f"📊 Sticker price card",
                parse_mode=ParseMode.MARKDOWN
            )
    else:
        # Multiple matches, show options
        keyboard = []
        for filename in matches[:10]:  # Limit to 10 results
            name = filename[:-15]  # Remove "_price_card.png"
            keyboard.append([InlineKeyboardButton(name, callback_data=f"sticker_file_{filename}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            f"Found {len(matches)} stickers matching '{query}'.\nSelect one to view:",
            reply_markup=reply_markup
        )

def callback_query_handler(update: Update, context: CallbackContext) -> None:
    """Handle callback queries."""
    query = update.callback_query
    data = query.data
    
    try:
        # Help
        if data == "help":
            help_text = (
                "🎁 *Gift Price Bot Help*\n\n"
                "*Commands:*\n"
                "/start - Start the bot\n"
                "/help - Show this help message\n"
                "/gift <name> - Show price for a specific gift\n"
                "/search <query> - Search for gifts\n"
                "/browse - Browse all gift categories\n\n"
                "You can also send me the name of a gift, and I'll show you its price!\n\n"
                "📊 *Sticker Commands:*\n"
                "/sticker - Browse sticker collections\n"
                "/stickersearch <query> - Search for stickers\n"
                "/stickercollection <collection> - Show packs in a collection\n"
                "/stickerpack <collection> <pack> - Show a specific sticker pack"
            )
            
            query.edit_message_text(help_text, parse_mode=ParseMode.MARKDOWN)
        
        # Browse stickers
        elif data == "browse_stickers":
            # Create keyboard with collection options
            keyboard = []
            collections = []
            
            # Get all collections
            for filename in os.listdir(STICKER_CARDS_DIR):
                if filename.endswith("_price_card.png"):
                    parts = filename.split("_")
                    if len(parts) >= 2:
                        collection = parts[0]
                        if collection not in collections:
                            collections.append(collection)
            
            # Create keyboard
            for collection in sorted(collections):
                keyboard.append([InlineKeyboardButton(collection, callback_data=f"sticker_collection_{collection}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            query.edit_message_text(
                "Browse sticker collections:",
                reply_markup=reply_markup
            )
        
        # Sticker collection
        elif data.startswith("sticker_collection_"):
            collection = data[len("sticker_collection_"):]
            
            # Get all packs in this collection
            packs = []
            for filename in os.listdir(STICKER_CARDS_DIR):
                if filename.endswith("_price_card.png") and filename.startswith(f"{collection}_"):
                    parts = filename[len(collection)+1:-15].split("_")  # Remove collection_ and _price_card.png
                    if parts:
                        pack = "_".join(parts)
                        packs.append(pack)
            
            if not packs:
                query.edit_message_text(f"No packs found in collection '{collection}'.")
                return
            
            # Create keyboard with packs
            keyboard = []
            for pack in sorted(packs):
                keyboard.append([InlineKeyboardButton(pack.replace("_", " "), callback_data=f"sticker_pack_{collection}_{pack}")])
            
            # Add back button
            keyboard.append([InlineKeyboardButton("🔙 Back to Collections", callback_data="browse_stickers")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            query.edit_message_text(
                f"Packs in collection '{collection}':",
                reply_markup=reply_markup
            )
        
        # Sticker pack
        elif data.startswith("sticker_pack_"):
            parts = data[len("sticker_pack_"):].split("_", 1)
            if len(parts) == 2:
                collection, pack = parts
                
                # Send the sticker price card
                filepath = os.path.join(STICKER_CARDS_DIR, f"{collection}_{pack}_price_card.png")
                
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as photo:
                        update.effective_message.reply_photo(
                            photo=photo,
                            caption=f"📊 *{collection} - {pack.replace('_', ' ')}* price card",
                            parse_mode=ParseMode.MARKDOWN
                        )
                    
                    query.answer("Sticker price card sent!")
                else:
                    query.answer(f"Sorry, I couldn't find a price card for {collection} - {pack}.")
        
        # Sticker file
        elif data.startswith("sticker_file_"):
            filename = data[len("sticker_file_"):]
            
            # Send the sticker price card
            filepath = os.path.join(STICKER_CARDS_DIR, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'rb') as photo:
                    update.effective_message.reply_photo(
                        photo=photo,
                        caption=f"📊 Sticker price card",
                        parse_mode=ParseMode.MARKDOWN
                    )
                
                query.answer("Sticker price card sent!")
            else:
                query.answer("Sorry, I couldn't find that sticker price card.")
        
        # Search stickers
        elif data == "search_stickers":
            query.edit_message_text(
                "Please use the /stickersearch command followed by your search term.\n"
                "Example: /stickersearch dogs"
            )
        
        # Start
        elif data == "start":
            start(update, context)
        
        # Browse gifts
        elif data == "browse_gifts":
            # Get all gift categories
            categories = set()
            for filename in os.listdir(GIFT_CARDS_DIR):
                if filename.endswith("_card.png"):
                    gift_name = filename[:-9]  # Remove "_card.png"
                    
                    # Extract category (before first underscore)
                    if "_" in gift_name:
                        category = gift_name.split("_")[0]
                        categories.add(category)
            
            if not categories:
                query.edit_message_text("No gift categories found.")
                return
            
            # Create keyboard with categories
            keyboard = []
            for category in sorted(categories):
                keyboard.append([InlineKeyboardButton(category, callback_data=f"category_{category}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            query.edit_message_text(
                "Browse gift categories:",
                reply_markup=reply_markup
            )
        
        # Category
        elif data.startswith("category_"):
            category = data[len("category_"):]
            
            # Find all gifts in this category
            gifts = []
            for filename in os.listdir(GIFT_CARDS_DIR):
                if filename.endswith("_card.png"):
                    gift_name = filename[:-9]  # Remove "_card.png"
                    
                    if gift_name.startswith(f"{category}_") or gift_name == category:
                        gifts.append(gift_name)
            
            if not gifts:
                query.edit_message_text(f"No gifts found in category '{category}'.")
                return
            
            # Create keyboard with gifts
            keyboard = []
            for gift_name in sorted(gifts):
                keyboard.append([InlineKeyboardButton(gift_name, callback_data=f"gift_{gift_name}")])
            
            # Add back button
            keyboard.append([InlineKeyboardButton("🔙 Back to Categories", callback_data="browse_gifts")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            query.edit_message_text(
                f"Gifts in category '{category}':",
                reply_markup=reply_markup
            )
        
        # Gift
        elif data.startswith("gift_"):
            gift_name = data[len("gift_"):]
            
            # Get the gift card path
            gift_card_path = os.path.join(GIFT_CARDS_DIR, f"{gift_name}_card.png")
            
            if not os.path.exists(gift_card_path):
                query.answer(f"Sorry, I couldn't find a price card for '{gift_name}'.")
                return
            
            # Send the gift price card
            with open(gift_card_path, 'rb') as photo:
                update.effective_message.reply_photo(
                    photo=photo,
                    caption=f"🎁 *{gift_name}* price card",
                    parse_mode=ParseMode.MARKDOWN
                )
            
            query.answer("Gift price card sent!")
        
        # Search gifts
        elif data == "search_gifts":
            query.edit_message_text(
                "Please use the /search command followed by your search term.\n"
                "Example: /search star"
            )
        
        else:
            query.answer("Unknown callback query")
    except Exception as e:
        logger.error(f"Error handling callback query: {e}")
        query.answer("An error occurred while processing your request.")

def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle incoming messages."""
    message_text = update.message.text
    
    # Check if this is a potential gift name
    if message_text and len(message_text) <= 50:  # Limit to reasonable gift names
        # Try to find a matching gift card
        gift_card_path = None
        for filename in os.listdir(GIFT_CARDS_DIR):
            if filename.endswith("_card.png"):
                name = filename[:-9]  # Remove "_card.png"
                if message_text.lower() in name.lower():
                    gift_card_path = os.path.join(GIFT_CARDS_DIR, filename)
                    gift_name = name
                    break
        
        if gift_card_path:
            # Send the gift price card
            with open(gift_card_path, 'rb') as photo:
                update.message.reply_photo(
                    photo=photo,
                    caption=f"🎁 *{gift_name}* price card",
                    parse_mode=ParseMode.MARKDOWN
                )
            return
        
        # Try to find a matching sticker card
        sticker_card_path = None
        for filename in os.listdir(STICKER_CARDS_DIR):
            if filename.endswith("_price_card.png"):
                if message_text.lower() in filename.lower():
                    sticker_card_path = os.path.join(STICKER_CARDS_DIR, filename)
                    break
        
        if sticker_card_path:
            # Send the sticker price card
            with open(sticker_card_path, 'rb') as photo:
                update.message.reply_photo(
                    photo=photo,
                    caption=f"📊 Sticker price card",
                    parse_mode=ParseMode.MARKDOWN
                )
            return
    
    # If no gift or sticker was found, send a help message
    update.message.reply_text(
        "I didn't recognize that as a gift or sticker name. "
        "Try using /gift, /search, or /sticker commands for more options."
    )

def search_command(update: Update, context: CallbackContext) -> None:
    """Handle the /search command."""
    if not context.args:
        update.message.reply_text("Please specify a search term. Example: /search star")
        return
    
    query = " ".join(context.args).lower()
    
    # Search for matching gift cards
    matches = []
    for filename in os.listdir(GIFT_CARDS_DIR):
        if filename.endswith("_card.png"):
            gift_name = filename[:-9]  # Remove "_card.png"
            if query in gift_name.lower():
                matches.append(gift_name)
    
    if not matches:
        update.message.reply_text(f"No gifts found matching '{query}'.")
        return
    
    if len(matches) == 1:
        # Only one match, send the price card directly
        gift_name = matches[0]
        gift_card_path = os.path.join(GIFT_CARDS_DIR, f"{gift_name}_card.png")
        with open(gift_card_path, 'rb') as photo:
            update.message.reply_photo(
                photo=photo,
                caption=f"🎁 *{gift_name}* price card",
                parse_mode=ParseMode.MARKDOWN
            )
    else:
        # Multiple matches, show options
        keyboard = []
        for gift_name in matches[:10]:  # Limit to 10 results
            keyboard.append([InlineKeyboardButton(gift_name, callback_data=f"gift_{gift_name}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        update.message.reply_text(
            f"Found {len(matches)} gifts matching '{query}'.\nSelect one to view:",
            reply_markup=reply_markup
        )

def browse_command(update: Update, context: CallbackContext) -> None:
    """Handle the /browse command."""
    # Get all gift categories
    categories = set()
    for filename in os.listdir(GIFT_CARDS_DIR):
        if filename.endswith("_card.png"):
            gift_name = filename[:-9]  # Remove "_card.png"
            
            # Extract category (before first underscore)
            if "_" in gift_name:
                category = gift_name.split("_")[0]
                categories.add(category)
    
    if not categories:
        update.message.reply_text("No gift categories found.")
        return
    
    # Create keyboard with categories
    keyboard = []
    for category in sorted(categories):
        keyboard.append([InlineKeyboardButton(category, callback_data=f"category_{category}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        "Browse gift categories:",
        reply_markup=reply_markup
    )

def main() -> None:
    """Start the bot."""
    try:
        # Get bot token from environment variable or use a default
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not token:
            logger.error("No bot token found. Please set the TELEGRAM_BOT_TOKEN environment variable.")
            return
        
        logger.info("Using bot token from environment variable")
        
        # Create the updater and dispatcher
        updater = Updater(token)
        dispatcher = updater.dispatcher
        
        # Register command handlers
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("help", help_command))
        dispatcher.add_handler(CommandHandler("gift", gift_command))
        dispatcher.add_handler(CommandHandler("search", search_command))
        dispatcher.add_handler(CommandHandler("browse", browse_command))
        dispatcher.add_handler(CommandHandler("sticker", sticker_command))
        dispatcher.add_handler(CommandHandler("stickersearch", stickersearch_command))
        
        # Register callback query handler
        dispatcher.add_handler(CallbackQueryHandler(callback_query_handler))
        
        # Register message handler
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
        
        # Start the bot
        logger.info("Starting bot...")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
