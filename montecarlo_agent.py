import numpy as np

class MonteCarloAgent:

    def run(
        self,
        trade_returns,
        simulations=10000
    ):

        outcomes = []

        for _ in range(simulations):

            sample = np.random.choice(
                trade_returns,
                size=len(trade_returns),
                replace=True
            )

            outcomes.append(
                np.cumprod(1 + sample)[-1]
            )

        return outcomes
