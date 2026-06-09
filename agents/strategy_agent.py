"""
Strategy Agent
Selects appropriate trading strategy based on market regime
"""

class StrategyAgent:

    def generate_signals(self, data, regime):
        """Generate trading signals based on data and regime"""
        mapping = {
            "TREND_UP": "trend_following",
            "TREND_DOWN": "trend_following",
            "RANGE": "mean_reversion",
            "HIGH_VOL": "breakout"
        }
        
        # Return signals based on regime
        return {
            'strategy': mapping.get(regime, 'trend_following'),
            'data': data
        }
