from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from datetime import datetime, timezone

from app.core.config import settings

_client: AsyncIOMotorClient | None = None


async def connect_db() -> None:
    global _client
    _client = AsyncIOMotorClient(settings.mongodb_uri)


async def close_db() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


def get_database() -> AsyncIOMotorDatabase:
    if _client is None:
        raise RuntimeError("Database client is not initialised. Call connect_db() first.")
    return _client[settings.mongodb_db_name]


async def get_design_session(session_id: str) -> dict | None:
    """Fetch an entire stored session by UUID."""
    db = get_database()
    return await db.sessions.find_one({"session_id": session_id}, {"_id": 0})


async def update_design_session(session_id: str, chat_history: list, bom: list) -> None:
    """Upsert the active session's conversation history and computed BOM array."""
    db = get_database()
    await db.sessions.update_one(
        {"session_id": session_id},
        {"$set": {
            "session_id": session_id,
            "chat_history": chat_history,
            "bom": bom,
            "updated_at": datetime.now(timezone.utc)
        }},
        upsert=True
    )
