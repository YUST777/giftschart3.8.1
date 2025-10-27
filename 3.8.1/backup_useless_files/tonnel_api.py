import os
import sys
import logging
import requests
from datetime import datetime, timedelta
import time
from pprint import pformat

# Supply data cache
# This cache stores upgradedSupply values for all gifts to avoid multiple API calls

# Persistent supply data cache
_supply_data_cache = {}

# Function to initialize the API integration
def initialize_api():
    """
    Initialize API settings and logging
    """
    logger.info("API initialization complete")

def preload_supply_data():
    """
    Preload all supply data from the API to avoid multiple calls during card generation
    """
    global _supply_data_cache
    try:
        logger.info("Preloading supply data from API...")
        response = requests.get(
            "https://nft-gifts-api-1.onrender.com/gifts",
            timeout=10
        )
        
        if response.status_code == 200:
            api_data = response.json()
            # Cache all supply data at once
            for api_gift in api_data:
                gift_supply = api_gift.get("upgradedSupply", 0)
                gift_name = api_gift.get("name", "")
                if gift_supply > 0 and gift_name:
                    _supply_data_cache[gift_name] = gift_supply
            
            logger.info(f"Successfully preloaded supply data for {len(_supply_data_cache)} gifts")
        else:
            logger.error(f"Failed to preload supply data, API returned status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Error preloading supply data: {e}")

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tonnel_api")

# Add the virtual environment path for tonnelmp - platform independent approach
# Try multiple possible locations for the site-packages directory
possible_site_packages = [
    os.path.join(script_dir, "venv", "lib", "python3.12", "site-packages"),  # Linux
    os.path.join(script_dir, "venv", "Lib", "site-packages"),               # Windows
    os.path.join(script_dir, "venv", "lib", "python3.11", "site-packages"),  # Older Python version
    os.path.join(script_dir, "venv", "lib", "python3.10", "site-packages"),  # Older Python version
]

# Try each path and use the first one that exists
for site_packages in possible_site_packages:
    if os.path.exists(site_packages):
        sys.path.append(site_packages)
        logger.info(f"Added site-packages to path: {site_packages}")
        break
else:
    logger.warning("Could not find site-packages directory in virtual environment")
    
# Import the Tonnel API library
try:
    from tonnelmp import getGifts, filterStatsPretty
    TONNEL_API_AVAILABLE = True
    logger.info("Tonnel Marketplace API loaded successfully")
except ImportError:
    TONNEL_API_AVAILABLE = False
    logger.warning("Tonnel Marketplace API not available. Using fallback API.")

# Import authentication from config
try:
    from bot_config import TONNEL_API_AUTH, USE_TONNEL_API
    USER_AUTH = TONNEL_API_AUTH
    API_ENABLED = USE_TONNEL_API
    logger.info("Loaded Tonnel API configuration from bot_config.py")
except ImportError:
    # Fallback auth data
    USER_AUTH = "user=%7B%22id%22%3A8104656627%2C%22first_name%22%3A%22.%22%2C%22last_name%22%3A%22%22%2C%22language_code%22%3A%22ar%22%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FgCL42-4AfBQW0dSyFkSiDKr1BylGdW5vlh45dzchRSPHbIVJRHzDosx1BLiUp4uN.svg%22%7D&chat_instance=2270161767277426387&chat_type=sender&auth_date=1749544716&signature=OZ6SrxtypXh57YRE19D8eP7QAebPig1nFRBZhLUJUuca988L9cROiwfGjCtyogHYFf8UtoCd0qquYrrPku19Dg&hash=c61809095da9462c926d325bc89e763c701fb52d03a3224a5ac91e85dc7ea88a"
    API_ENABLED = True
    logger.warning("Could not load config, using fallback authentication data")

# Initialize API settings
initialize_api()

# Preload supply data at startup to avoid multiple API calls
preload_supply_data()

# Known premarket gifts that need special handling
PREMARKET_GIFTS = {
    "Heart Locket",
    "Lush Bouquet",
    "Bow Tie",
    "Heroic Helmet",
}

# Cache for gift data to reduce API calls
_gift_cache = {}
_cache_expiry = {}
_floor_cache = None
_floor_cache_expiry = 0
CACHE_DURATION = 10 * 60  # 10 minutes in seconds

