"""
Bot-gateway entry point — Telegram long-polling with owner-only auth.
"""

import os
import asyncio
import logging

from aiogram import Bot, Dispatcher

from .handlers import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")


async def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN env var is required")

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("bot-gateway starting long-polling ...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())