FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/tmp/uv-cache

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app
RUN mkdir -p /tmp/uv-cache && chown -R app:app /tmp/uv-cache

COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev

COPY --chown=app:app app ./app
COPY --chown=app:app alembic ./alembic
COPY --chown=app:app alembic.ini ./alembic.ini

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8000') + '/api/health/live')"]

CMD ["sh", "-c", "exec /app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
