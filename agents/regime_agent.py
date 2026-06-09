"""
Regime Detection Agent
Detects market regime (trending, range, high volatility)
"""
import pandas as pd
import numpy as np

class RegimeAgent:

    def detect_regime(self, df):
        """Detect market regime based on technical indicators"""
        df["ma50"] = df["Close"].rolling(50).mean()
        df["ma200"] = df["Close"].rolling(200).mean()

        returns = df["Close"].pct_change()

        volatility = returns.rolling(50).std()

        conditions = []

        for i in range(len(df)):

            if volatility.iloc[i] > volatility.quantile(0.75):

                conditions.append("HIGH_VOL")

            elif df["ma50"].iloc[i] > df["ma200"].iloc[i]:

                conditions.append("TREND_UP")

            elif df["ma50"].iloc[i] < df["ma200"].iloc[i]:

                conditions.append("TREND_DOWN")

            else:

                conditions.append("RANGE")

        df["regime"] = conditions

        return df
