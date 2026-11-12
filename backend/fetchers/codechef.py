import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from dateutil import parser as date_parser

import httpx

from backend.fetchers.base import BaseFetcher
from backend.models.contest import Contest

logger = logging.getLogger(__name__)


class CodeChefFetcher(BaseFetcher):
    """
    Fetcher for upcoming CodeChef contests.
    Uses a 2-tier resilient approach:
    1. Primary: Direct CodeChef listing API
    2. Fallback: Kontests API aggregator if blocked
    """

    PRIMARY_URL = "https://www.codechef.com/api/list/contests/all?sort_by=START&sorting_order=asc&offset=0&mode=all"
    FALLBACK_URL = "https://kontests.net/api/v1/code_chef"

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Referer": "https://www.codechef.com/contests",
    }

    @property
    def platform_name(self) -> str:
        return "codechef"

    @staticmethod
    def _extract_division(name: str) -> Optional[str]:
        """Detects contest category/series from title."""
        name_lower = name.lower()
        if "starters" in name_lower:
            return "Starters"
        elif "monday munch" in name_lower or "dsa monday" in name_lower:
            return "DSA Monday Munch"
        elif "cook-off" in name_lower:
            return "Cook-Off"
        elif "lunchtime" in name_lower:
            return "Lunchtime"
        return "Contest"

    async def _fetch_from_primary(self) -> List[Contest]:
        contests: List[Contest] = []

        async with httpx.AsyncClient(timeout=10.0, headers=self.HEADERS) as client:
            response = await client.get(self.PRIMARY_URL)
            response.raise_for_status()
            data = response.json()

        future_contests = data.get("future_contests", [])

        for item in future_contests:
            code = item.get("contest_code", "")
            name = item.get("contest_name", f"CodeChef {code}")
            start_date_str = item.get("contest_start_date_iso") or item.get("contest_start_date")
            duration_minutes = int(item.get("contest_duration", 120))
            duration_seconds = duration_minutes * 60

            if not start_date_str:
                continue

            start_time = date_parser.parse(start_date_str)
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone(timedelta(hours=5, minutes=30)))
            
            start_time_utc = start_time.astimezone(timezone.utc)
            end_time_utc = start_time_utc + timedelta(seconds=duration_seconds)

            contest = Contest(
                id=f"cc-{code.lower()}",
                title=name,
                platform=self.platform_name,
                url=f"https://www.codechef.com/{code}",
                start_time=start_time_utc,
                end_time=end_time_utc,
                duration_seconds=duration_seconds,
                division=self._extract_division(name)
            )
            contests.append(contest)

        return contests

    async def _fetch_from_fallback(self) -> List[Contest]:
        contests: List[Contest] = []

        async with httpx.AsyncClient(timeout=10.0, headers=self.HEADERS) as client:
            response = await client.get(self.FALLBACK_URL)
            response.raise_for_status()
            data = response.json()

        now_utc = datetime.now(timezone.utc)

        for item in data:
            name = item.get("name", "CodeChef Contest")
            url = item.get("url", "https://www.codechef.com/contests")
            start_str = item.get("start_time")
            duration_str = item.get("duration", "7200")

            if not start_str:
                continue

            start_time_utc = date_parser.parse(start_str).astimezone(timezone.utc)
            duration_seconds = int(float(duration_str))
            end_time_utc = start_time_utc + timedelta(seconds=duration_seconds)

            if end_time_utc < now_utc:
                continue

            contest = Contest(
                id=f"cc-{abs(hash(name)) % 100000}",
                title=name,
                platform=self.platform_name,
                url=url,
                start_time=start_time_utc,
                end_time=end_time_utc,
                duration_seconds=duration_seconds,
                division=self._extract_division(name)
            )
            contests.append(contest)

        return contests

    async def fetch_contests(self) -> List[Contest]:
        try:
            contests = await self._fetch_from_primary()
            logger.info(f"Successfully fetched {len(contests)} CodeChef contests from primary API.")
            return contests
        except Exception as primary_exc:
            logger.warning(f"Primary CodeChef API failed ({primary_exc}). Switching to fallback aggregator...")

        try:
            contests = await self._fetch_from_fallback()
            logger.info(f"Successfully fetched {len(contests)} CodeChef contests from fallback aggregator.")
            return contests
        except Exception as fallback_exc:
            logger.error(f"Both primary and fallback failed for CodeChef: {fallback_exc}")
            return []
