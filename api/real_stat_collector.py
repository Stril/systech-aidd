"""Real implementation of statistics collector using SQLite database"""

import logging
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.models import (
    ActivityPoint,
    RecentConversationItem,
    StatsResponse,
    StatsSummary,
    TopUserItem,
)
from api.stat_collector import StatCollector
from src.database_models import ConversationDB, MessageDB, UserDB

logger = logging.getLogger(__name__)


class RealStatCollector(StatCollector):
    """Real statistics collector that queries SQLite database"""

    def __init__(self, database_url: str) -> None:
        """
        Initialize real statistics collector

        Args:
            database_url: Database connection string (e.g. sqlite+aiosqlite:///data/bot.db)
        """
        self._engine = create_async_engine(database_url, echo=False)
        self._session_maker = async_sessionmaker(
            self._engine, class_=AsyncSession, expire_on_commit=False
        )
        logger.info(f"real_stat_collector|status=initialized|database_url={database_url}")

    async def close(self) -> None:
        """Close database connections"""
        await self._engine.dispose()
        logger.info("real_stat_collector|status=closed")

    async def get_stats(self, period: str) -> StatsResponse:
        """Get statistics for specified period

        Args:
            period: Statistics period ("day" or "week")

        Returns:
            StatsResponse with collected statistics

        Raises:
            ValueError: If invalid period is provided
        """
        if period not in ("day", "week"):
            raise ValueError(f"Invalid period: {period}")

        # Calculate start date based on period
        now = datetime.now()
        if period == "day":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            recent_limit = 10
            top_users_limit = 5
        else:  # week
            start_date = (now - timedelta(days=6)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            recent_limit = 15
            top_users_limit = 10

        logger.info(f"real_stat_collector|collecting_stats|period={period}|start_date={start_date}")

        # Collect all statistics in parallel
        async with self._session_maker() as session:
            summary = await self._get_summary(session, start_date)
            activity_chart = await self._get_activity_chart(session, start_date, period)
            recent_conversations = await self._get_recent_conversations(
                session, start_date, recent_limit
            )
            top_users = await self._get_top_users(session, start_date, top_users_limit)

        logger.info(
            f"real_stat_collector|stats_collected|period={period}|"
            f"conversations={summary.total_conversations}|messages={summary.total_messages}"
        )

        return StatsResponse(
            period=period,
            summary=summary,
            activity_chart=activity_chart,
            recent_conversations=recent_conversations,
            top_users=top_users,
        )

    async def _get_summary(self, session: AsyncSession, start_date: datetime) -> StatsSummary:
        """Get summary statistics

        Args:
            session: Database session
            start_date: Start date for statistics

        Returns:
            StatsSummary with aggregate metrics
        """
        # Count total conversations
        stmt_conversations = select(func.count(ConversationDB.id)).where(
            ConversationDB.created_at >= start_date,
            ConversationDB.deleted_at.is_(None),
        )
        result = await session.execute(stmt_conversations)
        total_conversations = result.scalar_one() or 0

        # Count active users (users with messages in period)
        stmt_users = (
            select(func.count(func.distinct(MessageDB.user_id)))
            .where(
                MessageDB.created_at >= start_date,
                MessageDB.deleted_at.is_(None),
            )
        )
        result = await session.execute(stmt_users)
        active_users = result.scalar_one() or 0

        # Count total messages
        stmt_messages = select(func.count(MessageDB.id)).where(
            MessageDB.created_at >= start_date,
            MessageDB.deleted_at.is_(None),
        )
        result = await session.execute(stmt_messages)
        total_messages = result.scalar_one() or 0

        # Calculate average conversation length
        if total_conversations > 0:
            average_conversation_length = total_messages / total_conversations
        else:
            average_conversation_length = 0.0

        logger.info(
            f"real_stat_collector|summary|conversations={total_conversations}|"
            f"users={active_users}|messages={total_messages}|avg_length={average_conversation_length:.2f}"
        )

        return StatsSummary(
            total_conversations=total_conversations,
            active_users=active_users,
            average_conversation_length=round(average_conversation_length, 1),
            total_messages=total_messages,
        )

    async def _get_activity_chart(
        self, session: AsyncSession, start_date: datetime, period: str
    ) -> list[ActivityPoint]:
        """Get activity chart data

        Args:
            session: Database session
            start_date: Start date for statistics
            period: Period type ("day" or "week")

        Returns:
            List of ActivityPoint with aggregated data by hour or day
        """
        if period == "day":
            # Group by hour for day period
            activity_points = []
            today = start_date.date()

            for hour in range(24):
                hour_start = datetime.combine(today, datetime.min.time()).replace(hour=hour)
                hour_end = hour_start + timedelta(hours=1)

                # Count messages in this hour
                stmt_messages = select(func.count(MessageDB.id)).where(
                    MessageDB.created_at >= hour_start,
                    MessageDB.created_at < hour_end,
                    MessageDB.deleted_at.is_(None),
                )
                result = await session.execute(stmt_messages)
                message_count = result.scalar_one() or 0

                # Count distinct conversations (by updated_at in this hour)
                stmt_conversations = (
                    select(func.count(func.distinct(MessageDB.conversation_id)))
                    .where(
                        MessageDB.created_at >= hour_start,
                        MessageDB.created_at < hour_end,
                        MessageDB.deleted_at.is_(None),
                    )
                )
                result = await session.execute(stmt_conversations)
                conversation_count = result.scalar_one() or 0

                activity_points.append(
                    ActivityPoint(
                        date=str(today),
                        hour=hour,
                        message_count=message_count,
                        conversation_count=conversation_count,
                    )
                )

        else:  # week
            # Group by day for week period
            activity_points = []

            for day_offset in range(7):
                day_start = start_date + timedelta(days=day_offset)
                day_end = day_start + timedelta(days=1)

                # Count messages in this day
                stmt_messages = select(func.count(MessageDB.id)).where(
                    MessageDB.created_at >= day_start,
                    MessageDB.created_at < day_end,
                    MessageDB.deleted_at.is_(None),
                )
                result = await session.execute(stmt_messages)
                message_count = result.scalar_one() or 0

                # Count distinct conversations in this day
                stmt_conversations = (
                    select(func.count(func.distinct(MessageDB.conversation_id)))
                    .where(
                        MessageDB.created_at >= day_start,
                        MessageDB.created_at < day_end,
                        MessageDB.deleted_at.is_(None),
                    )
                )
                result = await session.execute(stmt_conversations)
                conversation_count = result.scalar_one() or 0

                activity_points.append(
                    ActivityPoint(
                        date=str(day_start.date()),
                        hour=None,
                        message_count=message_count,
                        conversation_count=conversation_count,
                    )
                )

        logger.info(
            f"real_stat_collector|activity_chart|period={period}|points={len(activity_points)}"
        )
        return activity_points

    async def _get_recent_conversations(
        self, session: AsyncSession, start_date: datetime, limit: int
    ) -> list[RecentConversationItem]:
        """Get recent conversations

        Args:
            session: Database session
            start_date: Start date for statistics
            limit: Maximum number of conversations to return

        Returns:
            List of RecentConversationItem ordered by updated_at desc
        """
        # Get recent conversations with user info and message count
        stmt = (
            select(
                ConversationDB.id,
                ConversationDB.user_id,
                ConversationDB.created_at,
                ConversationDB.updated_at,
                UserDB.username,
                func.count(MessageDB.id).label("message_count"),
            )
            .join(UserDB, ConversationDB.user_id == UserDB.user_id)
            .outerjoin(
                MessageDB,
                (MessageDB.conversation_id == ConversationDB.id)
                & (MessageDB.deleted_at.is_(None)),
            )
            .where(
                ConversationDB.created_at >= start_date,
                ConversationDB.deleted_at.is_(None),
                UserDB.deleted_at.is_(None),
            )
            .group_by(
                ConversationDB.id,
                ConversationDB.user_id,
                ConversationDB.created_at,
                ConversationDB.updated_at,
                UserDB.username,
            )
            .order_by(ConversationDB.updated_at.desc())
            .limit(limit)
        )

        result = await session.execute(stmt)
        rows = result.all()

        recent_conversations = [
            RecentConversationItem(
                id=row.id,
                user_id=row.user_id,
                username=row.username,
                message_count=row.message_count,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]

        logger.info(
            f"real_stat_collector|recent_conversations|count={len(recent_conversations)}"
        )
        return recent_conversations

    async def _get_top_users(
        self, session: AsyncSession, start_date: datetime, limit: int
    ) -> list[TopUserItem]:
        """Get top users by activity

        Args:
            session: Database session
            start_date: Start date for statistics
            limit: Maximum number of users to return

        Returns:
            List of TopUserItem ordered by message count desc
        """
        # Get top users with conversation and message counts
        stmt = (
            select(
                UserDB.user_id,
                UserDB.username,
                UserDB.first_name,
                func.count(func.distinct(ConversationDB.id)).label("conversation_count"),
                func.count(MessageDB.id).label("message_count"),
            )
            .join(ConversationDB, UserDB.user_id == ConversationDB.user_id)
            .join(
                MessageDB,
                (MessageDB.conversation_id == ConversationDB.id)
                & (MessageDB.deleted_at.is_(None)),
            )
            .where(
                ConversationDB.created_at >= start_date,
                ConversationDB.deleted_at.is_(None),
                UserDB.deleted_at.is_(None),
            )
            .group_by(UserDB.user_id, UserDB.username, UserDB.first_name)
            .order_by(func.count(MessageDB.id).desc())
            .limit(limit)
        )

        result = await session.execute(stmt)
        rows = result.all()

        top_users = [
            TopUserItem(
                user_id=row.user_id,
                username=row.username,
                first_name=row.first_name,
                conversation_count=row.conversation_count,
                message_count=row.message_count,
            )
            for row in rows
        ]

        logger.info(f"real_stat_collector|top_users|count={len(top_users)}")
        return top_users

