def test_strategy(
    self,
    data,
    fast,
    slow
):

    close = data["Close"]

    fast_ma = close.rolling(fast).mean()
    slow_ma = close.rolling(slow).mean()

    signal = (
        fast_ma > slow_ma
    ).astype(int)

    returns = close.pct_change()

    strategy_returns = (
        signal.shift(1)
        * returns
    )

    strategy_returns = (
        strategy_returns
        .dropna()
    )

    if len(strategy_returns) < 30:
        return -999

    sharpe = (
        strategy_returns.mean()
        / strategy_returns.std()
    ) * np.sqrt(252)

    return sharpe
