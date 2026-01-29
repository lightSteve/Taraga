# 📈 Taraga (따라가)
> **"미국장이 가면, 국장도 간다."** > Wall Street의 나비효과를 Yeouido의 수익으로 연결하는 **미국-한국 증시 연동 인사이트 플랫폼**

![Project Status](https://img.shields.io/badge/Project-Active-green) ![Python](https://img.shields.io/badge/Backend-Python-3776AB) ![Flutter](https://img.shields.io/badge/App-Flutter-02569B) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 📖 Introduction
**Taraga(따라가)**는 밤사이 열린 미국 증시(The Cause)의 데이터와 뉴스를 분석하여, 당일 한국 증시(The Effect)에서 주목해야 할 **테마와 종목을 장 시작 전에 추천**해주는 모바일 애플리케이션 서비스입니다.

정보의 홍수 속에서 단순한 뉴스 나열이 아닌, **"그래서 오늘 한국장에서는 뭘 봐야 해?"**라는 질문에 대한 명확한 해답(Action Item)을 제공하는 것을 목표로 합니다.

---

## 🚀 Key Features (핵심 기능)

### 1. 🇺🇸 US Daily Briefing (출근길 5분 요약)
- 미국 3대 지수(다우, 나스닥, S&P500) 및 공포/탐욕 지수 시각화.
- 간밤의 핵심 이슈 및 주도 섹터(Sector) AI 3줄 요약.

### 2. 🔗 The Bridge (테마 맵핑 시스템)
- **AI 연관성 분석:** 미국 특정 종목 급등 시, 상관관계가 높은 한국 종목 자동 추출.
- *Example:* `Tesla(US) +10%` ➔ **`LG Energy Solution(KR)` & `Ecopro(KR)` 강세 예상**

### 3. ⏰ Pre-market Alert (장전 알림)
- 한국 증시 개장 전(08:30), 오늘 공략해야 할 'Key Sector' 푸시 알림 발송.
- 외국인/기관 수급이 예상되는 종목 리스트업.

### 4. 📊 Real-time Dashboard
- 테마별 미국 대장주와 한국 관련주의 등락률 비교 히트맵(Heatmap) 제공.

---

## 🛠 System Architecture

```mermaid
graph LR
    A[US Market Data] -->|Polygon/NewsAPI| B(Data Processing Server)
    B -->|OpenAI GPT-4o| C{Correlation Engine}
    D[KR Market Data] -->|KIS API| C
    C -->|Mapping Logic| E[Taraga DB]
    E -->|REST API| F[Client App]
