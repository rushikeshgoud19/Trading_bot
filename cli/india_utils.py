"""CLI utilities for Indian markets (NSE/BSE)."""

from typing import Tuple, Optional


def format_indian_symbol(symbol: str, exchange: str = "NSE") -> str:
    """Format an Indian stock symbol for yfinance.

    Args:
        symbol: Stock symbol (e.g., "RELIANCE", "500209")
        exchange: Exchange - "NSE" or "BSE"

    Returns:
        yfinance-compatible symbol (e.g., "RELIANCE.NS", "500209.BO")
    """
    symbol = symbol.upper().strip()

    # Already has exchange suffix
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        return symbol

    if exchange.upper() == "BSE":
        # BSE codes are numeric (e.g., "500209")
        return f"{symbol}.BO"
    else:
        # NSE codes are alphabetic (e.g., "RELIANCE")
        return f"{symbol}.NS"


def detect_exchange(symbol: str) -> str:
    """Detect the exchange from a symbol.

    Args:
        symbol: Stock symbol

    Returns:
        "NSE", "BSE", or "UNKNOWN"
    """
    symbol = symbol.upper()
    if symbol.endswith(".NS"):
        return "NSE"
    elif symbol.endswith(".BO"):
        return "BSE"
    return "NSE"  # Default to NSE


def validate_indian_symbol(symbol: str) -> Tuple[bool, str]:
    """Validate if a symbol appears to be a valid Indian stock symbol.

    Args:
        symbol: Stock symbol to validate

    Returns:
        Tuple of (is_valid, formatted_symbol_or_error)
    """
    symbol = symbol.strip()

    if not symbol:
        return False, "Symbol cannot be empty"

    # Check if it has exchange suffix
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        return True, symbol.upper()

    # Validate NSE symbol format (typically 3-10 uppercase letters)
    if symbol.isalpha() and 2 <= len(symbol) <= 15:
        return True, f"{symbol.upper()}.NS"

    # Validate BSE symbol format (typically numeric, 3-6 digits)
    if symbol.isdigit() and 3 <= len(symbol) <= 10:
        return True, f"{symbol.upper()}.BO"

    return False, (
        f"Invalid symbol format: '{symbol}'. "
        "Use NSE symbol (e.g., 'RELIANCE' -> 'RELIANCE.NS') "
        "or BSE code (e.g., '500209' -> '500209.BO')"
    )


def get_symbol_display_name(symbol: str, name: Optional[str] = None) -> str:
    """Get display name for a symbol.

    Args:
        symbol: Stock symbol
        name: Optional company name

    Returns:
        Display string like "RELIANCE (NSE)" or "RELIANCE - Reliance Industries (NSE)"
    """
    exchange = detect_exchange(symbol)
    if name:
        return f"{symbol.upper()} - {name} ({exchange})"
    return f"{symbol.upper()} ({exchange})"


# Indian market info
INDIAN_MARKET_INFO = {
    "NSE": {
        "name": "National Stock Exchange of India",
        "suffix": ".NS",
        "trading_hours": "9:15 AM - 3:30 PM IST",
        "timezone": "Asia/Kolkata",
    },
    "BSE": {
        "name": "Bombay Stock Exchange",
        "suffix": ".BO",
        "trading_hours": "9:15 AM - 3:30 PM IST",
        "timezone": "Asia/Kolkata",
    },
}


def get_market_info(exchange: str = "NSE") -> dict:
    """Get information about an Indian exchange.

    Args:
        exchange: Exchange name ("NSE" or "BSE")

    Returns:
        Dictionary with exchange info
    """
    return INDIAN_MARKET_INFO.get(exchange.upper(), INDIAN_MARKET_INFO["NSE"])
