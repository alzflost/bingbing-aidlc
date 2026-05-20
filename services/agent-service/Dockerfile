FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy shared models + prompts
COPY shared/ /app/shared/

# Copy service
COPY services/agent-service/ /app/services/agent-service/

# Install dependencies
RUN uv pip install --system --no-cache \
    /app/shared \
    /app/services/agent-service

WORKDIR /app/services/agent-service

EXPOSE 8081

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8081"]
