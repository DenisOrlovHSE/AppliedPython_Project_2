import asyncio
from aiogram import Bot, Dispatcher

from database.session import init_db
from tg_bot import setup_handlers, setup_middleware
from config import TG_BOT_TOKEN


bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher()

setup_middleware(dp)
setup_handlers(dp)


async def main():
    print("Running bot...")
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())