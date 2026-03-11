"""
Smart Score 엔진 — 다중 팩터 종목 스코어링 + Anomaly Detection

스코어링 로직 (0~100):
  1) Institutional Accumulation (40%): 최근 3일간 기관/외인 동반 순매수 강도
     - yfinance에서는 기관 데이터가 없으므로, 거래량 급증 + 양봉 조합으로 Proxy 추정
  2) Price Momentum (30%): VWAP 돌파 여부 및 5일 이동평균선 이격도
  3) Volume Surge (30%): 최근 20일 평균 거래량 대비 당일 거래량 폭증 비율

Anomaly Detection:
  - 최근 10거래일 중 전반부 거래량이 극히 낮고, 최근 급등한 '소외주 반등' 패턴
"""

import yfinance as yf
import pandas as pd
import numpy as np


def _safe_float(val, default=0.0):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def compute_smart_score(ticker: str, period: str = "1mo") -> dict | None:
    """
    개별 종목의 Smart Score를 계산한다.

    Returns:
        dict with keys:
          ticker, name, score, inst_score, momentum_score, volume_score,
          is_anomaly, anomaly_reason, price, change_percent,
          vwap, ma5, volume_ratio, volume_history, price_history
        or None on failure
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)

        if df is None or len(df) < 10:
            return None

        info = stock.info or {}
        name = info.get("shortName") or info.get("longName") or ticker
        shares_outstanding = info.get("sharesOutstanding", 0)

        close = df["Close"]
        volume = df["Volume"]
        high = df["High"]
        low = df["Low"]

        cur_price = _safe_float(close.iloc[-1])
        prev_price = _safe_float(close.iloc[-2]) if len(close) >= 2 else cur_price
        change_pct = ((cur_price - prev_price) / prev_price * 100) if prev_price > 0 else 0

        # ───────────────────────────────────────────────
        # 1. Institutional Accumulation Proxy (40%)
        # ───────────────────────────────────────────────
        # 기관 데이터 대신: (거래량 급증 + 양봉) 3일 연속이면 기관 매집 추정
        inst_score = _calc_institutional_proxy(df, shares_outstanding)

        # ───────────────────────────────────────────────
        # 2. Price Momentum (30%) — VWAP & MA5 이격도
        # ───────────────────────────────────────────────
        momentum_score, vwap, ma5 = _calc_price_momentum(df)

        # ───────────────────────────────────────────────
        # 3. Volume Surge (30%) — 20일 평균 대비 당일 거래량
        # ───────────────────────────────────────────────
        volume_score, volume_ratio = _calc_volume_surge(df)

        # ───────────────────────────────────────────────
        # 종합 점수
        # ───────────────────────────────────────────────
        total = inst_score * 0.4 + momentum_score * 0.3 + volume_score * 0.3
        total = max(0, min(100, round(total, 1)))

        # ───────────────────────────────────────────────
        # Anomaly Detection
        # ───────────────────────────────────────────────
        is_anomaly, anomaly_reason = _detect_anomaly(df)

        # 시각화용 히스토리
        vol_hist = volume.tail(20).tolist()
        price_hist = close.tail(20).tolist()
        dates_hist = [d.strftime("%m/%d") for d in df.index[-20:]]

        return {
            "ticker": ticker,
            "name": name,
            "score": total,
            "inst_score": round(inst_score, 1),
            "momentum_score": round(momentum_score, 1),
            "volume_score": round(volume_score, 1),
            "is_anomaly": is_anomaly,
            "anomaly_reason": anomaly_reason,
            "price": round(cur_price, 2),
            "change_percent": round(change_pct, 2),
            "vwap": round(vwap, 2) if vwap else None,
            "ma5": round(ma5, 2) if ma5 else None,
            "volume_ratio": round(volume_ratio, 2),
            "volume_history": vol_hist,
            "price_history": price_hist,
            "dates": dates_hist,
        }
    except Exception:
        return None


def _calc_institutional_proxy(df: pd.DataFrame, shares_outstanding: int) -> float:
    """
    기관/외인 매집 프록시 점수 (0~100)

    로직:
    - 최근 3일 각각에 대해:
      ① 양봉(종가 > 시가) 여부
      ② 거래량이 직전 5일 평균보다 높은지
      ③ 유통주식수 대비 거래량 비율
    - 3일 다 충족 → 100, 2일 → 70, 1일 → 35, 0일 → 10
    """
    if len(df) < 8:
        return 10.0

    score = 0
    bullish_days = 0

    for i in range(-3, 0):
        try:
            c = _safe_float(df["Close"].iloc[i])
            o = _safe_float(df["Open"].iloc[i])
            v = _safe_float(df["Volume"].iloc[i])

            # 직전 5일 평균 거래량
            window_start = max(0, len(df) + i - 5)
            window_end = len(df) + i
            avg_vol = df["Volume"].iloc[window_start:window_end].mean()

            is_bullish = c > o
            is_vol_above = v > avg_vol * 1.2

            if is_bullish and is_vol_above:
                bullish_days += 1

                # 유통주식 대비 거래량 가산점
                if shares_outstanding > 0:
                    buy_ratio = v / shares_outstanding
                    if buy_ratio > 0.03:
                        score += 15
                    elif buy_ratio > 0.01:
                        score += 8
        except (IndexError, TypeError):
            continue

    base = {0: 10, 1: 35, 2: 70, 3: 100}.get(bullish_days, 10)
    return min(100, base + score)


def _calc_price_momentum(df: pd.DataFrame) -> tuple[float, float | None, float | None]:
    """
    Price Momentum 점수 (0~100)

    VWAP = sum(전형가 * 거래량) / sum(거래량), 전형가 = (H+L+C)/3
    MA5 = 5일 종가 이동평균
    """
    if len(df) < 5:
        return 50.0, None, None

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # VWAP (당일)
    typical_price = (high + low + close) / 3
    cum_tp_vol = (typical_price * volume).cumsum()
    cum_vol = volume.cumsum()
    vwap_series = cum_tp_vol / cum_vol.replace(0, np.nan)
    vwap = _safe_float(vwap_series.iloc[-1])

    # MA5
    ma5 = _safe_float(close.rolling(5).mean().iloc[-1])

    cur = _safe_float(close.iloc[-1])

    score = 50.0  # 기본

    # VWAP 돌파: 현재가 > VWAP → 가산
    if vwap and vwap > 0:
        vwap_ratio = (cur - vwap) / vwap * 100
        if vwap_ratio > 2:
            score += 25
        elif vwap_ratio > 0:
            score += 15
        elif vwap_ratio > -1:
            score += 5
        else:
            score -= 15

    # MA5 이격도: 현재가가 MA5 위 → 가산
    if ma5 and ma5 > 0:
        gap_ratio = (cur - ma5) / ma5 * 100
        if gap_ratio > 3:
            score += 25
        elif gap_ratio > 1:
            score += 15
        elif gap_ratio > 0:
            score += 5
        else:
            score -= 10

    return max(0, min(100, score)), vwap, ma5


def _calc_volume_surge(df: pd.DataFrame) -> tuple[float, float]:
    """
    Volume Surge 점수 (0~100)

    당일 거래량 / 최근 20일 평균 거래량
    """
    if len(df) < 2:
        return 50.0, 1.0

    cur_vol = _safe_float(df["Volume"].iloc[-1])
    avg_20 = df["Volume"].tail(20).mean()

    if avg_20 <= 0:
        return 50.0, 1.0

    ratio = cur_vol / avg_20

    if ratio >= 5.0:
        score = 100
    elif ratio >= 3.0:
        score = 85
    elif ratio >= 2.0:
        score = 70
    elif ratio >= 1.5:
        score = 55
    elif ratio >= 1.0:
        score = 40
    elif ratio >= 0.5:
        score = 25
    else:
        score = 10

    return score, ratio


def _detect_anomaly(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Anomaly Detection — '소외주 반등' 패턴

    조건:
    1) 최근 10거래일 데이터 확보
    2) 전반부(1~7일) 평균 거래량이 전체 20일 평균의 50% 이하 (소외)
    3) 후반부(8~10일) 평균 거래량이 전반부의 3배 이상 (급증)
    4) 최근 3일 중 양봉이 2개 이상
    """
    if len(df) < 10:
        return False, ""

    recent_10 = df.tail(10)
    vol = recent_10["Volume"]

    early_vol = vol.iloc[:7].mean()  # 전반부 7일
    late_vol = vol.iloc[7:].mean()   # 후반부 3일

    # 20일 평균
    avg_20 = df["Volume"].tail(20).mean() if len(df) >= 20 else df["Volume"].mean()

    # 소외 조건: 전반부 거래량이 20일 평균의 50% 이하
    is_neglected = (early_vol < avg_20 * 0.5) if avg_20 > 0 else False

    # 급증 조건: 후반부가 전반부의 3배 이상
    is_surge = (late_vol > early_vol * 3) if early_vol > 0 else False

    # 양봉 확인
    last_3 = df.tail(3)
    bullish_count = sum(
        _safe_float(last_3["Close"].iloc[i]) > _safe_float(last_3["Open"].iloc[i])
        for i in range(len(last_3))
    )

    if is_neglected and is_surge and bullish_count >= 2:
        surge_ratio = late_vol / early_vol if early_vol > 0 else 0
        return True, f"소외주 반등 감지: 거래량 {surge_ratio:.1f}배 급증, 양봉 {bullish_count}개"

    if is_surge and bullish_count >= 2:
        surge_ratio = late_vol / early_vol if early_vol > 0 else 0
        return True, f"거래량 이상 급증: {surge_ratio:.1f}배, 양봉 {bullish_count}개"

    return False, ""


def scan_and_score(tickers: list[str], market: str = "KR") -> list[dict]:
    """
    여러 종목을 스캔하여 Smart Score 기준 정렬 후 반환한다.
    Anomaly 종목은 보너스 점수(+10)를 받는다.
    """
    results = []
    for ticker in tickers:
        result = compute_smart_score(ticker)
        if result:
            # Anomaly 보너스
            if result["is_anomaly"]:
                result["score"] = min(100, result["score"] + 10)
            result["market"] = market
            results.append(result)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results
