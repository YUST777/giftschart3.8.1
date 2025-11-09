#!/usr/bin/env python3
"""
MRKT and Quant Marketplace API Integration
Fetches price data for plus premarket gifts from MRKT (6 gifts) and Quant Marketplace (23 gifts)
"""

import os
import sys
import json
import logging
import asyncio
import requests
import urllib.parse
from typing import Optional, Dict, Any
from plus_premarket_gifts import PLUS_PREMARKET_GIFTS, is_mrkt_gift, get_gift_id

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Try to import cloudscraper for Quant API
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    cloudscraper = None
    CLOUDSCRAPER_AVAILABLE = False
    logging.warning("cloudscraper not available - Quant API will not work")

# Try to import Telethon for auth
try:
    from telethon import TelegramClient, functions
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    logging.warning("Telethon not available - automatic auth will not work")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
api_logger = logging.getLogger("mrkt_quant_api")

# API configuration
MRKT_API_BASE = 'https://api.tgmrkt.io'
MRKT_BOT_USERNAME = 'main_mrkt_bot'
QUANT_API_BASE = 'https://quant-marketplace.com'
QUANT_BOT_USERNAME = 'QuantMarketRobot'

# Telethon session configuration
TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
TELEGRAM_SESSION_NAME = os.getenv('TELEGRAM_SESSION_NAME', 'mrkt_session')

# Import TON price utility
try:
    from ton_price_utils import get_ton_price_usd
except ImportError:
    # Fallback if module not available
    def get_ton_price_usd():
        return 2.10  # Fallback value

# Cache for auth tokens
_mrkt_jwt_token = None
_mrkt_token_timestamp = 0
_quant_init_data = None
_quant_init_data_timestamp = 0

# Token refresh intervals
MRKT_TOKEN_REFRESH_INTERVAL = 45  # Refresh every 45 seconds
QUANT_TOKEN_REFRESH_INTERVAL = 300  # Refresh every 5 minutes

# Cache for gift data
_gift_cache = {}
_cache_expiry = {}
CACHE_DURATION = 60  # 1 minute cache

# Use shared TON price utility
get_ton_price_from_coinmarketcap = get_ton_price_usd

async def get_mrkt_init_data() -> Optional[str]:
    """Get fresh initData from MRKT bot using Telethon"""
    if not TELETHON_AVAILABLE:
        logger.error("Telethon not available - cannot get MRKT initData")
        return None
    
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        logger.error("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set")
        return None
    
    client = None
    try:
        client = TelegramClient(TELEGRAM_SESSION_NAME, int(TELEGRAM_API_ID), TELEGRAM_API_HASH)
        await client.connect()
        
        if not await client.is_user_authorized():
            logger.error("Telethon session not authorized. Run setup_mrkt_session.py")
            return None
        
        bot = await client.get_entity(MRKT_BOT_USERNAME)
        
        result = await client(functions.messages.RequestWebViewRequest(
            peer=bot,
            bot=bot,
            platform="ios",
            url=f"{MRKT_API_BASE}/api/v1/auth",
        ))
        
        if not result or not hasattr(result, 'url'):
            return None
        
        webview_url = result.url
        parsed = urllib.parse.urlparse(webview_url)
        
        # Check query params
        query_params = urllib.parse.parse_qs(parsed.query)
        if 'tgWebAppData' in query_params:
            init_data = urllib.parse.unquote(query_params['tgWebAppData'][0])
            return init_data
        
        # Check fragment
        fragment = parsed.fragment
        if fragment and 'tgWebAppData=' in fragment:
            init_data_encoded = fragment.split('tgWebAppData=')[1]
            if '&' in init_data_encoded:
                init_data_encoded = init_data_encoded.split('&')[0]
            init_data = urllib.parse.unquote(init_data_encoded)
            return init_data
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting MRKT initData: {e}")
        return None
    finally:
        if client:
            await client.disconnect()

