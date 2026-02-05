from fastapi.testclient import TestClient
from main import app
from database import SessionLocal
from models import User

client = TestClient(app)


def verify_api():
    """Test the Insight API endpoints"""
    print("🚀 Starting API Verification...")

    # 1. Get Demo User UUID
    db = SessionLocal()
    user = db.query(User).filter(User.user_uuid == "demo-user-123").first()
    db.close()

    if not user:
        print("❌ Error: Demo user not found. Did you run seed_themes.py?")
        return

    # 2. Test Personal Matches Endpoint
    print(
        f"\n📡 Testing GET /api/v1/insight/personal-matches?user_uuid={user.user_uuid}"
    )
    response = client.get(
        f"/api/v1/insight/personal-matches?user_uuid={user.user_uuid}"
    )

    if response.status_code == 200:
        data = response.json()
        print("✅ Response 200 OK")
        print(f"   Found {len(data['personal_matches'])} personal matches")
        assert len(data["personal_matches"]) > 0, "Should have matches for demo user"
        assert data["personal_matches"][0]["kr_stock"] == "000660", (
            "First match should be SK Hynix"
        )
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")

    # 3. Test Value Chain Endpoint
    # Assuming 'AI Semiconductor' is ID 1
    print("\n📡 Testing GET /api/v1/insight/value-chain?theme_id=1")
    response_vc = client.get("/api/v1/insight/value-chain?theme_id=1")

    if response_vc.status_code == 200:
        data_vc = response_vc.json()
        print("✅ Response 200 OK")
        print(f"   Theme: {data_vc.get('theme')}")
        assert "us_drivers" in data_vc
        assert "NVDA" in data_vc["us_drivers"]
    else:
        print(f"❌ Failed: {response_vc.status_code} - {response_vc.text}")


if __name__ == "__main__":
    verify_api()
