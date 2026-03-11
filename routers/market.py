"""
Market Router — US market data endpoints with server-side caching.
All responses are cached in MarketDataCache to prevent rate limits
and share data across all users.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import StockKR
from services.cache_service import (
    CacheService,
    TTL_MARKET_INDICES,
    TTL_GAINERS_LOSERS,
    TTL_SCRAPER,
)
from services.service_factory import ServiceFactory
from logic.correlation_engine import CorrelationEngine

router = APIRouter()


@router.get("/us/snapshot")
def get_us_market_snapshot(db: Session = Depends(get_db)):
    """
    Get snapshot of US major indices (cached, 15 min TTL).
    First request fetches from Yahoo Finance, subsequent requests use cache.
    """
    try:
        cache = CacheService(db)
        market_service = ServiceFactory.get_market_data_service(db)

        indices = cache.get_or_fetch(
            "US_INDICES_V2",
            lambda: market_service.get_market_indices(),
            ttl_minutes=TTL_MARKET_INDICES,
        )

        if not indices:
            return {
                "status": "error",
                "message": "시장 데이터를 가져올 수 없습니다.",
                "data": {},
            }

        return {"status": "success", "data": indices}
    except Exception as e:
        return {"status": "error", "message": str(e), "data": {}}


@router.get("/us/top-gainers")
def get_us_top_gainers(limit: int = 10, db: Session = Depends(get_db)):
    """Get top gaining stocks (cached, 30 min TTL)."""
    try:
        cache = CacheService(db)
        market_service = ServiceFactory.get_market_data_service(db)

        all_gainers = cache.get_or_fetch(
            "US_TOP_GAINERS",
            lambda: (
                market_service.get_top_gainers()
                if hasattr(market_service, "get_top_gainers")
                else []
            ),
            ttl_minutes=TTL_GAINERS_LOSERS,
        )

        return {"status": "success", "data": (all_gainers or [])[:limit]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/us/top-losers")
def get_us_top_losers(limit: int = 10, db: Session = Depends(get_db)):
    """Get top losing stocks (cached, 30 min TTL)."""
    try:
        cache = CacheService(db)
        market_service = ServiceFactory.get_market_data_service(db)

        all_losers = cache.get_or_fetch(
            "US_TOP_LOSERS",
            lambda: (
                market_service.get_top_losers()
                if hasattr(market_service, "get_top_losers")
                else []
            ),
            ttl_minutes=TTL_GAINERS_LOSERS,
        )

        return {"status": "success", "data": (all_losers or [])[:limit]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/service-status")
def get_service_status():
    """Get current API service configuration (free vs premium)"""
    try:
        status = ServiceFactory.get_service_status()
        return {"status": "success", "data": status}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/watchlist/{symbol}/us-impact")
def get_watchlist_us_impact(symbol: str):
    """Estimate potential US market impact for a given Korean symbol."""
    try:
        engine = CorrelationEngine()
        result = engine.get_us_impact_for_kr_symbol(symbol)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/us/trends/retail")
def get_retail_flow(region: str = "US", db: Session = Depends(get_db)):
    """Get Top Retail Picks (cached, 4 hour TTL). Supports region: US, KR, Coin."""
    try:
        cache = CacheService(db)

        from services.scraper_service import ScraperService

        service = ScraperService(db)

        # Cache key must include region now
        cache_key_suffix = f"RETAIL_PICKS_{region}"

        data = cache.get_or_fetch(
            cache_key_suffix,
            lambda: service.get_retail_picks(region=region),
            ttl_minutes=TTL_SCRAPER,
        )

        return {"status": "success", "data": data or []}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/us/trends/institutional")
def get_institutional_flow(region: str = "US", db: Session = Depends(get_db)):
    """Get Top Institutional Picks (cached, 4 hour TTL). Supports region: US, KR, Coin."""
    try:
        cache = CacheService(db)

        from services.scraper_service import ScraperService

        service = ScraperService(db)

        cache_key_suffix = f"INSTITUTIONAL_PICKS_{region}"

        data = cache.get_or_fetch(
            cache_key_suffix,
            lambda: service.get_institutional_picks(region=region),
            ttl_minutes=TTL_SCRAPER,
        )

        return {"status": "success", "data": data or []}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/search")
def search_stocks(query: str, db: Session = Depends(get_db)):
    """
    Search KR stocks by name or ticker.
    Case-insensitive partial match. (No caching — queries are dynamic)
    """
    if not query or len(query) < 1:
        return []

    results = (
        db.query(StockKR)
        .filter(
            (StockKR.name.ilike(f"%{query}%")) | (StockKR.ticker.ilike(f"%{query}%"))
        )
        .limit(20)
        .all()
    )

    return [
        {"ticker": stock.ticker, "name": stock.name, "sector": stock.sector}
        for stock in results
    ]


@router.get("/stock/{ticker}")
def get_stock_detail(ticker: str, db: Session = Depends(get_db)):
    """
    Get detailed stock info + 30 days history.
    """
    try:
        cache = CacheService(db)
        market_service = ServiceFactory.get_market_data_service(db)

        # Cache key specific to ticker
        cache_key = f"STOCK_DETAIL_{ticker}"

        def fetch_detail():
            info = market_service.get_stock_data(ticker)
            if not info:
                return None
            history = market_service.get_historical_data(ticker, days=30)
            info["history"] = history
            return info

        data = cache.get_or_fetch(
            cache_key,
            fetch_detail,
            ttl_minutes=15,  # 15 min cache for details
        )

        if not data:
            return {"status": "error", "message": "Stock not found"}

        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
