"""Install and test script for TradingAgents Indian Markets."""
import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Installing TradingAgents package...")
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "-e", "."],
    capture_output=True,
    text=True,
    timeout=300
)
print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
if result.returncode != 0:
    print("STDERR:", result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
    print(f"Install failed with code: {result.returncode}")
else:
    print("Install succeeded!")

    print("\n\nTesting imports...")

    # Test 1: Import the nse_data module
    print("\n[Test 1] Importing nse_data module...")
    try:
        from tradingagents.dataflows.nse_data import (
            _format_indian_symbol,
            _detect_exchange,
            get_NSE_data_online,
            get_NSE_fundamentals,
            get_NSE_indicators,
            get_NSE_news,
        )
        print("  PASS: nse_data imports OK")
    except Exception as e:
        print(f"  FAIL: {e}")

    # Test 2: Test symbol formatting
    print("\n[Test 2] Testing Indian symbol formatting...")
    try:
        assert _format_indian_symbol("RELIANCE") == "RELIANCE.NS"
        assert _format_indian_symbol("RELIANCE.NS") == "RELIANCE.NS"
        assert _format_indian_symbol("500209.BO") == "500209.BO"
        assert _detect_exchange("RELIANCE.NS") == "NSE"
        assert _detect_exchange("500209.BO") == "BSE"
        print("  PASS: Symbol formatting OK")
    except Exception as e:
        print(f"  FAIL: {e}")

    # Test 3: Import interface
    print("\n[Test 3] Importing dataflows interface...")
    try:
        from tradingagents.dataflows.interface import VENDOR_LIST, VENDOR_METHODS
        assert "nse" in VENDOR_LIST
        assert "get_stock_data" in VENDOR_METHODS
        assert "nse" in VENDOR_METHODS["get_stock_data"]
        print("  PASS: Interface includes NSE vendor")
    except Exception as e:
        print(f"  FAIL: {e}")

    # Test 4: Import CLI India config
    print("\n[Test 4] Importing CLI India config...")
    try:
        from cli.india_config import get_india_config, CLI_CONFIG_INDIA
        cfg = get_india_config()
        assert cfg["market"] == "india"
        assert "popular_tickers" in cfg
        print("  PASS: CLI India config OK")
    except Exception as e:
        print(f"  FAIL: {e}")

    # Test 5: Import CLI India utils
    print("\n[Test 5] Importing CLI India utils...")
    try:
        from cli.india_utils import (
            format_indian_symbol,
            detect_exchange,
            validate_indian_symbol,
        )
        valid, result = validate_indian_symbol("TCS")
        assert valid
        assert result == "TCS.NS"
        print("  PASS: CLI India utils OK")
    except Exception as e:
        print(f"  FAIL: {e}")

    # Test 6: Import main_india
    print("\n[Test 6] Importing main_india...")
    try:
        import main_india
        cfg_fn = main_india.get_india_config()
        assert cfg_fn["data_vendors"]["core_stock_apis"] == "nse"
        print("  PASS: main_india OK")
    except Exception as e:
        print(f"  FAIL: {e}")

    # Test 7: Test NSE data fetch (without running full agent)
    print("\n[Test 7] Testing NSE data fetch (RELIANCE.NS)...")
    try:
        from tradingagents.dataflows.nse_data import get_NSE_data_online
        result = get_NSE_data_online("RELIANCE", "2024-01-01", "2024-01-10")
        if "No data found" in result or result.startswith("Error"):
            print(f"  WARN: Data fetch returned: {result[:200]}")
        else:
            assert "Stock data for RELIANCE" in result
            assert "Open" in result or "Close" in result
            print(f"  PASS: Data fetch OK (got {len(result)} chars)")
    except Exception as e:
        print(f"  FAIL: {e}")

    print("\n" + "="*50)
    print("All tests completed!")
    print("="*50)
