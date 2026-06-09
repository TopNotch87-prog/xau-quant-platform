"""
Strategy Agent
Selects and executes trading strategy based on market regime,
returning actionable BUY / SELL / HOLD signals with levels.
"""
import numpy as np


class StrategyAgent:

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def generate_signals(self, data, regime):
        """
        Generate a trade recommendation for the current bar.

        Returns a dict with:
            strategy      – strategy name
            regime        – detected regime
            signal        – BUY | SELL | HOLD
            entry_price   – suggested entry (last close)
            stop_loss     – price to exit if wrong
            take_profit   – price target
            rationale     – one-line explanation
            data          – full OHLCV + regime DataFrame
        """

        mapping = {
            "TREND_UP":   "trend_following",
            "TREND_DOWN": "trend_following",
            "RANGE":      "mean_reversion",
            "HIGH_VOL":   "breakout",
            "UNKNOWN":    "trend_following",
        }

        strategy_name = mapping.get(str(regime), "trend_following")

        if strategy_name == "breakout":
            signal_info = self._breakout_signal(data)
        elif strategy_name == "mean_reversion":
            signal_info = self._mean_reversion_signal(data)
        else:
            signal_info = self._trend_following_signal(data)

        return {
            "strategy":    strategy_name,
            "regime":      regime,
            "signal":      signal_info["signal"],
            "entry_price": signal_info["entry_price"],
            "stop_loss":   signal_info["stop_loss"],
            "take_profit": signal_info["take_profit"],
            "rationale":   signal_info["rationale"],
            "data":        data,
        }

    # ------------------------------------------------------------------ #
    #  Strategy implementations                                           #
    # ------------------------------------------------------------------ #

    def _breakout_signal(self, data, period=20):
        """
        Donchian Channel breakout.
        BUY  when close > highest high of the last `period` bars.
        SELL when close < lowest  low  of the last `period` bars.
        """
        close  = data["Close"]
        high   = data["High"]
        low    = data["Low"]

        donchian_high = high.rolling(period).max().shift(1)
        donchian_low  = low.rolling(period).min().shift(1)
        atr           = self._atr(data)

        last_close = float(close.iloc[-1])
        d_high     = float(donchian_high.iloc[-1])
        d_low      = float(donchian_low.iloc[-1])
        last_atr   = float(atr.iloc[-1])

        if last_close > d_high:
            return {
                "signal":      "BUY",
                "entry_price": round(last_close, 2),
                "stop_loss":   round(last_close - 1.5 * last_atr, 2),
                "take_profit": round(last_close + 3.0 * last_atr, 2),
                "rationale":   f"Price {last_close:.2f} broke above {period}-bar high {d_high:.2f}",
            }
        elif last_close < d_low:
            return {
                "signal":      "SELL",
                "entry_price": round(last_close, 2),
                "stop_loss":   round(last_close + 1.5 * last_atr, 2),
                "take_profit": round(last_close - 3.0 * last_atr, 2),
                "rationale":   f"Price {last_close:.2f} broke below {period}-bar low {d_low:.2f}",
            }
        else:
            return {
                "signal":      "HOLD",
                "entry_price": round(last_close, 2),
                "stop_loss":   round(d_low, 2),
                "take_profit": round(d_high, 2),
                "rationale":   f"Inside channel ({d_low:.2f} – {d_high:.2f}), awaiting breakout",
            }

    def _trend_following_signal(self, data, fast=45, slow=70):
        """
        MA crossover.
        BUY  when fast MA > slow MA.
        SELL when fast MA < slow MA.
        """
        close   = data["Close"]
        fast_ma = close.rolling(fast).mean()
        slow_ma = close.rolling(slow).mean()
        atr     = self._atr(data)

        last_close   = float(close.iloc[-1])
        last_fast    = float(fast_ma.iloc[-1])
        last_slow    = float(slow_ma.iloc[-1])
        last_atr     = float(atr.iloc[-1])

        if last_fast > last_slow:
            return {
                "signal":      "BUY",
                "entry_price": round(last_close, 2),
                "stop_loss":   round(last_close - 1.5 * last_atr, 2),
                "take_profit": round(last_close + 3.0 * last_atr, 2),
                "rationale":   f"MA{fast} {last_fast:.2f} > MA{slow} {last_slow:.2f} (bullish trend)",
            }
        elif last_fast < last_slow:
            return {
                "signal":      "SELL",
                "entry_price": round(last_close, 2),
                "stop_loss":   round(last_close + 1.5 * last_atr, 2),
                "take_profit": round(last_close - 3.0 * last_atr, 2),
                "rationale":   f"MA{fast} {last_fast:.2f} < MA{slow} {last_slow:.2f} (bearish trend)",
            }
        else:
            return {
                "signal":      "HOLD",
                "entry_price": round(last_close, 2),
                "stop_loss":   round(last_close - last_atr, 2),
                "take_profit": round(last_close + last_atr, 2),
                "rationale":   "MAs equal — no clear trend direction",
            }

    def _mean_reversion_signal(self, data, period=14):
        """
        RSI mean reversion.
        BUY  when RSI < 35 (oversold).
        SELL when RSI > 65 (overbought).
        """
        close  = data["Close"]
        rsi    = self._rsi(close, period)
        atr    = self._atr(data)
        ma50   = close.rolling(50).mean()

        last_close = float(close.iloc[-1])
        last_rsi   = float(rsi.iloc[-1])
        last_atr   = float(atr.iloc[-1])
        last_ma50  = float(ma50.iloc[-1])

        if last_rsi < 35:
            return {
                "signal":      "BUY",
                "entry_price": round(last_close, 2),
                "stop_loss":   round(last_close - 1.5 * last_atr, 2),
                "take_profit": round(last_ma50, 2),
                "rationale":   f"RSI({period}) {last_rsi:.1f} — oversold, reversion toward MA50 {last_ma50:.2f}",
            }
        elif last_rsi > 65:
            return {
                "signal":      "SELL",
                "entry_price": round(last_close, 2),
                "stop_loss":   round(last_close + 1.5 * last_atr, 2),
                "take_profit": round(last_ma50, 2),
                "rationale":   f"RSI({period}) {last_rsi:.1f} — overbought, reversion toward MA50 {last_ma50:.2f}",
            }
        else:
            return {
                "signal":      "HOLD",
                "entry_price": round(last_close, 2),
                "stop_loss":   round(last_close - last_atr, 2),
                "take_profit": round(last_close + last_atr, 2),
                "rationale":   f"RSI({period}) {last_rsi:.1f} — neutral zone, no signal",
            }

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _atr(self, data, period=14):
        high  = data["High"]
        low   = data["Low"]
        close = data["Close"]
        prev_close = close.shift(1)
        tr = np.maximum(high - low,
             np.maximum(abs(high - prev_close),
                        abs(low  - prev_close)))
        return tr.rolling(period).mean()

    def _rsi(self, close, period=14):
        delta  = close.diff()
        gain   = delta.clip(lower=0).rolling(period).mean()
        loss   = (-delta.clip(upper=0)).rolling(period).mean()
        rs     = gain / loss.replace(0, np.nan)
        return 100 - (100 / (1 + rs))
