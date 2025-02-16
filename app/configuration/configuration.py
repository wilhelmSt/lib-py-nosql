from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_DB: str
    MONGO_USERNAME: str
    MONGO_PASSWORD: str

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
