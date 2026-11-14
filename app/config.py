import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_path: str = os.getenv("DATABASE_PATH", "data/tasks.db")
    environment: str = os.getenv("APP_ENV", "development")


settings = Settings()
