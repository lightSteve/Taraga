import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"


class PolygonService:
    """Service to fetch US market data from Polygon.io"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or POLYGON_API_KEY
        if not self.api_key:
            raise ValueError("Polygon API key is required")

    def get_previous_close(self, ticker: str):
        """Get previous day's close data for a ticker"""
        url = f"{BASE_URL}/v2/aggs/ticker/{ticker}/prev"
        params = {"apiKey": self.api_key}

        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_market_snapshot(self):
        """Get snapshot of major US indices"""
        tickers = ["SPY", "QQQ", "DIA"]  # S&P 500, Nasdaq, Dow ETFs
        snapshots = {}

        for ticker in tickers:
            try:
                data = self.get_previous_close(ticker)
                if data.get("results"):
                    result = data["results"][0]
                    snapshots[ticker] = {
                        "close": result.get("c"),
                        "open": result.get("o"),
                        "high": result.get("h"),
                        "low": result.get("l"),
                        "volume": result.get("v"),
                        "change_percent": (
                            (result.get("c") - result.get("o")) / result.get("o") * 100
                        ),
                    }
            except Exception as e:
                print(f"Error fetching {ticker}: {e}")

        return snapshots

    def get_top_gainers(self, date: str = None):
        """Get top gaining stocks for a specific date"""
        # Note: This requires Polygon.io premium tier
        # For now, returning placeholder
        # In production, use: /v2/snapshot/locale/us/markets/stocks/gainers
        url = f"{BASE_URL}/v2/snapshot/locale/us/markets/stocks/gainers"
        params = {"apiKey": self.api_key}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract top 10 gainers
            tickers = data.get("tickers", [])[:10]
            return [
                {
                    "ticker": t.get("ticker"),
                    "price": t.get("day", {}).get("c"),
                    "change_percent": t.get("todaysChangePerc"),
                    "volume": t.get("day", {}).get("v"),
                }
                for t in tickers
            ]
        except Exception as e:
            print(f"Error fetching top gainers: {e}")
            return []


if __name__ == "__main__":
    # Test the service
    service = PolygonService()
    print("📊 Market Snapshot:")
    print(service.get_market_snapshot())
    print("\n🚀 Top Gainers:")
    print(service.get_top_gainers())
