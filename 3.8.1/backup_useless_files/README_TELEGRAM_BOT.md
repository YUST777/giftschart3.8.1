# README: How to Use the Telegram Bot with Sticker Price Cards

To run the Telegram bot with sticker price card functionality:

1. Make sure you have all the required dependencies installed:
   ```
   source venv/bin/activate
   pip install python-telegram-bot
   ```

2. Make sure the price updater service is running:
   ```
   ./run_price_updater.sh
   ```

3. Run the Telegram bot:
   ```
   python telegram_bot.py
   ```

4. In the Telegram bot, you can now use the following commands:
   - /sticker - Browse sticker collections
   - /stickersearch <query> - Search for stickers
   - /stickercollection <collection> - Show packs in a collection
   - /stickerpack <collection> <pack> - Show a specific sticker pack

5. You can also search for stickers by typing their name in chat!

The bot will send the sticker price card image showing the current price and other information about the sticker.
