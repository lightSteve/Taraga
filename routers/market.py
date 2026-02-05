from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import StockKR
from services.service_factory import ServiceFactory
from logic.correlation_engine import CorrelationEngine

router = APIRouter()


@router.get("/us/snapshot")
def get_us_market_snapshot(db: Session = Depends(get_db)):
    """
    Get snapshot of US major indices

    Uses free Yahoo Finance or premium Polygon.io based on configuration
    """
    try:
        market_service = ServiceFactory.get_market_data_service(db)
        indices = market_service.get_market_indices()
        return {"status": "success", "data": indices}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/us/top-gainers")
def get_us_top_gainers(limit: int = 10, db: Session = Depends(get_db)):
    try:
        market_service = ServiceFactory.get_market_data_service(db)
        gainers = (
            market_service.get_top_gainers()
            if hasattr(market_service, "get_top_gainers")
            else []
        )
        # Handle param difference if any
        return {"status": "success", "data": gainers[:limit]}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/us/top-losers")
def get_us_top_losers(limit: int = 10, db: Session = Depends(get_db)):
    try:
        market_service = ServiceFactory.get_market_data_service(db)
        losers = (
            market_service.get_top_losers()
            if hasattr(market_service, "get_top_losers")
            else []
        )
        return {"status": "success", "data": losers[:limit]}
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
    """Get Top Retail (WSB) Picks"""
    try:
        from services.scraper_service import ScraperService

        service = ScraperService(db)
        return {"status": "success", "data": service.get_retail_picks(region=region)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/us/trends/institutional")
def get_institutional_flow(region: str = "US", db: Session = Depends(get_db)):
    """Get Top Institutional Picks"""
    try:
        from services.scraper_service import ScraperService

        service = ScraperService(db)
        return {"status": "success", "data": service.get_institutional_picks(region=region)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/search")
def search_stocks(query: str, db: Session = Depends(get_db)):
    """Search KR stocks by name or ticker."""
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
