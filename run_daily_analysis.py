"""
Standalone script to test the complete analysis pipeline
Run this to verify the entire system works end-to-end
"""

from logic.correlation_engine import CorrelationEngine
from datetime import date
import json


def main():
    """Run daily analysis and display results"""

    print("=" * 60)
    print("🌉 TARAGA - Wall Street to Yeouido Bridge")
    print("=" * 60)
    print()

    # Create engine
    engine = CorrelationEngine()

    # Run analysis
    try:
        result = engine.run_daily_analysis()

        print("\n" + "=" * 60)
        print("📊 ANALYSIS RESULTS")
        print("=" * 60)
        print()

        print(f"📝 US Market Summary:")
        print(f"   {result.get('us_summary', 'N/A')}")
        print()

        print(f"😱 Market Sentiment: {result.get('market_sentiment', 'N/A')}")
        print()

        print(f"🎯 Recommended Korean Themes:")
        for i, theme in enumerate(result.get("recommended_themes", []), 1):
            print(
                f"\n   {i}. {theme.get('theme_name')} (Score: {theme.get('impact_score')}/10)"
            )
            print(f"      Reason: {theme.get('reason')}")
            if theme.get("related_us_stocks"):
                print(f"      Related US: {', '.join(theme.get('related_us_stocks'))}")

        print("\n" + "=" * 60)
        print("✅ Analysis completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
