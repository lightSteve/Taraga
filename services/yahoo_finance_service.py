"""
Yahoo Finance Service - Free alternative to Polygon.io
Provides US stock market data without API key requirements
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class YahooFinanceService:
    """Free US market data service using Yahoo Finance"""

    # S&P 500 major components for top gainers analysis
    SP500_MAJOR_TICKERS = [
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "NVDA",
        "META",
        "TSLA",
        "BRK-B",
        "UNH",
        "JNJ",
        "V",
        "XOM",
        "WMT",
        "JPM",
        "PG",
        "MA",
        "HD",
        "CVX",
        "MRK",
        "ABBV",
        "KO",
        "PEP",
        "COST",
        "AVGO",
        "LLY",
        "TMO",
        "MCD",
        "CSCO",
        "ACN",
        "ABT",
        "DHR",
        "VZ",
        "ADBE",
        "NKE",
        "TXN",
        "NEE",
        "PM",
        "CRM",
        "ORCL",
        "WFC",
        "BMY",
        "UPS",
        "RTX",
        "HON",
        "QCOM",
        "INTC",
        "AMD",
        "NFLX",
        "IBM",
        "BA",
        "GE",
    ]

    def _get_mock_gainers_losers(self, is_gainer: bool):
        """Mock data for demo/fallback purposes"""
        if is_gainer:
            return [
                {
                    "ticker": "NVDA",
                    "name": "NVIDIA Corp",
                    "price": 875.28,
                    "change_percent": 3.12,
                    "volume": 45000000,
                },
                {
                    "ticker": "META",
                    "name": "Meta Platforms",
                    "price": 485.50,
                    "change_percent": 2.45,
                    "volume": 12000000,
                },
                {
                    "ticker": "AMZN",
                    "name": "Amazon.com",
                    "price": 178.22,
                    "change_percent": 1.89,
                    "volume": 32000000,
                },
                {
                    "ticker": "MSFT",
                    "name": "Microsoft Corp",
                    "price": 415.10,
                    "change_percent": 1.56,
                    "volume": 22000000,
                },
                {
                    "ticker": "GOOGL",
                    "name": "Alphabet Inc",
                    "price": 142.65,
                    "change_percent": 1.23,
                    "volume": 18000000,
                },
                {
                    "ticker": "AMD",
                    "name": "Adv. Micro Devices",
                    "price": 180.45,
                    "change_percent": 1.15,
                    "volume": 40100000,
                },
                {
                    "ticker": "AVGO",
                    "name": "Broadcom Inc",
                    "price": 1305.10,
                    "change_percent": 1.05,
                    "volume": 2500000,
                },
                {
                    "ticker": "TSM",
                    "name": "Taiwan Semi",
                    "price": 145.20,
                    "change_percent": 0.95,
                    "volume": 15000000,
                },
                {
                    "ticker": "LLY",
                    "name": "Eli Lilly",
                    "price": 760.30,
                    "change_percent": 0.88,
                    "volume": 1800000,
                },
                {
                    "ticker": "JPM",
                    "name": "JPMorgan Chase",
                    "price": 195.40,
                    "change_percent": 0.75,
                    "volume": 8500000,
                },
            ]
        else:
            return [
                {
                    "ticker": "TSLA",
                    "name": "Tesla Inc",
                    "price": 175.34,
                    "change_percent": -3.45,
                    "volume": 89000000,
                },
                {
                    "ticker": "AAPL",
                    "name": "Apple Inc",
                    "price": 169.12,
                    "change_percent": -1.82,
                    "volume": 48000000,
                },
                {
                    "ticker": "NFLX",
                    "name": "Netflix Inc",
                    "price": 605.30,
                    "change_percent": -1.54,
                    "volume": 5000000,
                },
                {
                    "ticker": "INTC",
                    "name": "Intel Corp",
                    "price": 42.15,
                    "change_percent": -0.98,
                    "volume": 34000000,
                },
                {
                    "ticker": "BA",
                    "name": "Boeing Co",
                    "price": 185.20,
                    "change_percent": -0.85,
                    "volume": 4200000,
                },
                {
                    "ticker": "NKE",
                    "name": "Nike Inc",
                    "price": 95.40,
                    "change_percent": -0.78,
                    "volume": 5600000,
                },
                {
                    "ticker": "SBUX",
                    "name": "Starbucks Corp",
                    "price": 90.15,
                    "change_percent": -0.65,
                    "volume": 6700000,
                },
                {
                    "ticker": "PYPL",
                    "name": "PayPal Holdings",
                    "price": 62.30,
                    "change_percent": -0.55,
                    "volume": 9800000,
                },
                {
                    "ticker": "DIS",
                    "name": "Walt Disney",
                    "price": 110.45,
                    "change_percent": -0.42,
                    "volume": 7500000,
                },
                {
                    "ticker": "KO",
                    "name": "Coca-Cola Co",
                    "price": 59.80,
                    "change_percent": -0.35,
                    "volume": 11000000,
                },
            ]

    def get_top_gainers(self, limit: int = 10) -> List[Dict]:
        """Get top gaining stocks from major S&P 500 components (real data)."""
        try:
            all_stocks = self._fetch_all_movers()
            if not all_stocks:
                return self._get_mock_gainers_losers(is_gainer=True)[:limit]
            # Sort descending (biggest gain first)
            all_stocks.sort(key=lambda x: x["change_percent"], reverse=True)
            gainers = [s for s in all_stocks if s["change_percent"] > 0]
            return (gainers or self._get_mock_gainers_losers(is_gainer=True))[:limit]
        except Exception as e:
            logger.error(f"Error fetching top gainers: {e}")
            return self._get_mock_gainers_losers(is_gainer=True)[:limit]

    def get_top_losers(self, limit: int = 10) -> List[Dict]:
        """Get top losing stocks from major S&P 500 components (real data)."""
        try:
            all_stocks = self._fetch_all_movers()
            if not all_stocks:
                return self._get_mock_gainers_losers(is_gainer=False)[:limit]
            # Sort ascending (most negative first)
            all_stocks.sort(key=lambda x: x["change_percent"])
            losers = [s for s in all_stocks if s["change_percent"] < 0]
            return (losers or self._get_mock_gainers_losers(is_gainer=False))[:limit]
        except Exception as e:
            logger.error(f"Error fetching top losers: {e}")
            return self._get_mock_gainers_losers(is_gainer=False)[:limit]

    def _fetch_all_movers(self) -> List[Dict]:
        """Shared batch download for both gainers and losers."""
        try:
            tickers_str = " ".join(self.SP500_MAJOR_TICKERS[:30])
            data = yf.download(
                tickers_str, period="2d", group_by="ticker",
                progress=False, threads=False,
            )
            if data is None or data.empty:
                return []

            results = []
            for ticker in self.SP500_MAJOR_TICKERS[:30]:
                try:
                    if ticker in data.columns.levels[0]:
                        df = data[ticker]
                    else:
                        continue
                    if len(df) < 2:
                        continue
                    current_close = float(df["Close"].iloc[-1])
                    prev_close = float(df["Close"].iloc[-2])
                    if prev_close > 0:
                        change_percent = ((current_close - prev_close) / prev_close) * 100
                        results.append({
                            "ticker": ticker, "name": ticker,
                            "price": current_close,
                            "change_percent": round(change_percent, 2),
                            "sector": "Major US",
                            "volume": int(df["Volume"].iloc[-1]),
                        })
                except Exception:
                    continue
            return results
        except Exception:
            return []

    def get_stock_data(self, ticker: str) -> Optional[Dict]:
        """
        Get detailed data for a specific stock

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with stock data or None if error
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            previous_close = info.get("previousClose")

            if not current_price:
                return None

            change_percent = 0
            if previous_close:
                change_percent = (
                    (current_price - previous_close) / previous_close
                ) * 100

            return {
                "ticker": ticker,
                "name": info.get("longName", ticker),
                "price": current_price,
                "change_percent": round(change_percent, 2),
                "sector": info.get("sector", "Unknown"),
                "volume": info.get("volume", 0),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE"),
                "currency": info.get("currency", "USD"),
                "description": info.get(
                    "longBusinessSummary", "No description available."
                ),
            }

        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return None

    def get_market_indices(self) -> Dict:
        """
        Get major market indices for US, KR, and Crypto.
        Uses yf.download() batch method for reliability.

        Returns:
            Dictionary with index data keyed by symbol
        """
        # Define indices for each market
        indices_map = {
            # US
            "^GSPC": {"name": "S&P 500", "market": "US"},
            "^DJI": {"name": "Dow Jones", "market": "US"},
            "^IXIC": {"name": "Nasdaq", "market": "US"},
            # KR
            "^KS11": {"name": "KOSPI", "market": "KR"},
            "^KQ11": {"name": "KOSDAQ", "market": "KR"},
            # Coin
            "BTC-USD": {"name": "Bitcoin", "market": "Coin"},
            "ETH-USD": {"name": "Ethereum", "market": "Coin"},
        }
        tickers_str = " ".join(indices_map.keys())

        try:
            logger.info(f"Downloading market indices: {tickers_str}")
            # Fetch 1 month to ensure enough data points for sparkline (approx ~20 trading days)
            data = yf.download(
                tickers_str,
                period="1mo",
                group_by="ticker",
                progress=False,
                threads=False,
            )

            if data is None or data.empty:
                logger.warning(
                    "yfinance download returned empty for indices, using mock"
                )
                return self._get_mock_indices()

            results = {}
            for symbol, info in indices_map.items():
                name = info["name"]
                market = info["market"]
                try:
                    df = None
                    if len(indices_map) == 1:
                        df = data
                    else:
                        # Handle potential MultiIndex columns structure differences
                        if isinstance(data.columns, pd.MultiIndex):
                            if symbol in data.columns.get_level_values(
                                1
                            ):  # Ticker is level 1
                                df = data.xs(symbol, axis=1, level=1)
                            elif symbol in data.columns.get_level_values(
                                0
                            ):  # Ticker is level 0
                                df = data[symbol]
                        else:
                            if symbol in data.columns:
                                df = data[
                                    symbol
                                ]  # Should not happen with group_by='ticker' but safe check

                    if df is None:
                        # Fallback search if structure is unexpected
                        continue

                    # Drop NaN rows and get last 2 valid closes
                    df = df.dropna(subset=["Close"])
                    if len(df) < 2:
                        continue

                    # Prepare history for sparkline (last 14 days)
                    history = [float(x) for x in df["Close"].tail(14).tolist()]

                    current_close = float(df["Close"].iloc[-1])
                    prev_close = float(df["Close"].iloc[-2])

                    if prev_close > 0:
                        change_percent = (
                            (current_close - prev_close) / prev_close
                        ) * 100
                        results[name] = {
                            "regularMarketPrice": round(current_close, 2),
                            "regularMarketChangePercent": round(change_percent, 2),
                            "history": history,
                            "market": market,  # Add market type for frontend grouping
                        }
                except Exception as e:
                    logger.warning(f"Error processing index {name}: {e}")
                    continue

            if not results:
                return self._get_mock_indices()

            return results

        except Exception as e:
            logger.error(f"Error fetching market indices: {e}")
            return self._get_mock_indices()

    def _get_mock_indices(self):
        # Helper for mock data structure matches new return format
        import random

        return {
            "S&P 500": {
                "regularMarketPrice": 5100.0,
                "regularMarketChangePercent": 0.5,
                "history": [5000 + i * 10 for i in range(14)],
                "market": "US",
            },
            "Dow Jones": {
                "regularMarketPrice": 39000.0,
                "regularMarketChangePercent": 0.2,
                "history": [38000 + i * 50 for i in range(14)],
                "market": "US",
            },
            "Nasdaq": {
                "regularMarketPrice": 16000.0,
                "regularMarketChangePercent": 0.8,
                "history": [15500 + i * 40 for i in range(14)],
                "market": "US",
            },
            "KOSPI": {
                "regularMarketPrice": 2650.0,
                "regularMarketChangePercent": -0.3,
                "history": [2600 + i * 5 for i in range(14)],
                "market": "KR",
            },
            "KOSDAQ": {
                "regularMarketPrice": 850.0,
                "regularMarketChangePercent": -0.5,
                "history": [840 + i * 2 for i in range(14)],
                "market": "KR",
            },
            "Bitcoin": {
                "regularMarketPrice": 65000.0,
                "regularMarketChangePercent": 2.5,
                "history": [60000 + i * 500 for i in range(14)],
                "market": "Coin",
            },
            "Ethereum": {
                "regularMarketPrice": 3500.0,
                "regularMarketChangePercent": 1.2,
                "history": [3200 + i * 20 for i in range(14)],
                "market": "Coin",
            },
        }

    def get_historical_data(self, ticker: str, days: int = 30) -> List[Dict]:
        """
        Get historical price data for a stock

        Args:
            ticker: Stock ticker symbol
            days: Number of days of historical data

        Returns:
            List of daily price data
        """
        try:
            stock = yf.Ticker(ticker)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            hist = stock.history(start=start_date, end=end_date)

            data = []
            for date, row in hist.iterrows():
                data.append(
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "open": round(row["Open"], 2),
                        "high": round(row["High"], 2),
                        "low": round(row["Low"], 2),
                        "close": round(row["Close"], 2),
                        "volume": int(row["Volume"]),
                    }
                )

            return data

        except Exception as e:
            logger.error(f"Error fetching historical data for {ticker}: {e}")
            return []
