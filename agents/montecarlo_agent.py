import numpy as np


class MonteCarloAgent:

    def generate_price_paths(
        self,
        data,
        num_simulations=1000,
        horizon=252
    ):

        returns = (
            data["Close"]
            .pct_change()
            .dropna()
        )

        mu = returns.mean()
        sigma = returns.std()

        paths = np.random.normal(
            mu,
            sigma,
            (num_simulations, horizon)
        )

        return {
            "simulations": num_simulations,
            "horizon": horizon,
            "mean_return": float(mu),
            "volatility": float(sigma),
            "paths": paths
        }
