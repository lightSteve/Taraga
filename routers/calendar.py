from fastapi import APIRouter, Query
from services.calendar_service import CalendarService
from datetime import datetime

router = APIRouter()
calendar_service = CalendarService()


@router.get("/events")
def get_calendar_events(year: int = Query(None), month: int = Query(None)):
    """
    Get economic and earnings events for a given month.
    Defaults to current year/month if not provided.
    """
    if not year or not month:
        now = datetime.now()
        year = now.year
        month = now.month

    try:
        events = calendar_service.get_monthly_events(year, month)
        return {"status": "success", "data": events}
    except Exception as e:
        return {"status": "error", "message": str(e)}
