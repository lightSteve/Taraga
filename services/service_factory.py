"""
Service Factory - Switch between free and premium API services
"""

import os
from typing import Union
import logging

logger = logging.getLogger(__name__)


class ServiceFactory:
    """Factory to manage free vs premium service implementations"""

    @staticmethod
    def use_premium_apis() -> bool:
        """Check if premium APIs should be used"""
        return os.getenv("USE_PREMIUM_APIS", "false").lower() == "true"

    @staticmethod
    def get_market_data_service():
        """
        Get US market data service (free or premium)

        Returns:
            YahooFinanceService (free) or PolygonService (premium)
        """
        if ServiceFactory.use_premium_apis():
            try:
                from .polygon_service import PolygonService

                logger.info("Using premium Polygon.io service")
                return PolygonService()
            except ImportError:
                logger.warning(
                    "Polygon service not available, falling back to free service"
                )

        from .yahoo_finance_service import YahooFinanceService

        logger.info("Using free Yahoo Finance service")
        return YahooFinanceService()

    @staticmethod
    def get_news_service():
        """
        Get news service (free or premium)

        Returns:
            RSSNewsService (free) or NewsAPIService (premium)
        """
        if ServiceFactory.use_premium_apis():
            try:
                from .news_service import NewsService

                logger.info("Using premium NewsAPI service")
                return NewsService()
            except ImportError:
                logger.warning(
                    "NewsAPI service not available, falling back to free service"
                )

        from .rss_news_service import RSSNewsService

        logger.info("Using free RSS news service")
        return RSSNewsService()

    @staticmethod
    def get_ai_service():
        """
        Get AI analysis service (free or premium)

        Returns:
            TemplateAnalysisService (free) or OpenAIService (premium)
        """
        if ServiceFactory.use_premium_apis():
            try:
                from .openai_service import OpenAIService

                logger.info("Using premium OpenAI service")
                return OpenAIService()
            except ImportError:
                logger.warning(
                    "OpenAI service not available, falling back to free service"
                )

        from .template_analysis_service import TemplateAnalysisService

        logger.info("Using free template analysis service")
        return TemplateAnalysisService()

    @staticmethod
    def get_korean_stock_service():
        """
        Get Korean stock data service (always free with KIS account)

        Returns:
            KISService
        """
        from .kis_service import KISService

        logger.info("Using KIS service for Korean stock data")
        return KISService()

    @staticmethod
    def get_service_status() -> dict:
        """
        Get current service configuration status

        Returns:
            Dictionary with service status information
        """
        use_premium = ServiceFactory.use_premium_apis()

        return {
            "mode": "premium" if use_premium else "free",
            "services": {
                "us_market_data": "Polygon.io" if use_premium else "Yahoo Finance",
                "news": "NewsAPI" if use_premium else "RSS Feeds",
                "ai_analysis": "OpenAI GPT-4" if use_premium else "Template Rules",
                "korean_stocks": "KIS API (Free)",
            },
            "estimated_monthly_cost": "$650+" if use_premium else "$0",
        }
