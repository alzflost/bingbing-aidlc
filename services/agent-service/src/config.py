"""Agent Service configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Agent Service configuration via environment variables."""

    valkey_endpoint: str = "localhost"
    valkey_port: int = 6379
    valkey_use_tls: bool = False
    dynamodb_table: str = "family-copilot-prod-vehicle-profiles"
    bedrock_model_id: str = "anthropic.claude-3-5-haiku-20241022-v1:0"
    aws_region: str = "us-east-1"
    environment: str = "local"
    prompts_dir: str = "shared/prompts"
    host: str = "0.0.0.0"
    port: int = 8081

    model_config = {"env_prefix": "", "case_sensitive": False}


settings = Settings()
