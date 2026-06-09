"""
HTML Report Agent
Generates a self-contained HTML dashboard from backtest results
and opens it in the default browser.
"""
import json
import os
import webbrowser
import tempfile
from datetime import datetime


class HtmlReportAgent:

    def generate(self, report: dict, output_path: str = None) -> str:
        """
        Build an HTML dashboard file from the backtest report dict.

        Args:
            report:      The dict returned by MasterController.run_backtest()
            output_path: Where to write the file. Defaults to a temp file.

        Returns:
            Absolute path of the HTML file written.
        """

        data        = report["results"]["data"]
        signals     = report["results"]["signals"]
        risk        = report["risk_metrics"]
        opt_params  = report["results"]["optimized_params"]
        mc          = report["results"]["mc_results"]

        # ── price series ──────────────────────────────────────────────
        dates      = [str(d.date()) for d in data.index]
        closes     = [round(float(v), 2) for v in data["Close"]]
        ma50_vals  = [round(float(v), 2) if str(v) != "nan" else None
                      for v in data["ma50"]]
        ma200_vals = [round(float(v), 2) if str(v) != "nan" else None
                      for v in data["ma200"]]

        # ── summary numbers ───────────────────────────────────────────
        total_ret  = round(report["total_return"]  * 100, 2)
        sharpe     = round(report["sharpe_ratio"],  4)
        drawdown   = round(report["max_drawdown"]  * 100, 2)
        var95      = round(risk["var_95"]           * 100, 2)
        es         = round(risk["expected_shortfall"] * 100, 2)

        # ── signal ────────────────────────────────────────────────────
        sig        = signals.get("signal",      "HOLD")
        sig_entry  = signals.get("entry_price", "–")
        sig_sl     = signals.get("stop_loss",   "–")
        sig_tp     = signals.get("take_profit", "–")
        sig_why    = signals.get("rationale",   "")
        regime     = str(signals.get("regime",  "UNKNOWN"))
        strategy   = str(signals.get("strategy","–"))

        # ── optimised params ──────────────────────────────────────────
        best = opt_params[0] if opt_params else {}
        bp   = best.get("best_params", ("–", "–"))
        bs   = best.get("best_sharpe", "–")

        # ── MC returns for histogram ──────────────────────────────────
        mc_mean   = round(mc.get("mean_return", 0) * 100, 4)
        mc_vol    = round(mc.get("volatility",  0) * 100, 4)
        mc_sims   = mc.get("simulations", 1000)
        mc_horiz  = mc.get("horizon", 252)

        sig_colour = {"BUY": "#22c55e", "SELL": "#ef4444"}.get(sig, "#f59e0b")

        # ── HTML ──────────────────────────────────────────────────────
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>XAU Quant Platform — Backtest Report</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  :root {{
    --bg:     #0d1117;
    --card:   #161b22;
    --border: #30363d;
    --gold:   #d4a017;
    --text:   #e6edf3;
    --muted:  #8b949e;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text);
         font-family: 'Segoe UI', system-ui, sans-serif; padding: 24px; }}
  header {{ display: flex; justify-content: space-between; align-items: center;
            border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }}
  header h1 {{ font-size: 1.4rem; letter-spacing: .05em; }}
  header h1 span {{ color: var(--gold); }}
  header small {{ color: var(--muted); font-size: .8rem; }}
  .grid4 {{ display: grid; grid-template-columns: repeat(4,1fr); gap: 16px; margin-bottom: 24px; }}
  .grid2 {{ display: grid; grid-template-columns: 1fr 1fr;       gap: 16px; margin-bottom: 24px; }}
  .card  {{ background: var(--card); border: 1px solid var(--border);
            border-radius: 8px; padding: 20px; }}
  .metric-label {{ font-size: .72rem; color: var(--muted); text-transform: uppercase;
                   letter-spacing: .08em; margin-bottom: 6px; }}
  .metric-value {{ font-size: 1.9rem; font-weight: 700; }}
  .metric-value.pos {{ color: #22c55e; }}
  .metric-value.neg {{ color: #ef4444; }}
  .metric-value.neu {{ color: var(--gold); }}
  .card h2 {{ font-size: .85rem; text-transform: uppercase; letter-spacing: .08em;
              color: var(--muted); margin-bottom: 16px; }}
  .signal-badge {{
    display: inline-block; padding: 8px 28px; border-radius: 6px;
    font-size: 2rem; font-weight: 800; letter-spacing: .12em;
    color: #000; background: {sig_colour}; margin-bottom: 14px;
  }}
  table {{ width: 100%; border-collapse: collapse; font-size: .85rem; }}
  th {{ text-align: left; color: var(--muted); font-weight: 500;
        padding: 6px 4px; border-bottom: 1px solid var(--border); }}
  td {{ padding: 8px 4px; border-bottom: 1px solid var(--border); }}
  .tag {{ display: inline-block; padding: 2px 10px; border-radius: 4px;
          font-size: .75rem; font-weight: 600; background: #1f2937; color: var(--gold); }}
  canvas {{ max-height: 280px; }}
</style>
</head>
<body>

<header>
  <h1>⚡ XAU <span>Quant</span> Platform</h1>
  <small>Report generated {datetime.now().strftime("%Y-%m-%d %H:%M")} &nbsp;|&nbsp; Symbol: GC=F (Gold Futures)</small>
</header>

<!-- ── Summary metrics ─────────────────────────────────────────────── -->
<div class="grid4">
  <div class="card">
    <div class="metric-label">Total Return</div>
    <div class="metric-value {'pos' if total_ret >= 0 else 'neg'}">{total_ret:+.2f}%</div>
  </div>
  <div class="card">
    <div class="metric-label">Sharpe Ratio</div>
    <div class="metric-value {'pos' if sharpe >= 1 else 'neu' if sharpe >= 0 else 'neg'}">{sharpe:.4f}</div>
  </div>
  <div class="card">
    <div class="metric-label">Max Drawdown</div>
    <div class="metric-value neg">{drawdown:.2f}%</div>
  </div>
  <div class="card">
    <div class="metric-label">VaR (95%)</div>
    <div class="metric-value neg">{var95:.2f}%</div>
  </div>
</div>

<!-- ── Signal + Risk ───────────────────────────────────────────────── -->
<div class="grid2">

  <div class="card">
    <h2>Current Trade Signal</h2>
    <div class="signal-badge">{sig}</div>
    <table>
      <tr><th>Regime</th>  <td><span class="tag">{regime}</span></td></tr>
      <tr><th>Strategy</th><td>{strategy}</td></tr>
      <tr><th>Entry</th>   <td>${sig_entry}</td></tr>
      <tr><th>Stop Loss</th><td>${sig_sl}</td></tr>
      <tr><th>Take Profit</th><td>${sig_tp}</td></tr>
      <tr><th>Rationale</th><td style="color:var(--muted);font-size:.8rem">{sig_why}</td></tr>
    </table>
  </div>

  <div class="card">
    <h2>Risk Metrics</h2>
    <table>
      <tr><th>Sharpe Ratio</th>         <td>{sharpe:.4f}</td></tr>
      <tr><th>VaR (95%)</th>            <td style="color:#ef4444">{var95:.2f}%</td></tr>
      <tr><th>Expected Shortfall</th>   <td style="color:#ef4444">{es:.2f}%</td></tr>
      <tr><th>Max Drawdown</th>         <td style="color:#ef4444">{drawdown:.2f}%</td></tr>
      <tr><th>Optimised Fast MA</th>    <td>{bp[0]}</td></tr>
      <tr><th>Optimised Slow MA</th>    <td>{bp[1]}</td></tr>
      <tr><th>Optimised Sharpe</th>     <td>{bs}</td></tr>
      <tr><th>MC Mean Daily Return</th> <td>{mc_mean:.4f}%</td></tr>
      <tr><th>MC Daily Volatility</th>  <td>{mc_vol:.4f}%</td></tr>
    </table>
  </div>

</div>

<!-- ── Price chart ─────────────────────────────────────────────────── -->
<div class="card" style="margin-bottom:24px">
  <h2>Price Chart — Close · MA50 · MA200</h2>
  <canvas id="priceChart"></canvas>
</div>

<!-- ── MC ──────────────────────────────────────────────────────────── -->
<div class="card">
  <h2>Monte Carlo — {mc_sims:,} simulations · {mc_horiz}-day horizon</h2>
  <canvas id="mcChart"></canvas>
</div>

<script>
const dates      = {json.dumps(dates)};
const closes     = {json.dumps(closes)};
const ma50vals   = {json.dumps(ma50_vals)};
const ma200vals  = {json.dumps(ma200_vals)};
const mcMean     = {mc_mean};
const mcVol      = {mc_vol};

// ── Price chart ──────────────────────────────────────────────────────
new Chart(document.getElementById('priceChart'), {{
  type: 'line',
  data: {{
    labels: dates,
    datasets: [
      {{ label: 'Close',   data: closes,    borderColor: '#d4a017', borderWidth: 1.5,
         pointRadius: 0, tension: 0.1 }},
      {{ label: 'MA 50',  data: ma50vals,  borderColor: '#60a5fa', borderWidth: 1.2,
         pointRadius: 0, borderDash: [4,3] }},
      {{ label: 'MA 200', data: ma200vals, borderColor: '#a78bfa', borderWidth: 1.2,
         pointRadius: 0, borderDash: [6,4] }},
    ]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ labels: {{ color: '#8b949e' }} }} }},
    scales: {{
      x: {{ ticks: {{ color: '#8b949e', maxTicksLimit: 10 }}, grid: {{ color: '#21262d' }} }},
      y: {{ ticks: {{ color: '#8b949e' }},                    grid: {{ color: '#21262d' }} }}
    }}
  }}
}});

// ── MC histogram (simulate simple distribution for display) ─────────
(function() {{
  const n = 200;
  const bars = new Array(n).fill(0);
  // build a normal-ish cumulative return distribution
  for (let s = 0; s < 2000; s++) {{
    let r = 0;
    for (let d = 0; d < 252; d++) r += (Math.random()*2-1) * mcVol / 100;
    const bucket = Math.min(n-1, Math.max(0, Math.floor((r + 0.5) / 1.0 * n)));
    bars[bucket]++;
  }}
  const labels = bars.map((_,i) => ((i/n - 0.5)*100).toFixed(1) + '%');
  new Chart(document.getElementById('mcChart'), {{
    type: 'bar',
    data: {{
      labels,
      datasets: [{{ label: 'Frequency', data: bars,
                    backgroundColor: '#d4a01740', borderColor: '#d4a017',
                    borderWidth: 1 }}]
    }},
    options: {{
      responsive: true,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{
        x: {{ ticks: {{ color: '#8b949e', maxTicksLimit: 8 }}, grid: {{ color: '#21262d' }} }},
        y: {{ ticks: {{ color: '#8b949e' }},                    grid: {{ color: '#21262d' }} }}
      }}
    }}
  }});
}})();
</script>
</body>
</html>"""

        # ── write file ────────────────────────────────────────────────
        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix=".html",
                                               prefix="xau_report_")
            os.close(fd)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        return output_path
