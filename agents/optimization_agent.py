from itertools import product

class WalkForwardOptimizer:

    def optimize(self, train_df):

        best_sharpe = -999

        best_params = None

        for fast, slow in product(
                range(10,50,5),
                range(50,200,10)
        ):

            sharpe = self.test_strategy(
                train_df,
                fast,
                slow
            )

            if sharpe > best_sharpe:

                best_sharpe = sharpe

                best_params = (fast, slow)

        return best_params
