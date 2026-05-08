import os
import pandas as pd
from alpaca_trade_api.rest import REST, TimeFrame
from dotenv import load_dotenv

load_dotenv()

class DataProvider:
    def __init__(self):
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY')
        self.base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        # Initialize REST API if keys are provided, otherwise use a dummy for structure
        if self.api_key and self.api_key != 'your_api_key_here':
            self.api = REST(self.api_key, self.secret_key, self.base_url, api_version='v2')
        else:
            self.api = None

    def get_historical_data(self, symbol, timeframe=TimeFrame.Minute, start=None, end=None, limit=1000):
        """
        Fetches historical bar data from Alpaca.
        """
        if not self.api:
            # Return empty DF or raise error if keys not set
            return pd.DataFrame()
            
        bars = self.api.get_bars(symbol, timeframe, start=start, end=end, limit=limit, feed='iex').df
        if bars.empty:
            return bars
            
        # Standardize column names
        bars = bars.rename(columns={'open': 'open', 'high': 'high', 'low': 'low', 'close': 'close', 'volume': 'volume'})
        return bars

    def get_latest_quote(self, symbol):
        """
        Fetches the latest quote for a symbol.
        """
        if not self.api:
            return None
        return self.api.get_latest_quote(symbol)

    def get_clock(self):
        """
        Checks if the market is open.
        """
        if not self.api:
            return None
        return self.api.get_clock()
