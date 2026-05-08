# Day Trading Bot

A Python-based day trading bot that scans the market for stock setups using EMA crossovers and RSI, with support for backtesting and paper trading (including simple options).

## Features
- Market Scanner: Scans for 5-minute EMA (9/21) crossovers confirmed by RSI (14).
- Backtesting: Test strategies on historical stock data.
- Paper Trading: Execute trades in Alpaca's paper trading environment.
- Options: Simple Call/Put buying for identified trends.
- Dashboard: Streamlit-based UI for monitoring and analysis.

## Setup
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your Alpaca API credentials.
4. Run the dashboard: `streamlit run src/dashboard.py`

## Project Structure
- `src/`: Source code for the bot.
  - `strategy.py`: Strategy logic.
  - `scanner.py`: Market scanning logic.
  - `backtester.py`: Backtesting engine.
  - `trading.py`: Alpaca API interaction and execution.
  - `dashboard.py`: Streamlit UI.
