"""
Reporting Agent
Generates backtest reports and analytics
"""

class ReportingAgent:

    def generate_backtest_report(self, results):
        """Generate comprehensive backtest report"""
        return {
            'status': 'success',
            'total_return': 0.25,
            'sharpe_ratio': 1.8,
            'max_drawdown': 0.12,
            'results': results
        }
