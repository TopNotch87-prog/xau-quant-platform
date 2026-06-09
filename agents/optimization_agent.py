"""
Optimization Agent
Walk-forward parameter optimization for XAUUSD trading strategies
"""
import numpy as np
from itertools import product


class OptimizationAgent:

    def walk_forward_optimization(self, data, strategy_agent, window_size=252):

        results = []
        n = len(data)

        if n < window_size:
            best_params = self.optimize(data)
            best_sharpe = (
                self.test_strategy(data, *best_params)
                if best_params else -999
            )
            results.append({
                "window": 1,
                "train_start": data.index[0],
                "train_end": data.index[-1],
                "best_params": best_params,
                "best_sharpe": best_sharpe
            })
            return results

        for i in range(0, n - window_size + 1, max(1, window_size // 4)):
            train_df = data.iloc[i: i + window_size]
            best_params = self.optimize(train_df)
            best_sharpe = (
                self.test_strategy(train_df, *best_params)
                if best_params else -999
            )
            results.append({
                "window": len(results) + 1,
                "train_start": train_df.index[0],
                "train_end": train_df.index[-1],
                "best_params": best_params,
                "best_sharpe": round(best_sharpe, 4)
            })

        return results

    def optimize(self, train_df):

        best_sharpe = -999
        best_params = None

        for fast, slow in product(range(10, 50, 5), range(50, 200, 10)):
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

        std = strategy_returns.std()
        if std == 0:
            return -999

        return (strategy_returns.mean() / std) * np.sqrt(252)
