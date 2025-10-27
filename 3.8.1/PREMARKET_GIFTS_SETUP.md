# New Premarket Gifts Setup

## Overview
The system has been updated to support 6 new premarket gifts:

1. **Clover Pin** (`Clover_Pin.png`)
2. **Fresh Socks** (`Fresh_Socks.png`) 
3. **Sky Stilettos** (`Sky_Stilettos.png`)
4. **Artisan Brick** (`Artisan_Brick.png`)
5. **Mighty Arm** (`Mighty_Arm.png`)
6. **Input Key** (`Input_Key.png`)

## Market Status Changes
The following gifts have moved from premarket to regular market:
- **Ionic Dryer** (now regular market)
- **Moon Pendant** (now regular market)
- **Jolly Chimp** (now regular market)
- **Stellar Rocket** (now regular market)

## Required Actions

### 1. Add Gift Images
Place the following PNG images in the `downloaded_images/` directory:
```
downloaded_images/
├── Clover_Pin.png
├── Fresh_Socks.png
├── Sky_Stilettos.png
├── Artisan_Brick.png
├── Mighty_Arm.png
└── Input_Key.png
```

### 2. System Updates Completed
✅ **tonnel_api.py** - Updated PREMARKET_GIFTS mapping with new gifts
✅ **portal_api.py** - Added premarket parameter support
✅ **new_card_design.py** - Updated to use Portal API for all gifts
✅ **main.py** - Added new premarket gifts to main gift names list

### 3. Unified API System Features
- **Price Fetching**: Uses Portal API for ALL gifts (both regular and premarket)
- **Premarket Support**: Portal API now supports premarket parameter
- **Supply Data**: Legacy API integration for supply information
- **Chart Data**: Historical price tracking and percentage changes
- **Scheduling**: Automatic price updates every 32 minutes
- **Simplified Architecture**: Single API source for all gift types

### 4. Testing the System
```bash
# Test Portal API with premarket gifts
python -c "
import asyncio
from portal_api import fetch_gift_data
async def test():
    # Test premarket gift
    data = await fetch_gift_data('Clover Pin', is_premarket=True)
    print(f'Clover Pin (premarket): {data}')
    
    # Test regular gift
    data = await fetch_gift_data('Ionic Dryer', is_premarket=False)
    print(f'Ionic Dryer (regular): {data}')
asyncio.run(test())
"
```

### 5. Integration Points
- **Gift Card Generation**: New cards will be generated with Portal API pricing
- **Bot Commands**: Users can request prices for new premarket gifts
- **Admin Dashboard**: Monitoring and analytics for premarket performance
- **Rate Limiting**: Same rate limits apply (5 requests/minute)

## Notes
- The system automatically handles premarket vs. market gift classification
- ALL gifts now use Portal API (with premarket parameter for premarket gifts)
- Historical price data will be collected automatically
- Supply data integration is already configured
- Simplified architecture with single API source

## Troubleshooting
If images are missing, the system will log warnings but continue to function for price fetching. Add the images to enable full gift card generation functionality.
