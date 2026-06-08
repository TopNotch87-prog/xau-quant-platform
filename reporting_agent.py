import matplotlib.pyplot as plt

class ReportingAgent:

    def create_report(
        self,
        equity_curve
    ):

        plt.figure(figsize=(12,6))

        equity_curve.plot()

        plt.title(
            "XAUUSD Equity Curve"
        )

        plt.grid()

        plt.savefig(
            "data/reports/equity_curve.png"
        )
