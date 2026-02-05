from datetime import datetime, time
import pytz


class SystemService:
    def get_current_app_mode(self):
        """
        Determine the current application mode based on KST time.

        Modes:
        - KR_MARKET: 08:30 ~ 16:00 (Korean Market Focus)
        - US_PRE: 17:00 ~ 22:30 (US Pre-market analysis)
        - US_MARKET: 22:30 ~ 06:00 (US Market Live)
        - GLOBAL_BRIEF: 06:00 ~ 08:30 (Overnight summary)
        """
        kst = pytz.timezone("Asia/Seoul")
        now = datetime.now(kst).time()

        # Define Time Ranges
        kr_start = time(8, 30)
        kr_end = time(16, 0)

        us_pre_start = time(17, 0)
        us_market_start = time(22, 30)  # Standard Time (approx)

        global_brief_start = time(6, 0)

        # Check Ranges
        if kr_start <= now < kr_end:
            return {
                "mode": "KR_MARKET",
                "label": "🇰🇷 한국장 실시간 (KR Market)",
                "primary_color": "0xFF3B82F6",  # Blue for KR
                "message": "현재 한국 시장이 열려있습니다.",
            }
        elif us_pre_start <= now < us_market_start:
            return {
                "mode": "US_PRE",
                "label": "🇺🇸 프리마켓/장전 (Pre-Market)",
                "primary_color": "0xFF6366F1",  # Indigo
                "message": "미국 개장 전, 프리마켓 동향을 확인하세요.",
            }
        elif now >= us_market_start or now < global_brief_start:
            return {
                "mode": "US_MARKET",
                "label": "🇺🇸 미국장 실시간 (US Market)",
                "primary_color": "0xFFEF4444",  # Red for US
                "message": "미국 시장이 활발히 거래 중입니다.",
            }
        else:
            return {
                "mode": "GLOBAL_BRIEF",
                "label": "🌏 글로벌 브리핑 (Daily Brief)",
                "primary_color": "0xFF10B981",  # Green
                "message": "밤사이 미국 증시 마감 상황입니다.",
            }
