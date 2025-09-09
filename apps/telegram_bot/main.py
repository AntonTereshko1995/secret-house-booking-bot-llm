import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from apps.telegram_bot.handlers import callbacks, messages, payments
from apps.telegram_bot.middlewares.rate_limit import RateLimitMiddleware
from core.config import settings
from core.logging import get_logger, setup_logging

async def main():
    setup_logging()
    logger = get_logger(__name__)

    logger.info("Запуск Telegram бота")

    # Initialize bot and dispatcher
    bot = Bot(token=settings.telegram_bot_token)

    # Use Redis for FSM state storage
    storage = RedisStorage.from_url(settings.redis_url)
    dp = Dispatcher(storage=storage)

    # Register middleware
    dp.message.middleware(RateLimitMiddleware())

    # Register handlers
    dp.include_router(messages.router)
    dp.include_router(payments.router)  # Payment handlers (document/photo uploads)
    dp.include_router(callbacks.router)  # Keep callbacks last to catch remaining callbacks

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
