import yfinance as yf
import pandas as pd

class DataAgent:

    def download(self):

        data = yf.download(
            "GC=F",
            period="5y",
            interval="1h"
        )

        data.to_csv("data/market_data.csv")

        return data
