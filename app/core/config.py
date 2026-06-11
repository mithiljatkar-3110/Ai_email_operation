from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="AI CRM System", validation_alias="APP_NAME")
    app_version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    environment: Literal["development", "staging", "production"] = Field(
        default="development",
        validation_alias="ENVIRONMENT",
    )
    debug: bool = Field(default=False, validation_alias="DEBUG")

    # API
    api_v1_prefix: str = Field(default="/api/v1", validation_alias="API_V1_PREFIX")

    # Database
    postgres_user: str = Field(default="postgres", validation_alias="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", validation_alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(default="localhost", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, validation_alias="POSTGRES_PORT")
    postgres_db: str = Field(default="ai_crm", validation_alias="POSTGRES_DB")
    database_url: PostgresDsn | None = Field(default=None, validation_alias="DATABASE_URL")

    # SQLAlchemy
    db_echo: bool = Field(default=False, validation_alias="DB_ECHO")
    db_pool_size: int = Field(default=5, validation_alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, validation_alias="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, validation_alias="DB_POOL_TIMEOUT")

    # LLM (Gemini)
    gemini_api_key: str | None = Field(default=None, validation_alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.5-flash", validation_alias="GEMINI_MODEL")
    classification_rag_top_k: int = Field(default=1, validation_alias="CLASSIFICATION_RAG_TOP_K")
    classification_max_thread_messages: int = Field(
        default=2, validation_alias="CLASSIFICATION_MAX_THREAD_MESSAGES"
    )
    classification_max_thread_body_chars: int = Field(
        default=400, validation_alias="CLASSIFICATION_MAX_THREAD_BODY_CHARS"
    )
    classification_max_email_body_chars: int = Field(
        default=1500, validation_alias="CLASSIFICATION_MAX_EMAIL_BODY_CHARS"
    )
    classification_max_rag_chunk_chars: int = Field(
        default=350, validation_alias="CLASSIFICATION_MAX_RAG_CHUNK_CHARS"
    )
    classification_max_output_tokens: int = Field(
        default=1024, validation_alias="CLASSIFICATION_MAX_OUTPUT_TOKENS"
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.database_url:
            return str(self.database_url)
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