async def get_quant_init_data() -> Optional[str]:
    """Get fresh initData from Quant bot using Telethon"""
    if not TELETHON_AVAILABLE:
        logger.error("Telethon not available - cannot get Quant initData")
        return None
    
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        logger.error("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set")
        return None
    
    client = None
    try:
        client = TelegramClient(TELEGRAM_SESSION_NAME, int(TELEGRAM_API_ID), TELEGRAM_API_HASH)
        await client.connect()
        
        if not await client.is_user_authorized():
            logger.error("Telethon session not authorized")
            return None
        
        bot = await client.get_entity(QUANT_BOT_USERNAME)
        
        result = await client(functions.messages.RequestWebViewRequest(
            peer=bot,
            bot=bot,
            platform="ios",
            url=QUANT_API_BASE,
        ))
        
        if not result or not hasattr(result, 'url'):
            return None
        
        webview_url = result.url
        parsed = urllib.parse.urlparse(webview_url)
        fragment = parsed.fragment
        
        if fragment and 'tgWebAppData=' in fragment:
            init_data_encoded = fragment.split('tgWebAppData=')[1]
            if '&' in init_data_encoded:
                init_data_encoded = init_data_encoded.split('&')[0]
            init_data = urllib.parse.unquote(init_data_encoded)
            return init_data
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting Quant initData: {e}")
        return None
    finally:
        if client:
            await client.disconnect()

