"""Tests for RealStatCollector class"""

from datetime import datetime, timedelta

import pytest

from api.models import ActivityPoint, RecentConversationItem, StatsSummary, TopUserItem
from api.real_stat_collector import RealStatCollector
from src.database_models import Base, ConversationDB, MessageDB, UserDB


@pytest.fixture
async def collector():
    """Create RealStatCollector with in-memory database"""
    collector = RealStatCollector("sqlite+aiosqlite:///:memory:")

    # Create tables
    async with collector._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield collector

    await collector.close()


@pytest.fixture
async def populated_collector():
    """Create RealStatCollector with test data"""
    collector = RealStatCollector("sqlite+aiosqlite:///:memory:")

    # Create tables
    async with collector._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Populate with test data
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    async with collector._session_maker() as session:
        # Create users
        user1 = UserDB(
            user_id=1001,
            username="alice",
            first_name="Alice",
            last_name="Wonder",
            language_code="en",
            created_at=today_start - timedelta(days=5),
        )
        user2 = UserDB(
            user_id=1002,
            username="bob",
            first_name="Bob",
            last_name="Builder",
            language_code="en",
            created_at=today_start - timedelta(days=3),
        )
        user3 = UserDB(
            user_id=1003,
            username="charlie",
            first_name="Charlie",
            last_name="Brown",
            language_code="en",
            created_at=today_start - timedelta(days=1),
        )
        session.add_all([user1, user2, user3])
        await session.flush()

        # Create conversations for today
        conv1 = ConversationDB(
            user_id=1001,
            created_at=today_start + timedelta(hours=9),
            updated_at=today_start + timedelta(hours=10),
        )
        conv2 = ConversationDB(
            user_id=1002,
            created_at=today_start + timedelta(hours=10),
            updated_at=today_start + timedelta(hours=11),
        )
        conv3 = ConversationDB(
            user_id=1003,
            created_at=today_start + timedelta(hours=14),
            updated_at=today_start + timedelta(hours=15),
        )
        session.add_all([conv1, conv2, conv3])
        await session.flush()

        # Create messages for today
        messages = [
            # Conversation 1: 5 messages at hour 9-10
            MessageDB(
                conversation_id=conv1.id,
                user_id=1001,
                role="user",
                content="Hello",
                content_length=5,
                created_at=today_start + timedelta(hours=9, minutes=10),
            ),
            MessageDB(
                conversation_id=conv1.id,
                user_id=1001,
                role="assistant",
                content="Hi there!",
                content_length=9,
                created_at=today_start + timedelta(hours=9, minutes=11),
            ),
            MessageDB(
                conversation_id=conv1.id,
                user_id=1001,
                role="user",
                content="How are you?",
                content_length=12,
                created_at=today_start + timedelta(hours=9, minutes=15),
            ),
            MessageDB(
                conversation_id=conv1.id,
                user_id=1001,
                role="assistant",
                content="I'm good!",
                content_length=9,
                created_at=today_start + timedelta(hours=10, minutes=0),
            ),
            MessageDB(
                conversation_id=conv1.id,
                user_id=1001,
                role="user",
                content="Great!",
                content_length=6,
                created_at=today_start + timedelta(hours=10, minutes=5),
            ),
            # Conversation 2: 3 messages at hour 10-11
            MessageDB(
                conversation_id=conv2.id,
                user_id=1002,
                role="user",
                content="Test message",
                content_length=12,
                created_at=today_start + timedelta(hours=10, minutes=30),
            ),
            MessageDB(
                conversation_id=conv2.id,
                user_id=1002,
                role="assistant",
                content="Test response",
                content_length=13,
                created_at=today_start + timedelta(hours=10, minutes=31),
            ),
            MessageDB(
                conversation_id=conv2.id,
                user_id=1002,
                role="user",
                content="Thanks",
                content_length=6,
                created_at=today_start + timedelta(hours=11, minutes=0),
            ),
            # Conversation 3: 2 messages at hour 14-15
            MessageDB(
                conversation_id=conv3.id,
                user_id=1003,
                role="user",
                content="Quick question",
                content_length=14,
                created_at=today_start + timedelta(hours=14, minutes=20),
            ),
            MessageDB(
                conversation_id=conv3.id,
                user_id=1003,
                role="assistant",
                content="Sure, what is it?",
                content_length=17,
                created_at=today_start + timedelta(hours=14, minutes=21),
            ),
        ]
        session.add_all(messages)

        # Create conversation for yesterday (week stats)
        conv_yesterday = ConversationDB(
            user_id=1001,
            created_at=today_start - timedelta(days=1, hours=10),
            updated_at=today_start - timedelta(days=1, hours=11),
        )
        session.add(conv_yesterday)
        await session.flush()

        # Add messages to yesterday's conversation
        msg_yesterday = MessageDB(
            conversation_id=conv_yesterday.id,
            user_id=1001,
            role="user",
            content="Yesterday message",
            content_length=17,
            created_at=today_start - timedelta(days=1, hours=10),
        )
        session.add(msg_yesterday)

        await session.commit()

    yield collector

    await collector.close()


