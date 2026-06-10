"""
Regime Detection Agent
Advanced market regime detection
"""

import pandas as pd
import numpy as np


class RegimeAgent:

    def detect_regime(self, df):

        df = df.copy()

        df["ma50"] = df["Close"].rolling(50).mean()
        df["ma200"] = df["Close"].rolling(200).mean()

        returns = df["Close"].pct_change()

        df["volatility"] = returns.rolling(20).std()

        vol_threshold = df["volatility"].quantile(0.75)

        regimes = []

        for i in range(len(df)):

            if i < 200:
                regimes.append("UNKNOWN")
                continue

            close = df["Close"].iloc[i]

            ma50 = df["ma50"].iloc[i]
            ma200 = df["ma200"].iloc[i]

            current_vol = df["volatility"].iloc[i]

            ma50_slope = (
                df["ma50"].iloc[i]
                - df["ma50"].iloc[max(0, i - 10)]
            )

            if current_vol > vol_threshold:
                regimes.append("HIGH_VOL")

            elif (
                close > ma50
                and ma50 > ma200
                and ma50_slope > 0
            ):
                regimes.append("TREND_UP")

            elif (
                close < ma50
                and ma50 < ma200
                and ma50_slope < 0
            ):
                regimes.append("TREND_DOWN")

            else:
                regimes.append("RANGE")

        df["regime"] = regimes

        return df
