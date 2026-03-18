"""Application configuration via environment variables."""
from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_SERVICE_KEY: str = Field(..., description="Supabase service role key")

    # AI APIs
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key for embeddings")
    COHERE_API_KEY: str = Field(..., description="Cohere API key for reranking")
    SARVAM_API_KEY: str = Field("", description="Sarvam AI key for translation")
    ANTHROPIC_API_KEY: str = Field("", description="Anthropic key for enrichment")

    # Redis
    UPSTASH_REDIS_URL: str = Field(..., description="Upstash Redis URL")
    UPSTASH_REDIS_TOKEN: str = Field("", description="Upstash Redis token")

    # GitHub crawling
    GITHUB_TOKEN: str = Field("", description="GitHub token for higher rate limits")

    # Auth
    JWT_SECRET: str = Field(..., description="JWT signing secret")
    INTERNAL_API_KEY: str = Field("", description="Internal API key for GitHub Actions")

    # App settings
    ENVIRONMENT: str = Field("development", description="development | staging | production")
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    ALLOWED_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "https://contextbharat.com"],
        description="CORS allowed origins",
    )

    # Rate limiting defaults
    FREE_TIER_DAILY_LIMIT: int = Field(100, description="Free tier daily query limit")
    PRO_TIER_DAILY_LIMIT: int = Field(10000, description="Pro tier daily query limit")

    # Ingestion settings
    DEFAULT_CHUNK_SIZE: int = Field(512, description="Default chunk size in tokens")
    DEFAULT_CHUNK_OVERLAP: int = Field(50, description="Default chunk overlap in tokens")
    EMBEDDING_BATCH_SIZE: int = Field(100, description="OpenAI embedding batch size")
    EMBEDDING_MODEL: str = Field("text-embedding-3-small", description="OpenAI embedding model")
    EMBEDDING_DIMENSIONS: int = Field(1536, description="Embedding vector dimensions")

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


settings = Settings()
