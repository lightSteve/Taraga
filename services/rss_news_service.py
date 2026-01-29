"""
RSS News Service - Free alternative to NewsAPI
Aggregates financial news from free RSS feeds
"""

import feedparser
from datetime import datetime
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class RSSNewsService:
    """Free news aggregation service using RSS feeds"""

    # Free financial news RSS feeds
    RSS_FEEDS = [
        {
            "url": "https://feeds.finance.yahoo.com/rss/2.0/headline",
            "source": "Yahoo Finance",
        },
        {
            "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
            "source": "CNBC",
        },
        {"url": "https://www.marketwatch.com/rss/topstories", "source": "MarketWatch"},
        {"url": "https://www.investing.com/rss/news.rss", "source": "Investing.com"},
    ]

    def get_market_news(self, limit: int = 10) -> List[Dict]:
        """
        Fetch latest market news from multiple RSS feeds

        Args:
            limit: Maximum number of news items to return

        Returns:
            List of news article dictionaries
        """
        try:
            logger.info(f"Fetching market news from {len(self.RSS_FEEDS)} RSS feeds")

            all_articles = []

            for feed_info in self.RSS_FEEDS:
                try:
                    feed = feedparser.parse(feed_info["url"])

                    for entry in feed.entries[:5]:  # Get top 5 from each feed
                        article = {
                            "title": entry.get("title", "No title"),
                            "description": entry.get(
                                "summary", entry.get("description", "")
                            ),
                            "url": entry.get("link", ""),
                            "source": feed_info["source"],
                            "published_at": self._parse_date(
                                entry.get("published", "")
                            ),
                        }
                        all_articles.append(article)

                except Exception as e:
                    logger.warning(f"Error fetching from {feed_info['source']}: {e}")
                    continue

            # Sort by published date (most recent first)
            all_articles.sort(
                key=lambda x: x["published_at"] if x["published_at"] else datetime.min,
                reverse=True,
            )

            logger.info(f"Fetched {len(all_articles)} articles, returning top {limit}")
            return all_articles[:limit]

        except Exception as e:
            logger.error(f"Error fetching market news: {e}")
            return []

    def get_sector_news(self, sector: str, limit: int = 5) -> List[Dict]:
        """
        Get news filtered by sector keywords

        Args:
            sector: Sector name (e.g., 'technology', 'healthcare')
            limit: Maximum number of articles

        Returns:
            List of filtered news articles
        """
        try:
            all_news = self.get_market_news(limit=30)

            # Filter by sector keywords
            sector_keywords = self._get_sector_keywords(sector.lower())

            filtered_news = []
            for article in all_news:
                title_lower = article["title"].lower()
                desc_lower = article["description"].lower()

                if any(
                    keyword in title_lower or keyword in desc_lower
                    for keyword in sector_keywords
                ):
                    filtered_news.append(article)

                if len(filtered_news) >= limit:
                    break

            return filtered_news

        except Exception as e:
            logger.error(f"Error fetching sector news: {e}")
            return []

    def _parse_date(self, date_str: str) -> datetime:
        """Parse various date formats from RSS feeds"""
        if not date_str:
            return datetime.now()

        try:
            # Try parsing common RSS date formats
            from email.utils import parsedate_to_datetime

            return parsedate_to_datetime(date_str)
        except:
            try:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except:
                return datetime.now()

    def _get_sector_keywords(self, sector: str) -> List[str]:
        """Get relevant keywords for a sector"""
        sector_map = {
            "technology": [
                "tech",
                "software",
                "ai",
                "chip",
                "semiconductor",
                "apple",
                "microsoft",
                "google",
                "nvidia",
            ],
            "healthcare": ["health", "pharma", "biotech", "drug", "vaccine", "medical"],
            "finance": ["bank", "financial", "fintech", "payment", "insurance"],
            "energy": ["oil", "gas", "energy", "renewable", "solar", "electric"],
            "automotive": ["car", "auto", "vehicle", "tesla", "ev", "electric vehicle"],
            "retail": ["retail", "consumer", "shopping", "amazon", "walmart"],
            "entertainment": [
                "entertainment",
                "media",
                "streaming",
                "netflix",
                "disney",
            ],
        }

        return sector_map.get(sector, [sector])

    def get_trending_topics(self) -> List[str]:
        """
        Extract trending topics from recent news headlines

        Returns:
            List of trending keywords/topics
        """
        try:
            news = self.get_market_news(limit=20)

            # Simple keyword extraction from titles
            all_words = []
            for article in news:
                words = article["title"].split()
                all_words.extend([w.lower().strip(".,!?") for w in words if len(w) > 4])

            # Count frequency
            from collections import Counter

            word_counts = Counter(all_words)

            # Get top trending words (excluding common words)
            common_words = {
                "stock",
                "market",
                "shares",
                "price",
                "trading",
                "today",
                "after",
            }
            trending = [
                word
                for word, count in word_counts.most_common(10)
                if word not in common_words
            ]

            return trending[:5]

        except Exception as e:
            logger.error(f"Error extracting trending topics: {e}")
            return []
