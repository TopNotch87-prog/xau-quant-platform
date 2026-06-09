"""
Strategy Agent
Selects appropriate trading strategy based on market regime
"""


class StrategyAgent:

    def generate_signals(self, data, regime):
        """
        Generate signals based on detected regime.
        """

        mapping = {
            "TREND_UP": "trend_following",
            "TREND_DOWN": "trend_following",
            "RANGE": "mean_reversion",
            "HIGH_VOL": "breakout",
            "UNKNOWN": "trend_following"
        }

        selected_strategy = mapping.get(
            str(regime),
            "trend_following"
        )

        return {
            "strategy": selected_strategy,
            "regime": regime,
            "data": data
        }