def get_mrkt_jwt_token(init_data: str) -> Optional[str]:
    """Exchange initData for JWT token from MRKT API"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        
        payload = {'data': init_data}
        
        response = requests.post(f"{MRKT_API_BASE}/api/v1/auth", headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if 'token' in data:
                return data['token']
            elif 'accessToken' in data:
                return data['accessToken']
        
        logger.error(f"MRKT auth failed: {response.status_code} - {response.text}")
        return None
        
    except Exception as e:
        logger.error(f"MRKT auth error: {e}")
        return None

async def ensure_mrkt_token() -> Optional[str]:
    """Ensure we have a valid MRKT JWT token"""
    global _mrkt_jwt_token, _mrkt_token_timestamp
    
    import time
    current_time = time.time()
    
    # Check if token needs refresh
    if _mrkt_jwt_token and (current_time - _mrkt_token_timestamp) < MRKT_TOKEN_REFRESH_INTERVAL:
        return _mrkt_jwt_token
    
    # Get fresh initData and exchange for JWT
    api_logger.info("[MRKT] Refreshing JWT token...")
    
    # Retry logic for database lock issues
    max_retries = 3
    for attempt in range(max_retries):
        try:
            init_data = await get_mrkt_init_data()
            if init_data:
                break
        except Exception as e:
            if "database is locked" in str(e).lower() and attempt < max_retries - 1:
                api_logger.warning(f"[MRKT] Database locked, retrying in 1 second... (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(1)
                continue
            else:
                logger.error(f"Error getting MRKT initData: {e}")
                return None
    
    if not init_data:
        logger.error("Could not get MRKT initData")
        return None
    
    jwt_token = get_mrkt_jwt_token(init_data)
    
    if jwt_token:
        _mrkt_jwt_token = jwt_token
        _mrkt_token_timestamp = current_time
        api_logger.info("[MRKT] JWT token refreshed successfully")
        return jwt_token
    
    return None

async def ensure_quant_init_data() -> Optional[str]:
    """Ensure we have valid Quant initData"""
    global _quant_init_data, _quant_init_data_timestamp
    
    import time
    current_time = time.time()
    
    # Check if initData needs refresh
    if _quant_init_data and (current_time - _quant_init_data_timestamp) < QUANT_TOKEN_REFRESH_INTERVAL:
        return _quant_init_data
    
    # Get fresh initData
    api_logger.info("[Quant] Refreshing initData...")
    init_data = await get_quant_init_data()
    
    if init_data:
        _quant_init_data = init_data
        _quant_init_data_timestamp = current_time
        api_logger.info("[Quant] initData refreshed successfully")
        return init_data
    
    logger.error("Could not get Quant initData")
    return None

async def fetch_from_mrkt(gift_id: str, gift_name: str) -> Optional[Dict[str, Any]]:
    """Fetch gift data from MRKT API"""
    try:
        token = await ensure_mrkt_token()
        if not token:
            return None
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
        }
        
        endpoint = f"{MRKT_API_BASE}/api/v1/gifts/collections"
        response = requests.get(endpoint, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Find gift by ID (name field in MRKT contains the numeric ID)
            for gift in data:
                if gift.get('name') == gift_id or gift.get('title', '').lower() == gift_name.lower():
                    # Extract price from nanoTons
                    floor_price_nano = gift.get('floorPriceNanoTons', 0)
                    floor_price_ton = floor_price_nano / 1_000_000_000  # Convert nanoTons to TON
                    
                    # Calculate 24h change if available
                    prev_price_nano = gift.get('previousDayFloorPriceNanoTons')
                    change_percentage = 0
                    if prev_price_nano and prev_price_nano > 0:
                        change_percentage = ((floor_price_nano - prev_price_nano) / prev_price_nano) * 100
                    
                    api_logger.info(f"[MRKT] Found {gift_name} - Price: {floor_price_ton} TON")
                    
                    # Get real TON price from CoinMarketCap
                    ton_price_usd = get_ton_price_from_coinmarketcap()
                    price_usd = floor_price_ton * ton_price_usd
                    
                    # Get supply from gift data
                    from plus_premarket_gifts import get_gift_supply
                    supply = get_gift_supply(gift_name)
                    
                    return {
                        "name": gift_name,
                        "priceUsd": price_usd,
                        "priceTon": floor_price_ton,
                        "changePercentage": change_percentage,
                        "model": "",
                        "backdrop": "",
                        "symbol": "",
                        "upgradedSupply": supply if supply else "N/A"
                    }
            
            api_logger.warning(f"[MRKT] Gift {gift_name} (ID: {gift_id}) not found in API response")
            return None
            
        else:
            api_logger.error(f"[MRKT] API request failed: {response.status_code}")
            return None
            
    except Exception as e:
        api_logger.error(f"[MRKT] Error fetching {gift_name}: {e}")
        return None

async def fetch_from_quant(gift_id: str, gift_name: str) -> Optional[Dict[str, Any]]:
    """Fetch gift data from Quant Marketplace API with Cloudflare bypass"""
    if not CLOUDSCRAPER_AVAILABLE:
        logger.error("cloudscraper not available - cannot access Quant API")
        return None
    
    try:
        init_data = await ensure_quant_init_data()
        if not init_data:
            return None
        
        # Create cloudscraper
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'ios',
                'mobile': True,
            }
        )
        
        headers = {
            'Authorization': f'Bearer {init_data}',
            'Accept': 'application/json',
            'Origin': QUANT_API_BASE,
            'Referer': f'{QUANT_API_BASE}/',
        }
        
        url = f"{QUANT_API_BASE}/api/gifts"
        response = scraper.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            
            # Find gift by ID
            for gift in data:
                if gift.get('id') == gift_id:
                    # Extract price - handle both string and numeric formats
                    floor_price_str = gift.get('floor_price', '0')
                    try:
                        floor_price = float(floor_price_str)
                    except (ValueError, TypeError):
                        floor_price = 0.0
                    
                    # If price is 0, check if gift exists but has no listings
                    if floor_price == 0:
                        api_logger.warning(f"[Quant] {gift_name} has no active listings (floor_price: 0)")
                        # Return None to allow fallback to mock data or other source
                        return None
                    
                    api_logger.info(f"[Quant] Found {gift_name} - Price: {floor_price} TON")
                    
                    # Get real TON price from CoinMarketCap
                    ton_price_usd = get_ton_price_from_coinmarketcap()
                    price_usd = floor_price * ton_price_usd
                    
                    # Get supply from API or gift data
                    api_supply = gift.get('supply')
                    from plus_premarket_gifts import get_gift_supply
                    supply = api_supply if api_supply else get_gift_supply(gift_name)
                    
                    return {
                        "name": gift_name,
                        "priceUsd": price_usd,
                        "priceTon": floor_price,
                        "changePercentage": 0,  # Quant doesn't provide 24h change
                        "model": "",
                        "backdrop": "",
                        "symbol": "",
                        "upgradedSupply": supply if supply else "N/A"
                    }
            
            api_logger.warning(f"[Quant] Gift {gift_name} (ID: {gift_id}) not found in API response")
            return None
            
        else:
            api_logger.error(f"[Quant] API request failed: {response.status_code}")
            return None
            
    except Exception as e:
        api_logger.error(f"[Quant] Error fetching {gift_name}: {e}")
        return None

async def fetch_gift_data(gift_name: str) -> Optional[Dict[str, Any]]:
    """
    Fetch gift data for plus premarket gifts from MRKT or Quant API.
    Automatically determines which API to use based on gift ID.
    
    Args:
        gift_name: Display name of the gift
        
    Returns:
        dict: Gift data with price information or None if not found
    """
    # Check cache first
    import time
    current_time = time.time()
    
    if gift_name in _gift_cache and current_time - _cache_expiry.get(gift_name, 0) < CACHE_DURATION:
        api_logger.info(f"[Cache] Returning cached data for {gift_name}")
        return _gift_cache[gift_name]
    
    # Get gift ID
    gift_id = get_gift_id(gift_name)
    if not gift_id:
        api_logger.error(f"Gift {gift_name} not found in plus premarket gifts")
        return None
    
    api_logger.info(f"Fetching {gift_name} (ID: {gift_id})")
    
    # Check if credentials are available
    if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
        api_logger.warning(f"[{gift_name}] No Telegram credentials - using mock data")
        return _generate_mock_data(gift_name)
    
    # Determine which API to use
    if is_mrkt_gift(gift_id):
        api_logger.info(f"[{gift_name}] Using MRKT API (special gift with numeric ID)")
        result = await fetch_from_mrkt(gift_id, gift_name)
    else:
        api_logger.info(f"[{gift_name}] Using Quant API")
        result = await fetch_from_quant(gift_id, gift_name)
    
    # Fallback to mock data if API fails
    if not result:
        api_logger.warning(f"[{gift_name}] API failed - using mock data")
        result = _generate_mock_data(gift_name)
    
    # Cache the result if successful
    if result:
        _gift_cache[gift_name] = result
        _cache_expiry[gift_name] = current_time
    
    return result

async def fetch_chart_data(gift_name: str) -> Optional[list]:
    """
    Fetch chart data for a plus premarket gift.
    Note: Currently returns mock data as MRKT/Quant don't provide historical price data.
    
    Args:
        gift_name: Name of the gift
        
    Returns:
        list: Chart data points (mock data for now)
    """
    # Generate mock chart data since MRKT/Quant don't provide historical data
    gift_data = await fetch_gift_data(gift_name)
    
    if not gift_data:
        return None
    
    # Generate simple flat chart based on current price
    price = gift_data.get('priceTon', 0)
    
    # Create 24 data points with slight variation
    import random
    chart_data = []
    for i in range(24):
        variation = random.uniform(-0.05, 0.05)  # ±5% variation
        point_price = price * (1 + variation)
        chart_data.append(point_price)
    
    return chart_data

def _generate_mock_data(gift_name: str) -> Dict[str, Any]:
    """Generate mock data for testing when API is not available"""
    import random
    from plus_premarket_gifts import get_gift_supply
    
    # Generate deterministic but varied pricing based on gift name
    base_price = (hash(gift_name) % 500 + 100) / 100  # 1.00 to 6.00 TON
    price_ton = round(base_price, 2)
    # Get real TON price from CoinMarketCap for mock data too
    ton_price_usd = get_ton_price_from_coinmarketcap()
    price_usd = round(price_ton * ton_price_usd, 2)
    
    # Generate random change percentage
    change_percentage = round(random.uniform(-15, 15), 2)
    
    # Get supply from gift data
    supply = get_gift_supply(gift_name)
    
    api_logger.info(f"[Mock] Generated mock data for {gift_name} - Price: {price_ton} TON, Supply: {supply}")
    
    return {
        "name": gift_name,
        "priceUsd": price_usd,
        "priceTon": price_ton,
        "changePercentage": change_percentage,
        "model": "",
        "backdrop": "",
        "symbol": "",
        "upgradedSupply": supply if supply else "N/A"
    }

# Cache clearing functions
def clear_all_caches():
    """Clear all caches to force fresh API calls"""
    global _gift_cache, _cache_expiry, _mrkt_jwt_token, _quant_init_data
    _gift_cache.clear()
    _cache_expiry.clear()
    _mrkt_jwt_token = None
    _quant_init_data = None
    api_logger.info("🧹 CLEARED: All caches cleared")

def clear_price_cache():
    """Clear only the price cache"""
    global _gift_cache, _cache_expiry
    _gift_cache.clear()
    _cache_expiry.clear()
    api_logger.info("🧹 CLEARED: Price cache cleared")

