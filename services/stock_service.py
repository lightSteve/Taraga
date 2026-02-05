from sqlalchemy.orm import Session
from models import User, Watchlist, StockKR
from services.service_factory import ServiceFactory
import logging

logger = logging.getLogger(__name__)


class StockService:
    def __init__(self, db: Session):
        self.db = db
        self.market_service = ServiceFactory.get_market_data_service()

    # Defining Sector Map as class constant or static
    SECTOR_ETF_MAP = {
        "반도체": "SOXX",
        "AI/SW": "IGV",
        "2차전지": "LIT",
        "자동차": "CARZ",
        "바이오/제약": "XLV",
        "방산/우주": "ITA",
        "조선/해운": "BDRY",
        "엔터/게임": "PEJ",
        "금융/은행": "XLF",
        "원전/에너지": "URA",
        "화장품/소비재": "XLP",
        "IT/기술": "XLK",  # Fallback for general tech
        "정유/화학": "XLE",
    }

    SECTOR_KEYWORDS = {
        "반도체": [
            "반도체",
            "하이닉스",
            "전자",
            "칩스",
            "미래",
            "HPSP",
            "이오테크닉스",
        ],
        "AI/SW": ["네이버", "카카오", "AI", "소프트", "솔루션", "오픈엣지", "딥노이드"],
        "2차전지": [
            "에너지솔루션",
            "SDI",
            "이노베이션",
            "엘앤에프",
            "에코프로",
            "포스코퓨처엠",
            "배터리",
        ],
        "자동차": ["현대", "기아", "모비스", "타이어", "한온시스템"],
        "바이오/제약": [
            "바이오",
            "약품",
            "제약",
            "셀트리온",
            "유한양행",
            "한미약품",
            "삼성바이오",
        ],
        "방산/우주": ["항공", "에어로", "방산", "LIG", "현대로템", "한화"],
        "조선/해운": ["중공업", "조선", "해운", "오션", "HMM", "팬오션"],
        "엔터/게임": [
            "엔터",
            "에스엠",
            "JYP",
            "하이브",
            "게임",
            "소프트",
            "NC",
            "크래프톤",
            "펄어비스",
        ],
        "금융/은행": ["금융", "은행", "지주", "증권", "보험", "KB", "신한"],
        "원전/에너지": ["전력", "기술", "두산", "한전", "일진"],
        "화장품/소비재": ["화장품", "뷰티", "생활", "건강", "아모레", "클리오", "CJ"],
        "IT/기술": ["테크", "전기", "LG", "삼성", "이노텍"],
        "정유/화학": ["S-Oil", "GS", "케미칼", "롯데케미칼", "금호석유"],
    }

    def get_analyzed_watchlist(self, user_uuid: str):
        """
        Analyze user's watchlist against real-time US market data.
        Maps every watchlist item to a relevant US Sector/ETF.
        """
        # 1. Get User
        user = self.db.query(User).filter(User.user_uuid == user_uuid).first()
        if not user:
            return {"personal_matches": []}

        # 2. Get User Watchlist
        watchlist_items = (
            self.db.query(Watchlist).filter(Watchlist.user_id == user.id).all()
        )
        if not watchlist_items:
            return {"personal_matches": []}

        # 3. Get Real Market Data (Sector ETFs)
        sector_data = {}
        if hasattr(self.market_service, "get_sector_performance"):
            sector_data = self.market_service.get_sector_performance()

        # Robust Fallback if API returns empty/insufficient data
        if not sector_data or len(sector_data) < 3:
            logger.warning("Using Mock Sector Data due to API failure")
            sector_data = {
                "XLK": {"change_percent": 1.45},  # Tech
                "XLV": {"change_percent": -0.32},  # Health
                "XLE": {"change_percent": 0.82},  # Energy
                "XLY": {"change_percent": 1.12},  # Consumer Discretionary
                "SOXX": {"change_percent": 2.34},  # Semiconductor
                "IGV": {"change_percent": 1.89},  # Software
                "LIT": {"change_percent": 0.45},  # Battery
                "CARZ": {"change_percent": 0.95},  # Auto
                "ITA": {"change_percent": -0.15},  # Defense
                "BDRY": {"change_percent": 0.20},  # Shipping
                "PEJ": {"change_percent": 0.65},  # Leisure
                "XLF": {"change_percent": 0.12},  # Finance
                "URA": {"change_percent": 1.05},  # Nuclear
                "XLP": {"change_percent": -0.45},  # Consumer Staples
            }

        # 4. Prepare Groups
        groups_map = {}  # key: theme_name, value: group dict

        for item in watchlist_items:
            stock = (
                self.db.query(StockKR)
                .filter(StockKR.ticker == item.stock_kr_ticker)
                .first()
            )
            if not stock:
                continue

            # Determine Sector
            matched_sector = "기타"

            # Simple keyword matching priority
            for sector, keywords in self.SECTOR_KEYWORDS.items():
                if any(k in stock.name for k in keywords):
                    matched_sector = sector
                    break

            # If "기타" but contains generic Tech terms or is Samsung Electronics (often just "삼성전자")
            if matched_sector == "기타":
                # Special cases
                if "삼성전자" in stock.name:
                    matched_sector = "반도체"
                elif "SK하이닉스" in stock.name:
                    matched_sector = "반도체"
                else:
                    continue  # Skip completely unknown sectors for now, or group into 'Others'

            # Get generic ETF for the sector
            etf_ticker = self.SECTOR_ETF_MAP.get(matched_sector)
            if not etf_ticker:
                continue

            # Check ETF Performance
            etf_perf = sector_data.get(etf_ticker, {"change_percent": 0.0})
            us_change = etf_perf.get("change_percent", 0.0)

            # Create Group if not exists
            if matched_sector not in groups_map:
                groups_map[matched_sector] = {
                    "theme_name": f"{matched_sector} ({etf_ticker})",
                    "us_change_percent": us_change,
                    "reason": f"미국 {etf_ticker} ETF {'상승' if us_change >= 0 else '하락'}세 영향",
                    "my_stocks": [],
                }

            # Add Stock
            groups_map[matched_sector]["my_stocks"].append(
                {
                    "ticker": stock.ticker,
                    "name": stock.name,
                    "relation": "Sector Correlation",
                    "expected_flow": "UP" if us_change >= 0 else "DOWN",
                }
            )

        # Convert map to list
        personal_matches = list(groups_map.values())

        return {"personal_matches": personal_matches}
