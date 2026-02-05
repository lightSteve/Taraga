from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from services.stock_service import StockService
from logic.correlation_engine import CorrelationEngine

router = APIRouter()


@router.get("/personal-matches")
def get_personal_matches(user_uuid: str, db: Session = Depends(get_db)):
    """
    Get personalized stock matches using Real Data Logic (StockService)
    """
    service = StockService(db)
    return service.get_analyzed_watchlist(user_uuid)


@router.get("/value-chain")
def get_value_chain(theme_id: int, db: Session = Depends(get_db)):
    """
    Get the hierarchical Value Chain visualization data for a specific theme.
    """
    engine = CorrelationEngine(db)
    tree = engine.get_value_chain_tree(theme_id)

    if not tree:
        raise HTTPException(status_code=404, detail="Theme or Value Chain not found")

    return tree


@router.get("/news-bridge")
def get_news_bridge(db: Session = Depends(get_db)):
    """
    Get the list of 'Bridge News' connecting US events to KR impacts.
    """
    # Mock Data for MVP
    news_items = [
        {
            "us_source": "Bloomberg",
            "us_headline": "Micron Starts Mass Production of HBM3E for Nvidia",
            "kr_impact": "Positive for SK Hynix (Process Partner) & Hanmi Semi (Equipment)",
            "related_stocks": [
                {"name": "SK Hynix", "ticker": "000660", "change": "+3.2%"},
                {"name": "Hanmi Semi", "ticker": "042700", "change": "+5.4%"},
            ],
            "timestamp": "2024-02-27T06:00:00",
        },
        {
            "us_source": "Reuters",
            "us_headline": "FDA Approves New Alzheimer's Drug by Eli Lilly",
            "kr_impact": "Boost for CDMOs likely to secure contracts",
            "related_stocks": [
                {"name": "Samsung Biologics", "ticker": "207940", "change": "+1.8%"},
                {"name": "Lotte Biologics", "ticker": "N/A", "change": "(Private)"},
            ],
            "timestamp": "2024-02-27T05:30:00",
        },
        {
            "us_source": "TechCrunch",
            "us_headline": "OpenAI Announces Sora: Text-to-Video Model",
            "kr_impact": "High demand for AI data centers & high-speed interface chips",
            "related_stocks": [
                {"name": "OpenEdge Tech", "ticker": "394280", "change": "+8.9%"},
                {"name": "DeepX", "ticker": "N/A", "change": "(Private)"},
            ],
            "timestamp": "2024-02-27T04:15:00",
        },
    ]
    return {"news": news_items}
