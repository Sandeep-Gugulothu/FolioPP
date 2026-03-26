import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Core
    APP_NAME: str = "FolioPP"
    APP_VERSION: str = "0.2.0"
    DEBUG: bool = True
    
    # Storage (Phase 1)
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/etdb"
    REDIS_URL: str = "redis://localhost:6379/0"
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_RAW: str = "raw-data"
    MINIO_BUCKET_PROCESSED: str = "processed-data"
    
    # Knowledge (Phase 2)
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    # AI (Phase 3)
    OPENAI_API_KEY: str = "sk-..."  # for LangGraph
    GROQ_API_KEY: str = "gsk-..." 
    LLM_MODEL: str = "gpt-4-turbo"
    
    # Providers
    INDMONEY_ACCESS_TOKEN: str | None = None
    
    # Scalability (Phase 4)
    RAY_ADDRESS: str = "auto"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
