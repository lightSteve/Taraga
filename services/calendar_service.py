import logging
import json
from datetime import date, datetime
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Major tickers for earnings calendar
EARNINGS_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA",
    "JPM", "V", "WMT", "MA", "UNH", "HD", "PG", "JNJ",
    "XOM", "CVX", "KO", "PEP", "COST", "MU", "NKE",
    "BA", "CRM", "ORCL", "AVGO", "LLY", "AMD", "NFLX", "QCOM",
]


class CalendarService:
    _fomc_cache: List[Dict] = []
    _fomc_cache_time: Optional[datetime] = None
    _earnings_cache: dict = {}  # {(year,month): (data, timestamp)}

    def get_monthly_events(self, year: int, month: int) -> List[Dict]:
        """
        Get real economic events and earnings for a specific month.
        Sources: yfinance (earnings), Federal Reserve (FOMC schedule).
        """
        events: List[Dict] = []

        # 1. Real earnings from yfinance
        try:
            events.extend(self._fetch_earnings(year, month))
        except Exception as e:
            logger.warning(f"Failed to fetch earnings: {e}")

        # 2. Real FOMC meeting schedule from Federal Reserve website
        try:
            events.extend(self._fetch_fomc_schedule(year, month))
        except Exception as e:
            logger.warning(f"Failed to fetch FOMC schedule: {e}")

        # Sort by date
        events.sort(key=lambda x: x.get("date", ""))
        return events

    def _fetch_earnings(self, year: int, month: int) -> List[Dict]:
        """Fetch real upcoming earnings dates from yfinance."""
        cache_key = (year, month)
        now = datetime.now()

        # Cache for 6 hours
        if cache_key in self._earnings_cache:
            cached_data, cached_time = self._earnings_cache[cache_key]
            if (now - cached_time).total_seconds() < 21600:
                return cached_data

        try:
            import yfinance as yf
        except ImportError:
            logger.warning("yfinance not installed, skipping earnings")
            return []

        results = []
        import time
        for ticker in EARNINGS_TICKERS:
            try:
                tk = yf.Ticker(ticker)
                cal = tk.calendar
                time.sleep(0.3)  # Rate limit: ~3 req/sec
                if not cal or "Earnings Date" not in cal:
                    continue
                for ed in cal["Earnings Date"]:
                    ed_date = ed if isinstance(ed, date) else datetime.strptime(str(ed), "%Y-%m-%d").date()
                    if ed_date.year == year and ed_date.month == month:
                        eps_est = cal.get("Earnings Average")
                        rev_est = cal.get("Revenue Average")
                        rev_str = f"${rev_est / 1e9:.1f}B" if rev_est else "N/A"
                        eps_str = f"${eps_est:.2f}" if eps_est else "N/A"
                        results.append({
                            "date": str(ed_date),
                            "type": "EARNINGS",
                            "title": f"{ticker} 실적 발표",
                            "country": "US",
                            "impact": 4,
                            "description": f"EPS 예상: {eps_str} | 매출 예상: {rev_str}",
                            "forecast": eps_str,
                            "previous": "—",
                            "category": "실적 발표",
                        })
                        # Also add dividend if available
                        ex_div = cal.get("Ex-Dividend Date")
                        if ex_div:
                            ex_date = ex_div if isinstance(ex_div, date) else datetime.strptime(str(ex_div), "%Y-%m-%d").date()
                            if ex_date.year == year and ex_date.month == month:
                                results.append({
                                    "date": str(ex_date),
                                    "type": "DIVIDEND",
                                    "title": f"{ticker} 배당락일",
                                    "country": "US",
                                    "impact": 2,
                                    "description": f"{ticker} 분기 배당 지급 기준일",
                                    "category": "배당",
                                })
            except Exception:
                continue

        self._earnings_cache[cache_key] = (results, now)
        return results

    def _fetch_fomc_schedule(self, year: int, month: int) -> List[Dict]:
        """Fetch real FOMC meeting dates from the Federal Reserve website."""
        now = datetime.now()

        # Cache FOMC data for 24 hours
        if self._fomc_cache and self._fomc_cache_time and (now - self._fomc_cache_time).total_seconds() < 86400:
            return [e for e in self._fomc_cache if e["date"].startswith(f"{year}-{month:02d}")]

        try:
            import re
            url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
            r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code != 200:
                return []

            soup = BeautifulSoup(r.text, "html.parser")
            all_events = []

            # Each year is in a panel with heading like "2026 FOMC Meetings"
            panels = soup.find_all("div", class_="panel")
            for panel in panels:
                heading = panel.find("div", class_="panel-heading")
                if not heading:
                    continue
                heading_text = heading.get_text(strip=True)
                year_match = re.search(r"(\d{4})\s*FOMC", heading_text)
                if not year_match:
                    continue
                panel_year = int(year_match.group(1))

                meetings = panel.find_all("div", class_="fomc-meeting")
                for meeting in meetings:
                    text = meeting.get_text(strip=True)
                    self._parse_fomc_meeting_with_year(text, panel_year, all_events)

            self._fomc_cache = all_events
            self._fomc_cache_time = now

            return [e for e in all_events if e["date"].startswith(f"{year}-{month:02d}")]

        except Exception as e:
            logger.warning(f"FOMC scrape failed: {e}")
            return []

    def _parse_fomc_meeting_with_year(self, text: str, year: int, events: List[Dict]):
        """Parse a single FOMC meeting div text into events with known year."""
        import re

        month_map = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12,
            "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
            "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9,
            "Oct": 10, "Nov": 11, "Dec": 12,
        }

        # Match "March17-18*" or "January27-28" or "Apr/May30-1" or "Jan/Feb31-1"
        match = re.match(r"([A-Za-z/]+?)(\d{1,2})-(\d{1,2})(\*?)", text)
        if not match:
            return

        month_str, start_day, end_day, has_star = match.groups()
        # Handle cross-month like "Apr/May" — use the second month for the end date
        if "/" in month_str:
            parts = month_str.split("/")
            month_num = month_map.get(parts[-1])
        else:
            month_num = month_map.get(month_str)

        if not month_num:
            return

        try:
            event_date = date(year, month_num, int(end_day))
        except ValueError:
            return

        has_statement = has_star or "Statement" in text
        has_press_conf = "Press Conference" in text or bool(has_star)

        title = "FOMC 금리 결정" if has_statement else "FOMC 회의"
        desc = "기준 금리 결정 및 성명서 발표."
        if has_press_conf:
            desc += " 파월 의장 기자회견 포함."
        if "Projection" in text:
            desc += " 경제 전망 자료(SEP) 발표."

        events.append({
            "date": str(event_date),
            "type": "ECONOMIC",
            "title": title,
            "country": "US",
            "impact": 5 if has_statement else 4,
            "description": desc,
            "time": "14:00 ET",
            "category": "중앙은행",
            "forecast": "—",
            "previous": "—",
        })
