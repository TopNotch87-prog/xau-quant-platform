import pandas as pd
from pathlib import Path

class TradeLogger:

    FILE = "data/trades.csv"

    def log(
        self,
        timestamp,
        direction,
        entry,
        exit_price,
        pnl
    ):

        row = pd.DataFrame([{

            "timestamp": timestamp,

            "direction": direction,

            "entry": entry,

            "exit": exit_price,

            "pnl": pnl
        }])

        if Path(self.FILE).exists():

            row.to_csv(
                self.FILE,
                mode="a",
                header=False,
                index=False
            )

        else:

            row.to_csv(
                self.FILE,
                index=False
            )
