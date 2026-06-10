"""
Strategy Agent
Runs all four strategies simultaneously, scores each one, and
produces a weighted-vote final signal based on the current regime.
"""
import numpy as np
from strategies.volatility_expansion import VolatilityExpansion

# ── regime weights {regime: {strategy: weight}} ───────────────────────
_WEIGHTS = {
    "HIGH_VOL":   {"breakout": 0.40, "trend": 0.15, "mean_rev": 0.10, "vol_exp": 0.35},
    "TREND_UP":   {"breakout": 0.20, "trend": 0.50, "mean_rev": 0.10, "vol_exp": 0.20},
    "TREND_DOWN": {"breakout": 0.20, "trend": 0.50, "mean_rev": 0.10, "vol_exp": 0.20},
    "RANGE":      {"breakout": 0.10, "trend": 0.10, "mean_rev": 0.60, "vol_exp": 0.20},
    "UNKNOWN":    {"breakout": 0.25, "trend": 0.25, "mean_rev": 0.25, "vol_exp": 0.25},
}

_THRESHOLD = 0.15   # weighted score must exceed this to call BUY or SELL


class StrategyAgent:

    def __init__(self):
        self.vol_strategy = VolatilityExpansion()
        self.fast_ma = 45   # updated by OptimizationAgent after walk-forward
        self.slow_ma = 70

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def generate_signals(self, data, regime):
        """
        Run all four strategies, score each, then produce a
        consensus BUY / SELL / HOLD via weighted voting.
        """
        regime_key = str(regime)
        weights    = _WEIGHTS.get(regime_key, _WEIGHTS["UNKNOWN"])

        # ── individual votes (each returns a score in [-1, 1]) ────────
        votes = {
            "breakout": self._breakout_vote(data),
            "trend":    self._trend_vote(data, self.fast_ma, self.slow_ma),
            "mean_rev": self._mean_reversion_vote(data),
            "vol_exp":  self.vol_strategy.signal(data),
        }

        # ── weighted score ────────────────────────────────────────────
        score = sum(weights[k] * votes[k] for k in votes)
        score = round(score, 4)

        # ── final signal ──────────────────────────────────────────────
        if score > _THRESHOLD:
            final_signal = "BUY"
        elif score < -_THRESHOLD:
            final_signal = "SELL"
        else:
            final_signal = "HOLD"

        # ── price levels ──────────────────────────────────────────────
        close = float(data["Close"].iloc[-1])
        atr   = float(self._atr(data).iloc[-1])

        if final_signal == "BUY":
            stop_loss   = round(close - 1.5 * atr, 2)
            take_profit = round(close + 3.0 * atr, 2)
        elif final_signal == "SELL":
            stop_loss   = round(close + 1.5 * atr, 2)
            take_profit = round(close - 3.0 * atr, 2)
        else:
            stop_loss   = round(close - atr, 2)
            take_profit = round(close + atr, 2)

        # ── confidence = how far score is from zero, capped at 1 ──────
        confidence = round(min(abs(score) / _THRESHOLD, 1.0), 2)

        # ── dominant strategy (highest weighted contribution) ─────────
        dominant = max(votes, key=lambda k: abs(votes[k]) * weights[k])

        rationale = (
            f"Weighted score {score:+.3f} (threshold ±{_THRESHOLD}) → {final_signal}. "
            f"Dominant: {dominant}."
        )

        return {
            "strategy":       dominant,
            "regime":         regime,
            "signal":         final_signal,
            "confidence":     confidence,
            "weighted_score": score,
            "entry_price":    round(close, 2),
            "stop_loss":      stop_loss,
            "take_profit":    take_profit,
            "rationale":      rationale,
            "votes": {k: self._decode(v) for k, v in votes.items()},
            "data":           data,
        }

    # ------------------------------------------------------------------ #
    #  Individual strategy votes — each returns a score in [-1, 1]       #
    # ------------------------------------------------------------------ #

    def _breakout_vote(self, data, period=20):
        high = data["High"].rolling(period).max().shift(1)
        low  = data["Low"].rolling(period).min().shift(1)
        close = float(data["Close"].iloc[-1])
        d_high = float(high.iloc[-1])
        d_low  = float(low.iloc[-1])
        channel = d_high - d_low + 1e-9

        if close > d_high:
            return min(1.0, (close - d_high) / (channel * 0.05))
        if close < d_low:
            return -min(1.0, (d_low - close) / (channel * 0.05))
        return 0.0

    def _trend_vote(self, data, fast=45, slow=70):
        close   = data["Close"]
        fast_ma = float(close.rolling(fast).mean().iloc[-1])
        slow_ma = float(close.rolling(slow).mean().iloc[-1])
        gap_pct = (fast_ma - slow_ma) / (slow_ma + 1e-9)
        return max(-1.0, min(1.0, gap_pct * 20))

    def _mean_reversion_vote(self, data, period=14):
        rsi    = self._rsi(data["Close"], period)
        latest = float(rsi.iloc[-1])
        # Map RSI to [-1, 1]: RSI=0→+1 (very oversold), RSI=100→-1 (very overbought)
        return round((50 - latest) / 50, 4)

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _atr(self, data, period=14):
        h, l, c = data["High"], data["Low"], data["Close"]
        pc = c.shift(1)
        tr = np.maximum(h - l, np.maximum(abs(h - pc), abs(l - pc)))
        return tr.rolling(period).mean()

    def _rsi(self, close, period=14):
        delta = close.diff()
        gain  = delta.clip(lower=0).rolling(period).mean()
        loss  = (-delta.clip(upper=0)).rolling(period).mean()
        rs    = gain / loss.replace(0, np.nan)
        return 100 - (100 / (1 + rs))

    def _decode(self, score):
        if score > 0: return "BUY"
        if score < 0: return "SELL"
        return "HOLD"
