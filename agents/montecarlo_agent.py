"""
Monte Carlo Agent
Generates price path simulations for risk analysis
"""
import numpy as np

class MonteCarloAgent:

    def generate_price_paths(self, data, num_simulations=1000, horizon=252):
        """Generate Monte Carlo price paths"""
        returns = np.random.normal(0, 0.01, (num_simulations, horizon))
        return {
            'simulations': num_simulations,
            'horizon': horizon,
            'paths': returns
        }
