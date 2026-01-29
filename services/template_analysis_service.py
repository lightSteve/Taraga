"""
Template Analysis Service - Free alternative to OpenAI GPT-4
Uses rule-based logic to map US stocks to Korean themes
"""

from typing import List, Dict
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class TemplateAnalysisService:
    """Rule-based market correlation analysis without AI costs"""

    # Mapping of US stocks/sectors to Korean themes
    CORRELATION_RULES = {
        # AI & Semiconductors
        "AI 반도체": {
            "us_stocks": ["NVDA", "AMD", "INTC", "AVGO", "QCOM", "TSM"],
            "keywords": ["ai", "chip", "semiconductor", "gpu", "nvidia", "processor"],
            "sectors": ["Technology"],
        },
        # Battery & EV
        "2차전지": {
            "us_stocks": ["TSLA", "RIVN", "LCID", "ALB", "LAC", "SQM"],
            "keywords": [
                "battery",
                "ev",
                "electric vehicle",
                "lithium",
                "tesla",
                "cathode",
            ],
            "sectors": ["Automotive", "Materials"],
        },
        # Biotech & Pharma
        "바이오/제약": {
            "us_stocks": ["PFE", "MRNA", "JNJ", "ABBV", "BMY", "LLY", "GILD"],
            "keywords": [
                "biotech",
                "pharma",
                "drug",
                "vaccine",
                "healthcare",
                "medicine",
            ],
            "sectors": ["Healthcare"],
        },
        # Entertainment
        "엔터테인먼트": {
            "us_stocks": ["NFLX", "DIS", "SPOT", "WBD", "PARA"],
            "keywords": [
                "entertainment",
                "streaming",
                "content",
                "media",
                "netflix",
                "disney",
            ],
            "sectors": ["Communication Services"],
        },
        # Defense
        "방산": {
            "us_stocks": ["LMT", "BA", "RTX", "NOC", "GD"],
            "keywords": [
                "defense",
                "military",
                "aerospace",
                "weapons",
                "lockheed",
                "boeing",
            ],
            "sectors": ["Industrials"],
        },
        # Cosmetics
        "화장품": {
            "us_stocks": ["EL", "ULTA", "CLX"],
            "keywords": ["cosmetics", "beauty", "skincare", "makeup"],
            "sectors": ["Consumer Staples"],
        },
        # Automotive
        "자동차": {
            "us_stocks": ["F", "GM", "TSLA", "RIVN"],
            "keywords": ["automotive", "car", "vehicle", "ford", "gm"],
            "sectors": ["Automotive"],
        },
        # Shipping
        "조선/해운": {
            "us_stocks": ["ZIM", "DAC", "MATX"],
            "keywords": ["shipping", "maritime", "container", "logistics"],
            "sectors": ["Industrials"],
        },
        # Gaming
        "게임": {
            "us_stocks": ["RBLX", "U", "EA", "TTWO", "ATVI"],
            "keywords": ["gaming", "game", "esports", "mobile game", "unity", "roblox"],
            "sectors": ["Communication Services"],
        },
        # Semiconductor Equipment
        "반도체 장비": {
            "us_stocks": ["ASML", "AMAT", "LRCX", "KLAC"],
            "keywords": ["semiconductor equipment", "asml", "applied materials", "fab"],
            "sectors": ["Technology"],
        },
    }

    def analyze_market_correlation(
        self, us_gainers: List[Dict], news_articles: List[Dict], themes: List[Dict]
    ) -> List[Dict]:
        """
        Analyze US market data and recommend Korean themes

        Args:
            us_gainers: List of top gaining US stocks
            news_articles: List of market news articles
            themes: List of available Korean themes

        Returns:
            List of recommended themes with reasoning
        """
        try:
            logger.info("Analyzing market correlations using template rules")

            recommendations = []
            theme_scores = {}

            # Score themes based on US stock performance
            for gainer in us_gainers:
                ticker = gainer["ticker"]
                change_pct = gainer.get("change_percent", 0)
                sector = gainer.get("sector", "")

                # Find matching themes
                for theme_name, rules in self.CORRELATION_RULES.items():
                    if ticker in rules["us_stocks"]:
                        score = theme_scores.get(theme_name, 0)
                        # Weight by performance
                        score += change_pct * 2  # Double weight for direct stock match
                        theme_scores[theme_name] = score

                    elif sector in rules["sectors"]:
                        score = theme_scores.get(theme_name, 0)
                        score += change_pct * 0.5  # Half weight for sector match
                        theme_scores[theme_name] = score

            # Score themes based on news keywords
            for article in news_articles:
                title = article.get("title", "").lower()
                description = article.get("description", "").lower()
                text = f"{title} {description}"

                for theme_name, rules in self.CORRELATION_RULES.items():
                    keyword_matches = sum(1 for kw in rules["keywords"] if kw in text)
                    if keyword_matches > 0:
                        score = theme_scores.get(theme_name, 0)
                        score += keyword_matches * 5  # 5 points per keyword match
                        theme_scores[theme_name] = score

            # Generate recommendations from scored themes
            sorted_themes = sorted(
                theme_scores.items(), key=lambda x: x[1], reverse=True
            )

            for theme_name, score in sorted_themes[:5]:  # Top 5 themes
                if score > 0:
                    # Find theme ID
                    theme_id = self._find_theme_id(theme_name, themes)
                    if theme_id:
                        # Generate reason
                        reason = self._generate_reason(
                            theme_name, us_gainers, news_articles
                        )

                        # Find related US stock
                        related_stock = self._find_related_stock(theme_name, us_gainers)

                        recommendations.append(
                            {
                                "theme_id": theme_id,
                                "theme_name": theme_name,
                                "reason": reason,
                                "related_us_stock": related_stock,
                                "impact_score": min(int(score), 100),  # Cap at 100
                                "date": datetime.now().date().isoformat(),
                            }
                        )

            logger.info(f"Generated {len(recommendations)} theme recommendations")
            return recommendations

        except Exception as e:
            logger.error(f"Error analyzing correlations: {e}")
            return []

    def _find_theme_id(self, theme_name: str, themes: List[Dict]) -> int:
        """Find theme ID by name"""
        for theme in themes:
            if theme.get("name") == theme_name:
                return theme.get("id")
        return None

    def _find_related_stock(self, theme_name: str, us_gainers: List[Dict]) -> str:
        """Find the best performing related US stock"""
        rules = self.CORRELATION_RULES.get(theme_name, {})
        related_stocks = rules.get("us_stocks", [])

        for gainer in us_gainers:
            if gainer["ticker"] in related_stocks:
                return gainer["ticker"]

        return related_stocks[0] if related_stocks else None

    def _generate_reason(
        self, theme_name: str, us_gainers: List[Dict], news_articles: List[Dict]
    ) -> str:
        """Generate human-readable reason for recommendation"""
        rules = self.CORRELATION_RULES.get(theme_name, {})
        related_stocks = rules.get("us_stocks", [])

        # Find performing stocks
        performing_stocks = [g for g in us_gainers if g["ticker"] in related_stocks]

        if performing_stocks:
            stock = performing_stocks[0]
            return (
                f"{stock['name']}({stock['ticker']}) "
                f"{stock['change_percent']:+.1f}% 상승으로 "
                f"관련 한국 종목 주목"
            )

        # Check news mentions
        keywords = rules.get("keywords", [])
        for article in news_articles[:3]:
            text = (
                f"{article.get('title', '')} {article.get('description', '')}".lower()
            )
            if any(kw in text for kw in keywords):
                return f"미국 시장에서 {theme_name} 관련 이슈 부각"

        return f"{theme_name} 섹터 관심 증가"

    def generate_daily_summary(
        self, us_indices: Dict, top_gainers: List[Dict], news: List[Dict]
    ) -> str:
        """
        Generate daily market summary

        Args:
            us_indices: Market indices data
            top_gainers: Top gaining stocks
            news: Market news articles

        Returns:
            Summary text
        """
        try:
            summary_parts = []

            # Indices summary
            if us_indices:
                indices_text = []
                for name, data in us_indices.items():
                    change = data.get("change_percent", 0)
                    sign = "+" if change >= 0 else ""
                    indices_text.append(f"{name} {sign}{change:.1f}%")

                summary_parts.append(f"미국 증시: {', '.join(indices_text)}")

            # Top gainers
            if top_gainers:
                top_stock = top_gainers[0]
                summary_parts.append(
                    f"최대 상승: {top_stock['name']} "
                    f"+{top_stock['change_percent']:.1f}%"
                )

            # Trending sectors
            sectors = [g.get("sector") for g in top_gainers if g.get("sector")]
            if sectors:
                from collections import Counter

                top_sector = Counter(sectors).most_common(1)[0][0]
                summary_parts.append(f"주목 섹터: {top_sector}")

            return ". ".join(summary_parts) + "."

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "미국 증시 데이터 분석 중"
