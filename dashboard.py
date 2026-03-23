"""
TradingAgents - Professional Financial Advisor Dashboard
The ultimate AI-powered investment platform
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="TradingAgents - Your AI Financial Advisor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium Financial Dashboard CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * { font-family: 'Inter', sans-serif !important; }

    .stApp { background: linear-gradient(135deg, #0a0a0f 0%, #0f1419 100%); }

    /* Headers */
    .main-title { font-size: 3rem; font-weight: 800; background: linear-gradient(120deg, #00d4aa, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .section-title { font-size: 1.5rem; font-weight: 600; color: #fff; margin: 1.5rem 0 1rem 0; }

    /* Cards */
    .card { background: linear-gradient(145deg, #1a1a24, #12121a); border: 1px solid #2a2a3a; border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; }
    .card:hover { border-color: #3a3a4a; }

    /* Signal Badges */
    .badge { padding: 6px 16px; border-radius: 50px; font-weight: 600; font-size: 0.85rem; letter-spacing: 0.5px; }
    .badge-buy { background: linear-gradient(135deg, #00d4aa, #00b894); color: #000; }
    .badge-sell { background: linear-gradient(135deg, #ff4757, #ff6b81); color: #fff; }
    .badge-hold { background: linear-gradient(135deg, #ffa502, #ffbe76); color: #000; }

    /* Price Display */
    .current-price { font-size: 2.5rem; font-weight: 700; color: #fff; }
    .company-name { font-size: 1rem; color: #888; }

    /* Returns */
    .return-positive { color: #00d4aa; font-weight: 600; }
    .return-negative { color: #ff4757; font-weight: 600; }

    /* Timeframe Pills */
    .timeframe-pill { background: linear-gradient(135deg, #7c3aed, #a855f7); padding: 8px 20px; border-radius: 50px; color: #fff; font-weight: 500; }

    /* Confidence Bar */
    .conf-bar { background: #2a2a3a; border-radius: 10px; height: 8px; }
    .conf-fill { height: 100%; border-radius: 10px; transition: width 0.5s ease; }

    /* Target/Stoploss Boxes */
    .target-card { background: rgba(0,212,170,0.1); border: 1px solid rgba(0,212,170,0.3); border-radius: 12px; padding: 1rem; text-align: center; }
    .stop-card { background: rgba(255,71,87,0.1); border: 1px solid rgba(255,71,87,0.3); border-radius: 12px; padding: 1rem; text-align: center; }

    /* Navigation Tabs */
    .nav-tab { padding: 10px 20px; border-radius: 10px; cursor: pointer; transition: all 0.3s; }
    .nav-tab:hover { background: #2a2a3a; }

    /* Metrics */
    .metric-card { background: #1a1a24; border-radius: 12px; padding: 1rem; text-align: center; }
    .metric-label { font-size: 0.75rem; color: #666; text-transform: uppercase; letter-spacing: 1px; }
    .metric-value { font-size: 1.5rem; font-weight: 700; color: #fff; }

    /* Market Status */
    .market-open { color: #00d4aa; }
    .market-closed { color: #ff4757; }

    /* Portfolio */
    .portfolio-card { background: linear-gradient(145deg, #1a1a24, #0f0f18); border-radius: 16px; padding: 1.5rem; }

    /* Footer */
    .footer { text-align: center; padding: 2rem; color: #444; }

    /* Hide default elements */
    #MainMenu, footer, header { visibility: hidden; }

    /* Custom scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #1a1a24; }
    ::-webkit-scrollbar-thumb { background: #3a3a4a; border-radius: 3px; }

    /* Button styles */
    .stButton > button { border-radius: 10px; font-weight: 600; }

    /* Status indicators */
    .status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 8px; }
    .status-green { background: #00d4aa; }
    .status-red { background: #ff4757; }
    .status-yellow { background: #ffa502; }

    /* Alert boxes */
    .alert-success { background: rgba(0,212,170,0.15); border-left: 4px solid #00d4aa; padding: 1rem; border-radius: 0 10px 10px 0; }
    .alert-danger { background: rgba(255,71,87,0.15); border-left: 4px solid #ff4757; padding: 1rem; border-radius: 0 10px 10px 0; }
    .alert-warning { background: rgba(255,165,2,0.15); border-left: 4px solid #ffa502; padding: 1rem; border-radius: 0 10px 10px 0; }

    /* Progress ring */
    .progress-ring { width: 60px; height: 60px; }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if "portfolio" not in st.session_state:
    st.session_state.portfolio = []
if "watchlist" not in st.session_state:
    st.session_state.watchlist = list(TOP_STOCKS.keys()) if 'TOP_STOCKS' in dir() else []
if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = "📊 Dashboard"


# Top Indian Stocks
TOP_STOCKS = {
    "RELIANCE": "Reliance Industries",
    "TCS": "Tata Consultancy Services",
    "HDFCBANK": "HDFC Bank",
    "INFOSYS": "Infosys",
    "ICICIBANK": "ICICI Bank",
    "SBIN": "State Bank of India",
    "BHARTIARTL": "Bharti Airtel",
    "ITC": "ITC Limited",
    "LT": "Larsen & Toubro",
    "TATASTEEL": "Tata Steel",
    "ADANIPORTS": "Adani Ports",
    "KOTAKBANK": "Kotak Mahindra Bank",
}

# US Stocks
US_STOCKS = {
    "AAPL": "Apple Inc.",
    "GOOGL": "Alphabet Inc.",
    "MSFT": "Microsoft Corp.",
    "AMZN": "Amazon.com",
    "NVDA": "NVIDIA Corp.",
    "META": "Meta Platforms",
    "TSLA": "Tesla Inc.",
    "JPM": "JPMorgan Chase",
}


def get_stock_data(ticker, market="india"):
    """Get comprehensive stock data with full indicators."""
    try:
        suffix = ".NS" if market == "india" else ""
        stock = yf.Ticker(f"{ticker}{suffix}")
        hist = stock.history(period="1y")

        if hist.empty or len(hist) < 50:
            return None

        close = hist["Close"]
        high = hist["High"]
        low = hist["Low"]
        volume = hist["Volume"]

        # Moving averages
        sma20 = close.rolling(20).mean()
        sma50 = close.rolling(50).mean()
        sma200 = close.rolling(200).mean()

        # EMA
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()

        # RSI
        rsi = calculate_rsi(close)

        # MACD
        macd = ema12 - ema26
        signal_line = macd.ewm(span=9, adjust=False).mean()
        macd_hist = macd - signal_line

        # Bollinger Bands
        bb_mid = close.rolling(20).mean()
        bb_std = close.rolling(20).std()
        bb_upper = bb_mid + (bb_std * 2)
        bb_lower = bb_mid - (bb_std * 2)

        # ATR (Average True Range)
        high_low = high - low
        high_close = abs(high - close.shift())
        low_close = abs(low - close.shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(14).mean()

        # Returns
        ret_1d = ((close.iloc[-1] / close.iloc[-2]) - 1) * 100 if len(close) > 1 else 0
        ret_1w = ((close.iloc[-1] / close.iloc[-5]) - 1) * 100 if len(close) > 5 else 0
        ret_1m = ((close.iloc[-1] / close.iloc[-22]) - 1) * 100 if len(close) > 22 else 0
        ret_3m = ((close.iloc[-1] / close.iloc[-66]) - 1) * 100 if len(close) > 66 else 0
        ret_6m = ((close.iloc[-1] / close.iloc[-126]) - 1) * 100 if len(close) > 126 else 0
        ret_1y = ((close.iloc[-1] / close.iloc[-252]) - 1) * 100 if len(close) > 252 else 0

        # Volatility
        volatility = close.pct_change().rolling(20).std() * (252 ** 0.5) * 100

        price = close.iloc[-1]
        current_sma20 = sma20.iloc[-1]
        current_sma50 = sma50.iloc[-1]
        current_sma200 = sma200.iloc[-1] if len(sma200) > 0 else price
        current_rsi = rsi.iloc[-1] if isinstance(rsi, pd.Series) else rsi
        current_macd = macd.iloc[-1] if isinstance(macd, pd.Series) else macd
        current_signal = signal_line.iloc[-1] if isinstance(signal_line, pd.Series) else signal_line
        current_atr = atr.iloc[-1] if isinstance(atr, pd.Series) else atr

        # Determine signal
        signal = determine_signal(price, current_sma20, current_sma50, current_sma200, current_rsi, current_macd, current_signal)
        confidence = calculate_confidence(price, current_sma20, current_sma50, current_sma200, current_rsi, current_macd, current_signal, signal)
        timeframe = calculate_hold_timeframe(signal, current_rsi)
        reason = generate_reason(signal, current_rsi, price, current_sma20, current_sma50, current_macd, current_signal)

        # Risk/Reward
        if signal == "BUY":
            target_pct = 10 + (50 - current_rsi) / 5 if current_rsi < 50 else 8
            target_price = price * (1 + target_pct / 100)
            stop_loss = price * (1 - (target_pct * 0.4) / 100)
            risk_reward = target_pct / (price - stop_loss) * 100 if price > stop_loss else 0
        elif signal == "SELL":
            target_pct = 8 + (current_rsi - 50) / 5 if current_rsi > 50 else 6
            target_price = price * (1 - target_pct / 100)
            stop_loss = price * (1 + (target_pct * 0.4) / 100)
            risk_reward = target_pct / (stop_loss - price) * 100 if stop_loss > price else 0
        else:
            target_price = price
            stop_loss = price
            risk_reward = 0
            target_pct = 0

        # Support and Resistance
        support = bb_lower.iloc[-1] if isinstance(bb_lower, pd.Series) else price * 0.95
        resistance = bb_upper.iloc[-1] if isinstance(bb_upper, pd.Series) else price * 1.05

        return {
            "ticker": ticker,
            "name": (TOP_STOCKS if market == "india" else US_STOCKS).get(ticker, ticker),
            "price": price,
            "rsi": float(current_rsi),
            "macd": float(current_macd),
            "signal": float(current_signal),
            "sma20": float(current_sma20),
            "sma50": float(current_sma50),
            "sma200": float(current_sma200),
            "atr": float(current_atr),
            "support": float(support),
            "resistance": float(resistance),
            "returns_1d": ret_1d,
            "returns_1w": ret_1w,
            "returns_1m": ret_1m,
            "returns_3m": ret_3m,
            "returns_6m": ret_6m,
            "returns_1y": ret_1y,
            "volatility": float(volatility.iloc[-1]) if isinstance(volatility, pd.Series) else 20.0,
            "signal": signal,
            "confidence": confidence,
            "timeframe": timeframe,
            "reason": reason,
            "target_price": target_price,
            "stop_loss": stop_loss,
            "potential_pct": target_pct,
            "risk_reward": risk_reward,
            "hist": hist,
        }
    except Exception as e:
        return None


def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def determine_signal(price, sma20, sma50, sma200, rsi, macd, signal):
    bullish = 0
    bearish = 0

    # RSI (weight: 3)
    if rsi < 30: bullish += 4
    elif rsi > 70: bearish += 4
    elif rsi < 40: bullish += 2
    elif rsi > 60: bearish += 2

    # Moving Averages (weight: 3)
    if price > sma20 > sma50 > sma200: bullish += 4
    elif price < sma20 < sma50 < sma200: bearish += 4
    elif price > sma20 > sma50: bullish += 2
    elif price < sma20 < sma50: bearish += 2
    elif price > sma20: bullish += 1
    elif price < sma20: bearish += 1

    # MACD (weight: 2)
    if macd > signal > 0: bullish += 2
    elif macd < signal < 0: bearish += 2
    elif macd > signal: bullish += 1
    elif macd < signal: bearish += 1

    if bullish > bearish + 2: return "BUY"
    elif bearish > bullish + 2: return "SELL"
    return "HOLD"


def calculate_confidence(price, sma20, sma50, sma200, rsi, macd, signal, sig):
    score = 50

    # RSI contribution
    if sig == "BUY":
        if rsi < 30: score += 20
        elif rsi < 40: score += 15
        elif rsi < 50: score += 5
        elif rsi > 70: score -= 15
    elif sig == "SELL":
        if rsi > 70: score += 20
        elif rsi > 60: score += 15
        elif rsi > 50: score += 5
        elif rsi < 30: score -= 15

    # Trend contribution
    if price > sma20 > sma50 > sma200 and sig == "BUY": score += 20
    elif price < sma20 < sma50 < sma200 and sig == "SELL": score += 20
    elif price > sma20 > sma50 and sig == "BUY": score += 10
    elif price < sma20 < sma50 and sig == "SELL": score += 10

    # MACD confirmation
    if macd > signal > 0 and sig == "BUY": score += 10
    elif macd < signal < 0 and sig == "SELL": score += 10

    return max(0, min(100, score))


def calculate_hold_timeframe(signal, rsi):
    if signal == "BUY":
        if rsi < 25: return "20-25 days"
        elif rsi < 35: return "25-30 days"
        elif rsi < 45: return "30-45 days"
        else: return "10-15 days"
    elif signal == "SELL":
        if rsi > 75: return "5-7 days"
        elif rsi > 65: return "7-12 days"
        elif rsi > 55: return "12-18 days"
        else: return "18-25 days"
    else:
        if rsi > 60: return "Wait 10-15 days"
        elif rsi < 40: return "Wait 12-18 days"
        return "Wait for signal"


def generate_reason(signal, rsi, price, sma20, sma50, macd, signal_line):
    if signal == "BUY":
        parts = []
        if rsi < 35: parts.append(f"RSI at {rsi:.0f} shows oversold")
        if price > sma20: parts.append("Trading above short-term trend")
        if sma20 > sma50: parts.append("Medium-term uptrend confirmed")
        if macd > signal_line: parts.append("MACD bullish crossover")
        return " • ".join(parts[:3]) if parts else "Strong buy setup"
    elif signal == "SELL":
        parts = []
        if rsi > 65: parts.append(f"RSI at {rsi:.0f} shows overbought")
        if price < sma20: parts.append("Below short-term trend")
        if sma20 < sma50: parts.append("Medium-term downtrend active")
        if macd < signal_line: parts.append("MACD bearish crossover")
        return " • ".join(parts[:3]) if parts else "Bearish pressure"
    else:
        if 40 <= rsi <= 60: return "Consolidating - await breakout"
        elif rsi > 50: return "Near resistance - stay cautious"
        return "Building base - watch for momentum"


def plot_advanced_chart(hist, ticker, show_indicators=True):
    """Create advanced chart with all indicators."""
    close = hist["Close"]
    sma20 = close.rolling(20).mean()
    sma50 = close.rolling(50).mean()
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal_line = macd.ewm(span=9, adjust=False).mean()
    macd_hist = macd - signal_line
    bb_mid = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    bb_upper = bb_mid + (bb_std * 2)
    bb_lower = bb_mid - (bb_std * 2)
    rsi = calculate_rsi(close)

    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=[0.5, 0.15, 0.15, 0.2],
        subplot_titles=("", "", "", ""),
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=hist.index, open=hist["Open"], high=hist["High"],
        low=hist["Low"], close=close,
        increasing_line_color="#00d4aa", decreasing_line_color="#ff4757",
        name="Price"
    ), row=1, col=1)

    # Bollinger Bands
    fig.add_trace(go.Scatter(x=hist.index, y=bb_upper, name="BB Upper",
        line=dict(color="#666", width=1), opacity=0.5), row=1, col=1)
    fig.add_trace(go.Scatter(x=hist.index, y=bb_mid, name="BB Mid",
        line=dict(color="#666", width=1, dash="dash"), opacity=0.5), row=1, col=1)
    fig.add_trace(go.Scatter(x=hist.index, y=bb_lower, name="BB Lower",
        line=dict(color="#666", width=1), opacity=0.5,
        fill='tonexty', fillcolor='rgba(102,102,102,0.1)'), row=1, col=1)

    # SMAs
    fig.add_trace(go.Scatter(x=hist.index, y=sma20, name="SMA 20",
        line=dict(color="#4fc3f7", width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=hist.index, y=sma50, name="SMA 50",
        line=dict(color="#ff9800", width=1.5)), row=1, col=1)

    # Volume
    colors = ["#00d4aa" if close.iloc[i] >= hist["Open"].iloc[i] else "#ff4757" for i in range(len(hist))]
    fig.add_trace(go.Bar(x=hist.index, y=hist["Volume"], marker_color=colors,
        name="Volume", opacity=0.7), row=2, col=1)

    # MACD
    colors_macd = ["#00d4aa" if macd_hist.iloc[i] >= 0 else "#ff4757" for i in range(len(hist))]
    fig.add_trace(go.Bar(x=hist.index, y=macd_hist, marker_color=colors_macd,
        name="MACD Hist", opacity=0.8), row=3, col=1)
    fig.add_trace(go.Scatter(x=hist.index, y=macd, name="MACD",
        line=dict(color="#4fc3f7", width=1.5)), row=3, col=1)
    fig.add_trace(go.Scatter(x=hist.index, y=signal_line, name="Signal",
        line=dict(color="#ff9800", width=1.5)), row=3, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=hist.index, y=rsi, name="RSI",
        line=dict(color="#a855f7", width=1.5)), row=4, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="#ff4757", opacity=0.7, row=4, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="#00d4aa", opacity=0.7, row=4, col=1)
    fig.add_hline(y=50, line_dash="dash", line_color="#666", opacity=0.3, row=4, col=1)

    fig.update_layout(
        template="plotly_dark",
        height=600,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
        xaxis_rangeslider_visible=False,
        margin=dict(t=30, l=50, r=50, b=30),
    )

    return fig


# Header
st.markdown('<div class="main-title">💰 TradingAgents</div>', unsafe_allow_html=True)
st.markdown('<p style="color:#888; font-size:1.1rem;">Your AI-Powered Financial Advisor</p>', unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "💼 Portfolio", "📈 Charts", "🔍 Compare", "⚙️ Settings"])

with tab1:
    st.markdown("### 📊 Market Overview & Stock Analysis")

    # Market status
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Market Status</div>', unsafe_allow_html=True)
        hour = datetime.now().hour
        is_open = 9 <= hour < 16
        status = '<span class="status-dot status-green"></span><span class="market-open">OPEN</span>' if is_open else '<span class="status-dot status-red"></span><span class="market-closed">CLOSED</span>'
        st.markdown(f'<div style="margin-top:5px">{status}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_m2:
        st.metric("Indices", "Nifty 50", "Live")

    with col_m3:
        st.metric("Analysis", f"{len(TOP_STOCKS)} Stocks", "Scanned")

    with col_m4:
        st.metric("Updated", datetime.now().strftime("%H:%M"), datetime.now().strftime("%d %b"))

    st.divider()

    # Analyze all stocks
    st.markdown("### 🔍 Analyzing Markets...")

    with st.spinner("Scanning stocks..."):
        progress_bar = st.progress(0)
        results = []

        all_stocks = {**TOP_STOCKS}
        for i, ticker in enumerate(all_stocks.keys()):
            progress_bar.progress((i + 1) / len(all_stocks))
            data = get_stock_data(ticker, "india")
            if data:
                results.append(data)

        progress_bar.empty()

    # Sort
    signal_order = {"BUY": 0, "SELL": 1, "HOLD": 2}
    results.sort(key=lambda x: (signal_order[x["signal"]], -x["confidence"]))

    # Display by signal
    buy_picks = [r for r in results if r["signal"] == "BUY"]
    sell_picks = [r for r in results if r["signal"] == "SELL"]
    hold_picks = [r for r in results if r["signal"] == "HOLD"]

    # Top BUY Opportunities
    if buy_picks:
        st.markdown("### 🟢 TOP BUY OPPORTUNITIES")
        for stock in buy_picks[:4]:
            col1, col2, col3, col4 = st.columns([2.5, 1.5, 1.5, 1.5])

            with col1:
                st.markdown(f'<div class="card">', unsafe_allow_html=True)
                st.markdown(f"**{stock['ticker']}** • {stock['name']}")
                st.markdown(f'<div class="current-price">₹{stock["price"]:,.0f}</div>', unsafe_allow_html=True)

                cols_ret = st.columns(4)
                with cols_ret[0]:
                    color = "return-positive" if stock['returns_1d'] > 0 else "return-negative"
                    st.markdown(f'<div class="metric-label">1D</div><div class="{color}">{stock["returns_1d"]:+.1f}%</div>', unsafe_allow_html=True)
                with cols_ret[1]:
                    color = "return-positive" if stock['returns_1w'] > 0 else "return-negative"
                    st.markdown(f'<div class="metric-label">1W</div><div class="{color}">{stock["returns_1w"]:+.1f}%</div>', unsafe_allow_html=True)
                with cols_ret[2]:
                    color = "return-positive" if stock['returns_1m'] > 0 else "return-negative"
                    st.markdown(f'<div class="metric-label">1M</div><div class="{color}">{stock["returns_1m"]:+.1f}%</div>', unsafe_allow_html=True)
                with cols_ret[3]:
                    rsi_color = "return-positive" if stock['rsi'] < 40 else ("return-negative" if stock['rsi'] > 60 else "")
                    st.markdown(f'<div class="metric-label">RSI</div><div class="{rsi_color}">{stock["rsi"]:.0f}</div>', unsafe_allow_html=True)

            with col2:
                st.markdown(f'<span class="badge badge-buy">🟢 BUY</span>', unsafe_allow_html=True)
                st.markdown(f'<div style="margin-top:10px"></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-label">Hold For</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="timeframe-pill">{stock["timeframe"]}</div>', unsafe_allow_html=True)

                st.markdown(f'<div class="metric-label" style="margin-top:15px">Confidence</div>', unsafe_allow_html=True)
                conf_color = "#00d4aa" if stock['confidence'] >= 70 else ("#ffa502" if stock['confidence'] >= 50 else "#ff4757")
                st.markdown(f'<div class="conf-bar"><div class="conf-fill" style="width:{stock["confidence"]}%; background:{conf_color}"></div></div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#888; font-size:0.8rem">{stock["confidence"]}%</div>', unsafe_allow_html=True)

            with col3:
                st.markdown('<div class="target-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Target Price</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:1.3rem; font-weight:700; color:#00d4aa;">₹{stock["target_price"]:,.0f}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#00d4aa; font-size:0.85rem;">+{stock["potential_pct"]:.1f}%</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="stop-card" style="margin-top:10px">', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Stop Loss</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:1.3rem; font-weight:700; color:#ff4757;">₹{stock["stop_loss"]:,.0f}</div>', unsafe_allow_html=True)
                risk = abs((stock['stop_loss'] - stock['price']) / stock['price'] * 100)
                st.markdown(f'<div style="color:#ff4757; font-size:0.85rem;">-{risk:.1f}%</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col4:
                st.markdown('<div class="metric-label">Risk/Reward</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:2rem; font-weight:700; color:{"#00d4aa" if stock["risk_reward"] > 2 else "#ffa502"};">{stock["risk_reward"]:.1f}:1</div>', unsafe_allow_html=True)

                st.markdown('<div class="metric-label" style="margin-top:15px">Why?</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#aaa; font-size:0.9rem;">{stock["reason"]}</div>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

            st.divider()

    # SELL Signals
    if sell_picks:
        st.markdown("### 🔴 SELL SIGNALS")
        for stock in sell_picks[:4]:
            col1, col2, col3, col4 = st.columns([2.5, 1.5, 1.5, 1.5])

            with col1:
                st.markdown(f'<div class="card">', unsafe_allow_html=True)
                st.markdown(f"**{stock['ticker']}** • {stock['name']}")
                st.markdown(f'<div class="current-price">₹{stock["price"]:,.0f}</div>', unsafe_allow_html=True)

                cols_ret = st.columns(4)
                with cols_ret[0]:
                    color = "return-positive" if stock['returns_1d'] > 0 else "return-negative"
                    st.markdown(f'<div class="metric-label">1D</div><div class="{color}">{stock["returns_1d"]:+.1f}%</div>', unsafe_allow_html=True)
                with cols_ret[1]:
                    color = "return-positive" if stock['returns_1w'] > 0 else "return-negative"
                    st.markdown(f'<div class="metric-label">1W</div><div class="{color}">{stock["returns_1w"]:+.1f}%</div>', unsafe_allow_html=True)
                with cols_ret[2]:
                    color = "return-positive" if stock['returns_1m'] > 0 else "return-negative"
                    st.markdown(f'<div class="metric-label">1M</div><div class="{color}">{stock["returns_1m"]:+.1f}%</div>', unsafe_allow_html=True)
                with cols_ret[3]:
                    rsi_color = "return-positive" if stock['rsi'] < 40 else ("return-negative" if stock['rsi'] > 60 else "")
                    st.markdown(f'<div class="metric-label">RSI</div><div class="{rsi_color}">{stock["rsi"]:.0f}</div>', unsafe_allow_html=True)

            with col2:
                st.markdown(f'<span class="badge badge-sell">🔴 SELL</span>', unsafe_allow_html=True)
                st.markdown(f'<div style="margin-top:10px"></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-label">Exit Within</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="timeframe-pill">{stock["timeframe"]}</div>', unsafe_allow_html=True)

                st.markdown(f'<div class="metric-label" style="margin-top:15px">Confidence</div>', unsafe_allow_html=True)
                conf_color = "#00d4aa" if stock['confidence'] >= 70 else ("#ffa502" if stock['confidence'] >= 50 else "#ff4757")
                st.markdown(f'<div class="conf-bar"><div class="conf-fill" style="width:{stock["confidence"]}%; background:{conf_color}"></div></div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#888; font-size:0.8rem">{stock["confidence"]}%</div>', unsafe_allow_html=True)

            with col3:
                st.markdown('<div class="target-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Target (Down)</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:1.3rem; font-weight:700; color:#ff4757;">₹{stock["target_price"]:,.0f}</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#ff4757; font-size:0.85rem;">{stock["potential_pct"]:.1f}%</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="stop-card" style="margin-top:10px">', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Avoid Above</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:1.3rem; font-weight:700; color:#ffa502;">₹{stock["stop_loss"]:,.0f}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col4:
                st.markdown('<div class="metric-label">Why Sell?</div>', unsafe_allow_html=True)
                st.markdown(f'<div style="color:#aaa; font-size:0.9rem; margin-top:5px;">{stock["reason"]}</div>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

            st.divider()

    # HOLD/WATCH
    if hold_picks:
        st.markdown("### 🟡 HOLD / WATCH LIST")
        cols = st.columns(3)
        for idx, stock in enumerate(hold_picks):
            with cols[idx % 3]:
                st.markdown(f'<div class="card" style="padding:1rem;">', unsafe_allow_html=True)
                st.markdown(f"**{stock['ticker']}** • {stock['name']}")
                st.markdown(f'<div class="current-price" style="font-size:1.8rem;">₹{stock["price"]:,.0f}</div>', unsafe_allow_html=True)

                rsi_color = "return-positive" if stock['rsi'] < 40 else ("return-negative" if stock['rsi'] > 60 else "")
                st.markdown(f'RSI: <span class="{rsi_color}">{stock["rsi"]:.0f}</span> | {stock["timeframe"]}')

                if stock['returns_1m'] > 0:
                    st.markdown(f'<span class="return-positive">+{stock["returns_1m"]:.1f}%</span> this month', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="return-negative">{stock["returns_1m"]:.1f}%</span> this month', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown("### 💼 Portfolio Tracker")

    # Add to portfolio
    col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
    with col_p1:
        portfolio_ticker = st.selectbox("Add Stock", list(TOP_STOCKS.keys()), format_func=lambda x: f"{x} - {TOP_STOCKS[x]}")
    with col_p2:
        shares = st.number_input("Shares", min_value=1, value=10)
    with col_p3:
        buy_price = st.number_input("Buy Price (₹)", min_value=0.0, value=1000.0)

    if st.button("➕ Add to Portfolio"):
        stock_data = get_stock_data(portfolio_ticker, "india")
        if stock_data:
            st.session_state.portfolio.append({
                "ticker": portfolio_ticker,
                "shares": shares,
                "buy_price": buy_price,
                "current_price": stock_data["price"],
                "signal": stock_data["signal"],
                "timeframe": stock_data["timeframe"],
            })
            st.success(f"Added {shares} shares of {portfolio_ticker} @ ₹{buy_price}")

    st.divider()

    # Display portfolio
    if st.session_state.portfolio:
        total_invested = 0
        total_current = 0
        total_pnl = 0

        col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns(5)
        with col_h1: st.markdown("**Stock**")
        with col_h2: st.markdown("**Investment**")
        with col_h3: st.markdown("**Current Value**")
        with col_h4: st.markdown("**P&L**")
        with col_h5: st.markdown("**Action**")

        for i, item in enumerate(st.session_state.portfolio):
            invested = item["shares"] * item["buy_price"]
            current = item["shares"] * item["current_price"]
            pnl = current - invested
            pnl_pct = (pnl / invested) * 100 if invested > 0 else 0
            total_invested += invested
            total_current += current
            total_pnl += pnl

            with col_h1:
                badge = "🟢" if item["signal"] == "BUY" else ("🔴" if item["signal"] == "SELL" else "🟡")
                st.markdown(f"{badge} **{item['ticker']}**")

            with col_h2:
                st.markdown(f"₹{invested:,.0f}")

            with col_h3:
                st.markdown(f"₹{current:,.0f}")

            with col_h4:
                if pnl >= 0:
                    st.markdown(f'<span class="return-positive">+₹{pnl:,.0f} (+{pnl_pct:.1f}%)</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="return-negative">-₹{abs(pnl):,.0f} ({pnl_pct:.1f}%)</span>', unsafe_allow_html=True)

            with col_h5:
                if st.button(f"Remove", key=f"rem_{i}"):
                    st.session_state.portfolio.pop(i)
                    st.rerun()

        st.divider()

        # Portfolio Summary
        total_pnl_pct = (total_pnl / total_invested) * 100 if total_invested > 0 else 0

        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("Total Invested", f"₹{total_invested:,.0f}")
        with col_s2:
            st.metric("Current Value", f"₹{total_current:,.0f}")
        with col_s3:
            st.metric("Total P&L", f"₹{total_pnl:+,.0f}", f"{total_pnl_pct:+.1f}%")
        with col_s4:
            signal_counts = {"BUY": 0, "SELL": 0, "HOLD": 0}
            for item in st.session_state.portfolio:
                signal_counts[item["signal"]] += 1
            st.markdown("**Signals**")
            st.markdown(f"🟢 {signal_counts['BUY']} Buy • 🔴 {signal_counts['SELL']} Sell • 🟡 {signal_counts['HOLD']} Hold")

        # Export to CSV
        if st.button("📥 Export Portfolio"):
            df = pd.DataFrame(st.session_state.portfolio)
            df["invested"] = df["shares"] * df["buy_price"]
            df["current_value"] = df["shares"] * df["current_price"]
            df["pnl"] = df["current_value"] - df["invested"]
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", csv, "portfolio.csv", "text/csv")

    else:
        st.info("Your portfolio is empty. Add stocks to track your investments.")

with tab3:
    st.markdown("### 📈 Advanced Technical Charts")

    col_c1, col_c2 = st.columns([1, 3])
    with col_c1:
        chart_ticker = st.selectbox("Select Stock", list(TOP_STOCKS.keys()), format_func=lambda x: f"{x} - {TOP_STOCKS[x]}", key="chart_select")
    with col_c2:
        period_options = {"1 Month": "1mo", "3 Months": "3mo", "6 Months": "6mo", "1 Year": "1y", "All": "2y"}
        chart_period = st.selectbox("Period", list(period_options.keys()))

    if st.button("📊 Generate Chart", type="primary"):
        with st.spinner("Loading chart..."):
            try:
                suffix = ".NS"
                stock = yf.Ticker(f"{chart_ticker}{suffix}")
                hist = stock.history(period=period_options[chart_period])

                if not hist.empty:
                    fig = plot_advanced_chart(hist, chart_ticker)
                    st.plotly_chart(fig, use_container_width=True)

                    # Stock details
                    stock_data = get_stock_data(chart_ticker, "india")
                    if stock_data:
                        col_d1, col_d2, col_d3, col_d4 = st.columns(4)
                        with col_d1:
                            st.metric("Support", f"₹{stock_data['support']:,.0f}")
                        with col_d2:
                            st.metric("Resistance", f"₹{stock_data['resistance']:,.0f}")
                        with col_d3:
                            st.metric("ATR (Volatility)", f"₹{stock_data['atr']:,.2f}")
                        with col_d4:
                            st.metric("Risk/Reward", f"{stock_data['risk_reward']:.1f}:1")
            except Exception as e:
                st.error(f"Error loading chart: {e}")

with tab4:
    st.markdown("### 🔍 Stock Comparison")

    comp_col1, comp_col2 = st.columns(2)
    with comp_col1:
        stock1 = st.selectbox("Stock 1", list(TOP_STOCKS.keys()), format_func=lambda x: f"{x}", key="comp1")
    with comp_col2:
        stock2 = st.selectbox("Stock 2", list(TOP_STOCKS.keys()), format_func=lambda x: f"{x}", key="comp2", index=1)

    if st.button("Compare", type="primary"):
        data1 = get_stock_data(stock1, "india")
        data2 = get_stock_data(stock2, "india")

        if data1 and data2:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"### {stock1}")
                st.markdown(f"**{TOP_STOCKS[stock1]}**")
                st.markdown(f"### ₹{data1['price']:,.0f}")

                signal_color = "#00d4aa" if data1['signal'] == "BUY" else ("#ff4757" if data1['signal'] == "SELL" else "#ffa502")
                st.markdown(f"<span style='color:{signal_color}; font-weight:bold'>{data1['signal']}</span> | RSI: {data1['rsi']:.0f}", unsafe_allow_html=True)

                st.markdown(f"**1M Return:** {'+' if data1['returns_1m'] > 0 else ''}{data1['returns_1m']:.1f}%")
                st.markdown(f"**3M Return:** {'+' if data1['returns_3m'] > 0 else ''}{data1['returns_3m']:.1f}%")
                st.markdown(f"**Confidence:** {data1['confidence']}%")

            with col2:
                st.markdown(f"### {stock2}")
                st.markdown(f"**{TOP_STOCKS[stock2]}**")
                st.markdown(f"### ₹{data2['price']:,.0f}")

                signal_color = "#00d4aa" if data2['signal'] == "BUY" else ("#ff4757" if data2['signal'] == "SELL" else "#ffa502")
                st.markdown(f"<span style='color:{signal_color}; font-weight:bold'>{data2['signal']}</span> | RSI: {data2['rsi']:.0f}", unsafe_allow_html=True)

                st.markdown(f"**1M Return:** {'+' if data2['returns_1m'] > 0 else ''}{data2['returns_1m']:.1f}%")
                st.markdown(f"**3M Return:** {'+' if data2['returns_3m'] > 0 else ''}{data2['returns_3m']:.1f}%")
                st.markdown(f"**Confidence:** {data2['confidence']}%")

            # Comparison verdict
            st.divider()
            st.markdown("### 📊 Comparison Analysis")

            winner = "🏆 Both are good - choose based on your strategy" if abs(data1['confidence'] - data2['confidence']) < 15 else (f"🏆 **{stock1}** looks stronger" if data1['confidence'] > data2['confidence'] else f"🏆 **{stock2}** looks stronger")

            if data1['signal'] == "BUY" and data2['signal'] != "BUY":
                st.success(f"{stock1} has a BUY signal while {stock2} is {data2['signal']}")
            elif data2['signal'] == "BUY" and data1['signal'] != "BUY":
                st.success(f"{stock2} has a BUY signal while {stock1} is {data1['signal']}")
            else:
                st.info(winner)

with tab5:
    st.markdown("### ⚙️ Settings")

    st.markdown("#### Market Selection")
    market_region = st.radio("Region", ["India (NSE)", "US (NYSE/NASDAQ)"])

    st.markdown("#### Refresh Settings")
    auto_refresh = st.checkbox("Auto-refresh data every 5 minutes")
    refresh_interval = st.slider("Refresh Interval (minutes)", 1, 15, 5) if auto_refresh else 5

    st.markdown("#### Display Settings")
    dark_mode = st.checkbox("Dark Mode", value=True)
    show_volatility = st.checkbox("Show Volatility", value=True)
    show_news = st.checkbox("Show News", value=True)

    st.markdown("#### Data Export")
    if st.button("📥 Export All Analysis Data"):
        st.info("Export feature - coming soon!")

    st.markdown("---")
    st.markdown(f"**Version:** 2.0 | **Last Updated:** {datetime.now().strftime('%d %b %Y')} | **Data Source:** Yahoo Finance")

# Footer
st.markdown("""
<div class="footer">
    <p>💰 TradingAgents AI • Your Smart Financial Advisor</p>
</div>
""", unsafe_allow_html=True)
