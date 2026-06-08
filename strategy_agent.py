class StrategyAgent:

    def choose(self, regime):

        mapping = {

            "TREND_UP": "trend_following",

            "TREND_DOWN": "trend_following",

            "RANGE": "mean_reversion",

            "HIGH_VOL": "breakout"
        }

        return mapping[regime]
