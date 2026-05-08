import pandas as pd
import pandas_ta as ta
import numpy as np

class TradingStrategy:
    def __init__(self, ema_fast=9, ema_slow=21, rsi_period=14):
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.rsi_period = rsi_period

    def calculate_indicators(self, df):
        """
        Calculates EMA and RSI indicators on the provided DataFrame.
        Expected columns: 'close'
        """
        if df.empty:
            return df
        
        df = df.copy()
        df['ema_fast'] = ta.ema(df['close'], length=self.ema_fast)
        df['ema_slow'] = ta.ema(df['close'], length=self.ema_slow)
        df['rsi'] = ta.rsi(df['close'], length=self.rsi_period)
        
        return df

    def check_signals(self, df):
        """
        Checks for EMA crossover signals confirmed by RSI.
        Returns 'buy', 'sell', or 'hold'.
        """
        if len(df) < self.ema_slow + 2: # Ensure we have enough data for indicators
            return 'hold'
        
        df_ind = self.calculate_indicators(df)
        
        current_row = df_ind.iloc[-1]
        previous_row = df_ind.iloc[-2]
        
        # Check for NaN values
        if pd.isna(current_row['ema_fast']) or pd.isna(current_row['ema_slow']) or \
           pd.isna(previous_row['ema_fast']) or pd.isna(previous_row['ema_slow']) or \
           pd.isna(current_row['rsi']):
            return 'hold'
        
        # EMA Crossover: fast crosses above slow
        bullish_crossover = (previous_row['ema_fast'] <= previous_row['ema_slow']) and \
                            (current_row['ema_fast'] > current_row['ema_slow'])
        
        # EMA Crossover: fast crosses below slow
        bearish_crossover = (previous_row['ema_fast'] >= previous_row['ema_slow']) and \
                             (current_row['ema_fast'] < current_row['ema_slow'])
        
        # RSI Confirmation (typical: RSI > 50 for bullish, RSI < 50 for bearish)
        if bullish_crossover and current_row['rsi'] > 10:
            return 'buy'
        elif bearish_crossover and current_row['rsi'] < 50:
            return 'sell'
        
        return 'hold'
