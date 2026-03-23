"""
TradingAgents Indian Markets - Main Entry Point

Usage:
    python main_india.py                           # Interactive mode
    python main_india.py --ticker TCS --date 2024-05-10  # Direct mode

Indian stocks are automatically formatted for NSE (.NS suffix).
For BSE stocks, use numeric codes like "500209.BO"

Example Indian tickers:
    NSE: RELIANCE, TCS, INFY, HDFCBANK, SBIN, etc.
    BSE: 500209 (for stocks with numeric BSE codes)

No additional API keys required - uses yfinance for all data.
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from cli.india_utils import format_indian_symbol, detect_exchange, validate_indian_symbol
from dotenv import load_dotenv
import sys

# Load environment variables from .env file
load_dotenv()


def get_india_config():
    """Get the default configuration for Indian markets."""
    config = DEFAULT_CONFIG.copy()
    # Use NSE data vendor for all data categories (yfinance with .NS/.BO suffix handling)
    config["data_vendors"] = {
        "core_stock_apis": "nse",
        "technical_indicators": "nse",
        "fundamental_data": "nse",
        "news_data": "nse",
    }
    return config


def run_analysis(
    ticker: str,
    trade_date: str,
    deep_think_llm: str = "gpt-5.2",
    quick_think_llm: str = "gpt-5-mini",
    max_debate_rounds: int = 1,
    selected_analysts: list = None,
    debug: bool = False,
    exchange: str = "NSE",
):
    """Run TradingAgents analysis for an Indian stock.

    Args:
        ticker: Indian stock symbol (e.g., "RELIANCE", "TCS", "500209")
        trade_date: Date to analyze in YYYY-MM-DD format
        deep_think_llm: Model for complex reasoning
        quick_think_llm: Model for quick tasks
        max_debate_rounds: Number of debate rounds
        selected_analysts: List of analysts to run
        debug: Enable debug mode with detailed tracing
        exchange: Preferred exchange ("NSE" or "BSE")

    Returns:
        Tuple of (final_state, decision)
    """
    # Validate and format the ticker
    is_valid, result = validate_indian_symbol(ticker)
    if not is_valid:
        print(f"Error: {result}")
        sys.exit(1)

    formatted_ticker = result
    detected_exchange = detect_exchange(formatted_ticker)

    print(f"\n{'='*60}")
    print(f"  TradingAgents - Indian Markets Edition")
    print(f"{'='*60}")
    print(f"  Ticker: {formatted_ticker}")
    print(f"  Exchange: {detected_exchange}")
    print(f"  Date: {trade_date}")
    print(f"  Deep Model: {deep_think_llm}")
    print(f"  Quick Model: {quick_think_llm}")
    print(f"{'='*60}\n")

    # Build config
    config = get_india_config()
    config["deep_think_llm"] = deep_think_llm
    config["quick_think_llm"] = quick_think_llm
    config["max_debate_rounds"] = max_debate_rounds

    if selected_analysts is None:
        selected_analysts = ["market", "social", "news", "fundamentals"]

    # Initialize TradingAgents
    ta = TradingAgentsGraph(
        debug=debug,
        config=config,
        selected_analysts=selected_analysts,
    )

    # Run analysis
    print(f"\nRunning analysis on {formatted_ticker} for {trade_date}...\n")
    _, decision = ta.propagate(formatted_ticker, trade_date)

    print(f"\n{'='*60}")
    print(f"  FINAL DECISION")
    print(f"{'='*60}")
    print(decision)
    print(f"{'='*60}\n")

    return ta


def main():
    """Main entry point with optional CLI arguments."""
    import argparse

    parser = argparse.ArgumentParser(
        description="TradingAgents for Indian Markets (NSE/BSE)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_india.py --ticker TCS --date 2024-05-10
  python main_india.py --ticker RELIANCE --date 2024-06-15 --debug
  python main_india.py --ticker 500209.BO --date 2024-03-20 --exchange BSE
  python main_india.py --ticker INFY --date 2024-04-01 --max-debate-rounds 2

Indian Ticker Formats:
  NSE stocks: RELIANCE, TCS, INFY (auto-appended with .NS)
  BSE stocks: 500209.BO (numeric BSE codes use .BO suffix)

Note: No additional API keys needed - uses yfinance for all data.
        """,
    )

    parser.add_argument(
        "--ticker",
        type=str,
        default=None,
        help="Indian stock ticker symbol (e.g., RELIANCE, TCS, 500209.BO)",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Trade date in YYYY-MM-DD format (e.g., 2024-05-10)",
    )
    parser.add_argument(
        "--deep-model",
        type=str,
        default="gpt-5.2",
        help="LLM model for deep reasoning (default: gpt-5.2)",
    )
    parser.add_argument(
        "--quick-model",
        type=str,
        default="gpt-5-mini",
        help="LLM model for quick tasks (default: gpt-5-mini)",
    )
    parser.add_argument(
        "--max-debate-rounds",
        type=int,
        default=1,
        help="Number of debate rounds (default: 1)",
    )
    parser.add_argument(
        "--exchange",
        type=str,
        default="NSE",
        choices=["NSE", "BSE"],
        help="Preferred exchange (default: NSE)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with detailed tracing",
    )
    parser.add_argument(
        "--analysts",
        type=str,
        nargs="+",
        default=None,
        help="Analysts to run (default: market social news fundamentals)",
    )

    args = parser.parse_args()

    # If no arguments provided, show help and example usage
    if len(sys.argv) == 1:
        print("\nTradingAgents - Indian Markets Edition")
        print("=" * 50)
        print("\nNo arguments provided. Showing example usage:")
        print("\nExample: Analyze TCS on NSE for May 10, 2024:")
        print("  python main_india.py --ticker TCS --date 2024-05-10")
        print("\nExample: Analyze BSE stock:")
        print("  python main_india.py --ticker 500209.BO --date 2024-03-20")
        print("\nExample: Debug mode with more debate rounds:")
        print("  python main_india.py --ticker RELIANCE --date 2024-06-15 --debug --max-debate-rounds 2")
        print("\nFor interactive mode, use the main CLI:")
        print("  tradingagents")
        print("  or")
        print("  python -m cli.main")
        print("\nFor help: python main_india.py --help")
        print()
        sys.exit(0)

    # Validate required arguments
    if not args.ticker:
        print("Error: --ticker is required")
        sys.exit(1)

    if not args.date:
        print("Error: --date is required (format: YYYY-MM-DD)")
        sys.exit(1)

    # Validate date format
    import datetime

    try:
        datetime.datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD format.")
        sys.exit(1)

    # Run the analysis
    run_analysis(
        ticker=args.ticker,
        trade_date=args.date,
        deep_think_llm=args.deep_model,
        quick_think_llm=args.quick_model,
        max_debate_rounds=args.max_debate_rounds,
        selected_analysts=args.analysts,
        debug=args.debug,
        exchange=args.exchange,
    )


if __name__ == "__main__":
    main()
