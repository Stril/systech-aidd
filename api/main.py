"""FastAPI application for bot statistics"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from api.mock_stat_collector import MockStatCollector
from api.models import StatsResponse
from api.real_stat_collector import RealStatCollector
from api.stat_collector import StatCollector
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

# Initialize collector based on configuration
settings = Settings()

if settings.USE_MOCK_STAT_COLLECTOR:
    collector: StatCollector = MockStatCollector()
else:
    collector: StatCollector = RealStatCollector(database_url=settings.DATABASE_URL)


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


@app.on_event("shutdown")
async def shutdown() -> None:
    """Cleanup on application shutdown"""
    if hasattr(collector, "close"):
        await collector.close()
