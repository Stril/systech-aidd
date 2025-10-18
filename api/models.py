"""Pydantic models for API contract"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class StatsSummary(BaseModel):
    """Summary statistics"""

    total_conversations: int = Field(..., description="Total number of conversations")
    active_users: int = Field(..., description="Number of active users")
    average_conversation_length: float = Field(
        ..., description="Average number of messages per conversation"
    )
    total_messages: int = Field(..., description="Total number of messages")


class ActivityPoint(BaseModel):
    """Activity chart data point"""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    hour: int | None = Field(None, description="Hour of the day (0-23) for day period")
    message_count: int = Field(..., description="Number of messages")
    conversation_count: int = Field(..., description="Number of conversations")


class RecentConversationItem(BaseModel):
    """Recent conversation information"""

    id: int = Field(..., description="Conversation ID")
    user_id: int = Field(..., description="User ID")
    username: str | None = Field(None, description="Username")
    message_count: int = Field(..., description="Number of messages in conversation")
    created_at: datetime = Field(..., description="Conversation creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class TopUserItem(BaseModel):
    """Top user statistics"""

    user_id: int = Field(..., description="User ID")
    username: str | None = Field(None, description="Username")
    first_name: str | None = Field(None, description="User first name")
    conversation_count: int = Field(..., description="Number of conversations")
    message_count: int = Field(..., description="Total number of messages")


class StatsResponse(BaseModel):
    """Statistics API response"""

    period: Literal["day", "week"] = Field(..., description="Statistics period")
    summary: StatsSummary = Field(..., description="Summary statistics")
    activity_chart: list[ActivityPoint] = Field(..., description="Activity chart data")
    recent_conversations: list[RecentConversationItem] = Field(
        ..., description="Recent conversations list"
    )
    top_users: list[TopUserItem] = Field(..., description="Top users by activity")
