import os
import logging
import pandas as pd
from alpaca_trade_api.rest import REST
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class TradingExecutor:
    def __init__(self):
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY')
        self.base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        if self.api_key and self.api_key != 'your_api_key_here':
            self.api = REST(self.api_key, self.secret_key, self.base_url)
        else:
            self.api = None
            logger.warning("Alpaca API keys not set. Trading executor will not be able to place orders.")

    def get_account(self):
        if not self.api: return None
        return self.api.get_account()

    def get_positions(self):
        if not self.api: return []
        return self.api.list_positions()

    def execute_stock_trade(self, symbol, side, qty=None, notional=None):
        """
        Executes a stock trade. side can be 'buy' or 'sell'.
        """
        if not self.api:
            logger.error(f"Cannot execute {side} for {symbol}: API not initialized.")
            return None
            
        try:
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                notional=notional,
                side=side,
                type='market',
                time_in_force='gtc'
            )
            logger.info(f"Successfully placed {side} order for {symbol}")
            return order
        except Exception as e:
            logger.error(f"Error placing {side} order for {symbol}: {e}")
            return None

    def execute_options_trade(self, symbol, side):
        """
        Executes a simple options trade (Call/Put).
        'side' is 'buy' (for bullish) or 'sell' (for bearish signals).
        Note: Options trading in Alpaca has specific requirements and contract strings.
        This is a simplified implementation.
        """
        if not self.api:
            logger.error(f"Cannot execute options trade for {symbol}: API not initialized.")
            return None
            
        try:
            # 1. Find the right option contract
            # We want ATM (At The Money) and near expiration
            # Alpaca V2 has an options API
            
            # This requires getting the underlying price first
            quote = self.api.get_latest_quote(symbol)
            underlying_price = quote.bp
            
            # Search for contracts
            # Alpaca's options support might vary by account.
            # We'll search for contracts for the symbol.
            
            # type can be 'call' or 'put'
            option_type = 'call' if side == 'buy' else 'put'
            
            contracts = self.api.search_options_contracts(
                underlying_symbols=[symbol],
                types=[option_type],
                status='active'
            )
            
            if not contracts:
                logger.warning(f"No option contracts found for {symbol}")
                return None
                
            # Filter for nearest expiration and ATM strike
            # Sort by expiration date
            contracts.sort(key=lambda x: x.expiration_date)
            nearest_expiry = contracts[0].expiration_date
            
            # Filter for nearest expiry
            expiry_contracts = [c for c in contracts if c.expiration_date == nearest_expiry]
            
            # Find ATM (closest strike to underlying_price)
            atm_contract = min(expiry_contracts, key=lambda x: abs(float(x.strike_price) - underlying_price))
            
            logger.info(f"Selected option contract: {atm_contract.symbol} for {symbol}")
            
            # Place order for the option contract
            order = self.api.submit_order(
                symbol=atm_contract.symbol,
                qty=1, # Default to 1 contract for simple implementation
                side='buy', # We are buying the option (long call or long put)
                type='market',
                time_in_force='gtc'
            )
            return order
            
        except Exception as e:
            logger.error(f"Error placing options trade for {symbol}: {e}")
            return None