# Initialization tests


@pytest.mark.unit
@pytest.mark.asyncio
async def test_collector_initialization():
    """Test RealStatCollector initialization"""
    collector = RealStatCollector("sqlite+aiosqlite:///:memory:")
    assert collector is not None
    assert collector._engine is not None
    assert collector._session_maker is not None
    await collector.close()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_collector_close(collector: RealStatCollector):
    """Test closing database connections"""
    await collector.close()
    # Engine should be disposed after close
    assert collector._engine is not None


# get_stats tests


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_stats_empty_database(collector: RealStatCollector):
    """Test get_stats with empty database"""
    stats = await collector.get_stats("day")

    assert stats.period == "day"
    assert stats.summary.total_conversations == 0
    assert stats.summary.active_users == 0
    assert stats.summary.total_messages == 0
    assert stats.summary.average_conversation_length == 0.0
    assert len(stats.activity_chart) == 24  # 24 hours
    assert len(stats.recent_conversations) == 0
    assert len(stats.top_users) == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_stats_day_period(populated_collector: RealStatCollector):
    """Test get_stats for day period"""
    stats = await populated_collector.get_stats("day")

    assert stats.period == "day"
    assert stats.summary.total_conversations == 3
    assert stats.summary.active_users == 3
    assert stats.summary.total_messages == 10
    assert stats.summary.average_conversation_length > 0
    assert len(stats.activity_chart) == 24  # 24 hours
    assert len(stats.recent_conversations) > 0
    assert len(stats.top_users) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_stats_week_period(populated_collector: RealStatCollector):
    """Test get_stats for week period"""
    stats = await populated_collector.get_stats("week")

    assert stats.period == "week"
    assert stats.summary.total_conversations == 4  # 3 today + 1 yesterday
    assert stats.summary.active_users == 3
    assert stats.summary.total_messages == 11  # 10 today + 1 yesterday
    assert len(stats.activity_chart) == 7  # 7 days
    assert all(point.hour is None for point in stats.activity_chart)
    assert len(stats.recent_conversations) > 0
    assert len(stats.top_users) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_stats_invalid_period(collector: RealStatCollector):
    """Test get_stats with invalid period"""
    with pytest.raises(ValueError, match="Invalid period"):
        await collector.get_stats("month")


# _get_summary tests


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_summary_empty(collector: RealStatCollector):
    """Test _get_summary with empty database"""
    now = datetime.now()
    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

    async with collector._session_maker() as session:
        summary = await collector._get_summary(session, start_date)

    assert isinstance(summary, StatsSummary)
    assert summary.total_conversations == 0
    assert summary.active_users == 0
    assert summary.total_messages == 0
    assert summary.average_conversation_length == 0.0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_summary_with_data(populated_collector: RealStatCollector):
    """Test _get_summary with populated database"""
    now = datetime.now()
    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

    async with populated_collector._session_maker() as session:
        summary = await populated_collector._get_summary(session, start_date)

    assert isinstance(summary, StatsSummary)
    assert summary.total_conversations == 3
    assert summary.active_users == 3
    assert summary.total_messages == 10
    assert summary.average_conversation_length == 3.3  # 10 messages / 3 conversations


# _get_activity_chart tests


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_activity_chart_day(populated_collector: RealStatCollector):
    """Test _get_activity_chart for day period"""
    now = datetime.now()
    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

    async with populated_collector._session_maker() as session:
        activity_chart = await populated_collector._get_activity_chart(session, start_date, "day")

    assert len(activity_chart) == 24
    assert all(isinstance(point, ActivityPoint) for point in activity_chart)
    assert all(point.hour is not None for point in activity_chart)
    assert all(point.hour >= 0 and point.hour <= 23 for point in activity_chart)

    # Check that hour 9-10 has messages
    hour_9 = next(p for p in activity_chart if p.hour == 9)
    hour_10 = next(p for p in activity_chart if p.hour == 10)
    assert hour_9.message_count > 0
    assert hour_10.message_count > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_activity_chart_week(populated_collector: RealStatCollector):
    """Test _get_activity_chart for week period"""
    now = datetime.now()
    start_date = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)

    async with populated_collector._session_maker() as session:
        activity_chart = await populated_collector._get_activity_chart(session, start_date, "week")

    assert len(activity_chart) == 7
    assert all(isinstance(point, ActivityPoint) for point in activity_chart)
    assert all(point.hour is None for point in activity_chart)
    assert all(point.date is not None for point in activity_chart)


