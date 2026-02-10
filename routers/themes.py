from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import date
from database import get_db
from models import RecommendedTheme, Theme
import json
import logging

logger = logging.getLogger(__name__)

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
    try:
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
            logger.warning(f"No theme recommendations found for {today}")
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
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while fetching recommendations",
        )
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in theme keywords: {e}")
        raise HTTPException(
            status_code=500,
            detail="Data format error in theme information",
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching recommendations: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred",
        )


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
    try:
        themes = db.query(Theme).all()

        return [
            {
                "id": theme.id,
                "name": theme.name,
                "keywords": json.loads(theme.keywords) if theme.keywords else [],
            }
            for theme in themes
        ]
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching themes: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while fetching themes",
        )
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in theme keywords: {e}")
        raise HTTPException(
            status_code=500,
            detail="Data format error in theme information",
        )
    except Exception as e:
        logger.error(f"Unexpected error while fetching themes: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred",
        )
