from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from services.stock_service import StockService
from logic.correlation_engine import CorrelationEngine

router = APIRouter()


@router.get("/personal-matches")
def get_personal_matches(user_uuid: str, db: Session = Depends(get_db)):
    """
    Get personalized stock matches using Real Data Logic (StockService)
    """
    service = StockService(db)
    return service.get_analyzed_watchlist(user_uuid)


@router.get("/value-chain")
def get_value_chain(theme_id: int, db: Session = Depends(get_db)):
    """
    Get the hierarchical Value Chain visualization data for a specific theme.
    """
    engine = CorrelationEngine(db)
    tree = engine.get_value_chain_tree(theme_id)

    if not tree:
        raise HTTPException(status_code=404, detail="Theme or Value Chain not found")

    return tree


@router.get("/news-bridge")
def get_news_bridge(db: Session = Depends(get_db)):
    """
    Get the list of 'Bridge News' connecting US events to KR impacts.
    """
    try:
        # 1. Check if Premium Services are enabled
        from services.service_factory import ServiceFactory

        # If premium, try to use Real Data + AI Translation
        if ServiceFactory.use_premium_apis():
            try:
                # A. Fetch Real US News
                news_service = ServiceFactory.get_news_service()
                if hasattr(news_service, "get_business_headlines"):
                    us_news = news_service.get_business_headlines()

                    # B. Translate & Analyze with AI
                    ai_service = ServiceFactory.get_ai_service()
                    if hasattr(ai_service, "translate_bridge_news"):
                        translated_result = ai_service.translate_bridge_news(
                            us_news[:5]
                        )  # Process top 5
                        return translated_result
            except Exception as e:
                print(f"AI Translation failed, falling back to mock: {e}")

        # Fallback to Mock Data (Korean)
        news_items = [
            {
                "us_source": "Bloomberg",
                "us_headline": "마이크론, 엔비디아용 HBM3E 양산 시작",
                "kr_impact": "SK하이닉스(공정 파트너) 및 한미반도체(장비) 수혜 예상",
                "related_stocks": [
                    {"name": "SK하이닉스", "ticker": "000660", "change": "+3.2%"},
                    {"name": "한미반도체", "ticker": "042700", "change": "+5.4%"},
                ],
                "timestamp": "2024-02-27T06:00:00",
            },
            {
                "us_source": "Reuters",
                "us_headline": "FDA, 일라이 릴리 알츠하이머 신약 승인",
                "kr_impact": "CDMO 기업 수주 확대 기대",
                "related_stocks": [
                    {"name": "삼성바이오로직스", "ticker": "207940", "change": "+1.8%"},
                    {"name": "롯데바이오로직스", "ticker": "N/A", "change": "(비상장)"},
                ],
                "timestamp": "2024-02-27T05:30:00",
            },
            {
                "us_source": "TechCrunch",
                "us_headline": "오픈AI, 텍스트-비디오 모델 '소라' 공개",
                "kr_impact": "AI 데이터센터 및 고속 인터페이스 칩 수요 급증 예상",
                "related_stocks": [
                    {
                        "name": "오픈엣지테크놀로지",
                        "ticker": "394280",
                        "change": "+8.9%",
                    },
                    {"name": "딥엑스", "ticker": "N/A", "change": "(비상장)"},
                ],
                "timestamp": "2024-02-27T04:15:00",
            },
        ]
        return {"news": news_items}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
