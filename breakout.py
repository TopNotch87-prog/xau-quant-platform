"""Breakout strategy — Donchian Channel. Returns numeric score in [-1, 1]."""
import numpy as np

def signal(df, period=20):
    high  = df["High"].rolling(period).max().shift(1)
    low   = df["Low"].rolling(period).min().shift(1)
    close = float(df["Close"].iloc[-1])
    d_high, d_low = float(high.iloc[-1]), float(low.iloc[-1])
    channel = d_high - d_low + 1e-9
    if close > d_high:
        return min(1.0, (close - d_high) / (channel * 0.05))
    if close < d_low:
        return -min(1.0, (d_low - close) / (channel * 0.05))
    return 0.0
