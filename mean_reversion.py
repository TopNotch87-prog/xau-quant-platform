"""Mean reversion — RSI. Returns numeric score in [-1, 1]."""
import numpy as np

def signal(df, period=14):
    close = df["Close"]
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, np.nan)
    rsi   = 100 - (100 / (1 + rs))
    return round((50 - float(rsi.iloc[-1])) / 50, 4)
