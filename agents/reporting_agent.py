import numpy as np


class ReportingAgent:

    def generate_backtest_report(
        self,
        results
    ):

        data = results["data"]

        returns = (
            data["Close"]
            .pct_change()
            .dropna()
        )

        total_return = (
            data["Close"].iloc[-1]
            / data["Close"].iloc[0]
        ) - 1

        sharpe = (
            returns.mean()
            / returns.std()
        ) * np.sqrt(252)

        equity = (1 + returns).cumprod()

        drawdown = (
            equity
            - equity.cummax()
        ) / equity.cummax()

        max_drawdown = drawdown.min()

        return {
            "status": "success",
            "total_return": float(total_return),
            "sharpe_ratio": float(sharpe),
            "max_drawdown": float(max_drawdown),
            "results": results
        }
