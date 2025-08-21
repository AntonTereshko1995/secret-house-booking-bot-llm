"""
Middleware для ограничения скорости запросов
"""

import asyncio
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from redis.asyncio import Redis

from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """Middleware for request rate limiting"""
    
    def __init__(self):
        super().__init__()
        self.redis = Redis.from_url(settings.redis_url)
        self.rate_limit = settings.rate_limit_per_minute
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        
        user_id = event.from_user.id
        key = f"rate_limit:{user_id}"
        
        try:
            # Check request count
            current_count = await self.redis.get(key)
            
            if current_count and int(current_count) >= self.rate_limit:
                await event.answer(
                    "Слишком много запросов. Попробуйте через минуту.",
                    show_alert=True
                )
                return
            
            # Increment counter
            pipe = self.redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, 60)  # TTL 60 секунд
            await pipe.execute()
            
            # Continue processing
            return await handler(event, data)
            
        except Exception as e:
            logger.error("Ошибка в rate limit middleware", exc_info=e)
            # In case of error continue processing
            return await handler(event, data)
