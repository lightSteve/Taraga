from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Watchlist, User, StockKR
from pydantic import BaseModel
from typing import List

router = APIRouter()


class WatchlistAddRequest(BaseModel):
    user_uuid: str
    ticker: str
    stock_name: str


class WatchlistItemResponse(BaseModel):
    id: int
    ticker: str
    stock_name: str
    alert_enabled: bool


@router.get("/{user_uuid}", response_model=List[WatchlistItemResponse])
def get_watchlist(user_uuid: str, db: Session = Depends(get_db)):
    """
    Get user's watchlist.
    """
    user = db.query(User).filter(User.user_uuid == user_uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    watchlist_items = db.query(Watchlist).filter(Watchlist.user_id == user.id).all()

    results = []
    for item in watchlist_items:
        # Fetch stock name from relation or fallback
        stock = db.query(StockKR).filter(StockKR.ticker == item.stock_kr_ticker).first()
        stock_name = stock.name if stock else "Unknown"

        results.append(
            WatchlistItemResponse(
                id=item.id,
                ticker=item.stock_kr_ticker,
                stock_name=stock_name,
                alert_enabled=item.alert_enabled,
            )
        )

    return results


@router.post("/", response_model=WatchlistItemResponse)
def add_to_watchlist(req: WatchlistAddRequest, db: Session = Depends(get_db)):
    """
    Add a stock to the user's watchlist.
    Auto-creates the stock in StockKR if it doesn't exist.
    """
    # 1. Get User
    user = db.query(User).filter(User.user_uuid == req.user_uuid).first()
    if not user:
        # Create user for MVP if doesn't exist (simplifies testing)
        user = User(user_uuid=req.user_uuid)
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. Check/Create StockKR
    stock = db.query(StockKR).filter(StockKR.ticker == req.ticker).first()
    if not stock:
        # Auto-create stock
        stock = StockKR(ticker=req.ticker, name=req.stock_name, sector="Unknown")
        db.add(stock)
        db.commit()

    # 3. Check if already in watchlist
    existing = (
        db.query(Watchlist)
        .filter(Watchlist.user_id == user.id, Watchlist.stock_kr_ticker == req.ticker)
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Stock already in watchlist")

    # 4. Add to Watchlist
    new_item = Watchlist(
        user_id=user.id, stock_kr_ticker=req.ticker, alert_enabled=True
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return WatchlistItemResponse(
        id=new_item.id,
        ticker=new_item.stock_kr_ticker,
        stock_name=stock.name,
        alert_enabled=new_item.alert_enabled,
    )


@router.delete("/{item_id}")
def delete_from_watchlist(item_id: int, db: Session = Depends(get_db)):
    """
    Remove an item from the watchlist.
    """
    item = db.query(Watchlist).filter(Watchlist.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")

    db.delete(item)
    db.commit()

    return {"status": "deleted"}
