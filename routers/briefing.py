from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import date
from database import get_db
from models import DailyBriefing
import logging

logger = logging.getLogger(__name__)

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
    try:
        today = date.today()
        briefing = db.query(DailyBriefing).filter_by(date=today).first()

        if not briefing:
            logger.warning(f"No briefing found for {today}")
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
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching briefing: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while fetching briefing data",
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching briefing: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred",
        )


@router.get("/{briefing_date}")
def get_briefing_by_date(briefing_date: date, db: Session = Depends(get_db)):
    """Get briefing for a specific date"""
    try:
        briefing = db.query(DailyBriefing).filter_by(date=briefing_date).first()

        if not briefing:
            logger.warning(f"No briefing found for {briefing_date}")
            raise HTTPException(
                status_code=404, detail=f"No briefing found for {briefing_date}"
            )

        return {
            "date": briefing.date,
            "us_summary": briefing.us_summary,
            "market_sentiment": briefing.market_sentiment,
            "key_indices": briefing.key_indices_json,
        }
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching briefing by date: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while fetching briefing data",
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching briefing by date: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred",
        )
