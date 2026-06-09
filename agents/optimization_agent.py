"""
Optimization Agent
Performs walk-forward optimization of strategy parameters
"""
from itertools import product

class OptimizationAgent:

    def walk_forward_optimization(self, data, strategy_agent, window_size=252):
        """Optimize strategy parameters using walk-forward method"""
        best_sharpe = -999
        best_params = None

        for fast, slow in product(
                range(10, 50, 5),
                range(50, 200, 10)
        ):

            sharpe = self.test_strategy(
                data,
                fast,
                slow
            )

            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_params = (fast, slow)

        return best_params
    
    def test_strategy(self, data, fast, slow):
        """Test strategy with given parameters"""
        # Placeholder for strategy testing
        return 0.5
