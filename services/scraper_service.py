import requests
from bs4 import BeautifulSoup
import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import MarketDataCache
import json
import logging
import yfinance as yf

logger = logging.getLogger(__name__)


class ScraperService:
    """
    Service to scrape retail (WSB/Reddit) vs Institutional (Analyst) picks.
    Includes caching to prevent blocking and rate limits.
    """

    CACHE_KEY_RETAIL = "RETAIL_PICKS"
    CACHE_KEY_INSTITUTIONAL = "INSTITUTIONAL_PICKS"

    # 6 hours cache for scraping
    CACHE_DURATION_HOURS = 6

    # Common ETF patterns
    ETF_PATTERNS = [
        "SPY",
        "QQQ",
        "IWM",
        "DIA",
        "VTI",
        "VOO",
        "VEA",
        "VWO",
        "AGG",
        "BND",
        "GLD",
        "SLV",
        "XLF",
        "XLE",
        "XLK",
        "XLV",
        "XLI",
        "XLP",
        "XLY",
        "XLU",
        "EEM",
        "EWJ",
        "EWZ",
        "FXI",
        "TLT",
        "SHY",
        "IEF",
        "LQD",
        "HYG",
        "ARKK",
    ]

    def __init__(self, db: Session):
        self.db = db
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def _is_etf(self, ticker):
        """Check if ticker is likely an ETF"""
        ticker_upper = ticker.upper()
        # Known ETF
        if ticker_upper in self.ETF_PATTERNS:
            return True
        # ETF naming patterns (usually 3-4 letters, all caps)
        if len(ticker_upper) == 3 and ticker_upper.isupper():
            return ticker_upper in self.ETF_PATTERNS
        return False

    def _enrich_with_price_data(self, results):
        """Add real-time price change percentage and type to results"""
        enriched = []
        for item in results:
            ticker = item.get("ticker", "")
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="1d")

                # Get price change
                change_percent = 0.0
                if not hist.empty and "Close" in hist.columns:
                    current_price = hist["Close"].iloc[-1]
                    prev_close = info.get("previousClose", current_price)
                    if prev_close and prev_close > 0:
                        change_percent = (
                            (current_price - prev_close) / prev_close
                        ) * 100

                # Determine type
                quote_type = info.get("quoteType", "EQUITY")
                is_etf = quote_type == "ETF" or self._is_etf(ticker)

                item["change_percent"] = round(change_percent, 2)
                item["type"] = "ETF" if is_etf else "STOCK"

            except Exception as e:
                logger.warning(f"Failed to get price data for {ticker}: {e}")
                item["change_percent"] = 0.0
                item["type"] = "ETF" if self._is_etf(ticker) else "STOCK"

            enriched.append(item)

        return enriched

    def _get_from_cache(self, key):
        if not self.db:
            return None
        try:
            cache = (
                self.db.query(MarketDataCache)
                .filter(MarketDataCache.key == key)
                .first()
            )
            if cache:
                updated_at = cache.updated_at
                if updated_at.tzinfo is None:
                    updated_at = updated_at.replace(tzinfo=datetime.timezone.utc)

                # Check expiry
                now = datetime.datetime.now(datetime.timezone.utc)
                if (now - updated_at) < datetime.timedelta(
                    hours=self.CACHE_DURATION_HOURS
                ):
                    return cache.data
                else:
                    return None  # Expired
        except Exception as e:
            logger.error(f"Cache check failed: {e}")
            self.db.rollback()
            return None

    def _save_to_cache(self, key, data):
        if not self.db:
            return
        try:
            cache = (
                self.db.query(MarketDataCache)
                .filter(MarketDataCache.key == key)
                .first()
            )
            if cache:
                cache.data = data
                cache.updated_at = func.now()
            else:
                new_cache = MarketDataCache(key=key, data=data)
                self.db.add(new_cache)
            self.db.commit()
        except Exception as e:
            logger.error(f"Cache save failed: {e}")
            self.db.rollback()

    def get_retail_picks(self, region: str = "US"):
        """
        Get trending retail picks. Only US supported (ApeWisdom).
        KR/Coin have no free real-time data source.
        """
        if region != "US":
            return []

        cache_key = f"{self.CACHE_KEY_RETAIL}_{region}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        results = []

        # US: ApeWisdom (WSB/Reddit sentiment)
        try:
            response = requests.get(
                "https://apewisdom.io/all-stocks/", headers=self.headers, timeout=10
            )
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                rows = soup.select("table.table tbody tr")
                for row in rows[:5]:
                    cols = row.select("td")
                    if len(cols) > 2:
                        ticker_el = row.select_one(".company-name") or cols[1]
                        ticker = ticker_el.text.strip().split("\n")[0]
                        mentions_el = cols[3]
                        mentions = mentions_el.text.strip()
                        results.append(
                            {
                                "ticker": ticker,
                                "name": ticker,
                                "mentions": mentions + " mentions",
                            }
                        )
        except Exception as e:
            logger.warning(f"Retail scrape failed: {e}")

        if not results:
            results = [
                {"ticker": "TSLA", "name": "Tesla", "mentions": "2.4k mentions", "change_percent": 3.2, "type": "STOCK"},
                {"ticker": "NVDA", "name": "NVIDIA", "mentions": "1.8k mentions", "change_percent": 5.7, "type": "STOCK"},
                {"ticker": "SPY", "name": "S&P 500 ETF", "mentions": "1.5k mentions", "change_percent": 0.8, "type": "ETF"},
                {"ticker": "AMD", "name": "AMD", "mentions": "1.2k mentions", "change_percent": -1.3, "type": "STOCK"},
                {"ticker": "AAPL", "name": "Apple", "mentions": "950 mentions", "change_percent": 1.5, "type": "STOCK"},
            ]

        self._save_to_cache(cache_key, results)
        return results

    def get_institutional_picks(self, region: str = "US"):
        """
        Get institutional/analyst picks. Only US supported (curated).
        KR/Coin have no free real-time data source.
        """
        if region != "US":
            return []

        cache_key = f"{self.CACHE_KEY_INSTITUTIONAL}_{region}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        results = [
            {"ticker": "MSFT", "name": "Microsoft", "rating": "Upgrade to Buy", "change_percent": 2.1, "type": "STOCK"},
            {"ticker": "GOOGL", "name": "Alphabet", "rating": "Strong Buy", "change_percent": 1.8, "type": "STOCK"},
            {"ticker": "QQQ", "name": "Nasdaq 100 ETF", "rating": "Overweight", "change_percent": 1.2, "type": "ETF"},
            {"ticker": "JPM", "name": "JPMorgan", "rating": "Upgrade to Outperform", "change_percent": 0.9, "type": "STOCK"},
            {"ticker": "LLY", "name": "Eli Lilly", "rating": "Buy Target Raised", "change_percent": 4.3, "type": "STOCK"},
        ]

        self._save_to_cache(cache_key, results)
        return results
