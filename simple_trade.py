"""
Simple Trading Bot - Gives clear BUY/SELL/HOLD advice
"""
import os
from dotenv import load_dotenv
import yfinance as yf
from datetime import datetime, timedelta

load_dotenv()

def get_simple_advice(ticker: str) -> dict:
    """Get simple trading advice without all the complexity."""

    print(f"Checking {ticker}...")

    stock = yf.Ticker(ticker)
    info = stock.info

    # Get recent price data
    hist = stock.history(period="3mo")
    current_price = info.get('currentPrice') or info.get('regularMarketPrice')
    fifty_avg = hist['Close'].rolling(50).mean().iloc[-1]
    two_hund_avg = hist['Close'].rolling(200).mean().iloc[-1]

    # Simple indicators
    price_change_1d = info.get('regularMarketChange', 0)
    volume = info.get('averageVolume', 0)

    # RSI calculation
    delta = hist['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
    rs = gain / loss if loss != 0 else 100
    rsi = 100 - (100 / (1 + rs))

    # Simple Moving Average Trend
    sma_trend = "UP" if current_price > fifty_avg else "DOWN"
    long_trend = "UP" if fifty_avg > two_hund_avg else "DOWN"

    # Score calculation
    score = 0
    if current_price > fifty_avg: score += 1
    if fifty_avg > two_hund_avg: score += 1
    if rsi < 70: score += 1  # Not overbought
    if price_change_1d > 0: score += 1
    if long_trend == "UP": score += 1

    # Determine action
    if score >= 4:
        action = "BUY"
    elif score <= 2:
        action = "SELL"
    else:
        action = "HOLD"

    return {
        "ticker": ticker,
        "action": action,
        "price": current_price,
        "rsi": round(rsi, 1),
        "sma_trend": sma_trend,
        "long_trend": long_trend,
        "day_change": round(price_change_1d, 2),
        "volume": volume,
        "score": score
    }

if __name__ == "__main__":
    import sys

    ticker = sys.argv[1].upper() if len(sys.argv) > 1 else "NVDA"

    print(f"\n{'='*50}")
    print(f"  SIMPLE TRADING BOT - {datetime.now().strftime('%Y-%m-%d')}")
    print(f"{'='*50}\n")

    result = get_simple_advice(ticker)

    print(f"Stock: {result['ticker']}")
    print(f"Current Price: ${result['price']:.2f}")
    print(f"Day Change: {result['day_change']}%")
    print(f"RSI (14): {result['rsi']}")
    print(f"50-Day SMA Trend: {result['sma_trend']}")
    print(f"200-Day SMA Trend: {result['long_trend']}")
    print(f"\n{'='*50}")
    print(f"  RECOMMENDATION: {result['action']}")
    print(f"{'='*50}\n")

    if result['action'] == "BUY":
        print("Reasons: Price above moving averages, not overbought, positive momentum")
    elif result['action'] == "SELL":
        print("Reasons: Price below moving averages, overbought, negative momentum")
    else:
        print("Reasons: Mixed signals - wait for clearer trend")
