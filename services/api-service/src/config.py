"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """API Service configuration."""

    valkey_endpoint: str = "localhost"
    valkey_port: int = 6379
    valkey_use_tls: bool = False
    dynamodb_table: str = "family-copilot-prod-vehicle-profiles"
    agent_service_url: str = "http://localhost:8081"
    environment: str = "local"
    aws_region: str = "us-east-1"
    transcribe_mode: str = "FALLBACK"  # LIVE | FALLBACK
    host: str = "0.0.0.0"
    port: int = 8080

    model_config = {"env_prefix": "", "case_sensitive": False}


settings = Settings()
