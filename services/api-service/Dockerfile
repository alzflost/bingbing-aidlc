FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy shared models
COPY shared/ /app/shared/

# Copy service
COPY services/api-service/ /app/services/api-service/

# Install dependencies
RUN uv pip install --system --no-cache \
    /app/shared \
    /app/services/api-service

WORKDIR /app/services/api-service

ENV PYTHONPATH="/app:/app/services/api-service"

EXPOSE 8080

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
