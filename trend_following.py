"""Trend following — MA crossover. Returns numeric score in [-1, 1]."""

def signal(df, fast=45, slow=70):
    close   = df["Close"]
    fast_ma = float(close.rolling(fast).mean().iloc[-1])
    slow_ma = float(close.rolling(slow).mean().iloc[-1])
    gap_pct = (fast_ma - slow_ma) / (slow_ma + 1e-9)
    return max(-1.0, min(1.0, gap_pct * 20))
