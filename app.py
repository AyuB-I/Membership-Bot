import asyncio

from loader import bot
from config import ADMIN_ID
from database import create_db


async def on_startup(dp):
    """ On starting up the bot """
    await asyncio.sleep(5)
    await create_db()
    await bot.send_message(text="Я запущен!", chat_id=ADMIN_ID)


async def on_shutdown(dp):
    """ On shutting down the bot """
    await bot.close()


if __name__ == "__main__":
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
