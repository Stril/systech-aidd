"""Pydantic models for Chat API"""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message model"""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatSessionCreate(BaseModel):
    """Request to create a new chat session"""

    mode: str = Field(..., pattern="^(normal|admin)$", description="Chat mode: 'normal' or 'admin'")


class ChatSessionInfo(BaseModel):
    """Chat session information"""

    session_id: str = Field(..., description="Unique session identifier (UUID)")
    mode: str = Field(..., description="Chat mode: 'normal' or 'admin'")


class ChatRequest(BaseModel):
    """Request to send a message in chat"""

    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., min_length=1, description="User message")
    mode: str = Field(..., pattern="^(normal|admin)$", description="Chat mode: 'normal' or 'admin'")


class ChatResponse(BaseModel):
    """Response from chat API"""

    content: str = Field(..., description="Assistant response content")
    sql_query: str | None = Field(None, description="SQL query used (admin mode only)")

