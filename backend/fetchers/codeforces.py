import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import httpx

from backend.fetchers.base import BaseFetcher
from backend.models.contest import Contest

logger = logging.getLogger(__name__)


class CodeforcesFetcher(BaseFetcher):
    """
    Fetcher for upcoming Codeforces contests.
    Uses the official Codeforces public REST API:
    https://codeforces.com/api/contest.list?gym=false
    """

    API_URL = "https://codeforces.com/api/contest.list?gym=false"

    @property
    def platform_name(self) -> str:
        return "codeforces"

    @staticmethod
    def _extract_division(name: str) -> Optional[str]:
        """Helper method to detect contest division or type from title."""
        name_lower = name.lower()
        if "div. 1 + div. 2" in name_lower or "div.1 + div.2" in name_lower:
            return "Div. 1 + Div. 2"
        elif "div. 1" in name_lower or "div.1" in name_lower:
            return "Div. 1"
        elif "div. 2" in name_lower or "div.2" in name_lower:
            return "Div. 2"
        elif "div. 3" in name_lower or "div.3" in name_lower:
            return "Div. 3"
        elif "div. 4" in name_lower or "div.4" in name_lower:
            return "Div. 4"
        elif "educational" in name_lower:
            return "Educational"
        elif "global" in name_lower:
            return "Global"
        return "Other"

    async def fetch_contests(self) -> List[Contest]:
        """Queries Codeforces API and returns upcoming contests."""
        contests: List[Contest] = []

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.API_URL)
                response.raise_for_status()
                data = response.json()

            if data.get("status") != "OK":
                logger.error(f"Codeforces API returned non-OK status: {data.get('comment')}")
                return []

            for item in data.get("result", []):
                if item.get("phase") != "BEFORE":
                    continue

                start_seconds = item.get("startTimeSeconds")
                duration_seconds = item.get("durationSeconds", 7200)

                if not start_seconds:
                    continue

                start_time = datetime.fromtimestamp(start_seconds, tz=timezone.utc)
                end_time = start_time + timedelta(seconds=duration_seconds)
                contest_id = str(item["id"])
                contest_name = item.get("name", f"Codeforces Round {contest_id}")

                contest = Contest(
                    id=f"cf-{contest_id}",
                    title=contest_name,
                    platform=self.platform_name,
                    url=f"https://codeforces.com/contestRegistration/{contest_id}",
                    start_time=start_time,
                    end_time=end_time,
                    duration_seconds=duration_seconds,
                    division=self._extract_division(contest_name)
                )
                contests.append(contest)

            contests.sort(key=lambda c: c.start_time)
            logger.info(f"Successfully fetched {len(contests)} upcoming Codeforces contests.")

        except httpx.RequestError as exc:
            logger.error(f"Network error while fetching Codeforces contests: {exc}")
        except Exception as exc:
            logger.error(f"Unexpected error in CodeforcesFetcher: {exc}")

        return contests
