
# 🗺 Project Plan: Taraga (따라가)

## 🎯 Goal
Build "Taraga," a mobile application that analyzes US stock market data overnight to predict and recommend related Korean stock market themes/sectors for the morning trading session.
**Concept:** "Wall Street to Yeouido" (The Cause -> The Effect).

## 📦 Phasing Strategy

### Phase 1: Foundation & Data Ingestion (Backend)
- **Objective:** Set up the Python environment, Database, and successfully fetch data from external APIs.
- **Focus:** Polygon.io (US Data), NewsAPI (US News), KIS (KR Data).
- **Deliverable:** Scripts that run and save raw market data to PostgreSQL.

### Phase 2: "The Bridge" Logic & AI Integration (Core)
- **Objective:** Implement the logic that connects US events to KR stocks.
- **Focus:** OpenAI GPT-4o integration for news summarization and theme extraction.
- **Deliverable:** A functional `CorrelationEngine` that takes US news and outputs KR stock codes.

### Phase 3: API Layer (FastAPI)
- **Objective:** Expose the data to the frontend via RESTful endpoints.
- **Focus:** Endpoints for Daily Briefing, Theme Map, and Real-time Dashboard.
- **Deliverable:** Swagger/Redoc documentation with working endpoints.

### Phase 4: Frontend Development (Flutter)
- **Objective:** Build the user interface.
- **Focus:** Daily Feed (Home), Calendar, Settings, and Push Notification UI.
- **Deliverable:** A runnable Flutter app connected to the local API.

### Phase 5: Automation & Deployment (DevOps)
- **Objective:** Schedule data fetching jobs (Cron) and prepare for release.
- **Focus:** Celery/Redis for task scheduling (06:00 AM KST).

---

## 📅 User Flows
1. **Morning Routine (User):** Opens app at 08:30 AM -> Checks US Market Summary -> Sees "Today's Recommended KR Themes" -> Clicks a theme to see specific KR stocks.
2. **System Flow:** Fetch US Close Data (06:00) -> Fetch News -> AI Analysis -> Map to KR Themes -> Store in DB -> API serves JSON.