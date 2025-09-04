from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Telegram Bot
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")

    # Database
    database_url: str = Field(..., env="DATABASE_URL")

    # Redis
    redis_url: str = Field(..., env="REDIS_URL")

    # LLM
    openai_api_key: str | None = Field(None, env="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(None, env="ANTHROPIC_API_KEY")

    # Vector Database
    chroma_host: str = Field("localhost", env="CHROMA_HOST")
    chroma_port: int = Field(8000, env="CHROMA_PORT")

    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_format: str = Field("json", env="LOG_FORMAT")

    # Telemetry
    otel_endpoint: str | None = Field(None, env="OTEL_ENDPOINT")
    otel_service_name: str = Field("booking-bot", env="OTEL_SERVICE_NAME")

    # Security
    rate_limit_per_minute: int = Field(60, env="RATE_LIMIT_PER_MINUTE")
    max_message_length: int = Field(4096, env="MAX_MESSAGE_LENGTH")

    # Timezone
    timezone: str = Field("Europe/Minsk", env="TIMEZONE")

    # Pricing
    pricing_cache_ttl: int = Field(300, env="PRICING_CACHE_TTL")
    default_tariff: str = Field("standard", env="DEFAULT_TARIFF")
    pricing_config_path: str = Field(
        "config/pricing_config.json", env="PRICING_CONFIG_PATH"
    )

    # FAQ System
    faq_llm_temperature: float = Field(0.7, env="FAQ_LLM_TEMPERATURE")
    faq_max_tokens: int = Field(500, env="FAQ_MAX_TOKENS")
    faq_conversation_history_limit: int = Field(
        12, env="FAQ_CONVERSATION_HISTORY_LIMIT"
    )
    faq_response_timeout: int = Field(30, env="FAQ_RESPONSE_TIMEOUT")  # seconds
    faq_escalation_threshold: float = Field(0.3, env="FAQ_ESCALATION_THRESHOLD")
    faq_context_cache_ttl: int = Field(1800, env="FAQ_CONTEXT_CACHE_TTL")  # 30 minutes
    faq_max_daily_questions_per_user: int = Field(
        50, env="FAQ_MAX_DAILY_QUESTIONS_PER_USER"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
