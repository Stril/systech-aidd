"""Abstract interface for statistics collector"""

from abc import ABC, abstractmethod

from api.models import StatsResponse


class StatCollector(ABC):
    """Abstract base class for statistics collectors"""

    @abstractmethod
    async def get_stats(self, period: str) -> StatsResponse:
        """Collect statistics for specified period

        Args:
            period: Statistics period ("day" or "week")

        Returns:
            StatsResponse with collected statistics
        """
        pass
