from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import StockKR


def seed_stocks():
    db = SessionLocal()

    # List of common stocks for demo
    stocks = [
        # Auto
        {"ticker": "005380", "name": "현대자동차", "sector": "자동차"},
        {"ticker": "000270", "name": "기아", "sector": "자동차"},
        {"ticker": "012330", "name": "현대모비스", "sector": "자동차부품"},
        # Tech
        {"ticker": "005930", "name": "삼성전자", "sector": "반도체"},
        {"ticker": "000660", "name": "SK하이닉스", "sector": "반도체"},
        {"ticker": "035420", "name": "NAVER", "sector": "인터넷"},
        {"ticker": "035720", "name": "카카오", "sector": "인터넷"},
        # Battery
        {"ticker": "373220", "name": "LG에너지솔루션", "sector": "2차전지"},
        {"ticker": "006400", "name": "삼성SDI", "sector": "2차전지"},
        {"ticker": "051910", "name": "LG화학", "sector": "화학"},
        # Bio
        {"ticker": "207940", "name": "삼성바이오로직스", "sector": "바이오"},
        {"ticker": "068270", "name": "셀트리온", "sector": "바이오"},
    ]

    print("Seeding stocks...")
    for item in stocks:
        existing = db.query(StockKR).filter(StockKR.ticker == item["ticker"]).first()
        if not existing:
            stock = StockKR(
                ticker=item["ticker"], name=item["name"], sector=item["sector"]
            )
            db.add(stock)
            print(f"Added {item['name']}")
        else:
            print(f"Skipped {item['name']} (Already exists)")

    db.commit()
    db.close()
    print("Done!")


if __name__ == "__main__":
    seed_stocks()
