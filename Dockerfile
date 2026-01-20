# Multi-stage build for GEO Pulse
# Single image that runs both FastAPI backend and Streamlit frontend

FROM python:3.12-slim as base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY src/ ./src/
COPY .python-version ./

COPY docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# 8000: FastAPI backend
# 8501: Streamlit frontend
EXPOSE 8000 8501

ENV PYTHONPATH=/app
ENV API_URL=http://localhost:8000

# Run entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]
