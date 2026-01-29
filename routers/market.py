from fastapi import APIRouter
from services.service_factory import ServiceFactory

router = APIRouter()


@router.get("/us/snapshot")
def get_us_market_snapshot():
    """
    Get snapshot of US major indices

    Uses free Yahoo Finance or premium Polygon.io based on configuration
    """
    try:
        market_service = ServiceFactory.get_market_data_service()
        indices = market_service.get_market_indices()
        return {"status": "success", "data": indices}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.get("/us/top-gainers")
def get_us_top_gainers(limit: int = 10):
    """
    Get top gaining US stocks

    Uses free Yahoo Finance or premium Polygon.io based on configuration
    """
    try:
        market_service = ServiceFactory.get_market_data_service()
        gainers = market_service.get_top_gainers(limit=limit)
        return {"status": "success", "data": gainers}
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
