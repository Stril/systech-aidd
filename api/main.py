"""FastAPI application for bot statistics"""

import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from api.chat_handler import ChatHandler
from api.chat_models import ChatRequest, ChatResponse, ChatSessionCreate, ChatSessionInfo
from api.chat_session_manager import ChatSessionManager
from api.mock_stat_collector import MockStatCollector
from api.models import StatsResponse
from api.real_stat_collector import RealStatCollector
from api.stat_collector import StatCollector
from api.text2sql_handler import Text2SQLHandler
from api.user_utils import parse_username_to_user_id, validate_username
from src.models import User
from src.openai_client import OpenAIClient
from src.settings import Settings
from src.sqlite_storage import SQLiteStorage

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bot Statistics API",
    description="API для получения статистики диалогов бота",
    version="1.0.0",
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize settings
settings = Settings()  # type: ignore[call-arg]

# Initialize storage for user management
storage = SQLiteStorage(database_url=settings.DATABASE_URL)

# Initialize collector based on configuration
collector: StatCollector
if settings.USE_MOCK_STAT_COLLECTOR:
    collector = MockStatCollector()
else:
    collector = RealStatCollector(database_url=settings.DATABASE_URL)

# Initialize chat components
openai_client = OpenAIClient(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
    model=settings.OPENAI_MODEL,
)

text2sql_handler = Text2SQLHandler(
    openai_client=openai_client,
    database_url=settings.DATABASE_URL,
    text2sql_prompt=settings.text2sql_prompt,
)

chat_session_manager = ChatSessionManager(max_context_messages=10)

chat_handler = ChatHandler(
    openai_client=openai_client,
    system_prompt=settings.system_prompt,
    text2sql_handler=text2sql_handler,
    session_manager=chat_session_manager,
)


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats(
    period: str = Query(..., pattern="^(day|week)$", description="Statistics period"),
) -> StatsResponse:
    """Get bot statistics for specified period

    Args:
        period: Statistics period ("day" or "week")

    Returns:
        Statistics response with summary, activity chart, recent conversations and top users

    Raises:
        HTTPException: If invalid period is provided
    """
    try:
        return await collector.get_stats(period)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint

    Returns:
        Health status
    """
    return {"status": "ok"}


@app.post("/api/chat/session", response_model=ChatSessionInfo)
async def create_chat_session(request: ChatSessionCreate) -> ChatSessionInfo:
    """Create a new chat session with user registration

    Args:
        request: Session creation request with mode and username

    Returns:
        Session information with session_id, username, and user_id

    Raises:
        HTTPException: If username validation fails or session creation fails
    """
    try:
        # 1. Validate username format
        if not validate_username(request.username):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid username format. Expected 'User_NNNNN', got '{request.username}'",
            )

        # 2. Parse username to user_id (negative for web users)
        user_id = parse_username_to_user_id(request.username)

        # 3. Create or update user in database
        user = User(
            user_id=user_id,
            username=request.username,
            first_name=None,
            last_name=None,
            language_code=None,
            created_at=datetime.now(),
            message_count=0,
            deleted_at=None,
        )
        await storage.add_user(user)
        logger.info(f"User created/updated: {request.username} (id={user_id})")

        # 4. Create session with username and user_id
        session_id = chat_session_manager.create_session(
            mode=request.mode, username=request.username, user_id=user_id
        )

        return ChatSessionInfo(
            session_id=session_id,
            mode=request.mode,
            username=request.username,
            user_id=user_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}") from e


@app.post("/api/chat/message", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest) -> ChatResponse:
    """Send a message in chat session

    Args:
        request: Chat request with session_id, message, and mode

    Returns:
        Chat response with answer and optional SQL query

    Raises:
        HTTPException: If session not found or processing fails
    """
    try:
        # Get user_id from session for message_count increment
        username, user_id = chat_session_manager.get_session_user(request.session_id)

        # Process message
        response = await chat_handler.handle_message(
            session_id=request.session_id, message=request.message, mode=request.mode
        )

        # Increment message count in database
        await storage.increment_user_message_count(user_id)

        return response
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}") from e


@app.delete("/api/chat/session/{session_id}")
async def delete_chat_session(session_id: str) -> dict[str, str]:
    """Delete chat session

    Args:
        session_id: Session identifier

    Returns:
        Status response

    Raises:
        HTTPException: If session not found
    """
    try:
        chat_session_manager.clear_session(session_id)
        return {"status": "ok"}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.on_event("shutdown")
async def shutdown() -> None:
    """Cleanup on application shutdown"""
    if hasattr(collector, "close"):
        await collector.close()
    await text2sql_handler.close()
    await storage.close()
