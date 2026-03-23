import datetime
import time
from pathlib import Path
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll, Vertical
from textual.widgets import (
    Header, Footer, Button, Input, Select, Checkbox, 
    DataTable, Log, Markdown, TabbedContent, TabPane, Static, Label
)
from textual import work
from textual.message import Message

# Import core business logic
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from cli.models import AnalystType
from cli.stats_handler import StatsCallbackHandler
from cli.main import (
    message_buffer, classify_message_type, format_tool_args, 
    update_analyst_statuses, update_research_team_status, 
    ANALYST_ORDER, save_report_to_disk
)

# Textual App Definition
class TradingApp(App):
    CSS = """
    Screen {
        layout: horizontal;
    }
    
    #sidebar {
        width: 35;
        dock: left;
        padding: 1;
        background: $panel;
        border-right: vkey $background;
    }
    
    #main-area {
        width: 1fr;
    }
    
    .section-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        margin-top: 1;
    }
    
    .sidebar-input {
        margin-bottom: 1;
    }

    #start-btn {
        width: 100%;
        margin-top: 2;
        variant: success;
    }
    
    Log {
        height: 1fr;
        border: solid $accent;
    }
    
    DataTable {
        height: 1fr;
        border: solid $accent;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    class UpdateStatus(Message):
        """Sent when progress or log changes."""
        pass

    class AnalysisComplete(Message):
        """Sent when the analysis is finished."""
        def __init__(self, final_state, results_dir):
            self.final_state = final_state
            self.results_dir = results_dir
            super().__init__()

    def __init__(self):
        super().__init__()
        self.stats_handler = None
        self.start_time = None
        self.current_report = ""

    def compose(self) -> ComposeResult:
        yield Header()
        
        # Sidebar for configuration
        with VerticalScroll(id="sidebar"):
            yield Label("Configuration", classes="section-title")
            yield Label("Ticker Symbol")
            yield Input(value="SPY", id="input-ticker", classes="sidebar-input")
            
            yield Label("Analysis Date")
            yield Input(value=datetime.datetime.now().strftime("%Y-%m-%d"), id="input-date", classes="sidebar-input")
            
            yield Label("LLM Provider")
            yield Select(
                [("OpenAI", "openai"), ("Anthropic", "anthropic"), ("Google", "google")], 
                value="openai", id="select-provider", classes="sidebar-input"
            )
            
            yield Label("Depth")
            yield Select(
                [("Level 1 (Fast)", 1), ("Level 2", 2), ("Level 3 (Deep)", 3)],
                value=2, id="select-depth", classes="sidebar-input"
            )
            
            yield Label("Select Analysts", classes="section-title")
            yield Checkbox("Market Analyst", value=True, id="cb-market")
            yield Checkbox("Social Analyst", value=True, id="cb-social")
            yield Checkbox("News Analyst", value=True, id="cb-news")
            yield Checkbox("Fundamentals", value=True, id="cb-funds")
            
            yield Button("START ANALYSIS", id="start-btn")
            
            yield Label("Stats", classes="section-title")
            yield Static(id="stats-label")

        # Main Area with tabs
        with Container(id="main-area"):
            with TabbedContent():
                with TabPane("Live Trace", id="tab-trace"):
                    yield Log(id="live-log", highlight=True)
                with TabPane("Agent Monitor", id="tab-progress"):
                    yield DataTable(id="agent-table")
                with TabPane("Reports", id="tab-reports"):
                    with VerticalScroll():
                        yield Markdown(id="md-reports")

        yield Footer()

    def on_mount(self) -> None:
        # Init DataTable
        table = self.query_one("#agent-table", DataTable)
        table.add_columns("Team", "Agent", "Status")
        self._refresh_agent_table()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "start-btn":
            event.button.disabled = True
            self.run_analysis()

    def update_stats_ui(self):
        stats_label = self.query_one("#stats-label", Static)
        if self.start_time:
            elapsed = time.time() - self.start_time
            time_str = f"Time: {int(elapsed // 60):02d}:{int(elapsed % 60):02d}\n"
        else:
            time_str = "Time: 00:00\n"

        llm_str = "LLM: 0\nTokens: --"
        if self.stats_handler:
            stats = self.stats_handler.get_stats()
            tokens_in = f"{stats['tokens_in']/1000:.1f}k" if stats['tokens_in'] >= 1000 else str(stats['tokens_in'])
            tokens_out = f"{stats['tokens_out']/1000:.1f}k" if stats['tokens_out'] >= 1000 else str(stats['tokens_out'])
            llm_str = f"LLM Calls: {stats['llm_calls']}\nTools: {stats['tool_calls']}\nTokens: {tokens_in}↑ {tokens_out}↓"
            
        stats_label.update(time_str + llm_str)

    def _refresh_agent_table(self):
        table = self.query_one("#agent-table", DataTable)
        table.clear()
        
        all_teams = {
            "Analyst Team": ["Market Analyst", "Social Analyst", "News Analyst", "Fundamentals Analyst"],
            "Research Team": ["Bull Researcher", "Bear Researcher", "Research Manager"],
            "Trading Team": ["Trader"],
            "Risk Management": ["Aggressive Analyst", "Neutral Analyst", "Conservative Analyst"],
            "Portfolio Management": ["Portfolio Manager"],
        }
        
        for team, agents in all_teams.items():
            active_agents = [a for a in agents if a in message_buffer.agent_status]
            if not active_agents:
                continue
                
            for i, agent in enumerate(active_agents):
                team_display = team if i == 0 else ""
                status = message_buffer.agent_status.get(agent, "pending")
                table.add_row(team_display, agent, status)

    @work(thread=True)
    def run_analysis(self):
        ticker = self.query_one("#input-ticker", Input).value
        analysis_date = self.query_one("#input-date", Input).value
        provider = self.query_one("#select-provider", Select).value
        depth = self.query_one("#select-depth", Select).value

        selected_analysts_enums = []
        if self.query_one("#cb-market", Checkbox).value: selected_analysts_enums.append(AnalystType.MARKET)
        if self.query_one("#cb-social", Checkbox).value: selected_analysts_enums.append(AnalystType.SOCIAL)
        if self.query_one("#cb-news", Checkbox).value: selected_analysts_enums.append(AnalystType.NEWS)
        if self.query_one("#cb-funds", Checkbox).value: selected_analysts_enums.append(AnalystType.FUNDAMENTALS)

        if not selected_analysts_enums:
            self.post_message(self.UpdateStatus())
            # We can use a notify or something but skipping for simplicity
            return

        selected_set = {a.value for a in selected_analysts_enums}
        selected_analyst_keys = [a for a in ANALYST_ORDER if a in selected_set]

        # Config
        config = DEFAULT_CONFIG.copy()
        config["max_debate_rounds"] = depth
        config["max_risk_discuss_rounds"] = depth
        config["llm_provider"] = provider
        
        # Simple default models
        if provider == "openai":
            config["quick_think_llm"] = "gpt-4o-mini"
            config["deep_think_llm"] = "o1-mini"
        elif provider == "anthropic":
            config["quick_think_llm"] = "claude-3-haiku-20240307"
            config["deep_think_llm"] = "claude-3-5-sonnet-20241022"
        else:
            config["quick_think_llm"] = "gemini-2.5-flash"
            config["deep_think_llm"] = "gemini-2.5-pro"

        self.stats_handler = StatsCallbackHandler()
        
        # Init graph
        graph = TradingAgentsGraph(
            selected_analyst_keys,
            config=config,
            debug=True,
            callbacks=[self.stats_handler],
        )

        message_buffer.init_for_analysis(selected_analyst_keys)
        self.start_time = time.time()
        
        # Output directory
        results_dir = Path(config["results_dir"]) / ticker / analysis_date
        results_dir.mkdir(parents=True, exist_ok=True)
        report_dir = results_dir / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        self.call_from_thread(self._refresh_agent_table)
        
        # Initial Logging
        log_widget = self.query_one("#live-log", Log)
        self.call_from_thread(log_widget.write_line, f"User selected ticker: {ticker}")
        self.call_from_thread(log_widget.write_line, f"Analysis date: {analysis_date}")
        self.call_from_thread(log_widget.write_line, f"Starting analysis... (Depth: {depth})")

        init_agent_state = graph.propagator.create_initial_state(ticker, analysis_date)
        args = graph.propagator.get_graph_args(callbacks=[self.stats_handler])
        
        trace = []
        for chunk in graph.graph.stream(init_agent_state, **args):
            # Process messages
            if len(chunk["messages"]) > 0:
                last_message = chunk["messages"][-1]
                msg_id = getattr(last_message, "id", None)
                if msg_id != message_buffer._last_message_id:
                    message_buffer._last_message_id = msg_id
                    msg_type, content = classify_message_type(last_message)
                    if content and content.strip():
                        self.call_from_thread(log_widget.write_line, f"[{msg_type}] {content}")
                    
                    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                        for tool_call in last_message.tool_calls:
                            t_name = tool_call["name"] if isinstance(tool_call, dict) else tool_call.name
                            t_args = format_tool_args(tool_call["args"] if isinstance(tool_call, dict) else tool_call.args)
                            self.call_from_thread(log_widget.write_line, f"[Tool] {t_name}({t_args})")
            
            update_analyst_statuses(message_buffer, chunk)

            # Check for debate states to update status & reports
            if chunk.get("investment_debate_state"):
                debate_state = chunk["investment_debate_state"]
                bull_hist, bear_hist = debate_state.get("bull_history", ""), debate_state.get("bear_history", "")
                judge = debate_state.get("judge_decision", "")
                if bull_hist or bear_hist: update_research_team_status("in_progress")
                if bull_hist: message_buffer.update_report_section("investment_plan", f"### Bull Analysis\n{bull_hist}")
                if bear_hist: message_buffer.update_report_section("investment_plan", f"### Bear Analysis\n{bear_hist}")
                if judge: 
                    message_buffer.update_report_section("investment_plan", f"### Res Manager Dec\n{judge}")
                    update_research_team_status("completed")
                    message_buffer.update_agent_status("Trader", "in_progress")

            if chunk.get("trader_investment_plan"):
                message_buffer.update_report_section("trader_investment_plan", chunk["trader_investment_plan"])
                if message_buffer.agent_status.get("Trader") != "completed":
                    message_buffer.update_agent_status("Trader", "completed")
                    message_buffer.update_agent_status("Aggressive Analyst", "in_progress")

            if chunk.get("risk_debate_state"):
                risk_state = chunk["risk_debate_state"]
                agg_hist, con_hist, neu_hist = risk_state.get("aggressive_history", ""), risk_state.get("conservative_history", ""), risk_state.get("neutral_history", "")
                judge = risk_state.get("judge_decision", "")
                if agg_hist and message_buffer.agent_status.get("Aggressive Analyst") != "completed":
                    message_buffer.update_agent_status("Aggressive Analyst", "in_progress")
                if judge and message_buffer.agent_status.get("Portfolio Manager") != "completed":
                    message_buffer.update_agent_status("Portfolio Manager", "in_progress")
                    message_buffer.update_agent_status("Aggressive Analyst", "completed")
                    message_buffer.update_agent_status("Conservative Analyst", "completed")
                    message_buffer.update_agent_status("Neutral Analyst", "completed")
                    message_buffer.update_agent_status("Portfolio Manager", "completed")

            self.post_message(self.UpdateStatus())
            trace.append(chunk)

        final_state = trace[-1]
        for agent in message_buffer.agent_status:
            message_buffer.update_agent_status(agent, "completed")
            
        self.call_from_thread(log_widget.write_line, "Analysis Complete!")
        self.post_message(self.UpdateStatus())
        self.post_message(self.AnalysisComplete(final_state, results_dir))

    def on_trading_app_update_status(self, message: UpdateStatus):
        self._refresh_agent_table()
        self.update_stats_ui()
        if message_buffer.final_report:
            md = self.query_one("#md-reports", Markdown)
            md.update(message_buffer.final_report)

    def on_trading_app_analysis_complete(self, message: AnalysisComplete):
        ticker = self.query_one("#input-ticker", Input).value
        # Auto-save report on completion
        try:
            report_file = save_report_to_disk(message.final_state, ticker, message.results_dir)
            self.query_one("#live-log", Log).write_line(f"Saved complete report to: {report_file}")
        except Exception as e:
            self.query_one("#live-log", Log).write_line(f"Error saving report: {e}")
            
        btn = self.query_one("#start-btn", Button)
        btn.disabled = False
        btn.label = "RESTART ANALYSIS"
        
        # Switch to reports tab at the end
        tabs = self.query_one(TabbedContent)
        tabs.active = "tab-reports"

if __name__ == "__main__":
    app = TradingApp()
    app.run()
