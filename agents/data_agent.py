"""
Data Collection Agent
Handles market data retrieval and preprocessing for XAUUSD
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class DataAgent:
    def __init__(self):
        """Initialize the data collection agent"""
        pass
    
    def fetch_market_data(self, symbol: str, start_date: str = None, end_date: str = None):
        """Fetch historical market data"""
        # For now, generate synthetic market data for XAUUSD
        # In production, this would fetch from yfinance or another data provider
        
        # Default to last 252 days of trading data (1 year)
        if end_date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start_date is None:
            start_date = end_date - timedelta(days=365)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        # Generate date range (business days only)
        dates = pd.bdate_range(start=start_date, end=end_date)
        
        # Generate realistic OHLCV data
        np.random.seed(42)  # For reproducibility
        n_days = len(dates)
        
        # Start price around gold's typical range
        price = 2000
        returns = np.random.normal(0.0005, 0.02, n_days)
        prices = price * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'Date': dates,
            'Open': prices + np.random.normal(0, 10, n_days),
            'High': prices + np.abs(np.random.normal(20, 10, n_days)),
            'Low': prices - np.abs(np.random.normal(20, 10, n_days)),
            'Close': prices,
            'Volume': np.random.randint(1000000, 5000000, n_days)
        })
        
        df.set_index('Date', inplace=True)
        
        return df
    
    def preprocess_data(self, data):
        """Clean and preprocess market data"""
        # Remove any NaN values
        data = data.dropna()
        
        # Ensure numeric types
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
        
        return data
    
    def validate_data(self, data):
        """Validate data integrity"""
        if data is None or data.empty:
            return False
        
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_columns):
            return False
        
        # Check for any remaining NaN values
        if data.isnull().any().any():
            return False
        
        return True
