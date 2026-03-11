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
                results.append({"ticker": t, "name": t, "price": cur, "change_percent": round(cp, 2)})
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
                results.append({"ticker": t.replace(".KS", ""), "name": name, "price": cur, "change_percent": round(cp, 2)})
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
                results.append({"ticker": t.replace("-USD", ""), "name": name, "price": cur, "change_percent": round(cp, 2)})
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
            ["📊 글로벌 시장", "📋 브리핑", "🔥 테마", "💡 인사이트", "📅 캘린더", "⭐ 관심종목", "📈 종목 상세", "⚙️ 시스템"],
            label_visibility="collapsed",
        )
    else:
        page = st.radio(
            "페이지 선택",
            ["📊 글로벌 시장", "📅 캘린더", "📈 종목 상세"],
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

    # ═══ 2. 시장 급등락 (시장별) ═══
    movers_title_map = {
        "US": "📈 미국 시장 급등락",
        "KR": "📈 한국 시장 급등락",
        "Coin": "📈 코인 급등락",
    }
    st.markdown(f'<p class="section-title">{movers_title_map[selected_market]}</p>', unsafe_allow_html=True)

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

    g_tab, l_tab = st.tabs(["🚀 급등 종목", "📉 급락 종목"])

    with g_tab:
        gainers = gainers_data.get("data", []) if gainers_data else []
        if gainers:
            for i, stock in enumerate(gainers):
                col1, col2, col3 = st.columns([1, 4, 2])
                with col1:
                    st.markdown(f"**{i+1}**")
                with col2:
                    st.markdown(f"**{stock.get('ticker', '')}** — {stock.get('name', '')}")
                with col3:
                    cp = stock.get("change_percent", 0)
                    st.markdown(f'<span class="metric-up">+{cp:.2f}%</span>', unsafe_allow_html=True)
        else:
            st.info("급등 종목 데이터가 없습니다.")

    with l_tab:
        losers = losers_data.get("data", []) if losers_data else []
        if losers:
            for i, stock in enumerate(losers):
                col1, col2, col3 = st.columns([1, 4, 2])
                with col1:
                    st.markdown(f"**{i+1}**")
                with col2:
                    st.markdown(f"**{stock.get('ticker', '')}** — {stock.get('name', '')}")
                with col3:
                    cp = stock.get("change_percent", 0)
                    st.markdown(f'<span class="metric-down">{cp:.2f}%</span>', unsafe_allow_html=True)
        else:
            st.info("급락 종목 데이터가 없습니다.")

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
