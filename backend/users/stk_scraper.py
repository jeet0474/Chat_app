import requests
from bs4 import BeautifulSoup
import logging
import time
from typing import Dict, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# Multiple user agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
]

def create_session_with_retries(max_retries=3, backoff_factor=0.3):
    """
    Create a requests session with automatic retry logic.
    """
    session = requests.Session()
    
    retry_strategy = Retry(
        total=max_retries,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],  # Changed from method_whitelist
        backoff_factor=backoff_factor
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def safe_text(el):
    """Safely extract text from a BeautifulSoup element."""
    try:
        return el.get_text(strip=True) if el else None
    except Exception as e:
        logger.warning(f"Error extracting text from element: {e}")
        return None

def validate_stock_input(symbol: str, exchange: str) -> tuple:
    """
    Validate stock symbol and exchange input.
    Returns (is_valid, error_message)
    """
    if not symbol or not isinstance(symbol, str):
        return False, "Symbol is required and must be a string"
    
    if not exchange or not isinstance(exchange, str):
        return False, "Exchange is required and must be a string"
    
    # Basic validation - allow alphanumeric, hyphens, and dots
    if not all(c.isalnum() or c in '-.' for c in symbol):
        return False, "Symbol contains invalid characters"
    
    if not all(c.isalnum() or c in '-' for c in exchange):
        return False, "Exchange contains invalid characters"
    
    # Length validation
    if len(symbol) > 10 or len(exchange) > 10:
        return False, "Symbol and exchange must be less than 10 characters"
    
    return True, ""

def get_google_finance_price(symbol: str, exchange: str = "NSE", max_attempts: int = 3) -> Dict:
    """
    Fetch stock price data from Google Finance with robust error handling and retries.
    
    Args:
        symbol: Stock symbol (e.g., "HINDCOPPER")
        exchange: Exchange code (e.g., "NSE", "BSE")
        max_attempts: Maximum number of retry attempts
    
    Returns:
        Dictionary with stock data or error information
    """
    
    # Validate input
    is_valid, error_msg = validate_stock_input(symbol, exchange)
    if not is_valid:
        logger.error(f"Invalid input - Symbol: {symbol}, Exchange: {exchange}, Error: {error_msg}")
        return {"error": error_msg, "success": False}
    
    symbol = symbol.strip().upper()
    exchange = exchange.strip().upper()
    url = f"https://www.google.com/finance/quote/{symbol}:{exchange}"
    
    session = create_session_with_retries(max_retries=max_attempts-1)
    
    for attempt in range(max_attempts):
        try:
            # Rotate user agent
            user_agent = USER_AGENTS[attempt % len(USER_AGENTS)]
            headers = {
                "User-Agent": user_agent,
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": "https://www.google.com/",
            }
            
            logger.info(f"Attempt {attempt + 1}/{max_attempts} - Fetching {symbol}:{exchange}")
            
            response = session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            data = {
                "success": True,
                "symbol": f"{exchange}:{symbol}",
                "name": None,
                "price": None,
                "change": None,
                "percent": None,
                "time": None,
                "timestamp": int(time.time()),
            }
            
            # Company name - try multiple selectors
            name_element = (
                soup.select_one("div.zzDege") or 
                soup.select_one("h1") or
                soup.select_one("div[data-symbol]")
            )
            data["name"] = safe_text(name_element)
            
            # Price - try multiple selectors
            price_element = (
                soup.select_one("div.YMlKec.fxKbKc") or
                soup.select_one("div[data-value]") or
                soup.select_one("span[jsname='qyyzf']")
            )
            data["price"] = safe_text(price_element)
            
            # Change and percentage - more robust approach
            change_spans = soup.select("span.JwB6zf, span.P2Luy")
            
            if len(change_spans) >= 2:
                data["change"] = safe_text(change_spans[0])
                data["percent"] = safe_text(change_spans[1])
            else:
                # Try alternative selectors
                change_alt = soup.select("span[role='text']")
                if len(change_alt) >= 2:
                    data["change"] = safe_text(change_alt[-2])
                    data["percent"] = safe_text(change_alt[-1])
            
            # Market time
            time_element = soup.select_one("div.ygUjEc")
            data["time"] = safe_text(time_element)
            
            # Validate that we got at least the price
            if data["price"] is None:
                if attempt < max_attempts - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Price not found, retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Failed to fetch price for {symbol}:{exchange} after {max_attempts} attempts")
                    return {
                        "error": f"Unable to fetch price data for {symbol}:{exchange}",
                        "success": False,
                        "symbol": f"{exchange}:{symbol}"
                    }
            
            logger.info(f"Successfully fetched data for {symbol}:{exchange}")
            session.close()
            return data
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt + 1}/{max_attempts} for {symbol}:{exchange}")
            if attempt < max_attempts - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                return {
                    "error": f"Request timeout after {max_attempts} attempts for {symbol}:{exchange}",
                    "success": False,
                    "symbol": f"{exchange}:{symbol}"
                }
        
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            logger.warning(f"HTTP {status_code} on attempt {attempt + 1}/{max_attempts} for {symbol}:{exchange}")
            
            # Don't retry on 404 or 400
            if status_code in [400, 404]:
                return {
                    "error": f"Stock {symbol}:{exchange} not found (HTTP {status_code})",
                    "success": False,
                    "symbol": f"{exchange}:{symbol}"
                }
            
            if attempt < max_attempts - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                return {
                    "error": f"HTTP error {status_code} for {symbol}:{exchange}",
                    "success": False,
                    "symbol": f"{exchange}:{symbol}"
                }
        
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Connection error on attempt {attempt + 1}/{max_attempts}: {e}")
            if attempt < max_attempts - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                return {
                    "error": f"Connection error after {max_attempts} attempts",
                    "success": False,
                    "symbol": f"{exchange}:{symbol}"
                }
        
        except Exception as e:
            logger.error(f"Unexpected error on attempt {attempt + 1}/{max_attempts}: {type(e).__name__}: {e}")
            if attempt < max_attempts - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                return {
                    "error": f"Unexpected error: {type(e).__name__}",
                    "success": False,
                    "symbol": f"{exchange}:{symbol}"
                }
    
    session.close()
    return {
        "error": "Failed to fetch stock data",
        "success": False,
        "symbol": f"{exchange}:{symbol}"
    }