from database import SessionLocal
from models import User
from logic.correlation_engine import CorrelationEngine
import json


def verify_logic():
    db = SessionLocal()
    try:
        # 1. Get Demo User
        user = db.query(User).filter(User.user_uuid == "demo-user-123").first()
        print(f"👤 Found User: ID={user.id}, UUID={user.user_uuid}")

        # 2. Mock US Market Data (The Cause)
        mock_drivers = [
            {
                "theme_name": "AI 반도체",
                "us_driver": "NVDA",
                "reason": "Verify Script Test: Nvidia Earnings Beat",
            }
        ]

        # 3. Run Engine
        engine = CorrelationEngine(db)
        results = engine.analyze_market_impact(mock_drivers, user_id=user.id)

        # 4. Assertions
        print("\n🔍 Analysis Results:")
        print(json.dumps(results, indent=2, ensure_ascii=False))

        # Check General Recommendations
        assert len(results["general_recommendations"]) >= 2, (
            "Should find at least 2 connections (Hynix, Samsung)"
        )

        # Check Personal Matches (Should be SK Hynix)
        personal = results["personal_matches"]
        assert len(personal) == 1, "Should have exactly 1 personal match"
        assert personal[0]["kr_stock"] == "000660", (
            "Personal match should be SK Hynix (000660)"
        )

        print("\n✅ Verification PASSED: Logic & Personalization working correctly.")

    except Exception as e:
        print(f"\n❌ Verification FAILED: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    verify_logic()
