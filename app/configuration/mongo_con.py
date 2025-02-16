from motor.motor_asyncio import AsyncIOMotorClient
from app.configuration import settings

MONGO_URI = f"mongodb://{settings.MONGO_USERNAME}:{settings.MONGO_PASSWORD}@{settings.MONGO_HOST}:{settings.MONGO_PORT}"

client = AsyncIOMotorClient(MONGO_URI)
db = client[settings.MONGO_DB]

async def get_database():
    return db
