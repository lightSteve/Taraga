"""
Seed script to populate initial Korean market themes, stocks, and value chains.
Run this once to initialize the database with data.
"""

from database import SessionLocal, init_db
from models import Theme, StockUS, StockKR, ValueChain, User, Watchlist
import json


def seed_data():
    """Insert initial data for Themes, Stocks, and Value Chains"""

    # Initialize database
    init_db()
    db = SessionLocal()

    try:
        # 1. Themes
        themes_data = [
            {
                "name": "AI 반도체",
                "keywords": json.dumps(["AI", "Semiconductor", "NVIDIA", "HBM"]),
            },
            {
                "name": "2차전지",
                "keywords": json.dumps(["EV", "Battery", "Tesla", "Lithium"]),
            },
        ]

        themes = {}
        for t_data in themes_data:
            theme = db.query(Theme).filter(Theme.name == t_data["name"]).first()
            if not theme:
                theme = Theme(**t_data)
                db.add(theme)
                db.commit()
                db.refresh(theme)
            themes[theme.name] = theme

        # 2. Stocks (US & KR)
        us_stocks = [
            {"ticker": "NVDA", "name": "NVIDIA", "sector": "Semiconductor"},
            {"ticker": "TSLA", "name": "Tesla", "sector": "Automotive"},
            {"ticker": "MU", "name": "Micron", "sector": "Semiconductor"},
        ]

        kr_stocks = [
            {
                "ticker": "000660",
                "name": "SK하이닉스",
                "sector": "Semiconductor",
            },  # Hynix
            {
                "ticker": "005930",
                "name": "삼성전자",
                "sector": "Semiconductor",
            },  # Samsung
            {"ticker": "006400", "name": "삼성SDI", "sector": "Battery"},
            {"ticker": "373220", "name": "LG에너지솔루션", "sector": "Battery"},
        ]

        for s in us_stocks:
            if not db.query(StockUS).filter(StockUS.ticker == s["ticker"]).first():
                db.add(StockUS(**s))

        for s in kr_stocks:
            if not db.query(StockKR).filter(StockKR.ticker == s["ticker"]).first():
                db.add(StockKR(**s))

        db.commit()

        # 3. Value Chains (The Bridge)
        # Map US Stock -> KR Stock
        vc_data = [
            # NVDA -> SK Hynix (HBM Supplier)
            {
                "theme_id": themes["AI 반도체"].id,
                "parent_stock_us": "NVDA",
                "child_stock_kr": "000660",
                "relation_type": "Supplier",
                "description": "Supplies HBM3E chips for H100 GPUs",
            },
            # NVDA -> Samsung (Potential Supplier)
            {
                "theme_id": themes["AI 반도체"].id,
                "parent_stock_us": "NVDA",
                "child_stock_kr": "005930",
                "relation_type": "Competitor/Supplier",
                "description": "Competes in Foundry, Supplies Memory",
            },
            # TSLA -> LG Energy Solution
            {
                "theme_id": themes["2차전지"].id,
                "parent_stock_us": "TSLA",
                "child_stock_kr": "373220",
                "relation_type": "Supplier",
                "description": "Supplies cylindrical batteries",
            },
        ]

        for vc in vc_data:
            existing = (
                db.query(ValueChain)
                .filter(
                    ValueChain.parent_stock_us == vc["parent_stock_us"],
                    ValueChain.child_stock_kr == vc["child_stock_kr"],
                )
                .first()
            )
            if not existing:
                db.add(ValueChain(**vc))

        db.commit()

        # 4. User & Watchlist (Demo)
        demo_user_uuid = "demo-user-123"
        user = db.query(User).filter(User.user_uuid == demo_user_uuid).first()
        if not user:
            user = User(user_uuid=demo_user_uuid)
            db.add(user)
            db.commit()
            db.refresh(user)

            # Add SK Hynix to watchlist
            wl = Watchlist(user_id=user.id, stock_kr_ticker="000660")
            db.add(wl)
            db.commit()

        # 4b. Test User (for App default)
        test_user_uuid = "test_user_uuid"
        user_test = db.query(User).filter(User.user_uuid == test_user_uuid).first()
        if not user_test:
            user_test = User(user_uuid=test_user_uuid)
            db.add(user_test)
            db.commit()
            db.refresh(user_test)

            # Add SK Hynix & Samsung to watchlist
            wl1 = Watchlist(user_id=user_test.id, stock_kr_ticker="000660")
            wl2 = Watchlist(user_id=user_test.id, stock_kr_ticker="005930")
            db.add(wl1)
            db.add(wl2)
            db.commit()

        print("✅ Seed data populated successfully!")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
