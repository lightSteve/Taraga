from sqlalchemy.orm import Session
from models import Theme, ValueChain, Watchlist


class CorrelationEngine:
    def __init__(self, db: Session):
        self.db = db

    def analyze_market_impact(self, driving_themes: list[dict], user_id: int = None):
        """
        Takes US market themes and maps them to KR stocks.
        If user_id is provided, filters for stocks in User's Watchlist.

        :param driving_themes: List of dicts e.g. [{"theme_name": "AI Semiconductor", "us_driver": "NVDA", "reason": "Earnings Beat"}]
        :param user_id: Optional User ID for personalization
        :return: Dict with 'general_recommendations' and 'personal_matches'
        """
        results = {"general_recommendations": [], "personal_matches": []}

        user_watchlist_tickers = set()
        if user_id:
            watchlist_items = (
                self.db.query(Watchlist).filter(Watchlist.user_id == user_id).all()
            )
            user_watchlist_tickers = {item.stock_kr_ticker for item in watchlist_items}

        for item in driving_themes:
            theme_name = item["theme_name"]
            us_driver_ticker = item["us_driver"]
            reason = item["reason"]

            # 1. Find the Theme
            theme = self.db.query(Theme).filter(Theme.name == theme_name).first()
            if not theme:
                continue

            # 2. Find Value Chain connections
            # Query Logic: Find connections where parent is the US driver OR theme matches
            # Ideally we want specific US Stock -> KR Stock links
            connections = (
                self.db.query(ValueChain)
                .filter(
                    ValueChain.theme_id == theme.id,
                    ValueChain.parent_stock_us == us_driver_ticker,
                )
                .all()
            )

            for conn in connections:
                rec_data = {
                    "theme": theme.name,
                    "us_driver": us_driver_ticker,
                    "kr_stock": conn.child_stock_kr,
                    "relation": conn.relation_type,
                    "description": conn.description,
                    "reason": reason,
                }

                results["general_recommendations"].append(rec_data)

                # 3. Check Personalization
                if conn.child_stock_kr in user_watchlist_tickers:
                    # Grouping Logic
                    theme_key = theme.name

                    # Check if group already exists
                    existing_group = next(
                        (
                            g
                            for g in results["personal_matches"]
                            if g["theme_name"] == theme_key
                        ),
                        None,
                    )

                    if not existing_group:
                        existing_group = {
                            "theme_name": theme.name,
                            "us_change_percent": 2.5
                            if "AI" in theme.name
                            else -1.2,  # Mock logic for now
                            "reason": reason,
                            "my_stocks": [],
                        }
                        results["personal_matches"].append(existing_group)

                    # Add stock to group
                    if conn.kr_stock:
                        stock_name = conn.kr_stock.name
                    else:
                        stock_name = conn.child_stock_kr  # Fallback to ticker

                    existing_group["my_stocks"].append(
                        {
                            "ticker": conn.child_stock_kr,
                            "name": stock_name,
                            "relation": conn.relation_type,
                            "expected_flow": "UP",  # Mock logic
                        }
                    )

        return results

    def get_value_chain_tree(self, theme_id: int):
        """Returns hierarchical view for a theme"""
        theme = self.db.query(Theme).filter(Theme.id == theme_id).first()
        if not theme:
            return None

        chains = self.db.query(ValueChain).filter(ValueChain.theme_id == theme_id).all()

        tree = {"theme": theme.name, "us_drivers": {}}

        for chain in chains:
            if chain.parent_stock_us not in tree["us_drivers"]:
                tree["us_drivers"][chain.parent_stock_us] = []

            tree["us_drivers"][chain.parent_stock_us].append(
                {
                    "kr_stock": chain.child_stock_kr,
                    "relation": chain.relation_type,
                    "description": chain.description,
                }
            )

        return tree

    def get_us_impact_for_kr_symbol(self, kr_symbol: str) -> dict:
        """Simple rule-based impact estimation for a given Korean symbol using US top gainers and theme keywords."""
        try:
            top_gainers = self.market_service.get_top_gainers(limit=50)
        except Exception:
            top_gainers = []

        db = SessionLocal()
        themes = db.query(Theme).all()
        db.close()

        theme_map = []
        for theme in themes:
            keywords = json.loads(theme.keywords) if theme.keywords else []
            theme_map.append({"name": theme.name, "keywords": keywords})

        matched = []
        for g in top_gainers:
            g_name = g.get("ticker") or g.get("symbol") or g.get("name", "")
            g_name_lower = g_name.lower()
            for t in theme_map:
                for kw in t["keywords"]:
                    if kw.lower() in g_name_lower:
                        matched.append({"us_gainer": g_name, "theme": t["name"]})

        summary = "No clear US-driven impact detected for this symbol."
        if matched:
            summary = f"Detected {len(matched)} potential US->KR links."

        return {"symbol": kr_symbol, "summary": summary, "matches": matched}


if __name__ == "__main__":
    engine = CorrelationEngine()
    result = engine.run_daily_analysis()
    print("\n📋 Analysis Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
