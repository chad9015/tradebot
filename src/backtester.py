import pandas as pd
import numpy as np
from src.strategy import TradingStrategy
from src.data_provider import DataProvider
from alpaca_trade_api.rest import TimeFrame, TimeFrameUnit

class Backtester:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.strategy = TradingStrategy()
        self.data_provider = DataProvider()

    def run_backtest(self, symbol, start, end, timeframe=TimeFrame(5, TimeFrameUnit.Minute)):
        """
        Runs a backtest for a single symbol.
        """
        df = self.data_provider.get_historical_data(symbol, timeframe=timeframe, start=start, end=end, limit=10000)
        
        if df.empty:
            return None
            
        df = self.strategy.calculate_indicators(df)
        
        # Simulation
        capital = self.initial_capital
        position = 0
        trades = []
        
        # We need to iterate and apply signals
        # Optimized: Indicators are already calculated. We just need the crossover logic.
        
        for i in range(1, len(df)):
            current_row = df.iloc[i]
            previous_row = df.iloc[i-1]
            
            # Check for NaN values in indicators
            if pd.isna(current_row['ema_fast']) or pd.isna(current_row['ema_slow']) or \
               pd.isna(previous_row['ema_fast']) or pd.isna(previous_row['ema_slow']) or \
               pd.isna(current_row['rsi']):
                continue

            current_price = current_row['close']
            current_time = df.index[i]
            
            # Re-implementing signal logic here for performance in backtest
            bullish_crossover = (previous_row['ema_fast'] <= previous_row['ema_slow']) and \
                                (current_row['ema_fast'] > current_row['ema_slow'])
            
            bearish_crossover = (previous_row['ema_fast'] >= previous_row['ema_slow']) and \
                                 (current_row['ema_fast'] < current_row['ema_slow'])
            
            if bullish_crossover and current_row['rsi'] > 50 and position == 0:
                # Buy as much as we can
                shares_to_buy = capital // current_price
                if shares_to_buy > 0:
                    position = shares_to_buy
                    capital -= position * current_price
                    trades.append({'time': current_time, 'type': 'buy', 'price': current_price, 'capital': capital})
                    
            elif bearish_crossover and current_row['rsi'] < 50 and position > 0:
                # Sell all
                capital += position * current_price
                trades.append({'time': current_time, 'type': 'sell', 'price': current_price, 'capital': capital})
                position = 0
                
        # Final value
        final_value = capital + (position * df.iloc[-1]['close'])
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        return {
            'symbol': symbol,
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'trades': pd.DataFrame(trades),
            'data': df
        }

if __name__ == "__main__":
    pass
