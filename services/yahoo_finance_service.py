"""
Yahoo Finance Service - Free alternative to Polygon.io
Provides US stock market data without API key requirements
"""

import yfinance as yf
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

    def get_top_gainers(self, limit: int = 10) -> List[Dict]:
        """
        Get top gaining stocks from major S&P 500 components

        Args:
            limit: Number of top gainers to return

        Returns:
            List of stock data dictionaries with ticker, name, price, change
        """
        try:
            logger.info(f"Fetching top {limit} gainers from Yahoo Finance")

            gainers = []

            # Fetch data for major tickers
            for ticker in self.SP500_MAJOR_TICKERS[:30]:  # Check top 30 for performance
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info

                    # Get current price and change
                    current_price = info.get("currentPrice") or info.get(
                        "regularMarketPrice"
                    )
                    previous_close = info.get("previousClose")

                    if current_price and previous_close:
                        change_percent = (
                            (current_price - previous_close) / previous_close
                        ) * 100

                        gainers.append(
                            {
                                "ticker": ticker,
                                "name": info.get("longName", ticker),
                                "price": current_price,
                                "change_percent": round(change_percent, 2),
                                "sector": info.get("sector", "Unknown"),
                                "volume": info.get("volume", 0),
                            }
                        )
                except Exception as e:
                    logger.warning(f"Error fetching data for {ticker}: {e}")
                    continue

            # Sort by change percentage and return top gainers
            gainers.sort(key=lambda x: x["change_percent"], reverse=True)

            logger.info(f"Found {len(gainers)} stocks, returning top {limit}")
            return gainers[:limit]

        except Exception as e:
            logger.error(f"Error fetching top gainers: {e}")
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
            }

        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return None

    def get_market_indices(self) -> Dict:
        """
        Get major US market indices (S&P 500, Dow, Nasdaq)

        Returns:
            Dictionary with index data
        """
        try:
            indices = {"^GSPC": "S&P 500", "^DJI": "Dow Jones", "^IXIC": "Nasdaq"}

            results = {}

            for symbol, name in indices.items():
                try:
                    index = yf.Ticker(symbol)
                    info = index.info

                    current_price = info.get("regularMarketPrice")
                    previous_close = info.get("previousClose")

                    if current_price and previous_close:
                        change_percent = (
                            (current_price - previous_close) / previous_close
                        ) * 100

                        results[name] = {
                            "value": current_price,
                            "change_percent": round(change_percent, 2),
                        }
                except Exception as e:
                    logger.warning(f"Error fetching {name}: {e}")
                    continue

            return results

        except Exception as e:
            logger.error(f"Error fetching market indices: {e}")
            return {}

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
