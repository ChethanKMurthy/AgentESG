from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    app_env: str = "development"
    app_name: str = "esg-ai-platform"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    cors_origins_raw: str = Field(
        default="http://localhost:3000",
        validation_alias="CORS_ORIGINS",
    )

    database_url: str = "postgresql+asyncpg://esg:esg@postgres:5432/esg"
    db_echo: bool = False
    db_pool_size: int = 10
    db_max_overflow: int = 20

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-opus-4-7"
    anthropic_max_tokens: int = 1024

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_device: str = "cpu"

    vector_store_path: str = "/app/data/faiss"
    documents_path: str = "/app/data/documents"

    rag_chunk_size: int = 800
    rag_chunk_overlap: int = 120
    rag_top_k: int = 5
    rag_dense_weight: float = 0.6
    rag_sparse_weight: float = 0.4
    rag_rrf_k: int = 60

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.cors_origins_raw.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
