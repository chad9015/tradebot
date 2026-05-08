import pandas as pd
import logging
from src.data_provider import DataProvider
from src.strategy import TradingStrategy
from alpaca_trade_api.rest import TimeFrame

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketScanner:
    def __init__(self):
        self.data_provider = DataProvider()
        self.strategy = TradingStrategy()
        # Default watch list - could be expanded or fetched dynamically
        self.default_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'AMD', 
            'NFLX', 'PYPL', 'JPM', 'BAC', 'DIS', 'V', 'MA', 'SPY', 'QQQ', 'IWM'
        ]

    def get_active_assets(self, limit=100):
        """
        Fetches active assets from Alpaca that are tradeable and marginable.
        """
        if not self.data_provider.api:
            return self.default_symbols
            
        assets = self.data_provider.api.list_assets(status='active', asset_class='us_equity')
        tradeable_assets = [a.symbol for a in assets if a.tradable and a.marginable and a.easy_to_borrow]
        
        # Sort by some criteria if possible, or just return top N
        # For now, let's stick to a curated list + some others if needed
        return tradeable_assets[:limit]

    def scan(self, symbols=None):
        """
        Scans a list of symbols for trading signals.
        """
        if not symbols:
            symbols = self.default_symbols
            
        results = []
        logger.info(f"Scanning {len(symbols)} symbols...")
        
        for symbol in symbols:
            try:
                # Fetch 5-minute bars (enough for indicators)
                # EMA 21 needs at least 21+ bars, let's get 100 to be safe
                df = self.data_provider.get_historical_data(symbol, timeframe=TimeFrame.Minute, limit=100)
                
                # Resample to 5-minute if needed, or if get_historical_data doesn't support it directly
                # Alpaca's REST API supports TimeFrame.Minute, but for 5-minute we might need to resample
                # or use Alpaca's native 5Min timeframe if supported.
                
                # Actually, alpaca_trade_api REST.get_bars supports TimeFrame.Minute, but 5-minute is better
                # Let's use 5-minute bars directly if possible.
                
                # In Alpaca V2, TimeFrame is a class. TimeFrame.Minute is 1Min.
                # To get 5Min: TimeFrame(5, TimeFrameUnit.Minute)
                from alpaca_trade_api.rest import TimeFrameUnit
                tf_5min = TimeFrame(5, TimeFrameUnit.Minute)
                
                df_5min = self.data_provider.get_historical_data(symbol, timeframe=tf_5min, limit=100)
                
                if df_5min.empty:
                    continue
                    
                signal = self.strategy.check_signals(df_5min)
                
                if signal != 'hold':
                    results.append({
                        'symbol': symbol,
                        'signal': signal,
                        'price': df_5min.iloc[-1]['close'],
                        'time': df_5min.index[-1]
                    })
                    logger.info(f"Signal found: {symbol} -> {signal}")
                    
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
                
        return pd.DataFrame(results)

if __name__ == "__main__":
    scanner = MarketScanner()
    # Note: This will likely return empty if API keys are not set
    results = scanner.scan()
    print(results)