# _get_recent_conversations tests


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_recent_conversations_empty(collector: RealStatCollector):
    """Test _get_recent_conversations with empty database"""
    now = datetime.now()
    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

    async with collector._session_maker() as session:
        recent = await collector._get_recent_conversations(session, start_date, 10)

    assert len(recent) == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_recent_conversations_with_data(populated_collector: RealStatCollector):
    """Test _get_recent_conversations with populated database"""
    now = datetime.now()
    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

    async with populated_collector._session_maker() as session:
        recent = await populated_collector._get_recent_conversations(session, start_date, 10)

    assert len(recent) == 3  # 3 conversations today
    assert all(isinstance(item, RecentConversationItem) for item in recent)
    assert all(item.user_id is not None for item in recent)
    assert all(item.message_count > 0 for item in recent)

    # Check ordering by updated_at desc
    for i in range(len(recent) - 1):
        assert recent[i].updated_at >= recent[i + 1].updated_at


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_recent_conversations_limit(populated_collector: RealStatCollector):
    """Test _get_recent_conversations respects limit"""
    now = datetime.now()
    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

    async with populated_collector._session_maker() as session:
        recent = await populated_collector._get_recent_conversations(session, start_date, 2)

    assert len(recent) == 2  # Limited to 2


# _get_top_users tests


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_top_users_empty(collector: RealStatCollector):
    """Test _get_top_users with empty database"""
    now = datetime.now()
    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

    async with collector._session_maker() as session:
        top_users = await collector._get_top_users(session, start_date, 5)

    assert len(top_users) == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_top_users_with_data(populated_collector: RealStatCollector):
    """Test _get_top_users with populated database"""
    now = datetime.now()
    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

    async with populated_collector._session_maker() as session:
        top_users = await populated_collector._get_top_users(session, start_date, 5)

    assert len(top_users) == 3  # 3 users today
    assert all(isinstance(item, TopUserItem) for item in top_users)
    assert all(item.user_id is not None for item in top_users)
    assert all(item.message_count > 0 for item in top_users)
    assert all(item.conversation_count > 0 for item in top_users)

    # Check ordering by message_count desc
    for i in range(len(top_users) - 1):
        assert top_users[i].message_count >= top_users[i + 1].message_count


@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_top_users_limit(populated_collector: RealStatCollector):
    """Test _get_top_users respects limit"""
    now = datetime.now()
    start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

    async with populated_collector._session_maker() as session:
        top_users = await populated_collector._get_top_users(session, start_date, 2)

    assert len(top_users) <= 2  # Limited to 2


# Soft delete tests


@pytest.mark.integration
@pytest.mark.asyncio
async def test_soft_deleted_not_included():
    """Test that soft deleted records are not included in statistics"""
    collector = RealStatCollector("sqlite+aiosqlite:///:memory:")

    # Create tables
    async with collector._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    async with collector._session_maker() as session:
        # Create user and conversation
        user = UserDB(
            user_id=1001,
            username="test",
            first_name="Test",
            created_at=today_start,
            deleted_at=today_start + timedelta(hours=1),  # Soft deleted
        )
        session.add(user)
        await session.flush()

        conv = ConversationDB(
            user_id=1001,
            created_at=today_start + timedelta(hours=2),
            updated_at=today_start + timedelta(hours=3),
            deleted_at=today_start + timedelta(hours=4),  # Soft deleted
        )
        session.add(conv)
        await session.flush()

        msg = MessageDB(
            conversation_id=conv.id,
            user_id=1001,
            role="user",
            content="Test",
            content_length=4,
            created_at=today_start + timedelta(hours=2),
            deleted_at=today_start + timedelta(hours=5),  # Soft deleted
        )
        session.add(msg)
        await session.commit()

    # Get stats - should be empty because all records are soft deleted
    stats = await collector.get_stats("day")

    assert stats.summary.total_conversations == 0
    assert stats.summary.active_users == 0
    assert stats.summary.total_messages == 0
    assert len(stats.recent_conversations) == 0
    assert len(stats.top_users) == 0

    await collector.close()
