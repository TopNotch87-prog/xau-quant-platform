import numpy as np


class RiskAgent:

    def assess_portfolio_risk(self, signals, data):

        returns = data["Close"].pct_change().dropna()

        if len(returns) == 0:
            return {}

        sharpe = (
            returns.mean()
            / returns.std()
        ) * np.sqrt(252)

        cumulative = (1 + returns).cumprod()

        rolling_max = cumulative.cummax()

        drawdown = (
            cumulative - rolling_max
        ) / rolling_max

        max_drawdown = drawdown.min()

        var95 = np.percentile(
            returns,
            5
        )

        expected_shortfall = (
            returns[returns <= var95]
            .mean()
        )

        return {
            "sharpe_ratio": float(sharpe),
            "var_95": float(var95),
            "expected_shortfall": float(expected_shortfall),
            "max_drawdown": float(max_drawdown)
        }
