#!/usr/bin/env python3
"""
API Monitor for Admin Dashboard

This script monitors API fetches and logs them for the admin dashboard.
"""

import time
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def monitor_gift_api_fetch():
    """Monitor gift API fetch and log it."""
    try:
        from admin_dashboard import log_api_fetch
        start_time = time.time()
        
        # Simulate API fetch (replace with actual API call)
        # import new_card_design
        # new_card_design.fetch_all_gift_data()
        
        response_time = time.time() - start_time
        log_api_fetch("gifts", "success", response_time)
        logger.info(f"Gift API fetch logged - Response time: {response_time:.2f}s")
        
    except Exception as e:
        logger.error(f"Error monitoring gift API fetch: {e}")
        try:
            from admin_dashboard import log_api_fetch
            log_api_fetch("gifts", "failed", None)
        except:
            pass

def monitor_sticker_api_fetch():
    """Monitor sticker API fetch and log it."""
    try:
        from admin_dashboard import log_api_fetch
        start_time = time.time()
        
        # Simulate API fetch (replace with actual API call)
        # import place_market_integration
        # place_market_integration.fetch_sticker_data()
        
        response_time = time.time() - start_time
        log_api_fetch("stickers", "success", response_time)
        logger.info(f"Sticker API fetch logged - Response time: {response_time:.2f}s")
        
    except Exception as e:
        logger.error(f"Error monitoring sticker API fetch: {e}")
        try:
            from admin_dashboard import log_api_fetch
            log_api_fetch("stickers", "failed", None)
        except:
            pass

# Function to be called from other modules
def log_gift_api_call(response_time=None, status="success"):
    """Log gift API call from external modules."""
    try:
        from admin_dashboard import log_api_fetch
        log_api_fetch("gifts", status, response_time)
    except ImportError:
        logger.warning("Admin dashboard not available for API logging")

def log_sticker_api_call(response_time=None, status="success"):
    """Log sticker API call from external modules."""
    try:
        from admin_dashboard import log_api_fetch
        log_api_fetch("stickers", status, response_time)
    except ImportError:
        logger.warning("Admin dashboard not available for API logging") 