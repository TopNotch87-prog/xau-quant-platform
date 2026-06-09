INITIAL_CAPITAL = 10000
RISK_PER_TRADE = 0.01
SYMBOL = 'GC=F'


def get_config():
    """
    Returns the configuration dictionary for the XAU Quant Platform
    """
    return {
        'initial_capital': INITIAL_CAPITAL,
        'risk_per_trade': RISK_PER_TRADE,
        'symbol': SYMBOL
    }
