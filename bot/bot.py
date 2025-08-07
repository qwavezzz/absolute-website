import asyncio
import logging

from aiogram import Bot, Dispatcher

import config
import db
from handlers import router


logging.basicConfig(level=logging.INFO)


async def main() -> None:
    db.init_db()
    bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
