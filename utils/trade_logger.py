from pathlib import Path
import pandas as pd
from datetime import datetime


class TradeLogger:

    def __init__(self):

        self.file = Path("data/trades.csv")

        self.file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

    def log(self, signal):

        row = {
            "timestamp": datetime.now(),
            "signal": signal.get("signal"),
            "confidence": signal.get("confidence"),
            "regime": signal.get("regime"),
            "entry_price": signal.get("entry_price"),
            "stop_loss": signal.get("stop_loss"),
            "take_profit": signal.get("take_profit"),
            "weighted_score": signal.get("weighted_score")
        }

        df = pd.DataFrame([row])

        if self.file.exists():

            df.to_csv(
                self.file,
                mode="a",
                header=False,
                index=False
            )

        else:

            df.to_csv(
                self.file,
                index=False
            )
