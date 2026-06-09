"""
Volatility Expansion Strategy
Trades increases in market volatility
"""

import pandas as pd
import numpy as np

class VolatilityExpansion:
    def __init__(self, period=20, vol_threshold=1.5):
        """
        Initialize volatility expansion strategy
        
        Args:
            period: Lookback period for volatility calculation
            vol_threshold: Multiplier for volatility threshold
        """
        self.period = period
        self.vol_threshold = vol_threshold
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate volatility metrics"""
        data['returns'] = data['close'].pct_change()
        data['volatility'] = data['returns'].rolling(self.period).std()
        data['avg_volatility'] = data['volatility'].rolling(self.period).mean()
        return data
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate volatility expansion signals"""
        signals = pd.Series(index=data.index, dtype=float)
        vol_expansion = data['volatility'] > (data['avg_volatility'] * self.vol_threshold)
        
        # Buy when volatility expands and price is up
        signals[(vol_expansion) & (data['returns'] > 0)] = 1
        # Sell when volatility expands and price is down
        signals[(vol_expansion) & (data['returns'] < 0)] = -1
        return signals
