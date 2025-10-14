from pydantic_settings import BaseSettings
from pydantic import AnyUrl

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    RQ_QUEUE: str = "hub-queue"
    APP_SECRET: str = "devsecret"
    ENV: str = "dev"
    PORT: int = 8000

    STRIPE_WEBHOOK_SECRET: str | None = None
    SLACK_WEBHOOK_URL: str | None = None
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_CHAT_ID: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
