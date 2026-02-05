# 🛠 Technical Specifications

## 💻 Tech Stack

- **Language:** Python 3.11+ (Backend), Dart (Frontend)
- **Framework:** FastAPI, Flutter
- **Database:** PostgreSQL (Primary), Redis (Caching)
- **AI:** OpenAI GPT-4o (Reasoning & Summarization)

## 🗄 Database Schema (Enhanced)

### 1. `users` & `watchlists` (New for Personalization)

- `user_id`: UUID
- `stock_kr_code`: String (FK)
- `alert_setting`: Boolean

### 2. `value_chains` (New for Depth)

- `id`: Integer
- `theme_id`: FK
- `parent_stock_us`: String (e.g., NVDA)
- `child_stock_kr`: String (e.g., 000660)
- `relation_type`: String (e.g., "Supplier", "Competitor", "Sympathy")
- `description`: Text ("Supplies HBM3E chips")

### 3. `themes` & `stocks` (Core)

- Existing tables from previous spec.

### 4. `daily_insights`

- `date`: Date
- `market_weather`: String (Sunny/Cloudy/Rainy)
- `ai_comment`: Text (One-line impact summary)

## 📱 Frontend Architecture (Flutter)

### 1. Navigation Controller (`MainScreen`)

- Uses `BottomNavigationBar` to manage 4 distinct tabs.
- Maintains state (current index) using Provider or Riverpod.

### 2. Screen Specifications

- **`HomeScreen` (Tab 1):**
  - `MarketWeatherWidget`: Displays AI sentiment summary.
  - `IndicesCarousel`: Horizontal scroll of major indices (S&P, Nasdaq).
  - `ThemeHeatmap`: Grid view of top sectors.

- **`InsightScreen` (Tab 2 - NEW):**
  - **Layout:** Vertical ListView of `BridgeNewsCard` widgets.
  - **`BridgeNewsCard` Data:**
    - `us_source`: String (e.g., "Reuters", "Bloomberg") - *Ref: SAVE App*
    - `us_headline`: String
    - `kr_impact_summary`: String (AI Generated)
    - `related_stocks`: List<Stock> (Clickable chips)

- **`CalendarScreen` (Tab 3 - NEW):**
  - **Library:** `table_calendar`.
  - **Data:** Events grouped by date.
  - **Visual:** Red dots for high-impact events (CPI, FOMC).

- **`MyPageScreen` (Tab 4):**
  - **Watchlist Manager:** Reorderable list of user's KR stocks.
  - **Profile Header:** User stats (like SAVE's point system, but for "Streak").

### 3. API Requirements for New Tabs

- `GET /api/v1/news/bridge`: Returns list of mapped news for Insight Tab.
- `GET /api/v1/calendar/events`: Returns monthly economic events with impact scores.

## 🤖 AI "Bridge" Logic (Advanced Prompt)

**System Prompt:**
"Analyze the US market close data.

1. Identify top 3 driving themes.
2. For each theme, identify the 'US Driver Stock'.
3. Map this to Korean 'Value Chain' stocks defined in our DB.
4. **Crucial:** Flag if any mapped KR stock exists in the User's Watchlist (I will provide the watchlist list)."

## 🔌 API Endpoints (New)

### `GET /api/v1/insight/personal-matches?user_id={id}`

- Returns: List of stocks from the user's watchlist that are triggered by today's US news.

### `GET /api/v1/insight/value-chain?theme_id={id}`

- Returns: A hierarchical JSON representing the US->KR connection graph.

### `GET /api/v1/system/mode`

- Returns: `{"current_mode": "PRE_MARKET"}` (Based on KST time: 07:00~09:00).
