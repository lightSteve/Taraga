Taraga vs OCEANS save — 초기 초안
작성: 자비스
일시: 2026-02-09 13:28 KST

요약 (한 문장)
- Taraga는 "미국장→한국장" 연동 인사이트에 초점을 맞춘 플랫폼으로, 데이터 파이프라인(Polygon/뉴스API/KIS)과 AI 연관성 매핑을 통해 장전 추천을 제공한다. OCEANS save(경쟁사)는 UI/사용자 경험, 시각화, 특정 테마 추천 방식에서 차별화 요소가 있을 가능성이 있어, 기능·성능·운영 측면에서 갭 분석이 필요하다.

초기 관찰(Repo 기반)
- 핵심 기능: US Daily Briefing, The Bridge(테마 매핑), Pre-market Alert, Real-time Dashboard
- 기술 스택: Python(FastAPI) 백엔드, Flutter 모바일 앱, PostgreSQL/Redis, Docker
- 데이터 플로우: 외부 마켓 데이터(POLYGON), 뉴스, KIS(한국시장) 연동 → correlation engine → DB → API → App
- 자동화/파이프라인: run_daily_analysis.py 존재, seed_themes.py로 초기 테마 주입

우선 점검 포인트(초기 6개) — 빠른 개선 우선순위(단기)
1) 데이터 소스 장애/회복 처리(난이도: 중) — 외부 API 장애(Polygon/NewsAPI/KIS)시 graceful degradation 정책 필요.
2) 매핑 정확도 검증(난이도: 중) — correlation_engine의 연관성 로직에 대한 백테스트/정량평가 필요.
3) 알림(Pre-market) 품질 개선(난이도: 낮) — 사용자별 필터/우선순위 제공으로 클릭률 개선 가능.
4) 테스트 커버리지 부족(난이도: 낮) — 핵심 로직(unit tests), API 통합 테스트 추가 권장.
5) 보안(환경변수·시크릿 관리)(난이도: 중) — .env.example 사용 안내 있으나 시크릿 하드코딩 존재 여부 확인 필요.
6) 성능·스케일(난이도: 중) — correlation batch 처리 시 메모리/쿼리 최적화 필요(데이터 증가 대비).

다음 단계(작업 계획)
- 단계 A (1시간 내): 공개된 OCEANS save 기능/앱 설명 수집 → 기능 매핑 테이블 생성 + 단기 우선순위(갭) 업데이트
- 단계 B (3–6시간): Taraga 코드의 correlation_engine 심층 리뷰 → 백테스트 가능 여부·데이터 요구사항 정리
- 단계 C (추후): PR 단위 개선 작업(테스트·에러 처리·알고리즘 조정) 및 성능 테스트

산출물 위치
- 초기 초안: analysis/taraga_vs_oceans_report.md (본 파일)

요청사항
- OCEANS save에서 특히 비교하길 원하는 항목(추천 정확도, UI/UX, 리텐션 등)을 알려주세요. 기본은 기능·알고리즘·UX·운영으로 진행합니다.

진행상태: Taraga 리포지토리 복제 완료, 초기 초안 작성. 다음: 공개 자료를 수집하여 상세 비교(60분 내 초안 업데이트 예정).
