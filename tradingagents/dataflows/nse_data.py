"""Indian market (NSE/BSE) data fetching functions using yfinance.

This module provides data retrieval for Indian stocks listed on NSE (.NS suffix)
and BSE (.BO suffix). yfinance provides native support for these exchanges.
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
from typing import Annotated
from .stockstats_utils import StockstatsUtils, _clean_dataframe, yf_retry


# Mapping of common Indian stock symbols to their yfinance format
# For most NSE stocks, yfinance auto-appends .NS; for BSE, use .BO
# Users can pass either "RELIANCE" or "RELIANCE.NS" - this module handles both


def _format_indian_symbol(symbol: str) -> str:
    """Format an Indian stock symbol for yfinance.

    Handles various input formats:
    - "RELIANCE" -> "RELIANCE.NS" (NSE, default)
    - "RELIANCE.NS" -> "RELIANCE.NS"
    - "RELIANCE.BO" -> "RELIANCE.BO"
    - "500209.BO" -> "500209.BO" (BSE codes work as-is)
    """
    symbol = symbol.upper().strip()

    # Already has exchange suffix
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        return symbol

    # Assume NSE if just a symbol provided (most common for Indian stocks)
    # BSE codes are numeric (e.g., "500209")
    if symbol.isdigit():
        return f"{symbol}.BO"
    else:
        return f"{symbol}.NS"


def _detect_exchange(symbol: str) -> str:
    """Detect the exchange from a symbol."""
    symbol = symbol.upper()
    if symbol.endswith(".NS"):
        return "NSE"
    elif symbol.endswith(".BO"):
        return "BSE"
    return "NSE"  # Default assumption


def get_NSE_data_online(
    symbol: Annotated[str, "Indian stock ticker symbol (e.g., RELIANCE, RELIANCE.NS, 500209.BO)"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
):
    """Fetch OHLCV stock price data for Indian stocks (NSE/BSE).

    Args:
        symbol: Indian stock ticker. Examples: "RELIANCE", "RELIANCE.NS", "TCS.NS", "500209.BO"
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format

    Returns:
        CSV string with stock price data or error message
    """
    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")

    # Format symbol for yfinance
    yf_symbol = _format_indian_symbol(symbol)
    exchange = _detect_exchange(yf_symbol)

    # Create ticker object
    ticker = yf.Ticker(yf_symbol)

    # Fetch historical data for the specified date range
    data = yf_retry(lambda: ticker.history(start=start_date, end=end_date))

    # Check if data is empty
    if data.empty:
        return (
            f"No data found for symbol '{symbol}' ({exchange}) between {start_date} and {end_date}. "
            f"Please verify the ticker symbol is correct for Indian markets."
        )

    # Remove timezone info from index for cleaner output
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    # Round numerical values to 2 decimal places for cleaner display
    numeric_columns = ["Open", "High", "Low", "Close", "Adj Close"]
    for col in numeric_columns:
        if col in data.columns:
            data[col] = data[col].round(2)

    # Convert DataFrame to CSV string
    csv_string = data.to_csv()

    # Add header information
    header = (
        f"# Stock data for {symbol.upper()} ({exchange}) from {start_date} to {end_date}\n"
        f"# Formatted as: {yf_symbol}\n"
        f"# Total records: {len(data)}\n"
        f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    )

    return header + csv_string


def get_NSE_indicators(
    symbol: Annotated[str, "Indian stock ticker symbol"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    """Get technical indicators for Indian stocks.

    Args:
        symbol: Indian stock ticker (e.g., "RELIANCE", "RELIANCE.NS")
        indicator: Technical indicator name (e.g., "rsi", "macd", "close_50_sma")
        curr_date: Current trading date in YYYY-mm-dd format
        look_back_days: Number of days to look back for indicator calculation

    Returns:
        Formatted string with indicator values over the look-back period
    """
    best_ind_params = {
        # Moving Averages
        "close_50_sma": (
            "50 SMA: A medium-term trend indicator. "
            "Usage: Identify trend direction and serve as dynamic support/resistance. "
            "Tips: It lags price; combine with faster indicators for timely signals."
        ),
        "close_200_sma": (
            "200 SMA: A long-term trend benchmark. "
            "Usage: Confirm overall market trend and identify golden/death cross setups. "
            "Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries."
        ),
        "close_10_ema": (
            "10 EMA: A responsive short-term average. "
            "Usage: Capture quick shifts in momentum and potential entry points. "
            "Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals."
        ),
        # MACD Related
        "macd": (
            "MACD: Computes momentum via differences of EMAs. "
            "Usage: Look for crossovers and divergence as signals of trend changes. "
            "Tips: Confirm with other indicators in low-volatility or sideways markets."
        ),
        "macds": (
            "MACD Signal: An EMA smoothing of the MACD line. "
            "Usage: Use crossovers with the MACD line to trigger trades. "
            "Tips: Should be part of a broader strategy to avoid false positives."
        ),
        "macdh": (
            "MACD Histogram: Shows the gap between the MACD line and its signal. "
            "Usage: Visualize momentum strength and spot divergence early. "
            "Tips: Can be volatile; complement with additional filters in fast-moving markets."
        ),
        # Momentum Indicators
        "rsi": (
            "RSI: Measures momentum to flag overbought/oversold conditions. "
            "Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. "
            "Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis."
        ),
        # Volatility Indicators
        "boll": (
            "Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. "
            "Usage: Acts as a dynamic benchmark for price movement. "
            "Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals."
        ),
        "boll_ub": (
            "Bollinger Upper Band: Typically 2 standard deviations above the middle line. "
            "Usage: Signals potential overbought conditions and breakout zones. "
            "Tips: Confirm signals with other tools; prices may ride the band in strong trends."
        ),
        "boll_lb": (
            "Bollinger Lower Band: Typically 2 standard deviations below the middle line. "
            "Usage: Indicates potential oversold conditions. "
            "Tips: Use additional analysis to avoid false reversal signals."
        ),
        "atr": (
            "ATR: Averages true range to measure volatility. "
            "Usage: Set stop-loss levels and adjust position sizes based on current market volatility. "
            "Tips: It's a reactive measure, so use it as part of a broader risk management strategy."
        ),
        # Volume-Based Indicators
        "vwma": (
            "VWMA: A moving average weighted by volume. "
            "Usage: Confirm trends by integrating price action with volume data. "
            "Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses."
        ),
        "mfi": (
            "MFI: The Money Flow Index is a momentum indicator that uses both price and volume to measure buying and selling pressure. "
            "Usage: Identify overbought (>80) or oversold (<20) conditions and confirm the strength of trends or reversals. "
            "Tips: Use alongside RSI or MACD to confirm signals; divergence between price and MFI can indicate potential reversals."
        ),
    }

    if indicator not in best_ind_params:
        raise ValueError(
            f"Indicator {indicator} is not supported. Please choose from: {list(best_ind_params.keys())}"
        )

    end_date = curr_date
    curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    before = curr_date_dt - relativedelta(days=look_back_days)

    yf_symbol = _format_indian_symbol(symbol)

    # Optimized: Get stock data once and calculate indicators for all dates
    try:
        indicator_data = _get_nse_stockstats_bulk(yf_symbol, indicator, curr_date)

        # Generate the date range we need
        current_dt = curr_date_dt
        date_values = []

        while current_dt >= before:
            date_str = current_dt.strftime('%Y-%m-%d')

            # Look up the indicator value for this date
            if date_str in indicator_data:
                indicator_value = indicator_data[date_str]
            else:
                indicator_value = "N/A: Not a trading day (weekend or holiday)"

            date_values.append((date_str, indicator_value))
            current_dt = current_dt - relativedelta(days=1)

        # Build the result string
        ind_string = ""
        for date_str, value in date_values:
            ind_string += f"{date_str}: {value}\n"

    except Exception as e:
        print(f"Error getting bulk stockstats data: {e}")
        # Fallback to original implementation if bulk method fails
        ind_string = ""
        curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        while curr_date_dt >= before:
            indicator_value = _get_nse_stockstats_indicator(
                yf_symbol, indicator, curr_date_dt.strftime("%Y-%m-%d")
            )
            ind_string += f"{curr_date_dt.strftime('%Y-%m-%d')}: {indicator_value}\n"
            curr_date_dt = curr_date_dt - relativedelta(days=1)

    result_str = (
        f"## {indicator} values for {symbol.upper()} from {before.strftime('%Y-%m-%d')} to {end_date}:\n\n"
        + ind_string
        + "\n\n"
        + best_ind_params.get(indicator, "No description available.")
    )

    return result_str


def _get_nse_stockstats_bulk(
    symbol: Annotated[str, "yfinance-formatted symbol"],
    indicator: Annotated[str, "technical indicator to calculate"],
    curr_date: Annotated[str, "current date for reference"]
) -> dict:
    """Bulk calculation of stockstats indicators for Indian stocks."""
    from .config import get_config
    import pandas as pd
    from stockstats import wrap

    config = get_config()
    online = config["data_vendors"]["technical_indicators"] != "local"

    if not online:
        raise Exception("Local data not supported for Indian market in this implementation")

    today_date = pd.Timestamp.today()
    curr_date_dt = pd.to_datetime(curr_date)

    end_date = today_date
    start_date = today_date - pd.DateOffset(years=15)
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    data_file = f"{symbol}-NSE-data-{start_date_str}-{end_date_str}.csv"
    data_file = data_file.replace(":", "-").replace("+", "-")
    data_file = f"dataflows/data_cache/{data_file}"

    import os
    os.makedirs(config["data_cache_dir"], exist_ok=True)
    data_file = os.path.join(os.path.dirname(__file__), "..", "..", data_file)
    data_file = os.path.normpath(data_file)

    if os.path.exists(data_file):
        data = pd.read_csv(data_file, on_bad_lines="skip")
    else:
        data = yf_retry(lambda: yf.download(
            symbol,
            start=start_date_str,
            end=end_date_str,
            multi_level_index=False,
            progress=False,
            auto_adjust=True,
        ))
        data = data.reset_index()
        data.to_csv(data_file, index=False)

    data = _clean_dataframe(data)
    df = wrap(data)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    # Calculate the indicator for all rows at once
    df[indicator]

    # Create a dictionary mapping date strings to indicator values
    result_dict = {}
    for _, row in df.iterrows():
        date_str = row["Date"]
        indicator_value = row[indicator]

        # Handle NaN/None values
        if pd.isna(indicator_value):
            result_dict[date_str] = "N/A"
        else:
            result_dict[date_str] = str(indicator_value)

    return result_dict


def _get_nse_stockstats_indicator(
    symbol: Annotated[str, "yfinance-formatted symbol"],
    indicator: Annotated[str, "technical indicator to get"],
    curr_date: Annotated[str, "The current trading date"],
) -> str:
    """Get a single indicator value for Indian stock."""
    curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    curr_date_str = curr_date_dt.strftime("%Y-%m-%d")

    try:
        indicator_value = StockstatsUtils.get_stock_stats(
            symbol,
            indicator,
            curr_date_str,
        )
    except Exception as e:
        print(
            f"Error getting stockstats indicator data for indicator {indicator} on {curr_date}: {e}"
        )
        return ""

    return str(indicator_value)


def get_NSE_fundamentals(
    ticker: Annotated[str, "Indian stock ticker symbol"],
    curr_date: Annotated[str, "current date (not used)"] = None
):
    """Get company fundamentals overview for Indian stocks from yfinance.

    Args:
        ticker: Indian stock ticker (e.g., "RELIANCE", "RELIANCE.NS", "TCS")
        curr_date: Current date (not used, yfinance provides latest data)

    Returns:
        Formatted string with company fundamentals
    """
    yf_symbol = _format_indian_symbol(ticker)
    exchange = _detect_exchange(yf_symbol)

    try:
        ticker_obj = yf.Ticker(yf_symbol)
        info = yf_retry(lambda: ticker_obj.info)

        if not info:
            return f"No fundamentals data found for symbol '{ticker}' ({exchange})"

        fields = [
            ("Name", info.get("longName")),
            ("Exchange", exchange),
            ("Sector", info.get("sector")),
            ("Industry", info.get("industry")),
            ("Market Cap", info.get("marketCap")),
            ("PE Ratio (TTM)", info.get("trailingPE")),
            ("Forward PE", info.get("forwardPE")),
            ("PEG Ratio", info.get("pegRatio")),
            ("Price to Book", info.get("priceToBook")),
            ("EPS (TTM)", info.get("trailingEps")),
            ("Forward EPS", info.get("forwardEps")),
            ("Dividend Yield", info.get("dividendYield")),
            ("Beta", info.get("beta")),
            ("52 Week High", info.get("fiftyTwoWeekHigh")),
            ("52 Week Low", info.get("fiftyTwoWeekLow")),
            ("50 Day Average", info.get("fiftyDayAverage")),
            ("200 Day Average", info.get("twoHundredDayAverage")),
            ("Revenue (TTM)", info.get("totalRevenue")),
            ("Gross Profit", info.get("grossProfits")),
            ("EBITDA", info.get("ebitda")),
            ("Net Income", info.get("netIncomeToCommon")),
            ("Profit Margin", info.get("profitMargins")),
            ("Operating Margin", info.get("operatingMargins")),
            ("Return on Equity", info.get("returnOnEquity")),
            ("Return on Assets", info.get("returnOnAssets")),
            ("Debt to Equity", info.get("debtToEquity")),
            ("Current Ratio", info.get("currentRatio")),
            ("Book Value", info.get("bookValue")),
            ("Free Cash Flow", info.get("freeCashflow")),
        ]

        lines = []
        for label, value in fields:
            if value is not None:
                lines.append(f"{label}: {value}")

        header = (
            f"# Company Fundamentals for {ticker.upper()} ({exchange})\n"
            f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        return header + "\n".join(lines)

    except Exception as e:
        return f"Error retrieving fundamentals for {ticker} ({exchange}): {str(e)}"


def get_NSE_balance_sheet(
    ticker: Annotated[str, "Indian stock ticker symbol"],
    freq: Annotated[str, "frequency of data: 'annual' or 'quarterly'"] = "quarterly",
    curr_date: Annotated[str, "current date (not used)"] = None
):
    """Get balance sheet data for Indian stocks."""
    yf_symbol = _format_indian_symbol(ticker)
    exchange = _detect_exchange(yf_symbol)

    try:
        ticker_obj = yf.Ticker(yf_symbol)

        if freq.lower() == "quarterly":
            data = yf_retry(lambda: ticker_obj.quarterly_balance_sheet)
        else:
            data = yf_retry(lambda: ticker_obj.balance_sheet)

        if data.empty:
            return f"No balance sheet data found for symbol '{ticker}' ({exchange})"

        csv_string = data.to_csv()

        header = (
            f"# Balance Sheet data for {ticker.upper()} ({exchange}, {freq})\n"
            f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        return header + csv_string

    except Exception as e:
        return f"Error retrieving balance sheet for {ticker} ({exchange}): {str(e)}"


def get_NSE_cashflow(
    ticker: Annotated[str, "Indian stock ticker symbol"],
    freq: Annotated[str, "frequency of data: 'annual' or 'quarterly'"] = "quarterly",
    curr_date: Annotated[str, "current date (not used)"] = None
):
    """Get cash flow data for Indian stocks."""
    yf_symbol = _format_indian_symbol(ticker)
    exchange = _detect_exchange(yf_symbol)

    try:
        ticker_obj = yf.Ticker(yf_symbol)

        if freq.lower() == "quarterly":
            data = yf_retry(lambda: ticker_obj.quarterly_cashflow)
        else:
            data = yf_retry(lambda: ticker_obj.cashflow)

        if data.empty:
            return f"No cash flow data found for symbol '{ticker}' ({exchange})"

        csv_string = data.to_csv()

        header = (
            f"# Cash Flow data for {ticker.upper()} ({exchange}, {freq})\n"
            f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        return header + csv_string

    except Exception as e:
        return f"Error retrieving cash flow for {ticker} ({exchange}): {str(e)}"


def get_NSE_income_statement(
    ticker: Annotated[str, "Indian stock ticker symbol"],
    freq: Annotated[str, "frequency of data: 'annual' or 'quarterly'"] = "quarterly",
    curr_date: Annotated[str, "current date (not used)"] = None
):
    """Get income statement data for Indian stocks."""
    yf_symbol = _format_indian_symbol(ticker)
    exchange = _detect_exchange(yf_symbol)

    try:
        ticker_obj = yf.Ticker(yf_symbol)

        if freq.lower() == "quarterly":
            data = yf_retry(lambda: ticker_obj.quarterly_income_stmt)
        else:
            data = yf_retry(lambda: ticker_obj.income_stmt)

        if data.empty:
            return f"No income statement data found for symbol '{ticker}' ({exchange})"

        csv_string = data.to_csv()

        header = (
            f"# Income Statement data for {ticker.upper()} ({exchange}, {freq})\n"
            f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        return header + csv_string

    except Exception as e:
        return f"Error retrieving income statement for {ticker} ({exchange}): {str(e)}"


def get_NSE_insider_transactions(
    ticker: Annotated[str, "Indian stock ticker symbol"]
):
    """Get insider transactions data for Indian stocks."""
    yf_symbol = _format_indian_symbol(ticker)
    exchange = _detect_exchange(yf_symbol)

    try:
        ticker_obj = yf.Ticker(yf_symbol)
        data = yf_retry(lambda: ticker_obj.insider_transactions)

        if data is None or data.empty:
            return f"No insider transactions data found for symbol '{ticker}' ({exchange})"

        csv_string = data.to_csv()

        header = (
            f"# Insider Transactions data for {ticker.upper()} ({exchange})\n"
            f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        return header + csv_string

    except Exception as e:
        return f"Error retrieving insider transactions for {ticker} ({exchange}): {str(e)}"


def get_NSE_news(
    ticker: Annotated[str, "Indian stock ticker symbol"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    """Retrieve news for a specific Indian stock ticker using yfinance.

    Args:
        ticker: Stock ticker symbol (e.g., "RELIANCE", "RELIANCE.NS")
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format

    Returns:
        Formatted string containing news articles
    """
    yf_symbol = _format_indian_symbol(ticker)
    exchange = _detect_exchange(yf_symbol)

    try:
        stock = yf.Ticker(yf_symbol)
        news = stock.get_news(count=20)

        if not news:
            return f"No news found for {ticker} ({exchange})"

        # Parse date range for filtering
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        news_str = ""
        filtered_count = 0

        for article in news:
            # Handle nested content structure
            if "content" in article:
                content = article["content"]
                title = content.get("title", "No title")
                summary = content.get("summary", "")
                provider = content.get("provider", {})
                publisher = provider.get("displayName", "Unknown")
                url_obj = content.get("canonicalUrl") or content.get("clickThroughUrl") or {}
                link = url_obj.get("url", "")
                pub_date_str = content.get("pubDate", "")
                pub_date = None
                if pub_date_str:
                    try:
                        pub_date = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
                    except (ValueError, AttributeError):
                        pass
            else:
                title = article.get("title", "No title")
                summary = article.get("summary", "")
                publisher = article.get("publisher", "Unknown")
                link = article.get("link", "")
                pub_date = None

            # Filter by date if publish time is available
            if pub_date:
                pub_date_naive = pub_date.replace(tzinfo=None)
                if not (start_dt <= pub_date_naive <= end_dt + relativedelta(days=1)):
                    continue

            news_str += f"### {title} (source: {publisher})\n"
            if summary:
                news_str += f"{summary}\n"
            if link:
                news_str += f"Link: {link}\n"
            news_str += "\n"
            filtered_count += 1

        if filtered_count == 0:
            return f"No news found for {ticker} ({exchange}) between {start_date} and {end_date}"

        return f"## {ticker.upper()} ({exchange}) News, from {start_date} to {end_date}:\n\n{news_str}"

    except Exception as e:
        return f"Error fetching news for {ticker} ({exchange}): {str(e)}"


def get_NSE_global_news(
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "Number of days to look back"] = 7,
    limit: Annotated[int, "Maximum number of articles to return"] = 10,
) -> str:
    """Retrieve Indian and global market news relevant to Indian investors.

    Args:
        curr_date: Current date in yyyy-mm-dd format
        look_back_days: Number of days to look back
        limit: Maximum number of articles to return

    Returns:
        Formatted string containing global/Indian market news
    """
    # Search queries for Indian and global market news
    search_queries = [
        "NSE India stock market",
        "BSE Sensex India",
        "RBI interest rate India economy",
        "Indian rupee INR forex",
        "India inflation economy",
        "FII DII Indian markets",
        "global stock markets",
    ]

    all_news = []
    seen_titles = set()

    try:
        for query in search_queries:
            search = yf.Search(
                query=query,
                news_count=limit,
                enable_fuzzy_query=True,
            )

            if search.news:
                for article in search.news:
                    if "content" in article:
                        title = article["content"].get("title", "")
                    else:
                        title = article.get("title", "")

                    if title and title not in seen_titles:
                        seen_titles.add(title)
                        all_news.append(article)

            if len(all_news) >= limit:
                break

        if not all_news:
            return f"No global/Indian market news found for {curr_date}"

        curr_dt = datetime.strptime(curr_date, "%Y-%m-%d")
        start_dt = curr_dt - relativedelta(days=look_back_days)
        start_date = start_dt.strftime("%Y-%m-%d")

        news_str = ""
        for article in all_news[:limit]:
            if "content" in article:
                content = article["content"]
                title = content.get("title", "No title")
                publisher = content.get("provider", {}).get("displayName", "Unknown")
                link = (content.get("canonicalUrl") or content.get("clickThroughUrl") or {}).get("url", "")
                summary = content.get("summary", "")
            else:
                title = article.get("title", "No title")
                publisher = article.get("publisher", "Unknown")
                link = article.get("link", "")
                summary = ""

            news_str += f"### {title} (source: {publisher})\n"
            if summary:
                news_str += f"{summary}\n"
            if link:
                news_str += f"Link: {link}\n"
            news_str += "\n"

        return f"## Indian & Global Market News, from {start_date} to {curr_date}:\n\n{news_str}"

    except Exception as e:
        return f"Error fetching Indian/global news: {str(e)}"
