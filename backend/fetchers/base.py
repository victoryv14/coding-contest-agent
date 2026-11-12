from abc import ABC, abstractmethod
from typing import List
from backend.models.contest import Contest


class BaseFetcher(ABC):
    """
    Abstract Base Class for all contest platform fetchers.
    """

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """The identifier of the platform (e.g. 'codeforces', 'leetcode', 'codechef')."""
        pass

    @abstractmethod
    async def fetch_contests(self) -> List[Contest]:
        """
        Fetch upcoming contests from the platform.

        Returns:
            List[Contest]: A list of standardized, validated Contest objects.
        """
        pass
