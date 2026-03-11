"""
Briefing Router — Auto-generates daily briefing from live market data.
If no briefing exists for today, creates one dynamically using:
  1. Market indices from Yahoo Finance (cached)
  2. Fear & Greed index from CNN (cached)
  3. Template-based summary generation
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
import requests
import logging

from database import get_db
from models import DailyBriefing
from services.cache_service import (
    CacheService,
    TTL_FEAR_GREED,
    TTL_MARKET_INDICES,
)

logger = logging.getLogger(__name__)
router = APIRouter()


def _fetch_fear_greed() -> dict:
    """Fetch CNN Fear & Greed Index (free, no API key needed)."""
    try:
        resp = requests.get(
            "https://production.dataviz.cnn.io/index/fearandgreed/graphdata",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            fg = data.get("fear_and_greed", {})
            score = int(fg.get("score", 50))
            rating = fg.get("rating", "Neutral")
            return {"score": score, "rating": rating}
    except Exception as e:
        logger.warning(f"Fear & Greed fetch failed: {e}")

    return {"score": 50, "rating": "Neutral"}


def _sentiment_label(score: int) -> str:
    """Convert Fear & Greed score to Korean sentiment label."""
    if score >= 75:
        return "극도의 탐욕"
    elif score >= 55:
        return "탐욕"
    elif score >= 45:
        return "중립"
    elif score >= 25:
        return "공포"
    else:
        return "극도의 공포"


def _generate_summary(indices: dict, fg_score: int, sentiment: str) -> str:
    """Generate a Korean market summary from data."""
    parts = []

    # Overall market direction
    sp_change = 0.0
    if "S&P 500" in indices:
        sp_change = indices["S&P 500"].get("change_percent", 0)

    if sp_change >= 1.0:
        parts.append(
            f"미국 시장이 강한 상승세를 보였습니다. S&P 500이 {sp_change:+.2f}% 올랐습니다."
        )
    elif sp_change >= 0:
        parts.append(
            f"미국 시장이 소폭 상승했습니다. S&P 500이 {sp_change:+.2f}% 변동했습니다."
        )
    elif sp_change >= -1.0:
        parts.append(
            f"미국 시장이 소폭 하락했습니다. S&P 500이 {sp_change:+.2f}% 내렸습니다."
        )
    else:
        parts.append(
            f"미국 시장이 큰 폭으로 하락했습니다. S&P 500이 {sp_change:+.2f}% 급락했습니다."
        )

    # Index details
    for name, data in indices.items():
        if name != "S&P 500":
            cp = data.get("change_percent", 0)
            parts.append(f"{name}: {cp:+.2f}%")

    # Sentiment
    parts.append(f"시장 심리: {sentiment} (공포탐욕지수 {fg_score})")

    return " ".join(parts)


def _create_briefing_for_today(db: Session) -> DailyBriefing:
    """Auto-generate today's briefing from live market data."""
    cache = CacheService(db)

    # 1. Get market indices (cached)
    from services.service_factory import ServiceFactory

    market_service = ServiceFactory.get_market_data_service(db)

    indices = cache.get_or_fetch(
        "US_INDICES",
        lambda: market_service.get_market_indices(),
        ttl_minutes=TTL_MARKET_INDICES,
    )
    if not indices:
        indices = {}

    # 2. Get Fear & Greed (cached)
    fg_data = cache.get_or_fetch(
        "FEAR_GREED",
        _fetch_fear_greed,
        ttl_minutes=TTL_FEAR_GREED,
    )
    fg_score = fg_data.get("score", 50) if fg_data else 50
    # fg_rating available in fg_data["rating"] if needed

    # 3. Determine sentiment
    sentiment = _sentiment_label(fg_score)

    # 4. Generate summary
    summary = _generate_summary(indices, fg_score, sentiment)

    # 5. Build key_indices_json for frontend
    key_indices = {}
    for name, data in indices.items():
        key_indices[name] = {
            "value": data.get("value", 0),
            "change_percent": data.get("change_percent", 0),
        }

    # 6. Save to DB
    today = date.today()
    briefing = db.query(DailyBriefing).filter_by(date=today).first()

    if briefing:
        briefing.us_summary = summary
        briefing.market_sentiment = sentiment
        briefing.key_indices_json = key_indices
        briefing.fear_greed_score = fg_score
    else:
        briefing = DailyBriefing(
            date=today,
            us_summary=summary,
            market_sentiment=sentiment,
            key_indices_json=key_indices,
            fear_greed_score=fg_score,
            content=summary,
        )
        db.add(briefing)

    db.commit()
    db.refresh(briefing)
    return briefing


@router.get("/today")
def get_today_briefing(db: Session = Depends(get_db)):
    """
    Get today's US market briefing.
    Auto-generates one if it doesn't exist yet.

    Returns:
        - us_summary: Market summary in Korean
        - market_sentiment: Fear/Greed label
        - key_indices: Performance of major indices
        - fear_greed_score: 0-100 score
    """
    today = date.today()
    briefing = db.query(DailyBriefing).filter_by(date=today).first()

    # Auto-generate if missing or stale (no us_summary)
    if not briefing or not briefing.us_summary:
        try:
            briefing = _create_briefing_for_today(db)
        except Exception as e:
            logger.error(f"Failed to auto-generate briefing: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"브리핑 생성 실패: {str(e)}",
            )

    return {
        "date": str(briefing.date),
        "us_summary": briefing.us_summary or "",
        "market_sentiment": briefing.market_sentiment or "중립",
        "key_indices": briefing.key_indices_json or {},
        "fear_greed_score": briefing.fear_greed_score or 50,
    }


@router.get("/{briefing_date}")
def get_briefing_by_date(briefing_date: date, db: Session = Depends(get_db)):
    """Get briefing for a specific date"""
    briefing = db.query(DailyBriefing).filter_by(date=briefing_date).first()

    if not briefing:
        raise HTTPException(
            status_code=404, detail=f"{briefing_date} 브리핑이 없습니다."
        )

    return {
        "date": str(briefing.date),
        "us_summary": briefing.us_summary or briefing.content or "",
        "market_sentiment": briefing.market_sentiment or "중립",
        "key_indices": briefing.key_indices_json or {},
        "fear_greed_score": briefing.fear_greed_score or 50,
    }