def fetch_gift_data_tonnel(gift_name):
    """
    Fetch gift data from the Tonnel Marketplace API
    
    Args:
        gift_name: Name of the gift to fetch data for
        
    Returns:
        dict: Gift data with price information or None if not found
    """
    if not TONNEL_API_AVAILABLE or not API_ENABLED:
        logger.warning("Tonnel API not available or disabled, cannot fetch gift data")
        return None
    
    # Check if this is a premarket gift
    is_premarket = gift_name in PREMARKET_GIFTS
        
    cache_key = f"{gift_name.lower()}_{is_premarket}"
    
    # Check cache first
    if cache_key in _gift_cache:
        if time.time() < _cache_expiry.get(cache_key, 0):
            logger.debug(f"Using cached data for {gift_name}")
            return _gift_cache[cache_key]
    
    try:
        # Get data from Tonnel API with premarket=True for premarket gifts
        if is_premarket:
            logger.info(f"Fetching premarket gift data for {gift_name}")
            gifts = getGifts(gift_name=gift_name, limit=5, sort="price_asc", premarket=True, authData=USER_AUTH)
        else:
            gifts = getGifts(gift_name=gift_name, limit=5, sort="price_asc", authData=USER_AUTH)
        
        if not gifts:
            logger.warning(f"No gift data found for {gift_name}")
            # If regular request failed and not already tried as premarket, try as premarket
            if not is_premarket:
                logger.info(f"Attempting to fetch {gift_name} as premarket gift")
                gifts = getGifts(gift_name=gift_name, limit=5, sort="price_asc", premarket=True, authData=USER_AUTH)
                if gifts:
                    logger.info(f"Successfully found {gift_name} as premarket gift")
                    # Update our knowledge about premarket gifts
                    PREMARKET_GIFTS.add(gift_name)
                    
            if not gifts:
                return None
            
        # Use the lowest price gift for cards
        gift = gifts[0]
        
        # Try to get upgradedSupply from API
        try:
            # First check if supply data is already in Tonnel API response
            upgradedSupply = gift.get("upgradedSupply", 0)
            logger.info(f"Initial upgradedSupply from Tonnel API for {gift_name}: {upgradedSupply}")
            
            # If not found in Tonnel API, try the cache
            if not upgradedSupply and gift_name in _supply_data_cache:
                upgradedSupply = _supply_data_cache.get(gift_name, 0)
                logger.info(f"Using cached upgradedSupply for {gift_name}: {upgradedSupply}")
            
            # If still not found, try the fallback API
            if not upgradedSupply:
                try:
                    logger.info(f"Fetching upgradedSupply from fallback API for {gift_name}")
                    response = requests.get(
                        "https://nft-gifts-api-1.onrender.com/gifts", 
                        timeout=5  # Shorter timeout to fail faster
                    )
                    
                    if response.status_code == 200:
                        api_data = response.json()
                        # Cache all supply data at once
                        for api_gift in api_data:
                            gift_supply = api_gift.get("upgradedSupply", 0)
                            gift_name_in_api = api_gift.get("name", "")
                            if gift_supply > 0 and gift_name_in_api:
                                _supply_data_cache[gift_name_in_api] = gift_supply
                        
                        # Get our specific gift's supply from cache now
                        if gift_name in _supply_data_cache:
                            upgradedSupply = _supply_data_cache[gift_name]
                            logger.info(f"Found upgradedSupply from fallback API for {gift_name}: {upgradedSupply}")
                        else:
                            logger.warning(f"Gift {gift_name} not found in fallback API")
                    else:
                        logger.error(f"Fallback API request failed with status code: {response.status_code}")
                except Exception as e:
                    # Just log and continue if fallback API fails
                    logger.error(f"Error fetching from fallback API: {e}")
        except Exception as e:
            logger.error(f"Error getting upgraded supply: {e}")
            upgradedSupply = 0
        
        # Format data to match expected structure in existing code
        result = {
            "name": gift["name"],
            "priceUsd": gift["price"] * 3.0,  # Approximate TON-to-USD conversion
            "priceTon": gift["price"],
            "changePercentage": 0,  # We don't have percentage change from this API
            "model": gift.get("model", ""),
            "backdrop": gift.get("backdrop", ""),
            "symbol": gift.get("symbol", ""),
            "upgradedSupply": upgradedSupply
        }
        
        logger.info(f"Fetched data for {gift_name} from Tonnel API")
        logger.debug(pformat(result))
        
        # Cache the result
        _gift_cache[cache_key] = result
        _cache_expiry[cache_key] = time.time() + CACHE_DURATION
        
        return result
    except Exception as e:
        logger.error(f"Error fetching gift data from Tonnel API: {e}")
        return None

