"""Mock implementation of statistics collector"""

from datetime import datetime, timedelta

from api.models import (
    ActivityPoint,
    RecentConversationItem,
    StatsResponse,
    StatsSummary,
    TopUserItem,
)
from api.stat_collector import StatCollector


class MockStatCollector(StatCollector):
    """Mock statistics collector with hardcoded test data"""

    async def get_stats(self, period: str) -> StatsResponse:
        """Get mock statistics for specified period

        Args:
            period: Statistics period ("day" or "week")

        Returns:
            StatsResponse with mock data
        """
        if period == "day":
            return self._get_day_stats()
        elif period == "week":
            return self._get_week_stats()
        else:
            raise ValueError(f"Invalid period: {period}")

    def _get_day_stats(self) -> StatsResponse:
        """Get mock statistics for day period"""
        today = datetime.now().date()

        return StatsResponse(
            period="day",
            summary=StatsSummary(
                total_conversations=52,
                active_users=25,
                average_conversation_length=12.5,
                total_messages=650,
            ),
            activity_chart=[
                ActivityPoint(date=str(today), hour=0, message_count=15, conversation_count=3),
                ActivityPoint(date=str(today), hour=1, message_count=8, conversation_count=2),
                ActivityPoint(date=str(today), hour=2, message_count=5, conversation_count=1),
                ActivityPoint(date=str(today), hour=3, message_count=3, conversation_count=1),
                ActivityPoint(date=str(today), hour=4, message_count=2, conversation_count=1),
                ActivityPoint(date=str(today), hour=5, message_count=7, conversation_count=2),
                ActivityPoint(date=str(today), hour=6, message_count=18, conversation_count=4),
                ActivityPoint(date=str(today), hour=7, message_count=25, conversation_count=5),
                ActivityPoint(date=str(today), hour=8, message_count=35, conversation_count=7),
                ActivityPoint(date=str(today), hour=9, message_count=42, conversation_count=8),
                ActivityPoint(date=str(today), hour=10, message_count=48, conversation_count=9),
                ActivityPoint(date=str(today), hour=11, message_count=38, conversation_count=7),
                ActivityPoint(date=str(today), hour=12, message_count=32, conversation_count=6),
                ActivityPoint(date=str(today), hour=13, message_count=40, conversation_count=8),
                ActivityPoint(date=str(today), hour=14, message_count=45, conversation_count=9),
                ActivityPoint(date=str(today), hour=15, message_count=50, conversation_count=10),
                ActivityPoint(date=str(today), hour=16, message_count=55, conversation_count=11),
                ActivityPoint(date=str(today), hour=17, message_count=48, conversation_count=9),
                ActivityPoint(date=str(today), hour=18, message_count=42, conversation_count=8),
                ActivityPoint(date=str(today), hour=19, message_count=38, conversation_count=7),
                ActivityPoint(date=str(today), hour=20, message_count=35, conversation_count=6),
                ActivityPoint(date=str(today), hour=21, message_count=28, conversation_count=5),
                ActivityPoint(date=str(today), hour=22, message_count=22, conversation_count=4),
                ActivityPoint(date=str(today), hour=23, message_count=18, conversation_count=3),
            ],
            recent_conversations=[
                RecentConversationItem(
                    id=101,
                    user_id=1001,
                    username="alice_wonder",
                    message_count=24,
                    created_at=datetime.now() - timedelta(hours=2, minutes=15),
                    updated_at=datetime.now() - timedelta(minutes=5),
                ),
                RecentConversationItem(
                    id=102,
                    user_id=1002,
                    username="bob_builder",
                    message_count=18,
                    created_at=datetime.now() - timedelta(hours=3, minutes=30),
                    updated_at=datetime.now() - timedelta(minutes=12),
                ),
                RecentConversationItem(
                    id=103,
                    user_id=1003,
                    username="charlie_brown",
                    message_count=15,
                    created_at=datetime.now() - timedelta(hours=4, minutes=45),
                    updated_at=datetime.now() - timedelta(minutes=20),
                ),
                RecentConversationItem(
                    id=104,
                    user_id=1004,
                    username="diana_prince",
                    message_count=22,
                    created_at=datetime.now() - timedelta(hours=5, minutes=10),
                    updated_at=datetime.now() - timedelta(minutes=25),
                ),
                RecentConversationItem(
                    id=105,
                    user_id=1005,
                    username="eve_online",
                    message_count=12,
                    created_at=datetime.now() - timedelta(hours=6, minutes=20),
                    updated_at=datetime.now() - timedelta(minutes=35),
                ),
                RecentConversationItem(
                    id=106,
                    user_id=1006,
                    username="frank_ocean",
                    message_count=16,
                    created_at=datetime.now() - timedelta(hours=7, minutes=5),
                    updated_at=datetime.now() - timedelta(minutes=40),
                ),
                RecentConversationItem(
                    id=107,
                    user_id=1007,
                    username="grace_hopper",
                    message_count=20,
                    created_at=datetime.now() - timedelta(hours=8, minutes=15),
                    updated_at=datetime.now() - timedelta(minutes=50),
                ),
                RecentConversationItem(
                    id=108,
                    user_id=1008,
                    username="harry_potter",
                    message_count=14,
                    created_at=datetime.now() - timedelta(hours=9, minutes=30),
                    updated_at=datetime.now() - timedelta(hours=1, minutes=5),
                ),
                RecentConversationItem(
                    id=109,
                    user_id=1009,
                    username="iris_west",
                    message_count=19,
                    created_at=datetime.now() - timedelta(hours=10, minutes=45),
                    updated_at=datetime.now() - timedelta(hours=1, minutes=15),
                ),
                RecentConversationItem(
                    id=110,
                    user_id=1010,
                    username="jack_sparrow",
                    message_count=13,
                    created_at=datetime.now() - timedelta(hours=11, minutes=20),
                    updated_at=datetime.now() - timedelta(hours=1, minutes=30),
                ),
            ],
            top_users=[
                TopUserItem(
                    user_id=1001,
                    username="alice_wonder",
                    first_name="Alice",
                    conversation_count=8,
                    message_count=95,
                ),
                TopUserItem(
                    user_id=1004,
                    username="diana_prince",
                    first_name="Diana",
                    conversation_count=7,
                    message_count=88,
                ),
                TopUserItem(
                    user_id=1007,
                    username="grace_hopper",
                    first_name="Grace",
                    conversation_count=6,
                    message_count=76,
                ),
                TopUserItem(
                    user_id=1002,
                    username="bob_builder",
                    first_name="Bob",
                    conversation_count=5,
                    message_count=65,
                ),
                TopUserItem(
                    user_id=1009,
                    username="iris_west",
                    first_name="Iris",
                    conversation_count=5,
                    message_count=58,
                ),
            ],
        )

    def _get_week_stats(self) -> StatsResponse:
        """Get mock statistics for week period"""
        today = datetime.now().date()

        return StatsResponse(
            period="week",
            summary=StatsSummary(
                total_conversations=312,
                active_users=95,
                average_conversation_length=14.8,
                total_messages=4618,
            ),
            activity_chart=[
                ActivityPoint(
                    date=str(today - timedelta(days=6)),
                    hour=None,
                    message_count=580,
                    conversation_count=38,
                ),
                ActivityPoint(
                    date=str(today - timedelta(days=5)),
                    hour=None,
                    message_count=620,
                    conversation_count=42,
                ),
                ActivityPoint(
                    date=str(today - timedelta(days=4)),
                    hour=None,
                    message_count=695,
                    conversation_count=48,
                ),
                ActivityPoint(
                    date=str(today - timedelta(days=3)),
                    hour=None,
                    message_count=710,
                    conversation_count=51,
                ),
                ActivityPoint(
                    date=str(today - timedelta(days=2)),
                    hour=None,
                    message_count=665,
                    conversation_count=45,
                ),
                ActivityPoint(
                    date=str(today - timedelta(days=1)),
                    hour=None,
                    message_count=698,
                    conversation_count=46,
                ),
                ActivityPoint(date=str(today), hour=None, message_count=650, conversation_count=42),
            ],
            recent_conversations=[
                RecentConversationItem(
                    id=201,
                    user_id=2001,
                    username="alice_wonder",
                    message_count=28,
                    created_at=datetime.now() - timedelta(hours=2, minutes=30),
                    updated_at=datetime.now() - timedelta(minutes=10),
                ),
                RecentConversationItem(
                    id=202,
                    user_id=2002,
                    username="bob_builder",
                    message_count=22,
                    created_at=datetime.now() - timedelta(hours=4, minutes=15),
                    updated_at=datetime.now() - timedelta(minutes=25),
                ),
                RecentConversationItem(
                    id=203,
                    user_id=2003,
                    username="charlie_brown",
                    message_count=19,
                    created_at=datetime.now() - timedelta(hours=6, minutes=45),
                    updated_at=datetime.now() - timedelta(minutes=40),
                ),
                RecentConversationItem(
                    id=204,
                    user_id=2004,
                    username="diana_prince",
                    message_count=26,
                    created_at=datetime.now() - timedelta(hours=8, minutes=20),
                    updated_at=datetime.now() - timedelta(minutes=55),
                ),
                RecentConversationItem(
                    id=205,
                    user_id=2005,
                    username="eve_online",
                    message_count=15,
                    created_at=datetime.now() - timedelta(hours=10, minutes=35),
                    updated_at=datetime.now() - timedelta(hours=1, minutes=15),
                ),
                RecentConversationItem(
                    id=206,
                    user_id=2006,
                    username="frank_ocean",
                    message_count=20,
                    created_at=datetime.now() - timedelta(hours=12, minutes=50),
                    updated_at=datetime.now() - timedelta(hours=1, minutes=30),
                ),
                RecentConversationItem(
                    id=207,
                    user_id=2007,
                    username="grace_hopper",
                    message_count=24,
                    created_at=datetime.now() - timedelta(hours=14, minutes=10),
                    updated_at=datetime.now() - timedelta(hours=2, minutes=5),
                ),
                RecentConversationItem(
                    id=208,
                    user_id=2008,
                    username="harry_potter",
                    message_count=18,
                    created_at=datetime.now() - timedelta(hours=16, minutes=25),
                    updated_at=datetime.now() - timedelta(hours=2, minutes=20),
                ),
                RecentConversationItem(
                    id=209,
                    user_id=2009,
                    username="iris_west",
                    message_count=23,
                    created_at=datetime.now() - timedelta(hours=18, minutes=40),
                    updated_at=datetime.now() - timedelta(hours=3, minutes=10),
                ),
                RecentConversationItem(
                    id=210,
                    user_id=2010,
                    username="jack_sparrow",
                    message_count=17,
                    created_at=datetime.now() - timedelta(hours=20, minutes=55),
                    updated_at=datetime.now() - timedelta(hours=3, minutes=35),
                ),
                RecentConversationItem(
                    id=211,
                    user_id=2011,
                    username="kate_bishop",
                    message_count=21,
                    created_at=datetime.now() - timedelta(days=1, hours=1, minutes=10),
                    updated_at=datetime.now() - timedelta(hours=4, minutes=15),
                ),
                RecentConversationItem(
                    id=212,
                    user_id=2012,
                    username="luke_skywalker",
                    message_count=16,
                    created_at=datetime.now() - timedelta(days=1, hours=3, minutes=25),
                    updated_at=datetime.now() - timedelta(hours=5, minutes=30),
                ),
                RecentConversationItem(
                    id=213,
                    user_id=2013,
                    username="mary_jane",
                    message_count=25,
                    created_at=datetime.now() - timedelta(days=1, hours=5, minutes=40),
                    updated_at=datetime.now() - timedelta(hours=6, minutes=45),
                ),
                RecentConversationItem(
                    id=214,
                    user_id=2014,
                    username="nick_fury",
                    message_count=14,
                    created_at=datetime.now() - timedelta(days=1, hours=7, minutes=55),
                    updated_at=datetime.now() - timedelta(hours=8, minutes=20),
                ),
                RecentConversationItem(
                    id=215,
                    user_id=2015,
                    username="olivia_pope",
                    message_count=22,
                    created_at=datetime.now() - timedelta(days=1, hours=10, minutes=15),
                    updated_at=datetime.now() - timedelta(hours=10, minutes=5),
                ),
            ],
            top_users=[
                TopUserItem(
                    user_id=2001,
                    username="alice_wonder",
                    first_name="Alice",
                    conversation_count=42,
                    message_count=588,
                ),
                TopUserItem(
                    user_id=2004,
                    username="diana_prince",
                    first_name="Diana",
                    conversation_count=38,
                    message_count=532,
                ),
                TopUserItem(
                    user_id=2007,
                    username="grace_hopper",
                    first_name="Grace",
                    conversation_count=35,
                    message_count=490,
                ),
                TopUserItem(
                    user_id=2013,
                    username="mary_jane",
                    first_name="Mary",
                    conversation_count=32,
                    message_count=448,
                ),
                TopUserItem(
                    user_id=2002,
                    username="bob_builder",
                    first_name="Bob",
                    conversation_count=30,
                    message_count=420,
                ),
                TopUserItem(
                    user_id=2009,
                    username="iris_west",
                    first_name="Iris",
                    conversation_count=28,
                    message_count=392,
                ),
                TopUserItem(
                    user_id=2011,
                    username="kate_bishop",
                    first_name="Kate",
                    conversation_count=26,
                    message_count=364,
                ),
                TopUserItem(
                    user_id=2003,
                    username="charlie_brown",
                    first_name="Charlie",
                    conversation_count=24,
                    message_count=336,
                ),
                TopUserItem(
                    user_id=2015,
                    username="olivia_pope",
                    first_name="Olivia",
                    conversation_count=22,
                    message_count=308,
                ),
                TopUserItem(
                    user_id=2006,
                    username="frank_ocean",
                    first_name="Frank",
                    conversation_count=20,
                    message_count=280,
                ),
            ],
        )
