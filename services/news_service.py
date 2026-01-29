import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2"


class NewsService:
    """Service to fetch US financial news from NewsAPI"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or NEWS_API_KEY
        if not self.api_key:
            raise ValueError("NewsAPI key is required")

    def get_business_headlines(self, country: str = "us", category: str = "business"):
        """Get top business headlines from US"""
        url = f"{BASE_URL}/top-headlines"
        params = {
            "apiKey": self.api_key,
            "country": country,
            "category": category,
            "pageSize": 20,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        articles = data.get("articles", [])

        # Extract headlines
        headlines = [
            {
                "title": article.get("title"),
                "description": article.get("description"),
                "source": article.get("source", {}).get("name"),
                "published_at": article.get("publishedAt"),
            }
            for article in articles
        ]

        return headlines

    def search_market_news(self, query: str = "stock market", days_back: int = 1):
        """Search for specific market-related news"""
        url = f"{BASE_URL}/everything"

        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)

        params = {
            "apiKey": self.api_key,
            "q": query,
            "from": from_date.strftime("%Y-%m-%d"),
            "to": to_date.strftime("%Y-%m-%d"),
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": 20,
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        articles = data.get("articles", [])

        headlines = [
            {
                "title": article.get("title"),
                "description": article.get("description"),
                "source": article.get("source", {}).get("name"),
            }
            for article in articles
        ]

        return headlines


if __name__ == "__main__":
    # Test the service
    service = NewsService()
    print("📰 Top Business Headlines:")
    headlines = service.get_business_headlines()
    for h in headlines[:5]:
        print(f"- {h['title']}")
