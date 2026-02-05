from datetime import date
from typing import List, Dict


class CalendarService:
    def get_monthly_events(self, year: int, month: int) -> List[Dict]:
        """
        Get major economic events and earnings for a specific month.
        Currently returns mocked high-impact events for demonstration.
        """
        # Mock Data for demo (can be replaced with scraping or API later)
        events = [
            {
                "date": f"{year}-{month:02d}-06",
                "type": "ECONOMIC",
                "title": "미국 고용보고서 (Non-farm Payrolls)",
                "country": "US",
                "impact_score": 95,
                "description": "연준 금리 결정의 핵심 지표. 예상 상회 시 긴축 우려.",
            },
            {
                "date": f"{year}-{month:02d}-12",
                "type": "ECONOMIC",
                "title": "미국 소비자물가지수 (CPI)",
                "country": "US",
                "impact_score": 98,
                "description": "인플레이션 추이 확인. 시장 변동성 최고조 예상.",
            },
            {
                "date": f"{year}-{month:02d}-14",
                "type": "ECONOMIC",
                "title": "미국 생산자물가지수 (PPI)",
                "country": "US",
                "impact_score": 85,
                "description": "CPI 선행 지표.",
            },
            {
                "date": f"{year}-{month:02d}-20",
                "type": "ECONOMIC",
                "title": "FOMC 금리 결정",
                "country": "US",
                "impact_score": 100,
                "description": "기준 금리 동결/인하 여부 발표. 파월 의장 연설 중요.",
            },
            {
                "date": f"{year}-{month:02d}-21",
                "type": "EARNINGS",
                "title": "마이크론 (MU) 실적 발표",
                "country": "US",
                "impact_score": 90,
                "description": "반도체 업황 가늠자. SK하이닉스/삼성전자 주가에 직접 영향.",
            },
            {
                "date": f"{year}-{month:02d}-28",
                "type": "EARNINGS",
                "title": "나이키 (NKE) 실적 발표",
                "country": "US",
                "impact_score": 75,
                "description": "소비재/의류 OEM (영원무역 등) 영향.",
            },
            {
                "date": f"{year}-{month:02d}-15",
                "type": "DIVIDEND",
                "title": "배당락일: 애플 (AAPL)",
                "country": "US",
                "impact_score": 40,
                "description": "분기 배당 지급 기준.",
            },
        ]

        # Filter logic could go here if we had a huge database
        return events
