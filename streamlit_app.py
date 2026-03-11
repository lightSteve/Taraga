"""
Taraga 🌉 - 따라가 대시보드
Wall Street → 여의도 브릿지 | Streamlit 실시간 모니터링
"""

import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import json

# ─── Page Config ───
st.set_page_config(
    page_title="Taraga 🌉 따라가",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Constants ───
API_BASE = "http://localhost:8000/api/v1"
DEFAULT_USER_UUID = "streamlit-user-001"

# ─── Session State ───
if "user_uuid" not in st.session_state:
    st.session_state.user_uuid = DEFAULT_USER_UUID


# ─── Helper Functions ───
def _is_server_up():
    """서버 실행 여부 확인"""
    try:
        resp = requests.get("http://localhost:8000/health", timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


@st.cache_data(ttl=900)
def fetch_api(endpoint: str):
    """API 호출 헬퍼"""
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


def post_api(endpoint: str, payload: dict):
    """API POST 헬퍼"""
    try:
        resp = requests.post(f"{API_BASE}{endpoint}", json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def delete_api(endpoint: str):
    """API DELETE 헬퍼"""
    try:
        resp = requests.delete(f"{API_BASE}{endpoint}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def add_to_watchlist(ticker: str, stock_name: str):
    """관심종목 추가"""
    result = post_api("/watchlist/", {
        "user_uuid": st.session_state.user_uuid,
        "ticker": ticker,
        "stock_name": stock_name,
    })
    if result:
        st.toast(f"✅ {stock_name} 관심종목에 추가됨")
        st.cache_data.clear()
    else:
        st.toast(f"⚠️ {stock_name} 추가 실패 (이미 등록됨)")


@st.cache_data(ttl=1800)
def fetch_indices_direct():
    """백엔드 없이 yfinance로 직접 시장 데이터 가져오기 (Standalone 모드)"""
    try:
        import yfinance as yf
        import pandas as pd

        indices_map = {
            "^GSPC": ("S&P 500", "US"),
            "^DJI": ("Dow Jones", "US"),
            "^IXIC": ("Nasdaq", "US"),
            "^KS11": ("KOSPI", "KR"),
            "^KQ11": ("KOSDAQ", "KR"),
            "BTC-USD": ("Bitcoin", "Coin"),
            "ETH-USD": ("Ethereum", "Coin"),
        }

        tickers_str = " ".join(indices_map.keys())
        data = yf.download(tickers_str, period="1mo", group_by="ticker", progress=False, threads=False)

        if data is None or data.empty:
            return {}

        results = {}
        for symbol, (name, market) in indices_map.items():
            try:
                if isinstance(data.columns, pd.MultiIndex):
                    if symbol in data.columns.get_level_values(1):
                        df = data.xs(symbol, axis=1, level=1)
                    elif symbol in data.columns.get_level_values(0):
                        df = data[symbol]
                    else:
                        continue
                else:
                    continue

                df = df.dropna(subset=["Close"])
                if len(df) < 2:
                    continue

                history = [float(x) for x in df["Close"].tail(14).tolist()]
                current = float(df["Close"].iloc[-1])
                prev = float(df["Close"].iloc[-2])
                change_pct = ((current - prev) / prev) * 100 if prev > 0 else 0

                results[name] = {
                    "regularMarketPrice": round(current, 2),
                    "regularMarketChangePercent": round(change_pct, 2),
                    "history": history,
                    "market": market,
                }
            except Exception:
                continue

        return results
    except ImportError:
        return {}
    except Exception:
        return {}


@st.cache_data(ttl=1800)
def fetch_movers_direct():
    """백엔드 없이 yfinance로 직접 급등락 가져오기"""
    try:
        import yfinance as yf

        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
                    "JPM", "V", "WMT", "UNH", "JNJ", "HD", "PG", "MA",
                    "XOM", "CVX", "KO", "PEP", "COST", "AVGO", "LLY",
                    "AMD", "NFLX", "INTC", "BA", "CRM", "ORCL", "QCOM", "ADBE"]

        data = yf.download(" ".join(tickers), period="2d", group_by="ticker", progress=False, threads=False)
        if data is None or data.empty:
            return [], []

        results = []
        for t in tickers:
            try:
                df = data[t] if t in data.columns.get_level_values(0) else None
                if df is None or len(df) < 2:
                    continue
                cur = float(df["Close"].iloc[-1])
                prev = float(df["Close"].iloc[-2])
                cp = ((cur - prev) / prev) * 100 if prev > 0 else 0
                vol = int(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0
                prev_vol = int(df["Volume"].iloc[-2]) if "Volume" in df.columns and len(df) >= 2 else 0
                vol_change = ((vol - prev_vol) / prev_vol * 100) if prev_vol > 0 else 0
                results.append({"ticker": t, "name": t, "price": cur, "change_percent": round(cp, 2), "volume": vol, "volume_change": round(vol_change, 1)})
            except Exception:
                continue

        results.sort(key=lambda x: x["change_percent"], reverse=True)
        gainers = [r for r in results if r["change_percent"] > 0][:10]
        losers = sorted([r for r in results if r["change_percent"] < 0], key=lambda x: x["change_percent"])[:10]
        return gainers, losers
    except Exception:
        return [], []


@st.cache_data(ttl=1800)
def fetch_kr_movers_direct():
    """백엔드 없이 yfinance로 한국 주요 종목 급등락 가져오기"""
    try:
        import yfinance as yf

        kr_tickers = {
            "005930.KS": "삼성전자", "000660.KS": "SK하이닉스", "373220.KS": "LG에너지솔루션",
            "207940.KS": "삼성바이오로직스", "005380.KS": "현대차", "006400.KS": "삼성SDI",
            "051910.KS": "LG화학", "035420.KS": "NAVER", "035720.KS": "카카오",
            "068270.KS": "셀트리온", "105560.KS": "KB금융", "055550.KS": "신한지주",
            "000270.KS": "기아", "012330.KS": "현대모비스", "066570.KS": "LG전자",
            "003670.KS": "포스코퓨처엠", "034730.KS": "SK", "015760.KS": "한국전력",
            "032830.KS": "삼성생명", "009150.KS": "삼성전기",
            "247540.KS": "에코프로비엠", "086520.KS": "에코프로",
            "003550.KS": "LG", "028260.KS": "삼성물산",
        }

        tickers_str = " ".join(kr_tickers.keys())
        data = yf.download(tickers_str, period="2d", group_by="ticker", progress=False, threads=False)
        if data is None or data.empty:
            return [], []

        results = []
        for t, name in kr_tickers.items():
            try:
                df = data[t] if t in data.columns.get_level_values(0) else None
                if df is None or len(df) < 2:
                    continue
                cur = float(df["Close"].iloc[-1])
                prev = float(df["Close"].iloc[-2])
                cp = ((cur - prev) / prev) * 100 if prev > 0 else 0
                vol = int(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0
                prev_vol = int(df["Volume"].iloc[-2]) if "Volume" in df.columns and len(df) >= 2 else 0
                vol_change = ((vol - prev_vol) / prev_vol * 100) if prev_vol > 0 else 0
                results.append({"ticker": t.replace(".KS", ""), "name": name, "price": cur, "change_percent": round(cp, 2), "volume": vol, "volume_change": round(vol_change, 1)})
            except Exception:
                continue

        results.sort(key=lambda x: x["change_percent"], reverse=True)
        gainers = [r for r in results if r["change_percent"] > 0][:10]
        losers = sorted([r for r in results if r["change_percent"] < 0], key=lambda x: x["change_percent"])[:10]
        return gainers, losers
    except Exception:
        return [], []


@st.cache_data(ttl=1800)
def fetch_coin_movers_direct():
    """백엔드 없이 yfinance로 코인 급등락 가져오기"""
    try:
        import yfinance as yf

        coin_tickers = {
            "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum", "BNB-USD": "BNB",
            "XRP-USD": "XRP", "ADA-USD": "Cardano", "SOL-USD": "Solana",
            "DOGE-USD": "Dogecoin", "DOT-USD": "Polkadot", "AVAX-USD": "Avalanche",
            "MATIC-USD": "Polygon", "LINK-USD": "Chainlink", "UNI-USD": "Uniswap",
            "ATOM-USD": "Cosmos", "LTC-USD": "Litecoin", "FIL-USD": "Filecoin",
            "NEAR-USD": "NEAR Protocol", "APT-USD": "Aptos", "ARB-USD": "Arbitrum",
            "OP-USD": "Optimism", "SUI-USD": "Sui",
        }

        tickers_str = " ".join(coin_tickers.keys())
        data = yf.download(tickers_str, period="2d", group_by="ticker", progress=False, threads=False)
        if data is None or data.empty:
            return [], []

        results = []
        for t, name in coin_tickers.items():
            try:
                df = data[t] if t in data.columns.get_level_values(0) else None
                if df is None or len(df) < 2:
                    continue
                cur = float(df["Close"].iloc[-1])
                prev = float(df["Close"].iloc[-2])
                cp = ((cur - prev) / prev) * 100 if prev > 0 else 0
                vol = int(df["Volume"].iloc[-1]) if "Volume" in df.columns else 0
                prev_vol = int(df["Volume"].iloc[-2]) if "Volume" in df.columns and len(df) >= 2 else 0
                vol_change = ((vol - prev_vol) / prev_vol * 100) if prev_vol > 0 else 0
                results.append({"ticker": t.replace("-USD", ""), "name": name, "price": cur, "change_percent": round(cp, 2), "volume": vol, "volume_change": round(vol_change, 1)})
            except Exception:
                continue

        results.sort(key=lambda x: x["change_percent"], reverse=True)
        gainers = [r for r in results if r["change_percent"] > 0][:10]
        losers = sorted([r for r in results if r["change_percent"] < 0], key=lambda x: x["change_percent"])[:10]
        return gainers, losers
    except Exception:
        return [], []


def format_change(val):
    """퍼센트 변화량 포맷"""
    if val is None:
        return "N/A"
    prefix = "+" if val >= 0 else ""
    return f"{prefix}{val:.2f}%"


def get_color(val):
    """한국 시장 규칙: 상승=빨강, 하락=파랑"""
    if val is None:
        return "gray"
    return "#FF5247" if val >= 0 else "#3182F6"


@st.cache_data(ttl=1800)
def fetch_sector_data(market="US"):
    """섹터별 데이터로 히트맵용 데이터 생성 (US/KR 지원)"""
    try:
        import yfinance as yf
        import pandas as pd

        if market == "KR":
            # 한국: 대분류 섹터별 대표 종목으로 섹터 등락률 계산
            sector_stocks = {
                "IT/반도체": {
                    "tickers": {"005930.KS": "삼성전자", "000660.KS": "SK하이닉스"},
                    "weight": 25,
                },
                "2차전지": {
                    "tickers": {"373220.KS": "LG에너지솔루션", "006400.KS": "삼성SDI", "051910.KS": "LG화학"},
                    "weight": 10,
                },
                "자동차": {
                    "tickers": {"005380.KS": "현대차", "000270.KS": "기아", "012330.KS": "현대모비스"},
                    "weight": 10,
                },
                "바이오/헬스케어": {
                    "tickers": {"207940.KS": "삼성바이오", "068270.KS": "셀트리온"},
                    "weight": 8,
                },
                "금융": {
                    "tickers": {"105560.KS": "KB금융", "055550.KS": "신한지주", "032830.KS": "삼성생명"},
                    "weight": 12,
                },
                "인터넷/플랫폼": {
                    "tickers": {"035420.KS": "NAVER", "035720.KS": "카카오"},
                    "weight": 8,
                },
                "에너지/화학": {
                    "tickers": {"096770.KS": "SK이노베이션", "010950.KS": "S-Oil"},
                    "weight": 5,
                },
                "철강/소재": {
                    "tickers": {"005490.KS": "POSCO홀딩스", "003670.KS": "포스코퓨처엠"},
                    "weight": 5,
                },
                "전자/부품": {
                    "tickers": {"009150.KS": "삼성전기", "066570.KS": "LG전자"},
                    "weight": 6,
                },
                "유틸리티/건설": {
                    "tickers": {"015760.KS": "한국전력", "028260.KS": "삼성물산"},
                    "weight": 5,
                },
                "통신": {
                    "tickers": {"017670.KS": "SK텔레콤", "030200.KS": "KT"},
                    "weight": 6,
                },
            }

            # 모든 종목 티커 수집
            all_tickers = []
            for sector_info in sector_stocks.values():
                all_tickers.extend(sector_info["tickers"].keys())

            tickers_str = " ".join(all_tickers)
            data = yf.download(tickers_str, period="5d", group_by="ticker", progress=False, threads=False)
            if data is None or data.empty:
                return [], None

            results = []
            data_date = None

            for sector_name, sector_info in sector_stocks.items():
                changes = []
                for ticker in sector_info["tickers"]:
                    try:
                        if isinstance(data.columns, pd.MultiIndex):
                            if ticker in data.columns.get_level_values(0):
                                df = data[ticker]
                            elif ticker in data.columns.get_level_values(1):
                                df = data.xs(ticker, axis=1, level=1)
                            else:
                                continue
                        else:
                            continue

                        df = df.dropna(subset=["Close"])
                        if len(df) < 2:
                            continue

                        if data_date is None:
                            last_idx = df.index[-1]
                            data_date = last_idx.strftime("%Y-%m-%d") if hasattr(last_idx, 'strftime') else str(last_idx)[:10]

                        cur = float(df["Close"].iloc[-1])
                        prev = float(df["Close"].iloc[-2])
                        cp = ((cur - prev) / prev) * 100 if prev > 0 else 0
                        changes.append(cp)
                    except Exception:
                        continue

                if changes:
                    avg_change = sum(changes) / len(changes)
                    stock_names = ", ".join(sector_info["tickers"].values())
                    results.append({
                        "ticker": stock_names,
                        "sector_kr": sector_name,
                        "sector_en": sector_name,
                        "change_percent": round(avg_change, 2),
                        "weight": sector_info["weight"],
                        "price": 0,
                    })

            return results, data_date

        else:  # US
            sector_etfs = {
                "XLK": ("IT/기술", "Technology", 30),
                "XLV": ("헬스케어", "Healthcare", 13),
                "XLF": ("금융", "Financials", 12),
                "XLY": ("경기소비재", "Cons. Disc.", 10),
                "XLP": ("필수소비재", "Cons. Staples", 7),
                "XLE": ("에너지", "Energy", 4),
                "XLI": ("산업재", "Industrials", 9),
                "XLB": ("소재", "Materials", 3),
                "XLU": ("유틸리티", "Utilities", 3),
                "XLRE": ("부동산", "Real Estate", 3),
                "XLC": ("통신서비스", "Comm. Services", 9),
            }

            tickers_str = " ".join(sector_etfs.keys())
            data = yf.download(tickers_str, period="5d", group_by="ticker", progress=False, threads=False)
            if data is None or data.empty:
                return [], None

            results = []
            data_date = None

            for ticker, (kr_name, en_name, weight) in sector_etfs.items():
                try:
                    if isinstance(data.columns, pd.MultiIndex):
                        if ticker in data.columns.get_level_values(0):
                            df = data[ticker]
                        elif ticker in data.columns.get_level_values(1):
                            df = data.xs(ticker, axis=1, level=1)
                        else:
                            continue
                    else:
                        continue

                    df = df.dropna(subset=["Close"])
                    if len(df) < 2:
                        continue

                    if data_date is None:
                        last_idx = df.index[-1]
                        data_date = last_idx.strftime("%Y-%m-%d") if hasattr(last_idx, 'strftime') else str(last_idx)[:10]

                    cur = float(df["Close"].iloc[-1])
                    prev = float(df["Close"].iloc[-2])
                    cp = ((cur - prev) / prev) * 100 if prev > 0 else 0

                    results.append({
                        "ticker": ticker,
                        "sector_kr": kr_name,
                        "sector_en": en_name,
                        "change_percent": round(cp, 2),
                        "weight": weight,
                        "price": round(cur, 2),
                    })
                except Exception:
                    continue

            return results, data_date
    except Exception:
        return [], None


@st.cache_data(ttl=21600)
def _fetch_calendar_direct(year: int, month: int):
    """백엔드 없이 yfinance에서 직접 실적 캘린더 가져오기 (Standalone)"""
    try:
        import yfinance as yf
        from datetime import date as d

        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
                    "JPM", "V", "WMT", "MA", "UNH", "HD", "PG", "JNJ",
                    "XOM", "CVX", "KO", "PEP", "COST", "MU", "NKE",
                    "BA", "CRM", "ORCL", "AVGO", "LLY", "AMD", "NFLX", "QCOM"]
        events = []
        for t in tickers:
            try:
                tk = yf.Ticker(t)
                cal = tk.calendar
                if not cal or "Earnings Date" not in cal:
                    continue
                for ed in cal["Earnings Date"]:
                    ed_date = ed if isinstance(ed, d) else d.fromisoformat(str(ed))
                    if ed_date.year == year and ed_date.month == month:
                        eps = cal.get("Earnings Average")
                        rev = cal.get("Revenue Average")
                        events.append({
                            "date": str(ed_date), "type": "EARNINGS",
                            "title": f"{t} 실적 발표", "country": "US", "impact": 4,
                            "description": f"EPS 예상: ${eps:.2f}" if eps else "",
                            "forecast": f"${eps:.2f}" if eps else "—",
                            "previous": "—", "category": "실적 발표",
                        })
            except Exception:
                continue
        events.sort(key=lambda x: x["date"])
        return {"status": "success", "data": events} if events else None
    except Exception:
        return None


@st.cache_data(ttl=1800, show_spinner="스마트 스코어 분석 중...")
def fetch_smart_scores(market: str = "KR"):
    """Smart Score 엔진으로 종목 스캔 및 스코어링"""
    try:
        from logic.smart_score import scan_and_score

        if market == "KR":
            tickers = [
                "005930.KS", "000660.KS", "373220.KS", "207940.KS",
                "005380.KS", "006400.KS", "051910.KS", "035420.KS",
                "035720.KS", "068270.KS", "105560.KS", "055550.KS",
                "000270.KS", "012330.KS", "066570.KS", "003670.KS",
                "015760.KS", "009150.KS", "247540.KS", "086520.KS",
                "003550.KS", "028260.KS", "017670.KS", "030200.KS",
            ]
        else:
            tickers = [
                "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
                "JPM", "V", "WMT", "UNH", "JNJ", "HD", "PG", "MA",
                "XOM", "CVX", "KO", "PEP", "COST", "AVGO", "LLY",
                "AMD", "NFLX", "INTC", "BA", "CRM", "ORCL", "QCOM", "ADBE",
            ]

        return scan_and_score(tickers, market=market)
    except Exception:
        return []


# ─── Custom CSS ───
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #191F28;
        letter-spacing: -0.5px;
    }
    .sub-header {
        color: #8B95A1;
        font-size: 0.95rem;
    }
    .metric-up { color: #FF5247; font-weight: 700; }
    .metric-down { color: #3182F6; font-weight: 700; }
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #191F28;
        margin-bottom: 0.5rem;
    }
    .card-container {
        background: #FFFFFF;
        border: 1px solid #E5E8EB;
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    .tag {
        display: inline-block;
        background: #EEF2FF;
        color: #3182F6;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 2px;
    }
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E5E8EB;
        border-radius: 12px;
        padding: 12px 16px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ───
server_up = _is_server_up()

with st.sidebar:
    st.markdown("## 🌉 Taraga")
    st.markdown("**따라가** — Wall Street → 여의도")
    st.divider()

    # Server Status
    if server_up:
        st.success("🟢 서버 연결됨 (Full Mode)")
    else:
        st.warning("🟡 Standalone 모드 (yfinance 직접 호출)")
        st.caption("FastAPI 서버 연결 없이 시장 데이터만 표시됩니다.")

    st.divider()
    if server_up:
        page = st.radio(
            "페이지 선택",
            ["📊 글로벌 시장", "📋 브리핑", "🔥 테마", "💡 인사이트", "🎯 스마트 스코어", "📅 캘린더", "⭐ 관심종목", "📈 종목 상세", "⚙️ 시스템"],
            label_visibility="collapsed",
        )
    else:
        page = st.radio(
            "페이지 선택",
            ["📊 글로벌 시장", "🎯 스마트 스코어", "📅 캘린더", "📈 종목 상세"],
            label_visibility="collapsed",
        )
        st.caption("서버 연결 시 브리핑, 테마, 인사이트 등 이용 가능")

    st.divider()
    st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if st.button("🔄 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# ═══════════════════════════════════════════
# 📊 글로벌 시장
# ═══════════════════════════════════════════
if page == "📊 글로벌 시장":
    st.markdown('<p class="main-header">📊 글로벌 시장 현황</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">미국, 한국, 코인 시장을 한눈에 확인하세요.</p>', unsafe_allow_html=True)
    st.divider()

    # ─── Market Indices ───
    indices = {}
    if server_up:
        data = fetch_api("/market/us/snapshot")
        indices = data.get("data", {}) if data else {}
    if not indices:
        indices = fetch_indices_direct()

    if indices:
        # Market Weather + Fear & Greed (side by side)
        sp500 = indices.get("S&P 500", {})
        sp_change = sp500.get("regularMarketChangePercent", 0)

        if sp_change >= 1.0:
            emoji, title, msg = "🔥", "Fires (불장)", "뜨거운 불장입니다! 테마주에 주목하세요."
        elif sp_change >= 0.0:
            emoji, title, msg = "☀️", "Sunny (맑음)", "시장이 맑습니다. 완만한 상승세."
        elif sp_change >= -1.0:
            emoji, title, msg = "☁️", "Cloudy (흐림)", "다소 흐린 장세입니다. 관망이 필요해요."
        else:
            emoji, title, msg = "☔", "Rain (비)", "비가 내립니다. 리스크 관리가 필수입니다."

        weather_col, fg_col = st.columns([3, 1])
        with weather_col:
            st.info(f"{emoji} **{title}** — {msg}")
        with fg_col:
            # Fear & Greed mini gauge
            if server_up:
                briefing_fg = fetch_api("/briefing/today")
                fg_score = briefing_fg.get("fear_greed_score", 50) if briefing_fg else 50
            else:
                fg_score = 50
            if fg_score >= 75:
                fg_label = "극도의 탐욕"
            elif fg_score >= 55:
                fg_label = "탐욕"
            elif fg_score >= 45:
                fg_label = "중립"
            elif fg_score >= 25:
                fg_label = "공포"
            else:
                fg_label = "극도의 공포"
            fg_color = "#FF5247" if fg_score < 40 else "#00C073" if fg_score > 60 else "#8B95A1"
            st.markdown(f'<div style="text-align:center"><span style="font-size:1.8rem;font-weight:800;color:{fg_color}">{fg_score}</span><br/><span style="font-size:0.8rem;color:#8B95A1">F&G: {fg_label}</span></div>', unsafe_allow_html=True)

        # ═══ Market Selector — 모든 섹션을 연동 ═══
        market_options = {"🇺🇸 미국 시장": "US", "🇰🇷 한국 시장": "KR", "🪙 코인": "Coin"}
        selected_label = st.radio(
            "시장 선택",
            list(market_options.keys()),
            horizontal=True,
            label_visibility="collapsed",
        )
        selected_market = market_options[selected_label]

        # ── Helper: sparkline 그리기 ──
        def _draw_sparkline(history, change, key):
            if history and len(history) > 2:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=history, mode="lines",
                    line=dict(color=get_color(change), width=2),
                    fill="tozeroy",
                    fillcolor=f"rgba({'255,82,71' if change >= 0 else '49,130,246'}, 0.1)",
                ))
                fig.update_layout(
                    height=80, margin=dict(l=0, r=0, t=0, b=0),
                    xaxis=dict(visible=False), yaxis=dict(visible=False),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig, use_container_width=True, key=key)

        # ═══ 1. 지수 카드 ═══
        if selected_market == "US":
            idx_names = ["S&P 500", "Nasdaq", "Dow Jones"]
            prefix = ""
        elif selected_market == "KR":
            idx_names = ["KOSPI", "KOSDAQ"]
            prefix = ""
        else:
            idx_names = ["Bitcoin", "Ethereum"]
            prefix = "$"

        cols = st.columns(len(idx_names))
        for i, name in enumerate(idx_names):
            idx = indices.get(name, {})
            price = idx.get("regularMarketPrice", 0)
            change = idx.get("regularMarketChangePercent", 0)
            with cols[i]:
                st.metric(label=name, value=f"{prefix}{price:,.2f}", delta=f"{change:+.2f}%", delta_color="normal")
                _draw_sparkline(idx.get("history", []), change, f"idx_{selected_market}_{name}")

        st.caption("※ 데이터는 야후 파이낸스 기반으로 약 15분 지연될 수 있으며, 투자 참고용입니다.")

    else:
        st.warning("시장 데이터를 불러올 수 없습니다. 서버 연결을 확인하세요.")
        selected_market = "US"

    st.divider()

    # ═══ 섹터 히트맵 (US, KR) ═══
    if selected_market in ("US", "KR"):
        market_label = {"US": "🇺🇸 미국", "KR": "🇰🇷 한국"}[selected_market]
        etf_label = {"US": "S&P 500 섹터 ETF", "KR": "대표 종목 가중평균"}[selected_market]
        st.markdown(f'<p class="section-title">🗺️ {market_label} 섹터 히트맵</p>', unsafe_allow_html=True)

        sector_data, data_date = fetch_sector_data(market=selected_market)
        if sector_data:
            # 데이터 기준일 표시
            date_str = data_date if data_date else "알 수 없음"
            st.caption(f"📅 기준일: **{date_str}** | {etf_label} 기반 — 박스 크기 = 시가총액 비중, 색상 = 전일 대비 등락률")

            labels = []
            parents = []
            values = []
            colors = []
            text_labels = []

            for s in sector_data:
                labels.append(s["sector_kr"])
                parents.append("")
                values.append(s["weight"])
                colors.append(s["change_percent"])
                cp = s["change_percent"]
                sign = "+" if cp >= 0 else ""
                text_labels.append(f"{s['sector_kr']}<br>{sign}{cp:.2f}%<br><span style='font-size:10px'>{s['ticker']}</span>")

            fig = go.Figure(go.Treemap(
                labels=labels,
                parents=parents,
                values=values,
                marker=dict(
                    colors=colors,
                    colorscale=[
                        [0, "#3182F6"],
                        [0.35, "#93B5F6"],
                        [0.5, "#E5E8EB"],
                        [0.65, "#F5A0A0"],
                        [1, "#FF5247"],
                    ],
                    cmid=0,
                    colorbar=dict(
                        title="등락률(%)",
                        ticksuffix="%",
                        len=0.6,
                    ),
                ),
                text=text_labels,
                textinfo="text",
                textfont=dict(size=14),
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    f"기준일: {date_str}<br>"
                    "등락률: %{color:.2f}%<br>"
                    "비중: %{value}%<extra></extra>"
                ),
            ))
            fig.update_layout(
                height=420,
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True, key=f"sector_heatmap_{selected_market}")

            # 요약 테이블
            with st.expander("📊 섹터별 상세 데이터"):
                sorted_sectors = sorted(sector_data, key=lambda x: x["change_percent"], reverse=True)
                for s in sorted_sectors:
                    cp = s["change_percent"]
                    color = "#FF5247" if cp >= 0 else "#3182F6"
                    sign = "+" if cp >= 0 else ""
                    st.markdown(
                        f"<span style='color:{color};font-weight:700'>{sign}{cp:.2f}%</span> "
                        f"**{s['sector_kr']}** ({s['ticker']}) — 비중 {s['weight']}%, 가격 {s['price']:,.2f}",
                        unsafe_allow_html=True,
                    )
        else:
            st.info("섹터 데이터를 불러올 수 없습니다.")

        st.divider()

    # ═══ 2. 시장 급등락 (시장별) ═══
    movers_title_map = {
        "US": "📈 미국 시장 급등락",
        "KR": "📈 한국 시장 급등락",
        "Coin": "📈 코인 급등락",
    }
    st.markdown(f'<p class="section-title">{movers_title_map[selected_market]}</p>', unsafe_allow_html=True)

    # ── 필터 조건 ──
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        min_change = st.slider("최소 등락률 (%)", min_value=0.0, max_value=20.0, value=0.0, step=0.5, key="min_change_filter")
    with filter_col2:
        min_vol_change = st.slider("최소 거래량 변화율 (%)", min_value=0.0, max_value=500.0, value=0.0, step=10.0, key="min_vol_filter")
    with filter_col3:
        sort_by = st.selectbox("정렬 기준", ["등락률", "거래량 변화율"], key="sort_filter")

    # 데이터 가져오기 — 시장별 분기
    gainers_data = None
    losers_data = None

    if selected_market == "US":
        if server_up:
            gainers_data = fetch_api("/market/us/top-gainers?limit=10")
            losers_data = fetch_api("/market/us/top-losers?limit=10")
        if not gainers_data or not losers_data:
            g_list, l_list = fetch_movers_direct()
            if not gainers_data:
                gainers_data = {"data": g_list}
            if not losers_data:
                losers_data = {"data": l_list}
    elif selected_market == "KR":
        g_list, l_list = fetch_kr_movers_direct()
        gainers_data = {"data": g_list}
        losers_data = {"data": l_list}
    else:  # Coin
        g_list, l_list = fetch_coin_movers_direct()
        gainers_data = {"data": g_list}
        losers_data = {"data": l_list}

    # ── 필터 + 정렬 적용 함수 ──
    def _apply_filters(items, is_gainer=True):
        filtered = []
        for s in items:
            cp = abs(s.get("change_percent", 0))
            vc = abs(s.get("volume_change", 0))
            if cp >= min_change and vc >= min_vol_change:
                filtered.append(s)
        if sort_by == "거래량 변화율":
            filtered.sort(key=lambda x: abs(x.get("volume_change", 0)), reverse=True)
        else:
            filtered.sort(key=lambda x: abs(x.get("change_percent", 0)), reverse=True)
        return filtered

    def _format_volume(vol):
        if vol >= 1_000_000_000:
            return f"{vol / 1_000_000_000:.1f}B"
        elif vol >= 1_000_000:
            return f"{vol / 1_000_000:.1f}M"
        elif vol >= 1_000:
            return f"{vol / 1_000:.0f}K"
        return str(vol)

    g_tab, l_tab = st.tabs(["🚀 급등 종목", "📉 급락 종목"])

    with g_tab:
        gainers = gainers_data.get("data", []) if gainers_data else []
        gainers = _apply_filters(gainers, is_gainer=True)
        if gainers:
            # Header
            hc1, hc2, hc3, hc4 = st.columns([1, 3, 2, 2])
            with hc1:
                st.caption("#")
            with hc2:
                st.caption("종목")
            with hc3:
                st.caption("등락률")
            with hc4:
                st.caption("거래량 (변화율)")
            for i, stock in enumerate(gainers):
                col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                with col1:
                    st.markdown(f"**{i+1}**")
                with col2:
                    st.markdown(f"**{stock.get('ticker', '')}** — {stock.get('name', '')}")
                with col3:
                    cp = stock.get("change_percent", 0)
                    st.markdown(f'<span class="metric-up">+{cp:.2f}%</span>', unsafe_allow_html=True)
                with col4:
                    vol = stock.get("volume", 0)
                    vc = stock.get("volume_change", 0)
                    vc_color = "#FF5247" if vc > 50 else "#00C073" if vc > 0 else "#8B95A1"
                    vol_str = _format_volume(vol) if vol else "—"
                    vc_str = f"+{vc:.0f}%" if vc >= 0 else f"{vc:.0f}%"
                    st.markdown(f'{vol_str} <span style="color:{vc_color};font-weight:600">({vc_str})</span>', unsafe_allow_html=True)
        else:
            st.info("필터 조건에 맞는 급등 종목이 없습니다.")

    with l_tab:
        losers = losers_data.get("data", []) if losers_data else []
        losers = _apply_filters(losers, is_gainer=False)
        if losers:
            hc1, hc2, hc3, hc4 = st.columns([1, 3, 2, 2])
            with hc1:
                st.caption("#")
            with hc2:
                st.caption("종목")
            with hc3:
                st.caption("등락률")
            with hc4:
                st.caption("거래량 (변화율)")
            for i, stock in enumerate(losers):
                col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                with col1:
                    st.markdown(f"**{i+1}**")
                with col2:
                    st.markdown(f"**{stock.get('ticker', '')}** — {stock.get('name', '')}")
                with col3:
                    cp = stock.get("change_percent", 0)
                    st.markdown(f'<span class="metric-down">{cp:.2f}%</span>', unsafe_allow_html=True)
                with col4:
                    vol = stock.get("volume", 0)
                    vc = stock.get("volume_change", 0)
                    vc_color = "#FF5247" if vc > 50 else "#00C073" if vc > 0 else "#8B95A1"
                    vol_str = _format_volume(vol) if vol else "—"
                    vc_str = f"+{vc:.0f}%" if vc >= 0 else f"{vc:.0f}%"
                    st.markdown(f'{vol_str} <span style="color:{vc_color};font-weight:600">({vc_str})</span>', unsafe_allow_html=True)
        else:
            st.info("필터 조건에 맞는 급락 종목이 없습니다.")

    st.divider()

    # ═══ 3. 시장 참여자 비교 (US만 — KR/Coin은 실제 데이터 소스 없음) ═══
    if selected_market == "US":
        st.markdown('<p class="section-title">🍔 버거형 vs 🏦 월가</p>', unsafe_allow_html=True)

        if not server_up:
            st.info("🔌 백엔드 서버 연결 시 커뮤니티/기관 데이터를 확인할 수 있습니다.")
        else:
            r_col, i_col = st.columns(2)

            with r_col:
                st.markdown("#### 🍔 커뮤니티(WSB) 인기 종목")
                retail = fetch_api("/market/us/trends/retail?region=US")
                retail_items = retail.get("data", []) if retail else []
                if retail_items:
                    for item in retail_items[:5]:
                        cp = item.get("change_percent", 0)
                        color = get_color(cp)
                        st.markdown(
                            f"**{item.get('ticker', '')}** {item.get('name', '')} "
                            f"<span style='color:{color}; font-weight:bold'>{format_change(cp)}</span> "
                            f"— {item.get('mentions', '')}",
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("데이터 없음")

            with i_col:
                st.markdown("#### 🏦 월가 기관 강력 매수")
                inst = fetch_api("/market/us/trends/institutional?region=US")
                inst_items = inst.get("data", []) if inst else []
                if inst_items:
                    for item in inst_items[:5]:
                        cp = item.get("change_percent", 0)
                        color = get_color(cp)
                        st.markdown(
                            f"**{item.get('ticker', '')}** {item.get('name', '')} "
                            f"<span style='color:{color}; font-weight:bold'>{format_change(cp)}</span> "
                            f"— {item.get('rating', '')}",
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("데이터 없음")


# ═══════════════════════════════════════════
# 📋 브리핑
# ═══════════════════════════════════════════
elif page == "📋 브리핑":
    st.markdown('<p class="main-header">📋 오늘의 시장 브리핑</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI가 분석한 미국 시장 요약과 공포탐욕 지수를 확인하세요.</p>', unsafe_allow_html=True)
    st.divider()

    # Date selector
    date_col1, date_col2 = st.columns([3, 1])
    with date_col2:
        sel_date = st.date_input("날짜 선택", value=date.today(), max_value=date.today())

    if sel_date == date.today():
        briefing = fetch_api("/briefing/today")
    else:
        briefing = fetch_api(f"/briefing/{sel_date.isoformat()}")

    if briefing:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"### 📰 {briefing.get('title', '시장 브리핑')}")
            st.markdown(f"**날짜:** {briefing.get('date', 'N/A')}")
            st.markdown(f"**감성:** {briefing.get('sentiment', 'N/A')}")
            st.divider()

            summary = briefing.get("us_summary") or briefing.get("content", "")
            if summary:
                st.markdown(summary)
            else:
                st.info("브리핑 내용이 아직 생성되지 않았습니다.")

        with col2:
            # Fear & Greed Gauge
            fg_score = briefing.get("fear_greed_score", 50)
            st.markdown("#### 공포 & 탐욕 지수")

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=fg_score,
                title={"text": "Fear & Greed"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#3182F6"},
                    "steps": [
                        {"range": [0, 25], "color": "#FF5247"},
                        {"range": [25, 45], "color": "#FF9F43"},
                        {"range": [45, 55], "color": "#E5E8EB"},
                        {"range": [55, 75], "color": "#00C073"},
                        {"range": [75, 100], "color": "#00C073"},
                    ],
                },
            ))
            fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)

            if fg_score >= 75:
                label = "극도의 탐욕 😈"
            elif fg_score >= 55:
                label = "탐욕 😊"
            elif fg_score >= 45:
                label = "중립 😐"
            elif fg_score >= 25:
                label = "공포 😨"
            else:
                label = "극도의 공포 😱"
            st.markdown(f"**현재 상태: {label}** (점수: {fg_score})")
    else:
        st.warning("브리핑 데이터를 불러올 수 없습니다.")


# ═══════════════════════════════════════════
# 🔥 테마
# ═══════════════════════════════════════════
elif page == "🔥 테마":
    st.markdown('<p class="main-header">🔥 지금 뜨는 테마</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">미국 시장에 영향받는 한국 투자 테마를 확인하세요.</p>', unsafe_allow_html=True)
    st.divider()

    # ─── AI 추천 테마 (오늘의 추천) ───
    recs = fetch_api("/themes/recommendations")
    if recs and isinstance(recs, list) and recs:
        st.markdown("### 🤖 AI 오늘의 추천 테마")
        for rec in recs[:5]:
            impact = rec.get("impact_score", 0)
            stars = "⭐" * min(impact, 10)
            st.markdown(
                f'<div class="card-container">'
                f'<strong style="color:#7C5CFC">{rec.get("theme_name", "")}</strong> '
                f'<span style="color:#FF9F43">{stars}</span><br/>'
                f'🇺🇸 {rec.get("related_us_stock", "")} → '
                f'<span style="color:#8B95A1">{rec.get("reason", "")}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.divider()

    # ─── 전체 테마 목록 ───
    themes_data = fetch_api("/themes/list")

    if themes_data and isinstance(themes_data, list):
        st.markdown("### 📂 전체 테마")
        theme_colors = ["#3182F6", "#7C5CFC", "#00C073", "#FF9F43"]
        cols = st.columns(2)

        for i, theme in enumerate(themes_data):
            with cols[i % 2]:
                color = theme_colors[i % len(theme_colors)]
                keywords = theme.get("keywords", [])
                if isinstance(keywords, str):
                    try:
                        keywords = json.loads(keywords)
                    except (json.JSONDecodeError, TypeError):
                        keywords = [keywords]

                keyword_tags = " ".join([f'<span class="tag">{k}</span>' for k in keywords[:4]])

                st.markdown(f"""
                <div class="card-container">
                    <h4 style="color:{color}; margin:0">{theme.get('name', 'Unknown')}</h4>
                    <p style="color:#8B95A1; font-size:0.85rem; margin:4px 0">{theme.get('description', '')}</p>
                    <div>{keyword_tags}</div>
                </div>
                """, unsafe_allow_html=True)

        # Theme detail: select a theme
        st.divider()
        st.markdown("### 📋 테마별 한국 종목")
        selected = st.selectbox(
            "테마를 선택하세요",
            options=[(t["id"], t["name"]) for t in themes_data],
            format_func=lambda x: x[1],
        )

        if selected:
            stocks_data = fetch_api(f"/themes/{selected[0]}/stocks")
            if stocks_data and isinstance(stocks_data, list) and stocks_data:
                for stock in stocks_data:
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    with col1:
                        st.markdown(f"**{stock.get('name', '')}** ({stock.get('ticker', '')})")
                    with col2:
                        price = stock.get("current_price")
                        st.markdown(f"₩{price:,.0f}" if price else "—")
                    with col3:
                        cp = stock.get("change_percent")
                        if cp is not None:
                            color = get_color(cp)
                            st.markdown(f'<span style="color:{color}; font-weight:bold">{format_change(cp)}</span>', unsafe_allow_html=True)
                        else:
                            st.markdown("—")
                    with col4:
                        ticker = stock.get("ticker", "")
                        name = stock.get("name", "")
                        if ticker and server_up:
                            if st.button("⭐", key=f"wl_theme_{ticker}"):
                                add_to_watchlist(ticker, name)
            else:
                st.info("이 테마에 해당하는 종목이 없습니다.")
    else:
        st.warning("테마 데이터를 불러올 수 없습니다.")


# ═══════════════════════════════════════════
# 💡 인사이트
# ═══════════════════════════════════════════
elif page == "💡 인사이트":
    st.markdown('<p class="main-header">💡 인사이트</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">미국발 뉴스가 한국 시장에 미치는 영향을 분석합니다.</p>', unsafe_allow_html=True)
    st.divider()

    # Bridge News
    st.markdown("### 🌉 뉴스 브릿지 (US → KR)")
    news_data = fetch_api("/insight/news-bridge")

    if news_data:
        news_list = news_data.get("news", [])
        if news_list:
            for news in news_list:
                headline = news.get('us_headline', news.get('headline', 'No title'))
                source = news.get('us_source', '')
                source_tag = f"[{source}] " if source else ""
                with st.expander(f"📰 {source_tag}{headline}", expanded=False):
                    kr_impact = news.get('kr_impact', news.get('impact', 'N/A'))
                    st.markdown(f"**🇰🇷 한국 영향:** {kr_impact}")

                    related = news.get("related_stocks", [])
                    if related:
                        st.markdown("**관련 한국 종목:**")
                        for stock in related:
                            if isinstance(stock, dict):
                                name = stock.get('name', '')
                                ticker = stock.get('ticker', '')
                                change = stock.get('change', stock.get('reason', ''))
                                st.markdown(f"- 🇰🇷 **{name}** ({ticker}): {change}")
                                if server_up and ticker and ticker != "N/A":
                                    if st.button(f"⭐ {name} 관심종목 추가", key=f"wl_news_{ticker}"):
                                        add_to_watchlist(ticker, name)
                            else:
                                st.markdown(f"- 🇰🇷 {stock}")
        else:
            st.info("뉴스 데이터가 없습니다.")
    else:
        st.warning("인사이트 데이터를 불러올 수 없습니다.")

    st.divider()

    # Value Chain
    st.markdown("### 🔗 밸류체인 맵")
    themes_data = fetch_api("/themes/list")
    if themes_data and isinstance(themes_data, list) and themes_data:
        selected_theme = st.selectbox(
            "테마 선택",
            options=[(t["id"], t["name"]) for t in themes_data],
            format_func=lambda x: x[1],
            key="vc_theme",
        )
        if selected_theme:
            vc_data = fetch_api(f"/insight/value-chain?theme_id={selected_theme[0]}")
            if vc_data:
                us_drivers = vc_data.get("us_drivers", {})
                if us_drivers:
                    for driver, connections in us_drivers.items():
                        st.markdown(f"#### 🇺🇸 {driver}")
                        for conn in connections:
                            if isinstance(conn, dict):
                                st.markdown(f"  → 🇰🇷 **{conn.get('kr_stock', '')}** — {conn.get('relation', '')}: {conn.get('description', '')}")
                            else:
                                st.markdown(f"  → 🇰🇷 {conn}")
                else:
                    st.info("밸류체인 데이터가 없습니다.")
            else:
                st.info("밸류체인 데이터를 불러올 수 없습니다.")

    st.divider()

    # Personal Matches
    st.markdown("### 🎯 나만의 종목 매칭")
    st.caption("관심종목과 현재 테마의 상관관계를 분석합니다.")
    matches_data = fetch_api(f"/insight/personal-matches?user_uuid={st.session_state.user_uuid}")
    if matches_data and isinstance(matches_data, list) and matches_data:
        for match in matches_data:
            ticker = match.get("ticker", "")
            name = match.get("stock_name", match.get("name", ticker))
            score = match.get("correlation_score", match.get("score", 0))
            reason = match.get("reason", match.get("theme_connections", ""))
            score_color = "#FF5247" if score >= 7 else "#FF9F43" if score >= 4 else "#3182F6"
            st.markdown(
                f'<div class="card-container">'
                f'<span style="font-size:1.5rem;font-weight:800;color:{score_color}">{score}</span> '
                f'<strong>{name}</strong> ({ticker})<br/>'
                f'<span style="color:#8B95A1;font-size:0.85rem">{reason}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
    elif matches_data and isinstance(matches_data, dict) and matches_data.get("watchlist"):
        # Alternative response format
        for item in matches_data["watchlist"]:
            st.markdown(f"- **{item.get('stock_name', '')}** ({item.get('ticker', '')}) — 상관 점수: {item.get('correlation_score', 'N/A')}")
    else:
        st.info("관심종목을 등록하면 테마와의 상관관계를 분석해 드립니다. ⭐ 관심종목 페이지에서 추가해 주세요.")


# ═══════════════════════════════════════════
# 📅 캘린더
# ═══════════════════════════════════════════
elif page == "📅 캘린더":
    st.markdown('<p class="main-header">📅 경제 캘린더</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">주요 경제 지표 발표 일정을 확인하세요.</p>', unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        sel_year = st.selectbox("연도", [2025, 2026, 2027], index=1)
    with col2:
        sel_month = st.selectbox("월", list(range(1, 13)), index=datetime.now().month - 1)

    cal_data = fetch_api(f"/calendar/events?year={sel_year}&month={sel_month}")

    # Standalone fallback: fetch directly if backend is down
    if not cal_data and not server_up:
        cal_data = _fetch_calendar_direct(sel_year, sel_month)

    if cal_data:
        events = cal_data.get("data", []) if isinstance(cal_data, dict) else cal_data if isinstance(cal_data, list) else []
        if events:
            # Group by date
            by_date = {}
            for ev in events:
                d = ev.get("date", "Unknown")
                by_date.setdefault(d, []).append(ev)

            for event_date, day_events in sorted(by_date.items()):
                st.markdown(f"### 📆 {event_date}")
                for ev in day_events:
                    impact = ev.get("impact", 0)
                    impact_stars = "⭐" * min(impact, 5) if isinstance(impact, int) else str(impact)
                    country = ev.get("country", "")
                    flag = {"US": "🇺🇸", "KR": "🇰🇷", "JP": "🇯🇵", "EU": "🇪🇺", "CN": "🇨🇳"}.get(country, "🌐")
                    title = ev.get("title", "N/A")
                    time_str = ev.get("time", "")
                    time_tag = f" ⏰ {time_str}" if time_str else ""

                    with st.expander(f"{flag} {impact_stars} **{title}**{time_tag}"):
                        detail_cols = st.columns(3)
                        with detail_cols[0]:
                            st.metric("이전", ev.get("previous", "—"))
                        with detail_cols[1]:
                            st.metric("예상", ev.get("forecast", "—"))
                        with detail_cols[2]:
                            actual_val = ev.get("actual", "—")
                            st.metric("실제", actual_val)
                        desc = ev.get("description", "")
                        if desc:
                            st.markdown(f"📝 {desc}")
                        category = ev.get("category", ev.get("type", ""))
                        if category:
                            st.caption(f"분류: {category}")
        else:
            st.info(f"{sel_year}년 {sel_month}월에 등록된 이벤트가 없습니다.")
    else:
        st.warning("캘린더 데이터를 불러올 수 없습니다.")


# ═══════════════════════════════════════════
# ⚙️ 시스템
# ═══════════════════════════════════════════
elif page == "⚙️ 시스템":
    st.markdown('<p class="main-header">⚙️ 시스템 상태</p>', unsafe_allow_html=True)
    st.divider()

    # App Mode
    mode_data = fetch_api("/system/mode")
    if mode_data:
        mode = mode_data.get("data", {}) if isinstance(mode_data, dict) else {}
        col1, col2 = st.columns(2)
        with col1:
            st.metric("현재 모드", mode.get("mode", "N/A"))
        with col2:
            st.metric("시간대", mode.get("timezone", "N/A"))

    st.divider()

    # Service Status
    svc_data = fetch_api("/market/service-status")
    if svc_data:
        svc = svc_data.get("data", {}) if isinstance(svc_data, dict) else {}
        st.markdown("### 서비스 구성")
        for k, v in svc.items():
            st.markdown(f"- **{k}:** `{v}`")

    st.divider()

    # API Endpoints Status
    st.markdown("### API 엔드포인트 상태")
    endpoints = [
        ("/market/us/snapshot", "시장 지수"),
        ("/market/us/top-gainers?limit=3", "급등 종목"),
        ("/market/us/top-losers?limit=3", "급락 종목"),
        ("/themes/list", "테마 목록"),
        ("/briefing/today", "오늘 브리핑"),
        ("/calendar/events?year=2026&month=3", "캘린더"),
        ("/insight/news-bridge", "뉴스 브릿지"),
        ("/system/mode", "시스템 모드"),
    ]

    for ep, name in endpoints:
        try:
            resp = requests.get(f"{API_BASE}{ep}", timeout=5)
            if resp.status_code == 200:
                st.markdown(f"✅ **{name}** (`{ep}`) — 정상")
            else:
                st.markdown(f"⚠️ **{name}** (`{ep}`) — HTTP {resp.status_code}")
        except Exception:
            st.markdown(f"❌ **{name}** (`{ep}`) — 연결 실패")

    st.divider()
    st.markdown("### 종목 검색")
    query = st.text_input("종목명 또는 티커를 입력하세요")
    if query:
        results = fetch_api(f"/market/search?query={query}")
        if results and isinstance(results, list):
            for r in results:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"- **{r.get('name', '')}** ({r.get('ticker', '')}) — {r.get('sector', '')}")
                with col2:
                    ticker = r.get("ticker", "")
                    name = r.get("name", "")
                    if ticker:
                        if st.button("⭐ 추가", key=f"wl_search_{ticker}"):
                            add_to_watchlist(ticker, name)
        else:
            st.info("검색 결과가 없습니다.")


# ═══════════════════════════════════════════
# ⭐ 관심종목
# ═══════════════════════════════════════════
elif page == "⭐ 관심종목":
    st.markdown('<p class="main-header">⭐ 관심종목 관리</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">나만의 관심 종목을 관리하고 테마 연동 분석을 받으세요.</p>', unsafe_allow_html=True)
    st.divider()

    # 종목 추가 섹션
    st.markdown("### ➕ 종목 추가")
    search_query = st.text_input("종목명 또는 티커 검색", key="wl_search")
    if search_query:
        search_results = fetch_api(f"/market/search?query={search_query}")
        if search_results and isinstance(search_results, list):
            for r in search_results[:10]:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{r.get('name', '')}** ({r.get('ticker', '')}) — {r.get('sector', '')}")
                with col2:
                    if st.button("⭐ 추가", key=f"wl_add_{r.get('ticker', '')}"):
                        add_to_watchlist(r.get("ticker", ""), r.get("name", ""))
        else:
            st.info("검색 결과가 없습니다.")

    st.divider()

    # 현재 관심종목 목록
    st.markdown("### 📋 내 관심종목")
    watchlist = fetch_api(f"/watchlist/{st.session_state.user_uuid}")
    if watchlist and isinstance(watchlist, list) and watchlist:
        for item in watchlist:
            col1, col2, col3 = st.columns([4, 2, 1])
            with col1:
                st.markdown(f"**{item.get('stock_name', '')}** ({item.get('ticker', '')})")
            with col2:
                alert = "🔔 알림 ON" if item.get("alert_enabled") else "🔕 알림 OFF"
                st.caption(alert)
            with col3:
                if st.button("🗑️", key=f"wl_del_{item.get('id', '')}"):
                    result = delete_api(f"/watchlist/{item['id']}")
                    if result:
                        st.toast(f"🗑️ {item.get('stock_name', '')} 삭제됨")
                        st.cache_data.clear()
                        st.rerun()
    elif watchlist is not None:
        st.info("관심종목이 없습니다. 위에서 종목을 검색하여 추가해 보세요!")
    else:
        st.warning("관심종목 데이터를 불러올 수 없습니다. 서버 연결을 확인하세요.")


# ═══════════════════════════════════════════
# 📈 종목 상세
# ═══════════════════════════════════════════
elif page == "📈 종목 상세":
    st.markdown('<p class="main-header">📈 종목 상세 정보</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">개별 종목의 차트, 통계, 기업 정보를 확인하세요.</p>', unsafe_allow_html=True)
    st.divider()

    # 종목 검색
    ticker_input = st.text_input("티커 또는 종목명 입력 (예: AAPL, 005930, 삼성전자)")

    # 빠른 접근: 관심종목에서 선택
    if server_up:
        watchlist = fetch_api(f"/watchlist/{st.session_state.user_uuid}")
        if watchlist and isinstance(watchlist, list) and watchlist:
            wl_options = ["직접 입력"] + [f"{w['stock_name']} ({w['ticker']})" for w in watchlist]
            wl_selected = st.selectbox("또는 관심종목에서 선택", wl_options)
            if wl_selected != "직접 입력":
                # Parse ticker from selection
                for w in watchlist:
                    if f"{w['stock_name']} ({w['ticker']})" == wl_selected:
                        ticker_input = w["ticker"]
                        break

    if ticker_input:
        # Try KR stock search first if it looks Korean
        actual_ticker = ticker_input.strip()

        # If it's a name, search for ticker
        if not actual_ticker.replace(".", "").replace("-", "").isalnum() or any('\uac00' <= c <= '\ud7a3' for c in actual_ticker):
            search_result = fetch_api(f"/market/search?query={actual_ticker}")
            if search_result and isinstance(search_result, list) and search_result:
                actual_ticker = search_result[0]["ticker"]
                st.caption(f"→ {search_result[0]['name']} ({actual_ticker})")

        # For KR stocks (6-digit number), add .KS suffix for yfinance
        yf_ticker = actual_ticker
        if actual_ticker.isdigit() and len(actual_ticker) == 6:
            yf_ticker = f"{actual_ticker}.KS"

        # Fetch from backend
        stock_data = None
        if server_up:
            stock_data_resp = fetch_api(f"/market/stock/{yf_ticker}")
            if stock_data_resp and isinstance(stock_data_resp, dict):
                stock_data = stock_data_resp.get("data", stock_data_resp)

        # Fallback: direct yfinance
        if not stock_data:
            try:
                import yfinance as yf
                stock = yf.Ticker(yf_ticker)
                info = stock.info
                hist = stock.history(period="1mo")
                current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
                prev_close = info.get("previousClose", 0)
                change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
                stock_data = {
                    "ticker": actual_ticker,
                    "name": info.get("longName", info.get("shortName", actual_ticker)),
                    "price": current_price,
                    "change_percent": round(change_pct, 2),
                    "sector": info.get("sector", "N/A"),
                    "volume": info.get("volume", 0),
                    "market_cap": info.get("marketCap", 0),
                    "pe_ratio": info.get("trailingPE"),
                    "currency": info.get("currency", "KRW" if actual_ticker.isdigit() else "USD"),
                    "description": info.get("longBusinessSummary", ""),
                    "history": [{"date": d.strftime("%Y-%m-%d"), "close": float(row["Close"])} for d, row in hist.iterrows()],
                }
            except Exception:
                stock_data = None

        if stock_data:
            # Header
            name = stock_data.get("name", actual_ticker)
            price = stock_data.get("price", 0)
            change = stock_data.get("change_percent", 0)
            currency = stock_data.get("currency", "USD")
            currency_symbol = "₩" if currency in ("KRW", "krw") else "$"

            h_col1, h_col2, h_col3 = st.columns([3, 2, 1])
            with h_col1:
                st.markdown(f"## {name}")
                st.caption(f"{actual_ticker} · {stock_data.get('sector', 'N/A')}")
            with h_col2:
                st.metric(
                    label="현재가",
                    value=f"{currency_symbol}{price:,.2f}" if currency != "KRW" else f"₩{price:,.0f}",
                    delta=f"{change:+.2f}%",
                )
            with h_col3:
                if server_up:
                    if st.button("⭐ 관심종목 추가", key="wl_detail"):
                        add_to_watchlist(actual_ticker, name)

            # Chart
            history = stock_data.get("history", [])
            if history:
                if isinstance(history[0], dict):
                    dates = [h.get("date", "") for h in history]
                    closes = [h.get("close", 0) for h in history]
                else:
                    dates = list(range(len(history)))
                    closes = history

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates, y=closes, mode="lines",
                    line=dict(color=get_color(change), width=2),
                    fill="tozeroy",
                    fillcolor=f"rgba({'255,82,71' if change >= 0 else '49,130,246'}, 0.08)",
                ))
                fig.update_layout(
                    height=350,
                    margin=dict(l=0, r=0, t=10, b=30),
                    xaxis=dict(title="", showgrid=False),
                    yaxis=dict(title=f"가격 ({currency})", showgrid=True, gridcolor="#E5E8EB"),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig, use_container_width=True)

            # Stats
            st.divider()
            st.markdown("### 📊 주요 지표")
            s1, s2, s3, s4 = st.columns(4)
            with s1:
                vol = stock_data.get("volume", 0)
                st.metric("거래량", f"{vol:,.0f}" if vol else "N/A")
            with s2:
                mcap = stock_data.get("market_cap", 0)
                if mcap and mcap > 0:
                    if mcap >= 1e12:
                        st.metric("시가총액", f"{currency_symbol}{mcap/1e12:.1f}T")
                    elif mcap >= 1e8:
                        st.metric("시가총액", f"{currency_symbol}{mcap/1e8:.0f}억")
                    else:
                        st.metric("시가총액", f"{currency_symbol}{mcap:,.0f}")
                else:
                    st.metric("시가총액", "N/A")
            with s3:
                pe = stock_data.get("pe_ratio")
                st.metric("P/E", f"{pe:.1f}" if pe else "N/A")
            with s4:
                st.metric("섹터", stock_data.get("sector", "N/A"))

            # Description
            desc = stock_data.get("description", "")
            if desc:
                st.divider()
                st.markdown("### 🏢 기업 개요")
                st.markdown(desc[:500] + ("..." if len(desc) > 500 else ""))
        else:
            st.warning(f"'{ticker_input}' 종목 데이터를 찾을 수 없습니다.")


# ═══════════════════════════════════════════
# 🎯 스마트 스코어
# ═══════════════════════════════════════════
elif page == "🎯 스마트 스코어":
    st.markdown('<p class="main-header">🎯 스마트 스코어</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">다중 팩터 분석으로 수급 이상 종목을 찾아냅니다. (기관 매집 40% + 모멘텀 30% + 거래량 폭증 30%)</p>', unsafe_allow_html=True)
    st.divider()

    # 시장 선택
    ss_market_label = st.radio(
        "분석 시장",
        ["🇰🇷 한국", "🇺🇸 미국"],
        horizontal=True,
        label_visibility="collapsed",
        key="ss_market",
    )
    ss_market = "KR" if "한국" in ss_market_label else "US"

    with st.spinner("종목 스캔 중... (20~30개 종목 분석)"):
        scored = fetch_smart_scores(market=ss_market)

    if not scored:
        st.warning("스코어 데이터를 불러올 수 없습니다. 잠시 후 다시 시도해 주세요.")
    else:
        # ── Top 3 카드 ──
        top3 = scored[:3]
        st.markdown(f'<p class="section-title">🏆 Top 3 종목</p>', unsafe_allow_html=True)

        cols = st.columns(3)
        medal = ["🥇", "🥈", "🥉"]
        for i, s in enumerate(top3):
            with cols[i]:
                sc = s["score"]
                sc_color = "#FF5247" if sc >= 70 else "#FF9F43" if sc >= 50 else "#8B95A1"
                chg = s["change_percent"]
                chg_color = "#FF5247" if chg >= 0 else "#3182F6"
                chg_str = f"+{chg:.2f}%" if chg >= 0 else f"{chg:.2f}%"
                anomaly_badge = '  <span style="background:#7C5CFC;color:white;padding:2px 8px;border-radius:8px;font-size:0.75rem">⚡ Anomaly</span>' if s["is_anomaly"] else ""

                st.markdown(f"""
                <div style="background:#FFFFFF;border:2px solid {sc_color};border-radius:16px;padding:1.2rem;text-align:center">
                    <div style="font-size:1.8rem">{medal[i]}</div>
                    <div style="font-size:1.1rem;font-weight:700;color:#191F28;margin:4px 0">{s['name']}</div>
                    <div style="font-size:0.85rem;color:#8B95A1">{s['ticker']}</div>
                    <div style="font-size:2.2rem;font-weight:800;color:{sc_color};margin:8px 0">{sc}</div>
                    <div style="font-size:0.8rem;color:#8B95A1">Smart Score</div>
                    <div style="margin-top:8px">
                        <span style="color:{chg_color};font-weight:700;font-size:1rem">{chg_str}</span>
                    </div>
                    <div style="margin-top:6px;font-size:0.8rem;color:#8B95A1">
                        기관매집 {s['inst_score']:.0f} · 모멘텀 {s['momentum_score']:.0f} · 거래량 {s['volume_score']:.0f}
                    </div>
                    {f'<div style="margin-top:6px">{anomaly_badge}</div>' if anomaly_badge else ''}
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # ── 수급 추이 차트 (Top 3) ──
        st.markdown(f'<p class="section-title">📊 Top 3 수급 추이</p>', unsafe_allow_html=True)

        for s in top3:
            with st.expander(f"{s['name']} ({s['ticker']}) — Score: {s['score']}", expanded=True):
                chart_col1, chart_col2 = st.columns(2)

                dates = s.get("dates", [])
                vol_hist = s.get("volume_history", [])
                price_hist = s.get("price_history", [])

                with chart_col1:
                    # 거래량 차트
                    if vol_hist and dates:
                        fig_vol = go.Figure()
                        colors = ["#3182F6" if i < len(vol_hist) - 3 else "#FF5247" for i in range(len(vol_hist))]
                        fig_vol.add_trace(go.Bar(
                            x=dates[-len(vol_hist):],
                            y=vol_hist,
                            marker_color=colors,
                            name="거래량",
                        ))
                        # 20일 평균선
                        if len(vol_hist) >= 5:
                            import numpy as np
                            avg_line = [np.mean(vol_hist)] * len(vol_hist)
                            fig_vol.add_trace(go.Scatter(
                                x=dates[-len(vol_hist):],
                                y=avg_line,
                                mode="lines",
                                line=dict(color="#FF9F43", width=2, dash="dash"),
                                name="평균 거래량",
                            ))
                        fig_vol.update_layout(
                            title=dict(text="거래량 추이", font=dict(size=14)),
                            height=280,
                            margin=dict(l=10, r=10, t=40, b=10),
                            showlegend=True,
                            legend=dict(orientation="h", y=-0.15),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                        )
                        fig_vol.update_yaxes(gridcolor="#E5E8EB")
                        st.plotly_chart(fig_vol, use_container_width=True, key=f"vol_{s['ticker']}")

                with chart_col2:
                    # 가격 + VWAP + MA5 차트
                    if price_hist and dates:
                        fig_price = go.Figure()
                        fig_price.add_trace(go.Scatter(
                            x=dates[-len(price_hist):],
                            y=price_hist,
                            mode="lines+markers",
                            line=dict(color="#191F28", width=2),
                            marker=dict(size=4),
                            name="종가",
                        ))
                        if s.get("vwap"):
                            fig_price.add_hline(
                                y=s["vwap"], line_dash="dash",
                                line_color="#7C5CFC", line_width=1.5,
                                annotation_text=f"VWAP {s['vwap']}",
                                annotation_position="top right",
                            )
                        if s.get("ma5"):
                            fig_price.add_hline(
                                y=s["ma5"], line_dash="dot",
                                line_color="#00C073", line_width=1.5,
                                annotation_text=f"MA5 {s['ma5']}",
                                annotation_position="bottom right",
                            )
                        fig_price.update_layout(
                            title=dict(text="가격 · VWAP · MA5", font=dict(size=14)),
                            height=280,
                            margin=dict(l=10, r=10, t=40, b=10),
                            showlegend=True,
                            legend=dict(orientation="h", y=-0.15),
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                        )
                        fig_price.update_yaxes(gridcolor="#E5E8EB")
                        st.plotly_chart(fig_price, use_container_width=True, key=f"price_{s['ticker']}")

                # 이상 징후 설명
                if s["is_anomaly"]:
                    st.warning(f"⚡ **Anomaly 감지** — {s['anomaly_reason']}")

        st.divider()

        # ── Anomaly 종목 섹션 ──
        anomalies = [s for s in scored if s["is_anomaly"]]
        if anomalies:
            st.markdown(f'<p class="section-title">⚡ 소외주 반등 감지 (Anomaly)</p>', unsafe_allow_html=True)
            st.caption("최근 10거래일간 거래량이 극히 낮다가 갑자기 수급이 유입된 종목입니다.")
            for a in anomalies:
                ac1, ac2, ac3, ac4 = st.columns([3, 2, 2, 3])
                with ac1:
                    st.markdown(f"**{a['name']}** ({a['ticker']})")
                with ac2:
                    chg = a['change_percent']
                    color = "#FF5247" if chg >= 0 else "#3182F6"
                    st.markdown(f'<span style="color:{color};font-weight:700">{("+" if chg >= 0 else "")}{chg:.2f}%</span>', unsafe_allow_html=True)
                with ac3:
                    st.markdown(f"Score: **{a['score']}**")
                with ac4:
                    st.caption(a["anomaly_reason"])
            st.divider()

        # ── 전체 순위 테이블 ──
        st.markdown(f'<p class="section-title">📋 전체 종목 스코어 순위</p>', unsafe_allow_html=True)
        for idx, s in enumerate(scored):
            rc1, rc2, rc3, rc4, rc5, rc6 = st.columns([0.5, 2.5, 1.5, 1.5, 1.5, 1.5])
            with rc1:
                st.markdown(f"**{idx+1}**")
            with rc2:
                anomaly_mark = " ⚡" if s["is_anomaly"] else ""
                st.markdown(f"**{s['name']}**{anomaly_mark}")
            with rc3:
                sc = s['score']
                sc_color = "#FF5247" if sc >= 70 else "#FF9F43" if sc >= 50 else "#8B95A1"
                st.markdown(f'<span style="color:{sc_color};font-weight:800;font-size:1.1rem">{sc}</span>', unsafe_allow_html=True)
            with rc4:
                st.caption(f"기관 {s['inst_score']:.0f}")
            with rc5:
                st.caption(f"모멘텀 {s['momentum_score']:.0f}")
            with rc6:
                st.caption(f"거래량 {s['volume_score']:.0f}")

        st.divider()
        st.caption("""
        **스코어링 기준 안내**
        - 🏦 **기관 매집 (40%)**: 최근 3일간 양봉 + 거래량 증가 동반 시 기관/외인 매집으로 추정
        - 📈 **모멘텀 (30%)**: VWAP(거래량 가중 평균가) 돌파 여부 + 5일 이동평균선 이격도
        - 📊 **거래량 폭증 (30%)**: 20일 평균 대비 당일 거래량 비율
        - ⚡ **Anomaly**: 10거래일 중 전반부 소외 → 후반부 수급 급증 패턴 감지 시 보너스 +10점
        """)
