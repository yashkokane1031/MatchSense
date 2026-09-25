FROM python:3.12-slim AS base

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY backend/ backend/
COPY ml/ ml/
COPY data/ data/
COPY alembic/ alembic/
COPY alembic.ini ./

EXPOSE 8000

CMD ["sh", "-c", "uv run uvicorn backend.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
