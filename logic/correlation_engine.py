"""
Correlation Engine: The Bridge between US and Korean Markets
This module orchestrates the entire analysis pipeline
"""

from datetime import datetime, date
from sqlalchemy.orm import Session
import json

from database import SessionLocal
from models import Theme, DailyBriefing, RecommendedTheme
from services.service_factory import ServiceFactory


class CorrelationEngine:
    """Main logic engine that connects US market events to Korean stock themes"""

    def __init__(self):
        # Use service factory to get appropriate services (free or premium)
        self.market_service = ServiceFactory.get_market_data_service()
        self.news_service = ServiceFactory.get_news_service()
        self.ai_service = ServiceFactory.get_ai_service()

    def run_daily_analysis(self, analysis_date: date = None):
        """
        Run the complete daily analysis pipeline

        Steps:
        1. Fetch US market data (indices, top gainers)
        2. Fetch US news headlines
        3. Get Korean themes from database
        4. Send to AI for analysis
        5. Save results to database
        """

        if analysis_date is None:
            analysis_date = date.today()

        print(f"🚀 Starting analysis for {analysis_date}")

        # Step 1: Fetch US market data
        print("📊 Fetching US market data...")
        market_indices = self.market_service.get_market_indices()
        top_gainers = self.market_service.get_top_gainers(limit=10)

        # Step 2: Fetch news
        print("📰 Fetching US news...")
        news_articles = self.news_service.get_market_news(limit=10)

        # Step 3: Get Korean themes
        print("🏷️  Loading Korean themes...")
        db = SessionLocal()
        themes = db.query(Theme).all()

        themes_data = [
            {
                "id": theme.id,
                "name": theme.name,
                "keywords": json.loads(theme.keywords) if theme.keywords else [],
            }
            for theme in themes
        ]

        # Step 4: AI Analysis (template-based or OpenAI)
        print("🤖 Running correlation analysis...")
        recommendations = self.ai_service.analyze_market_correlation(
            us_gainers=top_gainers, news_articles=news_articles, themes=themes_data
        )

        # Generate summary
        us_summary = self.ai_service.generate_daily_summary(
            us_indices=market_indices, top_gainers=top_gainers, news=news_articles
        )

        # Determine sentiment based on indices
        market_sentiment = self._determine_sentiment(market_indices)

        analysis_result = {
            "us_summary": us_summary,
            "market_sentiment": market_sentiment,
            "recommended_themes": recommendations,
        }

        # Step 5: Save to database
        print("💾 Saving results to database...")
        self._save_results(db, analysis_date, analysis_result, market_indices)

        db.close()

        print("✅ Analysis complete!")
        return analysis_result

    def _determine_sentiment(self, indices: dict) -> str:
        """Determine market sentiment from indices performance"""
        if not indices:
            return "Neutral"

        # Calculate average change
        changes = [data.get("change_percent", 0) for data in indices.values()]
        avg_change = sum(changes) / len(changes) if changes else 0

        if avg_change > 1.0:
            return "Greedy"
        elif avg_change < -1.0:
            return "Fearful"
        else:
            return "Neutral"

    def _save_results(
        self, db: Session, analysis_date: date, analysis: dict, market_data: dict
    ):
        """Save analysis results to database"""

        # Save daily briefing
        briefing = DailyBriefing(
            date=analysis_date,
            us_summary=analysis.get("us_summary", ""),
            market_sentiment=analysis.get("market_sentiment", "Neutral"),
            key_indices_json=market_data.get("indices", {}),
        )

        # Check if briefing already exists
        existing_briefing = (
            db.query(DailyBriefing).filter_by(date=analysis_date).first()
        )
        if existing_briefing:
            db.delete(existing_briefing)

        db.add(briefing)
        db.commit()

        # Save recommended themes
        recommended = analysis.get("recommended_themes", [])

        # Delete existing recommendations for this date
        db.query(RecommendedTheme).filter_by(date=analysis_date).delete()

        for rec in recommended:
            # Find theme by name
            theme = db.query(Theme).filter_by(name=rec["theme_name"]).first()
            if not theme:
                print(f"⚠️  Theme '{rec['theme_name']}' not found, skipping...")
                continue

            # Get first related US stock if available
            related_stocks = rec.get("related_us_stocks", [])
            related_us_stock = related_stocks[0] if related_stocks else None

            recommendation = RecommendedTheme(
                date=analysis_date,
                theme_id=theme.id,
                reason=rec.get("reason", ""),
                related_us_stock=related_us_stock,
                impact_score=rec.get("impact_score", 5),
            )

            db.add(recommendation)

        db.commit()
        print(f"💾 Saved {len(recommended)} theme recommendations")


    def get_us_impact_for_kr_symbol(self, kr_symbol: str) -> dict:
        """Simple rule-based impact estimation for a given Korean symbol using US top gainers and theme keywords.

        Returns a dict with summary and matched themes or an empty result if nothing matched.
        """
        try:
            top_gainers = self.market_service.get_top_gainers(limit=50)
        except Exception:
            top_gainers = []

        # Load themes from DB
        db = SessionLocal()
        themes = db.query(Theme).all()
        db.close()

        # Build a simple keyword->theme map
        theme_map = []
        for theme in themes:
            keywords = json.loads(theme.keywords) if theme.keywords else []
            theme_map.append({"name": theme.name, "keywords": keywords})

        # Check top gainers for keyword matches
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
    # Test the correlation engine
    engine = CorrelationEngine()
    result = engine.run_daily_analysis()
    print("\n📋 Analysis Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
