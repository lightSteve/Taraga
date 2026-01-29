"""
Seed script to populate initial Korean market themes
Run this once to initialize the themes table
"""

from database import SessionLocal, init_db
from models import Theme
import json


def seed_themes():
    """Insert initial Korean market themes"""

    themes_data = [
        {
            "name": "AI 반도체",
            "keywords": json.dumps(
                [
                    "AI",
                    "artificial intelligence",
                    "chip",
                    "semiconductor",
                    "GPU",
                    "NVIDIA",
                ]
            ),
        },
        {
            "name": "2차전지",
            "keywords": json.dumps(
                ["battery", "EV", "electric vehicle", "lithium", "cathode", "Tesla"]
            ),
        },
        {
            "name": "바이오/제약",
            "keywords": json.dumps(
                [
                    "biotech",
                    "pharmaceutical",
                    "drug",
                    "vaccine",
                    "healthcare",
                    "medicine",
                ]
            ),
        },
        {
            "name": "엔터테인먼트",
            "keywords": json.dumps(
                ["entertainment", "K-pop", "content", "streaming", "media", "Netflix"]
            ),
        },
        {
            "name": "방산",
            "keywords": json.dumps(
                [
                    "defense",
                    "military",
                    "aerospace",
                    "weapons",
                    "Lockheed Martin",
                    "Boeing",
                ]
            ),
        },
        {
            "name": "화장품",
            "keywords": json.dumps(
                ["cosmetics", "beauty", "skincare", "K-beauty", "Estee Lauder"]
            ),
        },
        {
            "name": "자동차",
            "keywords": json.dumps(
                ["automotive", "car", "vehicle", "Ford", "GM", "Hyundai"]
            ),
        },
        {
            "name": "조선/해운",
            "keywords": json.dumps(
                ["shipbuilding", "shipping", "maritime", "container", "logistics"]
            ),
        },
        {
            "name": "게임",
            "keywords": json.dumps(
                [
                    "gaming",
                    "game",
                    "esports",
                    "mobile game",
                    "console",
                    "Unity",
                    "Roblox",
                ]
            ),
        },
        {
            "name": "반도체 장비",
            "keywords": json.dumps(
                [
                    "semiconductor equipment",
                    "ASML",
                    "Applied Materials",
                    "fab equipment",
                ]
            ),
        },
    ]

    # Initialize database
    init_db()

    # Create session
    db = SessionLocal()

    try:
        # Check if themes already exist
        existing_count = db.query(Theme).count()
        if existing_count > 0:
            print(f"⚠️  Database already has {existing_count} themes. Skipping seed.")
            return

        # Insert themes
        for theme_data in themes_data:
            theme = Theme(**theme_data)
            db.add(theme)

        db.commit()
        print(f"✅ Successfully seeded {len(themes_data)} themes!")

        # Display inserted themes
        themes = db.query(Theme).all()
        print("\n📋 Inserted Themes:")
        for theme in themes:
            print(f"  {theme.id}. {theme.name}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding themes: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_themes()
