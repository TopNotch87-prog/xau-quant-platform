"""
Regime Detection Agent
Detects market regime (trending, range, high volatility)
"""

import pandas as pd
import numpy as np


class RegimeAgent:

    def detect_regime(self, df):
        """
        Detect market regime based on moving averages and volatility.
        Returns the dataframe with a 'regime' column added.
        """

        df = df.copy()

        df["ma50"] = df["Close"].rolling(50).mean()
        df["ma200"] = df["Close"].rolling(200).mean()

        returns = df["Close"].pct_change()
        volatility = returns.rolling(50).std()

        vol_threshold = volatility.quantile(0.75)

        conditions = []

        for i in range(len(df)):

            current_vol = volatility.iloc[i]
            ma50 = df["ma50"].iloc[i]
            ma200 = df["ma200"].iloc[i]

            if pd.isna(current_vol) or pd.isna(ma50) or pd.isna(ma200):
                conditions.append("UNKNOWN")

            elif current_vol > vol_threshold:
                conditions.append("HIGH_VOL")

            elif ma50 > ma200:
                conditions.append("TREND_UP")

            elif ma50 < ma200:
                conditions.append("TREND_DOWN")

            else:
                conditions.append("RANGE")

        df["regime"] = conditions

        return df
