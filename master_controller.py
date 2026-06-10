"""
Master Controller
Orchestrates all agents and manages the overall platform workflow
"""

import webbrowser

from agents.data_agent import DataAgent
from agents.regime_agent import RegimeAgent
from agents.strategy_agent import StrategyAgent
from agents.optimization_agent import OptimizationAgent
from agents.risk_agent import RiskAgent
from agents.montecarlo_agent import MonteCarloAgent
from agents.reporting_agent import ReportingAgent
from agents.html_report_agent import HtmlReportAgent
from utils.trade_logger import TradeLogger


class MasterController:

    def __init__(self, config):
        self.config = config
        self.data_agent         = DataAgent()
        self.regime_agent       = RegimeAgent()
        self.strategy_agent     = StrategyAgent()
        self.optimization_agent = OptimizationAgent()
        self.risk_agent         = RiskAgent()
        self.montecarlo_agent   = MonteCarloAgent()
        self.reporting_agent    = ReportingAgent()
        self.html_report_agent  = HtmlReportAgent()
        self.trade_logger       = TradeLogger()

    def run_backtest(self):
        print("Starting backtest workflow...")

        # ── Step 1: Fetch Data ────────────────────────────────────────
        print("Step 1: Fetching market data...")
        data = self.data_agent.fetch_market_data(
            symbol=self.config.get("symbol", "GC=F"),
            start_date=self.config.get("start_date"),
            end_date=self.config.get("end_date"),
        )
        if data is None or len(data) == 0:
            raise ValueError("No market data returned")
        print(f"Rows downloaded: {len(data)}")

        # ── Step 2: Detect Regime ────────────────────────────────────
        print("Step 2: Detecting market regime...")
        data = self.regime_agent.detect_regime(data)
        current_regime = data["regime"].iloc[-1]
        print(f"Current Regime: {current_regime}")

        # ── Step 3: Generate Signals ─────────────────────────────────
        print("Step 3: Generating trading signals...")
        signals = self.strategy_agent.generate_signals(data, current_regime)
        self.trade_logger.log(signals)

        if signals.get("confidence", 1.0) < 0.15:
            signals["signal"]    = "HOLD"
            signals["rationale"] = "Confidence below threshold"

        print("\n================ SIGNALS ================")
        print(signals)

        # ── Step 4: Walk-Forward Optimisation ────────────────────────
        print("Step 4: Optimizing strategy parameters...")
        optimized_params = self.optimization_agent.walk_forward_optimization(
            data, self.strategy_agent, window_size=252
        )
        if optimized_params:
            latest = optimized_params[-1]
            if latest.get("best_params"):
                fast, slow = latest["best_params"]
                self.strategy_agent.fast_ma = fast
                self.strategy_agent.slow_ma = slow
                print(f"Using optimized parameters FAST={fast} SLOW={slow}")

        print("\n========== OPTIMIZED PARAMETERS ==========")
        print(optimized_params)

        # ── Step 5: Risk Assessment ───────────────────────────────────
        print("Step 5: Assessing portfolio risk...")
        risk_metrics = self.risk_agent.assess_portfolio_risk(signals, data)
        print("\n============= RISK METRICS =============")
        print(risk_metrics)

        # ── Step 6: Monte Carlo ───────────────────────────────────────
        print("Step 6: Running Monte Carlo simulations...")
        mc_results = self.montecarlo_agent.generate_price_paths(
            data, num_simulations=1000, horizon=252
        )
        print("\n=========== MONTE CARLO TYPE ===========")
        print(type(mc_results))
        try:
            print(f"Monte Carlo paths: {len(mc_results)}")
        except Exception:
            pass

        # ── Step 7: Report ────────────────────────────────────────────
        print("Step 7: Generating report...")
        report = self.reporting_agent.generate_backtest_report({
            "data":             data,
            "signals":          signals,
            "optimized_params": optimized_params,
            "risk_metrics":     risk_metrics,
            "mc_results":       mc_results,
        })
        print("\n================ REPORT ================")
        print(report)
        print("\nBacktest workflow completed!")

        html_path = self.html_report_agent.generate(report)
        print(f"\n📊 Dashboard saved to: {html_path}")
        webbrowser.open(f"file://{html_path}")

        return report

    def run_optimization(self):
        print("Starting optimization workflow...")

    def run_live_trading(self):
        print("Starting live trading workflow...")
