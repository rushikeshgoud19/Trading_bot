# TradingAgents: Multi-Agents Financial Trading Framework

TradingAgents is a multi-agent trading framework that uses LLMs to simulate a real-world trading firm. It deploys specialized AI agents—ranging from fundamental and sentiment analysts to technical analysts and risk managers—to collaboratively evaluate market conditions and make trading decisions.

## Features
- **Multi-Agent Architecture**: Includes an Analyst Team, Research Team, Trading Team, and Risk Management Team.
- **Multiple LLM Providers**: Supports OpenAI (GPT), Google (Gemini), Anthropic (Claude), xAI (Grok), OpenRouter, and local Ollama models.
- **Terminal User Interface (TUI)**: Features an interactive, real-time "matrix-style" terminal UI with configuration sidebar, live execution traces, agent monitors, and final report rendering.

## Setup & Installation

Clone the repository and navigate to the project folder:
```bash
git clone https://github.com/rushikeshgoud19/Trading_bot.git
cd Trading_bot
```

Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

### Environment Variables
Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```
Ensure you provide keys for the model providers you intend to use (e.g. `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`).

## Usage

### Launching the TUI
To start the interactive Terminal User Interface, run:
```bash
tradingagents tui
```
Alternatively:
```bash
python -m cli.main tui
```
This will open the TUI where you can configure parameters (Ticker Symbol, Date, Agents) and execute the multi-agent simulation in real time.

### Using as a Python Package
You can import the module directly into your code:
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())
_, decision = ta.propagate("AAPL", "2025-01-01")
print(decision)
```
