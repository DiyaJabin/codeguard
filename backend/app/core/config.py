from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "local"
    ai_provider: str = "mock"
    aws_deploy_enabled: bool = False
    bedrock_enabled: bool = False
    database_url: str = "sqlite:///./codeguard.db"
    allowed_origins: list[str] = ["http://localhost:5173"]
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "amazon.nova-lite-v1:0"
    max_code_bytes: int = 100 * 1024
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

