import asyncio
import sys
from pathlib import Path
from aiogram.fsm.storage.memory import MemoryStorage

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from core.config import settings
from core.logging import setup_logging, get_logger
from apps.telegram_bot.handlers import messages, callbacks
from apps.telegram_bot.middlewares.rate_limit import RateLimitMiddleware


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
    dp.include_router(callbacks.router)

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    finally:
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