def fetch_chart_data_tonnel(gift_name):
    """
    Generate chart data points for a gift using data from Tonnel API
    
    Args:
        gift_name: Name of the gift to fetch chart data for
        
    Returns:
        list: List of data points with time and price information
    """
    if not TONNEL_API_AVAILABLE or not API_ENABLED:
        logger.warning("Tonnel API not available or disabled, cannot fetch chart data")
        return []
        
    try:
        # Get current gift price (will automatically handle premarket gifts)
        gift_data = fetch_gift_data_tonnel(gift_name)
        if not gift_data:
            logger.warning(f"No gift price data available for chart: {gift_name}")
            return []
            
        # Since the API doesn't provide historical data, we'll generate
        # simulated chart data based on the current price
        current_price = float(gift_data["priceTon"])
        
        # Generate 24 data points representing last 24 hours with realistic variations
        data_points = []
        current_time = datetime.now()
        
        # Create a more pronounced percentage change between -10% and +10%
        # Use gift name hash to make it consistent for each gift
        name_hash = abs(hash(gift_name)) % 1000
        
        # Generate a percentage change between -10% and +10%
        # Use the hash to determine if it's positive or negative
        is_positive = name_hash % 2 == 0
        percentage = (name_hash % 10) + 1  # 1-10
        
        if not is_positive:
            percentage = -percentage
            
        # Calculate start price based on percentage change
        start_price = current_price / (1 + (percentage / 100))
        
        # Create 24 data points with realistic price movement
        for i in range(24):
            point_time = current_time - timedelta(hours=23-i)
            time_str = point_time.strftime("%H:%M")
            
            # Calculate progress through the timeline
            progress = i / 23  # 0 to 1 as we move through time
            
            # Add some random noise to make the chart look more realistic
            random_factor = ((hash(f"{gift_name}-{i}") % 100) - 50) / 1000  # -0.05 to 0.05 variation
            
            # Create a price that moves from start_price to current_price with some randomness
            point_price = start_price + (current_price - start_price) * progress + (current_price * random_factor)
            point_price = max(point_price, min(start_price, current_price) * 0.9)  # Don't go below 90% of min price
            
            data_points.append({
                "time": time_str,
                "priceUsd": str(point_price * 3.0),  # Approximate USD price
                "priceTon": str(point_price)
            })
        
        # Calculate the actual percentage change from the generated data
        if data_points and len(data_points) >= 2:
            start_price = float(data_points[0]["priceTon"])
            end_price = float(data_points[-1]["priceTon"])
            
            # Calculate percentage change from the simulated data
            percent_change = ((end_price - start_price) / start_price) * 100
            
            # Update the gift data with this percentage change
            if gift_data:
                # Update the returned gift data object directly
                gift_data["changePercentage"] = percent_change
                
                # Also update the cache if it exists
                is_premarket = gift_name in PREMARKET_GIFTS
                cache_key = f"{gift_name.lower()}_{is_premarket}"
                if cache_key in _gift_cache:
                    _gift_cache[cache_key]["changePercentage"] = percent_change
                    
            logger.info(f"Generated chart data with {percent_change:.2f}% change for {gift_name}")
        else:
            logger.info(f"Generated chart data for {gift_name} based on Tonnel API price data")
        
        return data_points
        
    except Exception as e:
        logger.error(f"Error generating chart data from Tonnel API: {e}")
        return []

def get_all_gift_floors():
    """
    Get floor prices for all available gifts using the filterStatsPretty function
    
    Returns:
        dict: Dictionary with gift names as keys and floor prices as values
    """
    global _floor_cache, _floor_cache_expiry
    
    if not TONNEL_API_AVAILABLE or not API_ENABLED:
        logger.warning("Tonnel API not available or disabled, cannot fetch gift floors")
        return {}
        
    # Check cache first
    if _floor_cache and time.time() < _floor_cache_expiry:
        logger.debug("Using cached floor prices")
        return _floor_cache
        
    try:
        # Get all floor prices using filterStatsPretty - now we can use it with auth
        stats = filterStatsPretty(authData=USER_AUTH)
        
        if stats.get('status') != 'success' or 'data' not in stats:
            logger.error("Failed to get floor prices from API")
            return {}
            
        floor_data = {}
        raw_data = stats['data']
        
        # Process the data into a simplified format
        for gift_name, gift_data in raw_data.items():
            if 'data' in gift_data and 'floorPrice' in gift_data['data']:
                floor_data[gift_name] = {
                    'floorPrice': gift_data['data']['floorPrice'],
                    'howMany': gift_data['data']['howMany']
                }
                
                # Also include model-specific data if available
                models = {}
                for model_name, model_data in gift_data.items():
                    if model_name != 'data' and isinstance(model_data, dict) and 'floorPrice' in model_data:
                        models[model_name] = {
                            'floorPrice': model_data['floorPrice'],
                            'howMany': model_data['howMany'],
                            'rarity': model_data.get('rarity', 0)
                        }
                        
                if models:
                    floor_data[gift_name]['models'] = models
        
        logger.info(f"Retrieved floor prices for {len(floor_data)} gifts")
        
        # Cache the result
        _floor_cache = floor_data
        _floor_cache_expiry = time.time() + CACHE_DURATION
        
        return floor_data
    except Exception as e:
        logger.error(f"Error getting all gift floors: {e}")
        return {} 