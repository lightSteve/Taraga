from sqlalchemy.orm import Session
from database import SessionLocal
from models import ValueChain, Theme, StockUS


def seed_value_chain():
    db = SessionLocal()

    print("Seeding Value Chain Data...")

    # 1. Ensure Themes exist
    themes = [
        {"name": "AI 반도체", "keywords": '["AI", "Semiconductor", "Nvidia", "HBM"]'},
        {"name": "2차전지", "keywords": '["EV", "Battery", "Tesla", "Lithium"]'},
        {"name": "방산/우주", "keywords": '["Defense", "Space", "War", "Lockheed"]'},
        {"name": "자동차", "keywords": '["Auto", "EV", "Hybrid", "GM"]'},
    ]

    theme_map = {}
    for t_data in themes:
        theme = db.query(Theme).filter(Theme.name == t_data["name"]).first()
        if not theme:
            theme = Theme(name=t_data["name"], keywords=t_data["keywords"])
            db.add(theme)
            db.commit()
            db.refresh(theme)
        theme_map[t_data["name"]] = theme.id

    # 2. Ensure US Stocks exist
    us_stocks = [
        {"ticker": "NVDA", "name": "Nvidia", "theme_id": theme_map["AI 반도체"]},
        {"ticker": "TSLA", "name": "Tesla", "theme_id": theme_map["2차전지"]},
        {
            "ticker": "LMT",
            "name": "Lockheed Martin",
            "theme_id": theme_map["방산/우주"],
        },
        {"ticker": "GM", "name": "General Motors", "theme_id": theme_map["자동차"]},
    ]

    for us in us_stocks:
        stock = db.query(StockUS).filter(StockUS.ticker == us["ticker"]).first()
        if not stock:
            db.add(
                StockUS(ticker=us["ticker"], name=us["name"], theme_id=us["theme_id"])
            )
    db.commit()

    # 3. Create ValueChain connections (US Driver -> KR Stock)
    connections = [
        # AI Semiconductor (NVDA)
        {
            "theme_id": theme_map["AI 반도체"],
            "parent": "NVDA",
            "child": "000660",  # SK Hynix
            "relation": "Supplier (HBM3)",
            "desc": "Supplies HBM3 chips exclusively to Nvidia",
        },
        {
            "theme_id": theme_map["AI 반도체"],
            "parent": "NVDA",
            "child": "005930",  # Samsung Electronics
            "relation": "Supplier (HBM3E)",
            "desc": "Testing HBM3E for next-gen Nvidia GPUs",
        },
        {
            "theme_id": theme_map["AI 반도체"],
            "parent": "NVDA",
            "child": "042700",  # Hanmi Semiconductor (Need to ensure this exists in stocks_kr if seeded)
            "relation": "Equipment",
            "desc": "Core bonder equipment for HBM production",
        },
        # EV Battery (TSLA)
        {
            "theme_id": theme_map["2차전지"],
            "parent": "TSLA",
            "child": "373220",  # LG Energy Solution
            "relation": "Supplier",
            "desc": "Main cylindrical battery supplier for Tesla",
        },
        {
            "theme_id": theme_map["2차전지"],
            "parent": "TSLA",
            "child": "006400",  # Samsung SDI
            "relation": "Competitor/Supplier",
            "desc": "Expanding 4680 battery production targets",
        },
        # Defense (LMT)
        {
            "theme_id": theme_map["방산/우주"],
            "parent": "LMT",
            "child": "012450",  # Hanwha Aerospace
            "relation": "Partner",
            "desc": "Joint development of missile systems",
        },
        # Auto (GM)
        {
            "theme_id": theme_map["자동차"],
            "parent": "GM",
            "child": "005380",  # Hyundai Motor
            "relation": "Competitor/Partner",
            "desc": "Joint EV battery plant ventures in US",
        },
        {
            "theme_id": theme_map["자동차"],
            "parent": "GM",
            "child": "012330",  # Hyundai Mobis
            "relation": "Supplier",
            "desc": "Supplies chassis modules to GM",
        },
    ]

    count = 0
    for conn in connections:
        existing = (
            db.query(ValueChain)
            .filter(
                ValueChain.parent_stock_us == conn["parent"],
                ValueChain.child_stock_kr == conn["child"],
            )
            .first()
        )

        if not existing:
            vc = ValueChain(
                theme_id=conn["theme_id"],
                parent_stock_us=conn["parent"],
                child_stock_kr=conn["child"],
                relation_type=conn["relation"],
                description=conn["desc"],
            )
            db.add(vc)
            count += 1

    db.commit()
    db.close()
    print(f"🎉 Value Chain Seeded! Added {count} connections.")


if __name__ == "__main__":
    seed_value_chain()
