# Multi-stage build for LLM Telegram Bot

# Builder stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv sync --no-dev

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install uv in runtime
RUN pip install --no-cache-dir uv

# Copy from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

# Copy application code
COPY src/ /app/src/
COPY system_prompt.txt /app/system_prompt.txt
COPY migrations/ /app/migrations/
COPY alembic.ini /app/alembic.ini

# Create data directory
RUN mkdir -p /app/data /app/logs

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# Run migrations and start bot
CMD ["sh", "-c", "alembic upgrade head && python -m src.main"]

