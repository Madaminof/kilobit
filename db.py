import asyncpg
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

async def init_db():
    return await asyncpg.create_pool(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

async def save_kino(pool, kino_kodi, message_id):
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO kino (kino_kodi, message_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            kino_kodi,
            message_id
        )

async def get_message_id(pool, kino_kodi):
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT message_id FROM kino WHERE kino_kodi = $1",
            kino_kodi
        )
