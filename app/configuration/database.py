from pydantic import BaseSettings
from motor.motor_asyncio import AsyncIOMotorClient

class Settings(BaseSettings):
    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_DB: str

    class Config:
        env_file = ".env"


settings = Settings()

MONGO_URI = f"mongodb://{settings.MONGO_HOST}:{settings.MONGO_PORT}"

client = AsyncIOMotorClient(MONGO_URI)
db = client[settings.MONGO_DB]
