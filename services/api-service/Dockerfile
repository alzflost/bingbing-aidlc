FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy shared models
COPY shared/ /app/shared/

# Copy service
COPY services/api-service/ /app/services/api-service/

# Copy frontend build
COPY frontend/dist/ /app/static/

# Install dependencies
RUN uv pip install --system --no-cache \
    "pydantic>=2.0.0" "fastapi>=0.115.0" "uvicorn[standard]>=0.30.0" \
    "websockets>=13.0" "pydantic-settings>=2.0.0" "redis>=5.0.0" \
    "httpx>=0.27.0" "structlog>=24.0.0" "boto3>=1.35.0" \
    "amazon-transcribe>=0.6.0"

ENV PYTHONPATH="/app:/app/services/api-service"

WORKDIR /app/services/api-service

EXPOSE 8080

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
