from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Watchlist, ValueChain, Theme
from logic.correlation_engine import CorrelationEngine


def debug_matches():
    db = SessionLocal()
    user_uuid = "test_user_uuid"

    print(f"🔍 Debugging for User: {user_uuid}")

    # 1. Check User & Watchlist
    user = db.query(User).filter(User.user_uuid == user_uuid).first()
    if not user:
        print("❌ User not found!")
        return

    watchlist = db.query(Watchlist).filter(Watchlist.user_id == user.id).all()
    print(f"📋 Watchlist ({len(watchlist)} items):")
    masked_watchlist = set()
    for item in watchlist:
        print(f"   - {item.stock_kr_ticker} (ID: {item.id})")
        masked_watchlist.add(item.stock_kr_ticker)

    # 2. Check Value Chain Data
    print("\n🔗 Value Chain Data:")
    vcs = db.query(ValueChain).all()
    for vc in vcs:
        print(f"   - {vc.parent_stock_us} -> {vc.child_stock_kr} ({vc.relation_type})")

    # 3. Simulate Logic
    print("\n🧠 Simulating Correlation Engine...")
    mock_drivers = [
        {"theme_name": "AI 반도체", "us_driver": "NVDA", "reason": "Earnings Beat"},
        {"theme_name": "2차전지", "us_driver": "TSLA", "reason": "Delivery Beat"},
        {"theme_name": "방산/우주", "us_driver": "LMT", "reason": "Contract Win"},
        {"theme_name": "자동차", "us_driver": "GM", "reason": "Partnership"},
    ]

    engine = CorrelationEngine(db)
    results = engine.analyze_market_impact(mock_drivers, user_id=user.id)

    print("\n🚀 Results:")
    print(f"   - Personal Matches: {len(results['personal_matches'])}")
    for match in results["personal_matches"]:
        print(f"     * MATCH: {match}")

    print(f"   - General Recs: {len(results['general_recommendations'])}")

    if len(results["personal_matches"]) == 0:
        print("\n⚠️  Why no match?")
        # Deep dive into intersections
        for driver in mock_drivers:
            print(f"   Checking Driver: {driver['us_driver']} ({driver['theme_name']})")
            theme = db.query(Theme).filter(Theme.name == driver["theme_name"]).first()
            if not theme:
                print(f"   ❌ Theme '{driver['theme_name']}' not found in DB")
                continue

            connections = (
                db.query(ValueChain)
                .filter(
                    ValueChain.theme_id == theme.id,
                    ValueChain.parent_stock_us == driver["us_driver"],
                )
                .all()
            )

            found_targets = [c.child_stock_kr for c in connections]
            print(f"   Found Targets in DB: {found_targets}")

            intersection = set(found_targets).intersection(masked_watchlist)
            print(f"   Intersection with Watchlist: {intersection}")

    db.close()


if __name__ == "__main__":
    debug_matches()
