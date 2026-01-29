
# ✅ To-Do List

## Phase 1: Setup & Data Layer

- [x] Initialize Python Virtual Environment & Install `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg2`, `requests`.
- [x] Create `docker-compose.yml` for PostgreSQL and Redis.
- [x] Design `models.py` using SQLAlchemy based on `tech_spec.md`.
- [x] Implement `database.py` for DB connection handling.
- [x] Create `services/polygon_service.py` to fetch US OHLCV and Top Gainers.
- [x] Create `services/kis_service.py` to fetch KR stock current prices (Authentication required).

## Phase 2: The Logic (AI & Mapping)

- [x] Create `services/openai_service.py` with the prompt defined in `tech_spec.md`.
- [x] Seed the Database with initial `themes` data (Create a `seed_themes.py` script with ~10 major themes like AI, EV, Bio).
- [x] Implement `logic/correlation_engine.py`:
  - Fetch US Data -> Send to AI -> Get Theme IDs -> Save to `recommended_themes`.
- [x] Create a standalone script `run_daily_analysis.py` to test the full pipeline.

## Phase 3: API Implementation

- [x] Setup FastAPI main app structure (`main.py`, routers).
- [x] Implement `GET /briefing/today` endpoint.
- [x] Implement `GET /themes/recommendations` endpoint.
- [x] Add CORS middleware for frontend communication.

## Phase 4: Flutter App (Frontend)

- [x] `flutter create taraga_app`.
- [x] Setup folder structure: `lib/models`, `lib/services`, `lib/screens`, `lib/widgets`.
- [x] Implement HTTP client (Dio or http package) to connect to FastAPI.
- [x] **UI - Home Screen:** Display Daily Briefing Summary card.
- [x] **UI - Theme List:** Display the recommended themes as a horizontal list.
- [x] **UI - Detail View:** Clicking a theme shows the list of KR stocks with current prices.

## Phase 5: Polish

- [ ] Add error handling for API failures.
- [ ] Write a simple README with instructions on how to run the backend and frontend.
