# XAU Quant Platform

A multi-agent quantitative research framework for XAUUSD.

## Recommended Structure

```
xau-quant-platform/
│
├── agents/
│   ├── data_agent.py
│   ├── regime_agent.py
│   ├── strategy_agent.py
│   ├── optimization_agent.py
│   ├── risk_agent.py
│   ├── montecarlo_agent.py
│   └── reporting_agent.py
│
├── strategies/
├── backtests/
├── notebooks/
├── reports/
├── data/
├── tests/
├── requirements.txt
├── .gitignore
├── config.py
└── master_controller.py
```

## Core Features

- Data acquisition
- Regime detection
- Walk-forward optimization
- Monte Carlo stress testing
- Sharpe, Sortino, Calmar
- VaR and Expected Shortfall
- Trade logging
- Risk reports
- Equity curves
