"""
Cache Service - Centralized caching layer using MarketDataCache table.
All external API results are cached in DB so:
  1. First user request triggers the actual fetch
  2. Subsequent users get cached data until TTL expires
  3. Rate limits are never hit
"""

import datetime
import logging
from typing import Any, Callable, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import MarketDataCache

logger = logging.getLogger(__name__)

# Default TTLs (minutes) — conservative for single-user, rate-limit safe
TTL_MARKET_INDICES = 30  # 30 min for live indices
TTL_BRIEFING = 120  # 2 hours for daily briefing
TTL_GAINERS_LOSERS = 60  # 1 hour for movers
TTL_SCRAPER = 360  # 6 hours for scraped picks
TTL_FEAR_GREED = 120  # 2 hours for fear & greed


class CacheService:
    """Centralized DB cache using MarketDataCache model."""

    def __init__(self, db: Session):
        self.db = db

    def get_cached(self, key: str, ttl_minutes: int = 15) -> Optional[Any]:
        """
        Get cached data if it exists and is not expired.

        Args:
            key: Cache key (e.g. "US_INDICES", "BRIEFING_2026-02-11")
            ttl_minutes: Time-to-live in minutes

        Returns:
            Cached data dict/list or None if expired/missing
        """
        try:
            cache = (
                self.db.query(MarketDataCache)
                .filter(MarketDataCache.key == key)
                .first()
            )
            if not cache:
                return None

            updated_at = cache.updated_at
            if updated_at and updated_at.tzinfo is None:
                updated_at = updated_at.replace(tzinfo=datetime.timezone.utc)

            now = datetime.datetime.now(datetime.timezone.utc)
            if updated_at and (now - updated_at) < datetime.timedelta(
                minutes=ttl_minutes
            ):
                logger.info(
                    f"Cache HIT for '{key}' (age: {(now - updated_at).seconds}s)"
                )
                return cache.data
            else:
                logger.info(f"Cache EXPIRED for '{key}'")
                return None

        except Exception as e:
            logger.error(f"Cache read error for '{key}': {e}")
            self.db.rollback()
            return None

    def save_cache(self, key: str, data: Any) -> bool:
        """
        Save data to cache. Upserts (update if exists, insert if not).

        Args:
            key: Cache key
            data: JSON-serializable data

        Returns:
            True if saved successfully
        """
        try:
            cache = (
                self.db.query(MarketDataCache)
                .filter(MarketDataCache.key == key)
                .first()
            )
            if cache:
                cache.data = data
                cache.updated_at = func.now()
            else:
                new_cache = MarketDataCache(key=key, data=data)
                self.db.add(new_cache)

            self.db.commit()
            logger.info(f"Cache SAVED for '{key}'")
            return True
        except Exception as e:
            logger.error(f"Cache save error for '{key}': {e}")
            self.db.rollback()
            return False

    def get_or_fetch(
        self,
        key: str,
        fetcher_fn: Callable[[], Any],
        ttl_minutes: int = 15,
    ) -> Optional[Any]:
        """
        Main method: get from cache or fetch fresh data.

        If cache is valid, return cached data.
        If cache is expired/missing, call fetcher_fn, save result, return it.
        If fetcher_fn fails, return stale cache as fallback.

        Args:
            key: Cache key
            fetcher_fn: Callable that returns fresh data
            ttl_minutes: TTL in minutes

        Returns:
            Data (cached or fresh) or None if everything fails
        """
        # 1. Try cache first
        cached = self.get_cached(key, ttl_minutes)
        if cached is not None:
            return cached

        # 2. Cache miss/expired — fetch fresh data
        try:
            logger.info(f"Fetching fresh data for '{key}'...")
            fresh_data = fetcher_fn()

            if fresh_data is not None and fresh_data != {} and fresh_data != []:
                self.save_cache(key, fresh_data)
                return fresh_data
            else:
                logger.warning(f"Fetcher returned empty data for '{key}'")

        except Exception as e:
            logger.error(f"Fetcher failed for '{key}': {e}")

        # 3. Fallback: return stale cache if available
        try:
            stale = (
                self.db.query(MarketDataCache)
                .filter(MarketDataCache.key == key)
                .first()
            )
            if stale and stale.data:
                logger.warning(f"Returning STALE cache for '{key}' as fallback")
                return stale.data
        except Exception:
            pass

        return None

    def invalidate(self, key: str) -> bool:
        """Remove a cache entry."""
        try:
            self.db.query(MarketDataCache).filter(MarketDataCache.key == key).delete()
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Cache invalidation error for '{key}': {e}")
            self.db.rollback()
            return False
