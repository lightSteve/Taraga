# 🗺 Project Plan: Taraga (따라가) - Advanced Version

## 🎯 Goal

Build "Taraga," a personalized investment strategy app that connects US market moves (The Cause) to specific KR stock recommendations (The Effect).
**Core Value:** "From Wall Street to My Portfolio" - Go beyond news summary to personalized action items.

## 📦 Phasing Strategy

### Phase 1: Foundation & Data Ingestion

- **Objective:** Setup Python env, DB, and fetch raw market data (US/KR).
- **Focus:** Polygon.io (US), KIS (KR), NewsAPI.

### Phase 2: The "Bridge" & Personalization Engine (Core)

- **Objective:** Build the logic that maps US Themes -> KR Stocks -> **User's Watchlist**.
- **Key Feature:** - **Correlation Engine:** Maps US headlines to KR themes.
  - **Value Chain Logic:** Defines the structure (e.g., Nvidia -> HBM -> SK Hynix).
  - **Personalization:** Filters recommendations based on user's registered stocks.

### Phase 3: API Layer (FastAPI)

- **Objective:** Expose data with user-specific context.
- **Focus:** Endpoints for `My Portfolio Matches`, `Value Chain Detail`, and `App Mode Status`.

### Phase 4: Frontend Expansion (Multi-Tab Structure)

- **Objective:** Expand the single-page MVP into a robust 4-tab application modeled after "Ocean's SAVE" but optimized for US-KR insights.
- **Navigation Structure (BottomNavigationBar):**
  1. **Home (Briefing):** Dashboard for Market Weather, Indices, and Top Themes.
  2. **Insight (The Bridge):** A news feed connecting US events to KR stocks (replacing static PDF reports).
  3. **Calendar (Schedule):** Economic calendar with "KR Market Impact Score".
  4. **My Page (Profile):** Watchlist management and notification settings.

- **Key UI Tasks:**
  - Implement `Scaffold` with `BottomNavigationBar` to switch between screens.
  - **Insight Tab:** Create a "Bridge Card" widget (Left: US News / Right: KR Effect).
  - **Calendar Tab:** Implement a monthly calendar view (using `table_calendar` package) and daily event list.
  - **Styling:** Adopt a clean, card-based design like "SAVE" with distinct tags and elevation.



### Phase 5: Automation & Deployment

- **Objective:** Schedule Cron jobs (06:00 AM analysis) and deploy.

---

## 📅 User Flows (Updated)

1. **The Hook:** User receives a push: *"Your watchlist item 'SK Hynix' is expected to rise today due to Micron's earnings."*
2. **The Insight:** User opens app -> Sees "Market Weather: Sunny" -> Clicks "Insight Tab".
3. **The Depth:** User taps "Semiconductor Theme" -> Sees **Value Chain Map** (US Driver -> KR Material/Equipment).
4. **The Action:** User adds recommended stocks to their trading plan.

### 🎨 UI Upgrade Plan

1. **Widget - Market Mood (Briefing):**
    - 단순 텍스트 대신 `SfRadialGauge` (또는 유사 라이브러리)를 사용해 '공포/탐욕 지수'를 시각적으로 보여줘.
    - S&P500, 나스닥 지수 옆에 `flutter_sparkline`을 사용해 작은 추세선 그래프를 추가해.

2. **Widget - Theme Heatmap:**
    - 'Hot Themes' 리스트를 `ListView` 대신 `GridView` (2 columns)로 변경해.
    - 각 카드의 배경색 투명도를 등락률(impact_score)에 비례하게 설정해서 히트맵처럼 보이게 만들어. (예: 강한 테마는 진한 붉은색)

3. **Widget - Causality Card (Watchlist):**
    - 'Your Watchlist Matches' 카드를 더 컴팩트하게 줄여.
    - 좌측엔 [미국 원인 종목 로고/티커], 우측엔 [한국 추천 종목]을 배치하고 가운데 화살표 아이콘(`arrow_forward`)을 넣어 인과관계를 강조해.

4. **Density:**
    - 전체적으로 Padding을 줄이고, 폰트 사이즈 위계(Hierarchy)를 확실히 줘 (타이틀은 크고 진하게, 본문은 작게).
    - 상승(Red)/하락(Blue) 색상을 텍스트와 아이콘에 적극적으로 적용해.

이 내용으로 `todo.md`를 업데이트하고, 바로 `home_screen.dart`와 관련 위젯 수정 작업을 시작해줘.
