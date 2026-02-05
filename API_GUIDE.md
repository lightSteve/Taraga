# 📡 Taraga 시스템 API 연동 및 운영 가이드

이 문서는 Taraga 서비스가 사용하는 외부 데이터 소스, 매핑 로직, 그리고 장애 대응을 위한 가이드입니다.

## 1. 데이터 소스 (Data Sources)

Taraga는 미국 시장과 한국 시장 데이터를 확보하기 위해 아래 3가지 핵심 Provider를 사용하지.

### 🇺🇸 미국 주식 데이터 (US Market)

* **Main Provider:** **[Polygon.io](https://polygon.io/)**
  * **사용 API:** `v2/snapshot/locale/us/markets/stocks/tickers` (실시간 스냅샷)
  * **용도:**
    * 시장 지수 (S&P 500, Nasdaq 등) 실시간 시세
    * 섹터별 ETF (XLK, SOXX 등) 등락률 분석
    * Top Gainers/Losers
  * **장점:** WebSocket급의 빠른 실시간성, 안정적인 API.
* **Fallback (비상용):** **[Yahoo Finance](https://pypi.org/project/yfinance/)** (Unofficial)
  * **라이브러리:** `yfinance` Python 라이브러리
  * **용도:** Polygon 장애 시 혹은 무료 티어 한계 도달 시 백업용.
  * **특징:** 별도 키 없이 사용 가능하나 속도가 느리고 호출 제한이 있을 수 있음.

### 🇰🇷 한국 주식 데이터 (KR Market)

* **Provider:** **[한국투자증권 (KIS) OpenAPI](https://apiportal.koreainvestment.com/)**
  * **사용 API:** `/uapi/domestic-stock/v1/quotations/inquire-price` (주식현재가 시세)
  * **용도:** 내 관심 종목(Watchlist)의 현재가, 등락률 등 실시간 정보.
  * **인증:** OAuth2 토큰 방식 (주기적 갱신 필요).

---

## 2. 데이터 맵핑 & 분석 (Mapping Logic)

미국 시장의 흐름이 한국 종목에 미치는 영향을 분석하는 핵심 로직은 백엔드 `StockService`에 있어.

### 🧠 Logic Flow

1. **US Market Fetch:** Polygon API를 통해 미국 주요 섹터 ETF(13개+)의 **실시간 등락률**을 가져옴.
    * 예: 반도체(SOXX) +1.5%, 2차전지(LIT) -0.5%
2. **User Watchlist Scan:** 사용자가 등록한 한국 주식 목록을 순회.
3. **Keyword Matching:** 한국 종목명에서 키워드를 추출하여 해당 섹터 ETF와 매핑.
    * "SK하이닉스" -> (키워드: 하이닉스) -> **반도체 섹터** -> **SOXX**와 매핑
    * "포스코퓨처엠" -> (키워드: 퓨처엠/이노베이션) -> **2차전지 섹터** -> **LIT**와 매핑
4. **Influence Score:** 미국 섹터가 상승 중이면 해당 한국 종목에 "상승 압력(UP)" 신호 부여.

---

## 3. 갱신 주기 및 장애 대응 (Refresh & Ops)

### 🔄 데이터 갱신 (Refresh Policy)

* **Real-time Calls:** 사용자가 앱에서 **새로고침(Refresh)** 하거나 화면에 진입할 때마다 백엔드는 **즉시 외부 API를 호출**하여 최신 데이터를 가져옴.
  * DB에 시세를 저장해두고 쓰는 Cached 방식이 아님 (항상 Live Data).
  * 장점: 지연 없는 최신 시세.
  * 단점: 사용자가 몰리면 API 호출량이 급증할 수 있음 (Rate Limit 주의).

### 🚨 장애 대응 시나리오 (Troubleshooting)

| 상황 | 증상 | 대응 방법 |
| :--- | :--- | :--- |
| **Polygon API 장애** | 미국 지수/섹터 정보가 안 나옴 | 1. `use_premium=False` 설정 변경하여 Yahoo Finance로 전환<br>2. 또는 Mock Data(더미) 모드 활성화 |
| **KIS (한투) 장애** | 한국 내 종목 가격 0원 표시 | 1. KIS 시스템 점검 공지 확인<br>2. 토큰(Token) 만료 여부 로그 확인 |
| **속도가 느림** | 로딩이 계속 돎 | 1. API Rate Limit 초과 의심<br>2. `YahooFinanceService`의 Batch Fetch 기능 점검 |

---

## 4. 운영 체크리스트

- [ ] **API 토큰 만료:** KIS 토큰은 주기적으로 자동 갱신되지만 로그 모니터링 필요.
* [ ] **Rate Limit:** Polygon 무료/스타터 플랜은 분당 호출 제한이 있음. 트래픽 증가 시 업그레이드 검토.
* [ ] **장 운영 시간:** 미국/한국 장 운영 시간(휴장일 포함)에 따라 데이터가 멈춰 있을 수 있음 (버그 아님).
