
# 🛠 Technical Specifications

## 💻 Tech Stack
- **Language:** Python 3.11+ (Backend), Dart (Frontend)
- **Framework:** FastAPI (Web), Flutter (Mobile)
- **Database:** PostgreSQL (Primary), Redis (Caching/Queue)
- **AI/LLM:** OpenAI API (GPT-4o) or LangChain
- **External APIs:**
    - `Polygon.io` (US Market Data)
    - `NewsAPI` (US News)
    - `Korea Investment (KIS)` (KR Market Data)

## 🗄 Database Schema (PostgreSQL)

### 1. `themes`
- `id` (PK): Integer
- `name`: String (e.g., "AI Semiconductor", "EV Battery")
- `keywords`: Text (JSON list of related English keywords)

### 2. `stocks_us` & `stocks_kr`
- `ticker`: String (PK) (e.g., "TSLA", "005930")
- `name`: String
- `sector`: String
- `theme_id`: FK (Nullable)

### 3. `daily_briefings`
- `date`: Date (PK)
- `us_summary`: Text (AI generated summary)
- `market_sentiment`: String (Fear/Greed)
- `key_indices_json`: JSON (Dow, Nasdaq, S&P changes)

### 4. `recommended_themes` (The Result)
- `date`: Date
- `theme_id`: FK
- `reason`: Text (Why this theme is hot today)
- `related_us_stock`: String (The cause ticker)
- `impact_score`: Integer (1-10)

## 🤖 AI "Bridge" Logic (Prompt Engineering)
**System Prompt for GPT-4o:**
"You are a financial analyst. I will provide US news headlines and top gainer stocks from last night. Your job is to:
1. Summarize the key market driver.
2. Identify the top 3 sectors that performed well.
3. Match these sectors to the provided list of Korean market themes.
4. Return the result in strictly JSON format."

## 🔌 API Endpoints (FastAPI)

### `GET /api/v1/briefing/today`
- Returns: `daily_briefings` data for the current date.

### `GET /api/v1/themes/recommendations`
- Returns: List of `recommended_themes` joined with `stocks_kr`.

### `GET /api/v1/market/us-snapshot`
- Returns: Real-time or delayed snapshot of US major indices.

## ⚙️ Environment Variables (.env)