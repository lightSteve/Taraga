import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class OpenAIService:
    """Service to interact with OpenAI GPT-4o for market analysis"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = OpenAI(api_key=self.api_key)

    def analyze_us_market(self, market_data: dict, news_headlines: list, themes: list):
        """
        Analyze US market data and news to recommend Korean themes

        Args:
            market_data: Dict with US market snapshot (indices, top gainers)
            news_headlines: List of news headline strings
            themes: List of available Korean themes with keywords

        Returns:
            Dict with analysis results in JSON format
        """

        # Build the system prompt
        system_prompt = """You are a financial analyst specializing in cross-market correlation between US and Korean stock markets.
Your job is to analyze US market movements and news to predict which Korean market themes will be affected.

You will receive:
1. US market snapshot (major indices performance)
2. Top gaining US stocks
3. News headlines from the US market
4. List of available Korean market themes

Your task:
1. Summarize the key market driver from the US market
2. Identify the top 3 sectors that performed well
3. Match these sectors to the provided Korean market themes
4. Provide a confidence score (1-10) for each theme recommendation
5. Explain the reasoning for each recommendation

Return your analysis in strict JSON format with this structure:
{
  "us_summary": "Brief summary of US market driver",
  "market_sentiment": "Fear/Greed/Neutral",
  "recommended_themes": [
    {
      "theme_name": "Theme name",
      "impact_score": 8,
      "reason": "Why this theme is relevant",
      "related_us_stocks": ["TICKER1", "TICKER2"]
    }
  ]
}"""

        # Build the user prompt
        user_prompt = f"""
**US Market Data:**
{json.dumps(market_data, indent=2)}

**News Headlines:**
{json.dumps(news_headlines, indent=2)}

**Available Korean Themes:**
{json.dumps(themes, indent=2)}

Please analyze and provide recommendations.
"""

        # Call OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        # Parse the response
        result = json.loads(response.choices[0].message.content)
        return result

    def summarize_news(self, headlines: list):
        """Summarize multiple news headlines into key insights"""
        prompt = f"""Summarize these US market news headlines into 3-5 key insights:

{json.dumps(headlines, indent=2)}

Return as a JSON array of strings."""

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.5,
        )

        return json.loads(response.choices[0].message.content)


if __name__ == "__main__":
    # Test the service
    service = OpenAIService()

    # Sample data
    market_data = {
        "SPY": {"change_percent": 1.2},
        "QQQ": {"change_percent": 2.5},
        "top_gainers": [
            {"ticker": "NVDA", "change_percent": 5.2},
            {"ticker": "TSLA", "change_percent": 3.8},
        ],
    }

    news = [
        "NVIDIA announces new AI chip breakthrough",
        "Tesla reports record deliveries in Q4",
    ]

    themes = [
        {"name": "AI Semiconductor", "keywords": ["AI", "chip", "semiconductor"]},
        {"name": "EV Battery", "keywords": ["electric vehicle", "battery", "EV"]},
    ]

    result = service.analyze_us_market(market_data, news, themes)
    print(json.dumps(result, indent=2, ensure_ascii=False))
