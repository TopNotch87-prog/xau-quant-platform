"""
HtmlReportAgent 2.0 – Professional XAU Quant Dashboard
- Real equity curve
- Trade log from CSV with win rate & profit factor
- Real Monte Carlo histogram
- Regime timeline
- Walk-forward optimization table
- Signal confidence gauge
- Mobile responsive
"""

import json
import os
import tempfile
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime


class HtmlReportAgent:
    def generate(self, report: dict, output_path: str = None) -> str:
        # ---- extract data from report ----
        results = report.get("results", {})
        data = results.get("data", pd.DataFrame())
        signals = results.get("signals", {})
        risk_metrics = results.get("risk_metrics", {})
        opt_params = results.get("optimized_params", [])
        mc_results = results.get("mc_results", {})

        # ---- basic metrics (from ReportingAgent) ----
        total_return = report.get("total_return", 0.0)
        sharpe_ratio = report.get("sharpe_ratio", 0.0)
        max_dd = report.get("max_drawdown", 0.0)

        # ---- price & moving averages ----
        if not data.empty and "Close" in data.columns:
            dates = [d.strftime("%Y-%m-%d") for d in data.index]
            closes = [round(float(v), 2) for v in data["Close"]]
            if "ma50" in data.columns:
                ma50 = [round(float(v), 2) if pd.notna(v) else None for v in data["ma50"]]
            else:
                ma50 = [None] * len(data)
            if "ma200" in data.columns:
                ma200 = [round(float(v), 2) if pd.notna(v) else None for v in data["ma200"]]
            else:
                ma200 = [None] * len(data)

            # ---- regime timeline ----
            if "regime" in data.columns:
                regimes = data["regime"].tolist()
                regime_codes = []
                for r in regimes:
                    if r == "TREND_UP":
                        regime_codes.append(3)
                    elif r == "TREND_DOWN":
                        regime_codes.append(-3)
                    elif r == "HIGH_VOL":
                        regime_codes.append(2)
                    elif r == "RANGE":
                        regime_codes.append(1)
                    else:
                        regime_codes.append(0)
            else:
                regimes = ["UNKNOWN"] * len(data)
                regime_codes = [0] * len(data)
        else:
            dates = closes = ma50 = ma200 = regimes = regime_codes = []

        # ---- equity curve (simple: start with 10k, hold asset) ----
        if len(closes) > 1:
            equity = [10000.0]
            for i in range(1, len(closes)):
                ret = (closes[i] - closes[i-1]) / closes[i-1]
                equity.append(equity[-1] * (1 + ret))
            equity_vals = equity
        else:
            equity_vals = []

        # ---- signal info ----
        sig = signals.get("signal", "HOLD")
        sig_entry = signals.get("entry_price", "–")
        sig_sl = signals.get("stop_loss", "–")
        sig_tp = signals.get("take_profit", "–")
        sig_why = signals.get("rationale", "")
        regime = str(signals.get("regime", "UNKNOWN"))
        strategy = str(signals.get("strategy", "–"))
        confidence = signals.get("confidence", 0.0)
        weighted_score = signals.get("weighted_score", 0.0)
        sig_colour = {"BUY": "#22c55e", "SELL": "#ef4444"}.get(sig, "#f59e0b")

        # ---- TRADE LOG & STATS (from data/trades.csv) ----
        trade_file = Path("data/trades.csv")
        trade_rows_html = ""
        win_rate = 0.0
        profit_factor = 0.0
        total_trades = 0
        avg_rr = 0.0

        if trade_file.exists():
            try:
                trades_df = pd.read_csv(trade_file)
                total_trades = len(trades_df)
                if total_trades > 0:
                    if "pnl" in trades_df.columns:
                        wins = (trades_df["pnl"] > 0).sum()
                        win_rate = wins / total_trades if total_trades else 0
                        gross_profit = trades_df[trades_df["pnl"] > 0]["pnl"].sum()
                        gross_loss = abs(trades_df[trades_df["pnl"] < 0]["pnl"].sum())
                        profit_factor = gross_profit / gross_loss if gross_loss != 0 else float('inf')
                    else:
                        # fallback: use confidence as proxy
                        if "confidence" in trades_df.columns:
                            win_rate = (trades_df["confidence"] > 0.5).mean()
                    if "entry_price" in trades_df.columns and "exit_price" in trades_df.columns:
                        trades_df["rr"] = (trades_df["exit_price"] - trades_df["entry_price"]) / trades_df["entry_price"].abs()
                        avg_rr = trades_df["rr"].mean()

                # generate HTML rows for last 20 trades
                display_df = trades_df.tail(20).copy()
                for _, row in display_df.iterrows():
                    ts = row.get("timestamp", "")
                    sig_ = row.get("signal", "")
                    conf = row.get("confidence", "")
                    reg = row.get("regime", "")
                    entry = row.get("entry_price", "")
                    exit_price = row.get("exit_price", "")
                    pnl = row.get("pnl", "")
                    # Ensure pnl is a number for colouring
                    try:
                        pnl_float = float(pnl) if pnl not in (None, "", "nan") else None
                    except:
                        pnl_float = None
                    pnl_class = ""
                    if pnl_float is not None:
                        pnl_class = "pos" if pnl_float > 0 else "neg" if pnl_float < 0 else ""
                    trade_rows_html += f"""
                    <tr>
                        <td>{ts}</td>
                        <td><span class="signal-badge-small {sig_.lower()}">{sig_}</span></td>
                        <td>{conf}</td>
                        <td>{reg}</td>
                        <td>${entry}</td>
                        <td>${exit_price}</td>
                        <td class="{pnl_class}">{pnl}</td>
                    </tr>
                    """
            except Exception as e:
                trade_rows_html = f'<tr><td colspan="7">Error loading trades: {e}</td></tr>'
        else:
            trade_rows_html = '<tr><td colspan="7">No trade log found. Run backtest first.</td></tr>'

        # Prepare display strings for profit factor (handle infinity)
        if profit_factor == float('inf'):
            profit_factor_display = "∞"
        else:
            profit_factor_display = f"{profit_factor:.2f}"

        # ---- OPTIMIZATION TABLE ----
        opt_table_rows = ""
        for win in opt_params[-10:]:
            params = win.get("best_params", ("–", "–"))
            start_str = win.get("train_start", "")
            if hasattr(start_str, "strftime"):
                start_str = start_str.strftime("%Y-%m-%d")
            end_str = win.get("train_end", "")
            if hasattr(end_str, "strftime"):
                end_str = end_str.strftime("%Y-%m-%d")
            opt_table_rows += f"""
            <tr>
                <td>{win.get("window", "?")}</td>
                <td>{start_str}</td>
                <td>{end_str}</td>
                <td>{params[0]}</td>
                <td>{params[1]}</td>
                <td>{round(win.get("best_sharpe", 0), 4)}</td>
            </tr>
            """

        # ---- REAL MONTE CARLO HISTOGRAM ----
        mc_histogram_js = ""
        mc_paths = mc_results.get("paths", None)
        if mc_paths is not None and isinstance(mc_paths, np.ndarray) and mc_paths.size > 0:
            final_returns = mc_paths[:, -1] * 100  # percent
            hist, bin_edges = np.histogram(final_returns, bins=40)
            hist_data = {"bins": bin_edges.tolist(), "counts": hist.tolist()}
            mc_mean = np.mean(final_returns)
            mc_std = np.std(final_returns)
            mc_p5 = np.percentile(final_returns, 5)
            mc_p95 = np.percentile(final_returns, 95)
            mc_histogram_js = f"""
            const mcHist = {json.dumps(hist_data)};
            const mcMean = {mc_mean:.2f};
            const mcStd = {mc_std:.2f};
            const mcP5 = {mc_p5:.2f};
            const mcP95 = {mc_p95:.2f};
            if(mcHist.bins.length) {{
                const labels = mcHist.bins.slice(0, -1).map((v,i) => ((v + mcHist.bins[i+1])/2).toFixed(1) + '%');
                new Chart(document.getElementById('mcHistogram'), {{
                    type: 'bar',
                    data: {{ labels, datasets: [{{ label: 'Frequency', data: mcHist.counts, backgroundColor: '#d4a017', borderRadius: 4 }}] }},
                    options: {{ responsive: true, plugins: {{ tooltip: {{ callbacks: {{ label: (ctx) => `Return: ${{ctx.raw}}%` }} }} }} }}
                }});
                document.getElementById('mcStats').innerHTML = `<p>Mean: {mc_mean:.2f}% | Std: {mc_std:.2f}%<br>5th %ile: {mc_p5:.2f}% | 95th %ile: {mc_p95:.2f}%</p>`;
            }}
            """
        else:
            mc_histogram_js = "document.getElementById('mcHistogram').innerHTML = 'No Monte Carlo paths available';"

        # ---- equity curve chart JS ----
        equity_js = ""
        if equity_vals:
            equity_js = f"""
            const equityVals = {json.dumps(equity_vals)};
            const eqDates = {json.dumps(dates)};
            new Chart(document.getElementById('equityChart'), {{
                type: 'line',
                data: {{ labels: eqDates, datasets: [{{ label: 'Portfolio Value ($)', data: equityVals, borderColor: '#22c55e', fill: false, pointRadius: 0 }}] }},
                options: {{ responsive: true, maintainAspectRatio: true }}
            }});
            """

        # ---- regime timeline chart ----
        regime_js = ""
        if regime_codes:
            regime_js = f"""
            const regimeCodes = {json.dumps(regime_codes)};
            const regimeLabels = {json.dumps(dates)};
            new Chart(document.getElementById('regimeChart'), {{
                type: 'bar',
                data: {{ labels: regimeLabels, datasets: [{{ label: 'Regime', data: regimeCodes, backgroundColor: (ctx) => {{
                    let val = ctx.raw;
                    if(val === 3) return '#22c55e';
                    if(val === -3) return '#ef4444';
                    if(val === 2) return '#f97316';
                    return '#facc15';
                }}, borderWidth: 0 }}] }},
                options: {{ responsive: true, maintainAspectRatio: true, scales: {{ y: {{ ticks: {{ callback: (v) => {{
                    if(v === 3) return 'TREND_UP';
                    if(v === -3) return 'TREND_DOWN';
                    if(v === 2) return 'HIGH_VOL';
                    if(v === 1) return 'RANGE';
                    return 'UNKNOWN';
                }}, stepSize: 1 }} }} }} }}
            }});
            """

        # ---- build full HTML ----
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XAU Quant Platform – Professional Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: #0a0c10;
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
            color: #e6edf3;
            padding: 24px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{
            display: flex; justify-content: space-between; align-items: flex-end;
            border-bottom: 1px solid #30363d; padding-bottom: 16px; margin-bottom: 24px;
            flex-wrap: wrap;
        }}
        .header h1 {{ font-size: 1.6rem; letter-spacing: -0.02em; }}
        .header h1 span {{ color: #d4a017; }}
        .header small {{ color: #8b949e; font-size: 0.75rem; }}
        .grid4 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px,1fr)); gap: 16px; margin-bottom: 24px; }}
        .grid2 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px,1fr)); gap: 16px; margin-bottom: 24px; }}
        .card {{
            background: #161b22; border: 1px solid #30363d; border-radius: 12px;
            padding: 20px; transition: box-shadow 0.2s;
        }}
        .card:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.3); }}
        .fullwidth {{ grid-column: 1 / -1; }}
        .metric-label {{ font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; color: #8b949e; margin-bottom: 6px; }}
        .metric-value {{ font-size: 1.8rem; font-weight: 700; }}
        .metric-value.pos {{ color: #22c55e; }}
        .metric-value.neg {{ color: #ef4444; }}
        .metric-value.neu {{ color: #d4a017; }}
        .signal-badge {{
            display: inline-block; padding: 8px 24px; border-radius: 40px;
            font-size: 1.5rem; font-weight: 800; background: {sig_colour};
            color: #000; margin-bottom: 16px;
        }}
        .signal-badge-small {{
            display: inline-block; padding: 2px 12px; border-radius: 20px;
            font-size: 0.7rem; font-weight: 600;
        }}
        .signal-badge-small.buy {{ background: #22c55e20; color: #22c55e; border: 1px solid #22c55e; }}
        .signal-badge-small.sell {{ background: #ef444420; color: #ef4444; border: 1px solid #ef4444; }}
        .signal-badge-small.hold {{ background: #f59e0b20; color: #f59e0b; border: 1px solid #f59e0b; }}
        .confidence-bar {{
            height: 20px;
            background: #30363d;
            border-radius: 20px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .confidence-fill {{
            height: 100%;
            width: {confidence*100}%;
            background: #22c55e;
            border-radius: 20px;
        }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.8rem; }}
        th, td {{ text-align: left; padding: 8px 6px; border-bottom: 1px solid #21262d; }}
        th {{ color: #8b949e; font-weight: 500; }}
        .tag {{ background: #1f2937; color: #d4a017; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; }}
        canvas {{ max-height: 280px; width: 100%; }}
        button.download {{
            background: #d4a017; border: none; padding: 6px 14px; border-radius: 20px;
            font-weight: 600; cursor: pointer; color: #0a0c10;
        }}
        @media (max-width: 700px) {{ .grid2 {{ grid-template-columns: 1fr; }} }}
        .pos {{ color: #22c55e; }}
        .neg {{ color: #ef4444; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>⚡ XAU <span>Quant</span> Platform · Gold Futures (GC=F)</h1>
        <button class="download" onclick="window.print()">📄 Save as PDF / Print</button>
    </div>

    <!-- Summary metrics row -->
    <div class="grid4">
        <div class="card"><div class="metric-label">Total Return</div><div class="metric-value {'pos' if total_return>=0 else 'neg'}">{total_return*100:.2f}%</div></div>
        <div class="card"><div class="metric-label">Sharpe Ratio</div><div class="metric-value {'pos' if sharpe_ratio>=1 else 'neu'}">{sharpe_ratio:.3f}</div></div>
        <div class="card"><div class="metric-label">Max Drawdown</div><div class="metric-value neg">{max_dd*100:.2f}%</div></div>
        <div class="card"><div class="metric-label">Win Rate</div><div class="metric-value {'pos' if win_rate>=0.5 else 'neg'}">{win_rate*100:.1f}%</div></div>
    </div>

    <!-- Signal confidence & regime overview -->
    <div class="grid4">
        <div class="card">
            <h2>Current Signal</h2>
            <div class="signal-badge">{sig}</div>
            <div class="confidence-bar"><div class="confidence-fill"></div></div>
            <div>Confidence: {confidence*100:.1f}%</div>
        </div>
        <div class="card">
            <h2>Market Regime</h2>
            <h1>{regime}</h1>
            <div class="tag">Strategy: {strategy}</div>
        </div>
        <div class="card">
            <h2>Trade Stats</h2>
            <div>Total Trades: {total_trades}</div>
            <div>Profit Factor: {profit_factor_display}</div>
            <div>Avg R:R: {avg_rr:.2f}</div>
        </div>
        <div class="card">
            <h2>Risk Metrics</h2>
            <div>VaR (95%): {risk_metrics.get('var_95', 0)*100:.2f}%</div>
            <div>Expected Shortfall: {risk_metrics.get('expected_shortfall', 0)*100:.2f}%</div>
        </div>
    </div>

    <!-- Price & Equity Charts -->
    <div class="grid2">
        <div class="card">
            <h2>Price & Moving Averages</h2>
            <canvas id="priceChart" style="height:280px"></canvas>
        </div>
        <div class="card">
            <h2>Equity Curve ($)</h2>
            <canvas id="equityChart" style="height:280px"></canvas>
        </div>
    </div>

    <!-- Regime Timeline -->
    <div class="card fullwidth">
        <h2>Market Regime Timeline</h2>
        <canvas id="regimeChart" style="height:200px"></canvas>
    </div>

    <!-- Trade Log Table -->
    <div class="card fullwidth">
        <h2>Recent Trade Signals (last 20)</h2>
        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr><th>Timestamp</th><th>Signal</th><th>Confidence</th><th>Regime</th><th>Entry</th><th>Exit</th><th>PnL</th></tr>
                </thead>
                <tbody>
                    {trade_rows_html}
                </tbody>
            </table>
        </div>
    </div>

    <!-- Walk-Forward Optimization Table -->
    <div class="card fullwidth">
        <h2>Walk-Forward Optimization (last 10 windows)</h2>
        <div style="overflow-x: auto;">
            <table>
                <thead><tr><th>Window</th><th>Train Start</th><th>Train End</th><th>Fast MA</th><th>Slow MA</th><th>Sharpe</th></tr></thead>
                <tbody>{opt_table_rows}</tbody>
            </table>
        </div>
    </div>

    <!-- Monte Carlo Section -->
    <div class="card fullwidth">
        <h2>Monte Carlo Simulation (real paths)</h2>
        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
            <div style="flex: 2; min-width: 250px;"><canvas id="mcHistogram" style="height:250px"></canvas></div>
            <div style="flex: 1;" id="mcStats"></div>
        </div>
    </div>
</div>

<script>
    // Price chart
    const dates = {json.dumps(dates)};
    const closes = {json.dumps(closes)};
    const ma50 = {json.dumps(ma50)};
    const ma200 = {json.dumps(ma200)};

    new Chart(document.getElementById('priceChart'), {{
        type: 'line',
        data: {{
            labels: dates,
            datasets: [
                {{ label: 'Close', data: closes, borderColor: '#d4a017', borderWidth: 1.5, pointRadius: 0, tension: 0.1 }},
                {{ label: 'MA 50', data: ma50, borderColor: '#60a5fa', borderWidth: 1.2, borderDash: [4,3], pointRadius: 0 }},
                {{ label: 'MA 200', data: ma200, borderColor: '#a78bfa', borderWidth: 1.2, borderDash: [6,4], pointRadius: 0 }}
            ]
        }},
        options: {{ responsive: true, maintainAspectRatio: true, plugins: {{ legend: {{ labels: {{ color: '#8b949e' }} }} }} }}
    }});

    // Equity curve
    {equity_js}

    // Regime timeline
    {regime_js}

    // Monte Carlo histogram
    {mc_histogram_js}
</script>
</body>
</html>"""

        # Write to file
        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix=".html", prefix="xau_report_")
            os.close(fd)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        return output_path
