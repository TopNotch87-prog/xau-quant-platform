import numpy as np

class RiskAgent:

    def sharpe(self, returns):

        return (
            returns.mean()
            /
            returns.std()
        ) * np.sqrt(252)

    def sortino(self, returns):

        downside = returns[returns < 0]

        return (
            returns.mean()
            /
            downside.std()
        ) * np.sqrt(252)

    def max_drawdown(self, equity):

        running_max = equity.cummax()

        dd = (
            equity -
            running_max
        ) / running_max

        return dd.min()
