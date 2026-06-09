"""
Optimization Agent
Walk-forward parameter optimization for XAUUSD trading strategies
"""
import numpy as np
from itertools import product


class OptimizationAgent:

    def optimize(self, train_df):

        best_sharpe = -999
        best_params = None

        for fast, slow in product(
                range(10, 50, 5),
                range(50, 200, 10)
        ):

            if fast >= slow:
                continue

            sharpe = self.test_strategy(train_df, fast, slow)

            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_params = (fast, slow)

        return best_params

    def test_strategy(self, data, fast, slow):

        close = data["Close"]

        fast_ma = close.rolling(fast).mean()
        slow_ma = close.rolling(slow).mean()

        signal = (fast_ma > slow_ma).astype(int)

        returns = close.pct_change()

        strategy_returns = (signal.shift(1) * returns).dropna()

        if len(strategy_returns) < 30:
            return -999

        sharpe = (
            strategy_returns.mean() / strategy_returns.std()
        ) * np.sqrt(252)

        return sharpe
