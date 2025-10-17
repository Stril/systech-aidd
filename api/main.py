"""FastAPI application for bot statistics"""

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
from src.openai_client import OpenAIClient
from src.settings import Settings

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
    """Create a new chat session

    Args:
        request: Session creation request with mode

    Returns:
        Session information with session_id
    """
    try:
        session_id = chat_session_manager.create_session(request.mode)
        return ChatSessionInfo(session_id=session_id, mode=request.mode)
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
        response = await chat_handler.handle_message(
            session_id=request.session_id, message=request.message, mode=request.mode
        )
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
