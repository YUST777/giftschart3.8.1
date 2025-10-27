#!/usr/bin/env python3
"""
Test Updated Sticker Integration
"""

import sticker_integration

def test_updated_sticker_format():
    """Test the updated sticker message format."""
    print("Testing updated sticker integration...")
    
    # Load sticker data
    data = sticker_integration.load_sticker_price_data()
    
    if data['stickers_with_prices']:
        # Get first sticker
        sticker = data['stickers_with_prices'][0]
        
        # Test the new format
        message = sticker_integration.format_sticker_price_message(sticker)
        print(f"New message format: {message}")
        
        # Check that it doesn't contain price info
        if "TON" not in message and "Supply" not in message and "Change" not in message:
            print("✅ Price details successfully removed from caption")
        else:
            print("❌ Price details still present in caption")
        
        # Test callback data format
        collection = sticker["collection"]
        sticker_name = sticker["sticker"]
        callback_data = f"sticker_markets_{collection}_{sticker_name}"
        print(f"✅ Callback data format: {callback_data}")
            
        print("✅ Updated sticker integration test completed")
    else:
        print("❌ No sticker data found")

if __name__ == "__main__":
    test_updated_sticker_format() 