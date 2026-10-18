from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Library Management API"
    database_url: str = "postgresql+asyncpg://library:library@localhost:5432/library"
    database_url_sync: str = "postgresql://library:library@localhost:5432/library"
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
