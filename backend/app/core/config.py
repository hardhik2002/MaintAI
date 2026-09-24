from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MaintAI API"
    environment: str = "development"
    database_url: str = "sqlite:///./maintai.db"
    model_path: Path = Path("ml/artifacts/model.joblib")
    cors_origins: list[str] = ["http://localhost:5173"]
    history_limit: int = 500

    model_config = SettingsConfigDict(env_file=".env", env_prefix="MAINTAI_", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()

