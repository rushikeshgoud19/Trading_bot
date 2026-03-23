"""CLI configuration for Indian markets (NSE/BSE)."""

CLI_CONFIG_INDIA = {
    # Announcements
    "announcements_url": "https://api.tauric.ai/v1/announcements",
    "announcements_timeout": 1.0,
    "announcements_fallback": "[cyan]For more information, please visit[/cyan] [link=https://github.com/TauricResearch]https://github.com/TauricResearch[/link]",
    # Indian market specific settings
    "market": "india",
    "default_exchange": "NSE",
    "supported_exchanges": ["NSE", "BSE"],
    # Example popular Indian tickers for quick selection
    "popular_tickers": [
        {"symbol": "RELIANCE", "name": "Reliance Industries", "exchange": "NSE"},
        {"symbol": "TCS", "name": "Tata Consultancy Services", "exchange": "NSE"},
        {"symbol": "HDFCBANK", "name": "HDFC Bank", "exchange": "NSE"},
        {"symbol": "INFY", "name": "Infosys", "exchange": "NSE"},
        {"symbol": "ICICIBANK", "name": "ICICI Bank", "exchange": "NSE"},
        {"symbol": "SBIN", "name": "State Bank of India", "exchange": "NSE"},
        {"symbol": "BHARTIARTL", "name": "Bharti Airtel", "exchange": "NSE"},
        {"symbol": "ITC", "name": "ITC Limited", "exchange": "NSE"},
        {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank", "exchange": "NSE"},
        {"symbol": "LT", "name": "Larsen & Toubro", "exchange": "NSE"},
        {"symbol": "HUL", "name": "Hindustan Unilever", "exchange": "NSE"},
        {"symbol": "ONGC", "name": "Oil & Natural Gas Corp", "exchange": "NSE"},
        {"symbol": "NTPC", "name": "NTPC Limited", "exchange": "NSE"},
        {"symbol": "POWERGRID", "name": "Power Grid Corporation", "exchange": "NSE"},
        {"symbol": "TATAMOTORS", "name": "Tata Motors", "exchange": "NSE"},
    ],
    # Nifty 50 index components (subset for quick selection)
    "nifty_50_tickers": [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
        "SBIN", "BHARTIARTL", "ITC", "KOTAKBANK", "LT",
        "HUL", "ONGC", "NTPC", "POWERGRID", "TATAMOTORS",
        "AXISBANK", "BAJFINANCE", "ASIANPAINT", "MARUTI", "SUNPHARMA",
        "ULTRATECHCEM", "TITAN", "NESTLE", "BAJAJFINSV", "WIPRO",
        "HCLTECH", "ADANIPORTS", "GRASIM", "INDUSINDBK", "JSWSTEEL",
        "TECHM", "M&M", "TATASTEEL", "CIPLA", "DRREDDY",
        "COALINDIA", "HEROMOTOCO", "BRITANNIA", "DIVISLAB", "SHREECEM",
        "ADANIENT", "BPCL", "EICHERMOT", "GRINDWELL", "HAVELLS",
        "INDIGO", "JUBLFOOD", "PIDILITIND", "SBILIFE", "SIEMENS",
    ],
}


def get_india_config():
    """Return the Indian market CLI configuration."""
    return CLI_CONFIG_INDIA
