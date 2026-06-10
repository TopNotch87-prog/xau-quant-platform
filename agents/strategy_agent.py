import numpy as np

from strategies.volatility_expansion import VolatilityExpansion


class StrategyAgent:

    def __init__(self):

        self.vol_strategy = VolatilityExpansion()
        self.fast_ma
        self.slow_ma

        self.weights = {
            "HIGH_VOL": {
                "breakout": 0.40,
                "trend": 0.20,
                "mean_reversion": 0.10,
                "volatility": 0.30
            },

            "TREND_UP": {
                "breakout": 0.20,
                "trend": 0.50,
                "mean_reversion": 0.10,
                "volatility": 0.20
            },

            "TREND_DOWN": {
                "breakout": 0.20,
                "trend": 0.50,
                "mean_reversion": 0.10,
                "volatility": 0.20
            },

            "RANGE": {
                "breakout": 0.10,
                "trend": 0.20,
                "mean_reversion": 0.50,
                "volatility": 0.20
            },

            "UNKNOWN": {
                "breakout": 0.25,
                "trend": 0.25,
                "mean_reversion": 0.25,
                "volatility": 0.25
            }
        }

    def generate_signals(self, data, regime):

        breakout = self._breakout_vote(data)

        trend = self._trend_vote(data)

        mean_rev = self._mean_reversion_vote(data)

        volatility = self.vol_strategy.signal(data)

        w = self.weights.get(
            str(regime),
            self.weights["UNKNOWN"]
        )

        score = (
            breakout * w["breakout"]
            + trend * w["trend"]
            + mean_rev * w["mean_reversion"]
            + volatility * w["volatility"]
        )

        if score > 0.25:
            final_signal = "BUY"
        elif score < -0.25:
            final_signal = "SELL"
        else:
            final_signal = "HOLD"

        close = float(data["Close"].iloc[-1])

        atr = float(
            self._atr(data).iloc[-1]
        )

        confidence = round(
            min(abs(score), 1.0),
            2
        )

        return {

            "signal": final_signal,

            "confidence": confidence,

            "weighted_score": round(score, 3),

            "regime": regime,

            "entry_price": round(close, 2),

            "stop_loss": round(
                close - 1.5 * atr,
                2
            ) if final_signal == "BUY"
            else round(
                close + 1.5 * atr,
                2
            ),

            "take_profit": round(
                close + 3 * atr,
                2
            ) if final_signal == "BUY"
            else round(
                close - 3 * atr,
                2
            ),

            "votes": {

                "breakout":
                    self._decode_vote(
                        breakout
                    ),

                "trend":
                    self._decode_vote(
                        trend
                    ),

                "mean_reversion":
                    self._decode_vote(
                        mean_rev
                    ),

                "volatility":
                    self._decode_vote(
                        volatility
                    )
            }
        }

    def _decode_vote(self, vote):

        if vote > 0:
            return "BUY"

        if vote < 0:
            return "SELL"

        return "HOLD"

    def _breakout_vote(
        self,
        data,
        period=20
    ):

        high = (
            data["High"]
            .rolling(period)
            .max()
            .shift(1)
        )

        low = (
            data["Low"]
            .rolling(period)
            .min()
            .shift(1)
        )

        close = data["Close"].iloc[-1]

        if close > high.iloc[-1]:
            return 1

        if close < low.iloc[-1]:
            return -1

        return 0

    def _trend_vote(
        self,
        data,
        fast=20,
        slow=50
    ):

        fast_ma = (
            data["Close"]
            .rolling(fast)
            .mean()
        )

        slow_ma = (
            data["Close"]
            .rolling(slow)
            .mean()
        )

        if fast_ma.iloc[-1] > slow_ma.iloc[-1]:
            return 1

        if fast_ma.iloc[-1] < slow_ma.iloc[-1]:
            return -1

        return 0

    def _mean_reversion_vote(
        self,
        data
    ):

        rsi = self._rsi(
            data["Close"]
        )

        latest = rsi.iloc[-1]

        if latest < 30:
            return 1

        if latest > 70:
            return -1

        return 0

    def _atr(
        self,
        data,
        period=14
    ):

        high = data["High"]

        low = data["Low"]

        close = data["Close"]

        prev = close.shift(1)

        tr = np.maximum(
            high - low,
            np.maximum(
                abs(high - prev),
                abs(low - prev)
            )
        )

        return tr.rolling(period).mean()

    def _rsi(
        self,
        close,
        period=14
    ):

        delta = close.diff()

        gain = (
            delta.clip(lower=0)
            .rolling(period)
            .mean()
        )

        loss = (
            -delta.clip(upper=0)
            .rolling(period)
            .mean()
        )

        rs = gain / loss.replace(
            0,
            np.nan
        )

        return 100 - (
            100 / (1 + rs)
        )
