import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.scanner import MarketScanner
from src.backtester import Backtester
from src.trading import TradingExecutor
from src.strategy import TradingStrategy
import datetime

st.set_page_config(page_title="Day Trading Bot Dashboard", layout="wide")

st.title("📈 Day Trading Bot Dashboard")

# Sidebar for configuration
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Alpaca API Key", type="password")
secret_key = st.sidebar.text_input("Alpaca Secret Key", type="password")

if api_key and secret_key:
    import os
    os.environ['ALPACA_API_KEY'] = api_key
    os.environ['ALPACA_SECRET_KEY'] = secret_key

# Initialize components
scanner = MarketScanner()
backtester = Backtester()
executor = TradingExecutor()
strategy = TradingStrategy()

tabs = st.tabs(["Market Scanner", "Backtesting", "Portfolio & Paper Trading"])

with tabs[0]:
    st.header("Market Scanner (5-Min EMA/RSI)")
    
    scan_mode = st.radio("Scan Mode", ["Curated List", "Active Market (Top 50)"])
    
    if st.button("Run Market Scan"):
        with st.spinner("Scanning market for setups..."):
            if scan_mode == "Curated List":
                symbols = scanner.default_symbols
            else:
                symbols = scanner.get_active_assets(limit=50)
                
            results = scanner.scan(symbols=symbols)
            if not results.empty:
                st.dataframe(results)
            else:
                st.info("No active signals found at this moment.")

with tabs[1]:
    st.header("Backtesting Engine")
    col1, col2, col3 = st.columns(3)
    with col1:
        bt_symbol = st.text_input("Symbol", value="AAPL")
    with col2:
        start_date = st.date_input("Start Date", value=datetime.date.today() - datetime.timedelta(days=30))
    with col3:
        end_date = st.date_input("End Date", value=datetime.date.today())
    
    if st.button("Run Backtest"):
        with st.spinner(f"Running backtest for {bt_symbol}..."):
            results = backtester.run_backtest(bt_symbol, start_date.isoformat(), end_date.isoformat())
            
            if results:
                st.subheader(f"Results for {bt_symbol}")
                metric1, metric2, metric3 = st.columns(3)
                metric1.metric("Final Value", f"${results['final_value']:,.2f}")
                metric2.metric("Total Return", f"{results['total_return']:.2%}")
                metric3.metric("Trade Count", len(results['trades']))
                
                # Plotly Chart
                df = results['data']
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df['close'], name='Close Price'))
                fig.add_trace(go.Scatter(x=df.index, y=df['ema_fast'], name='EMA 9'))
                fig.add_trace(go.Scatter(x=df.index, y=df['ema_slow'], name='EMA 21'))
                
                # Add buy/sell markers
                trades = results['trades']
                if not trades.empty:
                    buys = trades[trades['type'] == 'buy']
                    sells = trades[trades['type'] == 'sell']
                    fig.add_trace(go.Scatter(x=buys['time'], y=buys['price'], mode='markers', marker=dict(color='green', symbol='triangle-up', size=10), name='Buy'))
                    fig.add_trace(go.Scatter(x=sells['time'], y=sells['price'], mode='markers', marker=dict(color='red', symbol='triangle-down', size=10), name='Sell'))
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("Trade Log")
                st.dataframe(trades)
            else:
                st.error("No data found for the selected symbol and date range.")

with tabs[2]:
    st.header("Portfolio & Paper Trading")
    
    account = executor.get_account()
    if account:
        st.subheader("Account Summary")
        m1, m2, m3 = st.columns(3)
        m1.metric("Equity", f"${float(account.equity):,.2f}")
        m2.metric("Buying Power", f"${float(account.buying_power):,.2f}")
        # Safe lookup that checks for both naming versions and falls back to buying_power
        dt_power = getattr(account, 'day_trading_power', getattr(account, 'daytrading_power', account.buying_power))
        m3.metric("Day Trading Power", f"${float(dt_power):,.2f}")
        
        positions = executor.get_positions()
        if positions:
            st.subheader("Current Positions")
            pos_data = []
            for p in positions:
                pos_data.append({
                    'Symbol': p.symbol,
                    'Qty': p.qty,
                    'Market Value': f"${float(p.market_value):,.2f}",
                    'Avg Entry': f"${float(p.avg_entry_price):,.2f}",
                    'Unrealized P/L': f"${float(p.unrealized_pl):,.2f}"
                })
            st.dataframe(pd.DataFrame(pos_data))
        else:
            st.info("No open positions.")
    else:
        st.warning("Please enter valid Alpaca API keys in the sidebar to view portfolio and trade.")
    
    st.divider()
    st.subheader("Manual Paper Trade Execution")
    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    with t_col1:
        t_symbol = st.text_input("Symbol", key="trade_symbol", value="AAPL")
    with t_col2:
        t_side = st.selectbox("Side", ["buy", "sell"])
    with t_col3:
        t_type = st.selectbox("Asset Type", ["Stock", "Option"])
    with t_col4:
        t_qty = st.number_input("Qty", min_value=1, value=1)
        
    if st.button("Execute Trade"):
        if t_type == "Stock":
            order = executor.execute_stock_trade(t_symbol, t_side, qty=t_qty)
        else:
            order = executor.execute_options_trade(t_symbol, t_side)
            
        if order:
            st.success(f"Order placed: {order.id}")
        else:
            st.error("Order failed. Check console/logs for details.")
