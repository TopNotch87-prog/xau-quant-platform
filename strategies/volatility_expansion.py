import pandas as pd


class VolatilityExpansion:

    def __init__(self, period=20, threshold=1.5):
        self.period = period
        self.threshold = threshold

    def signal(self, data):

        df = data.copy()

        df["Returns"] = df["Close"].pct_change()

        df["Volatility"] = (
            df["Returns"]
            .rolling(self.period)
            .std()
        )

        df["AvgVolatility"] = (
            df["Volatility"]
            .rolling(self.period)
            .mean()
        )

        latest_vol = df["Volatility"].iloc[-1]
        avg_vol = df["AvgVolatility"].iloc[-1]

        latest_return = df["Returns"].iloc[-1]

        if pd.isna(latest_vol) or pd.isna(avg_vol):
            return 0

        if latest_vol > avg_vol * self.threshold:

            if latest_return > 0:
                return 1

            if latest_return < 0:
                return -1

        return 0
