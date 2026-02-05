# ✅ To-Do List

## Phase 1: Setup & Data Layer

- [x] Initialize Python Env & Install dependencies (`fastapi`, `sqlalchemy`, `pydantic`).
- [ ] Setup PostgreSQL with Docker.
- [ ] Implement `services/polygon_service.py` (US Data).
- [ ] Implement `services/kis_service.py` (KR Data).

## Phase 2: The Logic (Bridge & Personalization)

- [x] **[NEW]** Define `User` and `Watchlist` models in SQLAlchemy.
- [x] **[NEW]** Design `ValueChain` model to store specific US-KR stock relationships.
- [x] Implement `logic/correlation_engine.py` using GPT-4o.
- [x] Create a script to seed initial Value Chain data (e.g., NVDA -> SK Hynix).

## Phase 3: API Implementation

- [ ] Implement `GET /briefing/today` (General Summary).
- [x] **[NEW]** Implement `GET /insight/personal-matches` (Personalized Logic).
- [x] **[NEW]** Implement `GET /insight/value-chain` (Depth View).
- [ ] **[NEW]** Implement `GET /system/mode` (Time-based logic).

## Phase 4: Flutter App (Frontend)

- [ ] Setup Flutter Project & HTTP Client.
- [ ] **UI - Home:** Implement "Market Weather" widget & Top Drivers.
- [ ] **[UI Upgrade]** Implement `SfRadialGauge` for Market Mood.
- [ ] **[UI Upgrade]** Add Sparklines for index trends.
- [ ] **[UI Upgrade]** Change Hot Themes to GridView Heatmap.
- [ ] **[UI Upgrade]** Compact "Causality Card" (US -> KR with arrow).
- [ ] **[UI Upgrade]** Polish Density & Typography (Hierarchy/Colors).
- [ ] **UI - Insight Tab:** - [ ] Create "Sector Coupling" view.
  - [ ] **[NEW]** Build "Value Chain Popup" (Visual tree structure).
- [ ] **UI - My Page:** Create "Watchlist Management" screen.
- [ ] **Logic:** Implement "App Mode" switching based on current time (or API response).

## Phase 5: Polish

- [ ] Add Push Notification Logic (Firebase FCM).
- [ ] Finalize README and Documentation.
