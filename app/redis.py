from fastapi import Request, Depends
import redis.asyncio as redis


async def get_user_pending_uploads(request: Request) -> redis.Redis:
    return request.app.state.redis_pending_uploads