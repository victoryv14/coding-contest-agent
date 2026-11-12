import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Optional, Set

from backend.fetchers.codechef import CodeChefFetcher
from backend.fetchers.codeforces import CodeforcesFetcher
from backend.fetchers.leetcode import LeetCodeFetcher
from backend.models.contest import Contest

logger = logging.getLogger(__name__)


class ContestService:
    """
    Central orchestration service for fetching and caching contest schedules.
    """

    def __init__(self, cache_ttl_seconds: int = 600):
        self.fetchers = [
            CodeforcesFetcher(),
            LeetCodeFetcher(),
            CodeChefFetcher(),
        ]
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cached_contests: List[Contest] = []
        self._last_fetch_time: Optional[datetime] = None
        self._lock = asyncio.Lock()

    def _is_cache_valid(self) -> bool:
        if not self._last_fetch_time or not self._cached_contests:
            return False
        elapsed = (datetime.now(timezone.utc) - self._last_fetch_time).total_seconds()
        return elapsed < self.cache_ttl_seconds

    async def get_all_contests(self, force_refresh: bool = False) -> List[Contest]:
        async with self._lock:
            if not force_refresh and self._is_cache_valid():
                return self._cached_contests

            logger.info("Cache expired or empty. Fetching fresh contest data from all platforms...")

            results = await asyncio.gather(
                *(fetcher.fetch_contests() for fetcher in self.fetchers),
                return_exceptions=True
            )

            all_contests: List[Contest] = []
            for fetcher, result in zip(self.fetchers, results):
                if isinstance(result, Exception):
                    logger.error(f"Error fetching from {fetcher.platform_name}: {result}")
                elif isinstance(result, list):
                    all_contests.extend(result)

            all_contests.sort(key=lambda c: c.start_time)

            if all_contests:
                self._cached_contests = all_contests
                self._last_fetch_time = datetime.now(timezone.utc)
                logger.info(f"Updated cache with {len(all_contests)} total contests.")
            elif self._cached_contests:
                logger.warning("All fetches failed; retaining previous stale cache.")

            return self._cached_contests

    async def filter_contests(
        self,
        platforms: Optional[Set[str]] = None,
        divisions: Optional[Set[str]] = None,
    ) -> List[Contest]:
        contests = await self.get_all_contests()
        filtered = contests

        if platforms:
            filtered = [c for c in filtered if c.platform.lower() in {p.lower() for p in platforms}]

        if divisions:
            allowed_divs = {d.strip().lower() for d in divisions if d.strip()}
            if allowed_divs:
                filtered = [
                    c for c in filtered
                    if c.division and any(d in c.division.lower() for d in allowed_divs)
                ]

        return filtered
