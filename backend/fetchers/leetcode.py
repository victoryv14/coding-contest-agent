import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import httpx

from backend.fetchers.base import BaseFetcher
from backend.models.contest import Contest

logger = logging.getLogger(__name__)


class LeetCodeFetcher(BaseFetcher):
    """
    Fetcher for upcoming LeetCode contests.
    Uses LeetCode's public GraphQL endpoint:
    https://leetcode.com/graphql
    """

    GRAPHQL_URL = "https://leetcode.com/graphql"

    GRAPHQL_QUERY = """
    query upcomingContests {
      topTwoContests {
        title
        titleSlug
        startTime
        duration
      }
    }
    """

    HEADERS = {
        "Content-Type": "application/json",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Referer": "https://leetcode.com/contest/",
    }

    @property
    def platform_name(self) -> str:
        return "leetcode"

    @staticmethod
    def _extract_division(title: str) -> Optional[str]:
        """Categorize into 'Weekly', 'Biweekly', or 'Contest'."""
        title_lower = title.lower()
        if "biweekly" in title_lower:
            return "Biweekly"
        elif "weekly" in title_lower:
            return "Weekly"
        return "Contest"

    async def fetch_contests(self) -> List[Contest]:
        """Sends GraphQL query to LeetCode and parses upcoming contests."""
        contests: List[Contest] = []
        now_utc = datetime.now(timezone.utc)

        try:
            async with httpx.AsyncClient(timeout=10.0, headers=self.HEADERS) as client:
                response = await client.post(
                    self.GRAPHQL_URL,
                    json={"query": self.GRAPHQL_QUERY}
                )
                response.raise_for_status()
                data = response.json()

            top_contests = data.get("data", {}).get("topTwoContests", [])

            for item in top_contests:
                start_seconds = item.get("startTime")
                duration_seconds = item.get("duration", 5400)
                title = item.get("title", "LeetCode Contest")
                slug = item.get("titleSlug", "")

                if not start_seconds:
                    continue

                start_time = datetime.fromtimestamp(start_seconds, tz=timezone.utc)
                end_time = start_time + timedelta(seconds=duration_seconds)

                if end_time < now_utc:
                    continue

                contest = Contest(
                    id=f"lc-{slug or start_seconds}",
                    title=title,
                    platform=self.platform_name,
                    url=f"https://leetcode.com/contest/{slug}",
                    start_time=start_time,
                    end_time=end_time,
                    duration_seconds=duration_seconds,
                    division=self._extract_division(title)
                )
                contests.append(contest)

            contests.sort(key=lambda c: c.start_time)
            logger.info(f"Successfully fetched {len(contests)} upcoming LeetCode contests.")

        except httpx.RequestError as exc:
            logger.error(f"Network error while fetching LeetCode contests: {exc}")
        except Exception as exc:
            logger.error(f"Unexpected error in LeetCodeFetcher: {exc}")

        return contests
