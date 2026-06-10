"""
Data Collection Agent
Handles real market data retrieval and preprocessing for XAUUSD / GC=F
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


class DataAgent:

    def fetch_market_data(
        self,
        symbol: str = "GC=F",
        start_date: str = None,
        end_date: str = None
    ):
        """
        Fetch real OHLCV data from Yahoo Finance.

        Args:
            symbol:     Ticker symbol. GC=F = Gold Futures (front month),
                        XAUUSD=X = Spot gold (less reliable on yfinance)
            start_date: 'YYYY-MM-DD' string or None (defaults to 1 year ago)
            end_date:   'YYYY-MM-DD' string or None (defaults to today)

        Returns:
            DataFrame with Open/High/Low/Close/Volume columns indexed by Date
        """

        if not YFINANCE_AVAILABLE:
            raise ImportError(
                "yfinance is not installed. Run: pip install yfinance"
            )

        # ── date range ────────────────────────────────────────────────
        if end_date is None:
            end_dt = datetime.now()
        else:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        if start_date is None:
            start_dt = end_dt - timedelta(days=365)
        else:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")

        start_str = start_dt.strftime("%Y-%m-%d")
        end_str   = end_dt.strftime("%Y-%m-%d")

        # ── fetch ─────────────────────────────────────────────────────
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_str, end=end_str, auto_adjust=True)

        if df.empty:
            raise ValueError(
                f"No data returned for {symbol} "
                f"({start_str} → {end_str}). "
                "Check the symbol and your internet connection."
            )

        # ── normalise columns ─────────────────────────────────────────
        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df.index = pd.to_datetime(df.index).tz_localize(None)
        df.index.name = "Date"

        # drop any rows where Close is NaN or zero
        df = df[df["Close"] > 0].dropna(subset=["Close"])

        return df

    def preprocess_data(self, data):
        """Clean and preprocess market data."""
        data = data.dropna()
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors="coerce")
        return data

    def validate_data(self, data):
        """Validate data integrity."""
        if data is None or data.empty:
            return False
        required = ["Open", "High", "Low", "Close", "Volume"]
        if not all(c in data.columns for c in required):
            return False
        if data.isnull().any().any():
            return False
        return True
