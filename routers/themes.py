from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from database import get_db
from models import RecommendedTheme, Theme
import json

router = APIRouter()


@router.get("/recommendations")
def get_theme_recommendations(db: Session = Depends(get_db)):
    """
    Get today's recommended Korean themes based on US market analysis

    Returns list of recommended themes with:
        - theme_id, theme_name
        - reason for recommendation
        - related_us_stock (the cause)
        - impact_score (1-10)
    """
    today = date.today()

    # Query recommendations with theme details
    recommendations = (
        db.query(RecommendedTheme, Theme)
        .join(Theme, RecommendedTheme.theme_id == Theme.id)
        .filter(RecommendedTheme.date == today)
        .order_by(RecommendedTheme.impact_score.desc())
        .all()
    )

    if not recommendations:
        raise HTTPException(
            status_code=404,
            detail=f"No theme recommendations found for {today}. Run daily analysis first.",
        )

    result = []
    for rec, theme in recommendations:
        result.append(
            {
                "theme_id": theme.id,
                "theme_name": theme.name,
                "keywords": json.loads(theme.keywords) if theme.keywords else [],
                "reason": rec.reason,
                "related_us_stock": rec.related_us_stock,
                "impact_score": rec.impact_score,
                "date": rec.date,
            }
        )

    return result


@router.get("/recommendations/{recommendation_date}")
def get_recommendations_by_date(
    recommendation_date: date, db: Session = Depends(get_db)
):
    """Get theme recommendations for a specific date"""

    recommendations = (
        db.query(RecommendedTheme, Theme)
        .join(Theme, RecommendedTheme.theme_id == Theme.id)
        .filter(RecommendedTheme.date == recommendation_date)
        .order_by(RecommendedTheme.impact_score.desc())
        .all()
    )

    if not recommendations:
        raise HTTPException(
            status_code=404,
            detail=f"No recommendations found for {recommendation_date}",
        )

    result = []
    for rec, theme in recommendations:
        result.append(
            {
                "theme_id": theme.id,
                "theme_name": theme.name,
                "keywords": json.loads(theme.keywords) if theme.keywords else [],
                "reason": rec.reason,
                "related_us_stock": rec.related_us_stock,
                "impact_score": rec.impact_score,
                "date": rec.date,
            }
        )

    return result


@router.get("/list")
def get_all_themes(db: Session = Depends(get_db)):
    """Get list of all available Korean market themes"""

    themes = db.query(Theme).all()

    return [
        {
            "id": theme.id,
            "name": theme.name,
            "keywords": json.loads(theme.keywords) if theme.keywords else [],
        }
        for theme in themes
    ]


@router.get("/{theme_id}/stocks")
def get_stocks_by_theme(theme_id: int, db: Session = Depends(get_db)):
    """Get Korean stocks for a specific theme"""
    from models import StockKR

    # Verify theme exists
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail=f"Theme {theme_id} not found")

    # Get stocks for this theme
    stocks = db.query(StockKR).filter(StockKR.theme_id == theme_id).all()

    # If no stocks found, return mock data for now
    if not stocks:
        # Return some mock Korean stocks based on theme
        mock_stocks = {
            1: [  # AI 반도체
                {
                    "ticker": "005930",
                    "name": "삼성전자",
                    "sector": "반도체",
                    "current_price": 72000,
                    "change_percent": 2.5,
                },
                {
                    "ticker": "000660",
                    "name": "SK하이닉스",
                    "sector": "반도체",
                    "current_price": 185000,
                    "change_percent": 3.2,
                },
            ],
            2: [  # 2차전지
                {
                    "ticker": "373220",
                    "name": "LG에너지솔루션",
                    "sector": "2차전지",
                    "current_price": 425000,
                    "change_percent": 1.8,
                },
                {
                    "ticker": "006400",
                    "name": "삼성SDI",
                    "sector": "2차전지",
                    "current_price": 380000,
                    "change_percent": -0.5,
                },
            ],
            3: [  # 바이오/제약
                {
                    "ticker": "207940",
                    "name": "삼성바이오로직스",
                    "sector": "바이오",
                    "current_price": 850000,
                    "change_percent": 1.2,
                },
                {
                    "ticker": "068270",
                    "name": "셀트리온",
                    "sector": "바이오",
                    "current_price": 180000,
                    "change_percent": 0.8,
                },
            ],
        }

        return mock_stocks.get(
            theme_id,
            [
                {
                    "ticker": "000000",
                    "name": f"{theme.name} 관련 종목",
                    "sector": theme.name,
                    "current_price": None,
                    "change_percent": None,
                }
            ],
        )

    return [
        {
            "ticker": stock.ticker,
            "name": stock.name,
            "sector": stock.sector,
            "current_price": None,  # TODO: Fetch from KIS API
            "change_percent": None,  # TODO: Fetch from KIS API
        }
        for stock in stocks
    ]
