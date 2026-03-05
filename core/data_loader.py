import yfinance as yf
import pandas as pd
import numpy as np

def download_market_data(tickers, start_date, end_date):
    """
    Download market data using yfinance and return clean price DataFrames.
    Safely handles MultiIndex column issues.
    """
    try:
        data = yf.download(tickers, start=start_date, end=end_date)
        
        # Handle yfinance MultiIndex output if multiple tickers are passed
        if isinstance(data.columns, pd.MultiIndex):
            if 'Adj Close' in data.columns.levels[0]:
                data = data['Adj Close']
            else:
                data = data['Close']
        else:
            if 'Adj Close' in data.columns:
                data = data[['Adj Close']].rename(columns={'Adj Close': tickers[0]})
            else:
                data = data[['Close']].rename(columns={'Close': tickers[0]})
                
        # Forward fill missing data, then drop remainder
        data = data.ffill().dropna()
        return data

    except Exception as e:
        print(f"Error downloading data for {tickers}: {e}")
        return pd.DataFrame()
