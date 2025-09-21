from pydantic import BaseModel
import os

class Settings(BaseModel):
    # Prefer explicit DATABASE_URL; fall back to individual pieces
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/app"
    )

settings = Settings()
