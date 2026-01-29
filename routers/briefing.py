from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from database import get_db
from models import DailyBriefing

router = APIRouter()


@router.get("/today")
def get_today_briefing(db: Session = Depends(get_db)):
    """
    Get today's US market briefing

    Returns:
        - us_summary: AI-generated summary of US market
        - market_sentiment: Fear/Greed/Neutral
        - key_indices_json: Performance of major indices
    """
    today = date.today()

    briefing = db.query(DailyBriefing).filter_by(date=today).first()

    if not briefing:
        raise HTTPException(
            status_code=404,
            detail=f"No briefing found for {today}. Run daily analysis first.",
        )

    return {
        "date": briefing.date,
        "us_summary": briefing.us_summary,
        "market_sentiment": briefing.market_sentiment,
        "key_indices": briefing.key_indices_json,
    }


@router.get("/{briefing_date}")
def get_briefing_by_date(briefing_date: date, db: Session = Depends(get_db)):
    """Get briefing for a specific date"""

    briefing = db.query(DailyBriefing).filter_by(date=briefing_date).first()

    if not briefing:
        raise HTTPException(
            status_code=404, detail=f"No briefing found for {briefing_date}"
        )

    return {
        "date": briefing.date,
        "us_summary": briefing.us_summary,
        "market_sentiment": briefing.market_sentiment,
        "key_indices": briefing.key_indices_json,
    }
