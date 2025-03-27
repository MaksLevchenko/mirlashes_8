import sys
from users import (
    user_handlers,
    user_booking_handlers,
    other_handlers,
    user_account_handlers,
)
from keyboards.set_menu import set_main_menu
from config.config import config

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


# Вместо BOT TOKEN HERE нужно вставить токен вашего бота,
# полученный у @BotFather
BOT_TOKEN = config.bot_token


async def main():

    # Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
    storage = MemoryStorage()

    # Создаем объекты бота и диспетчера
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    await set_main_menu(bot)

    dp.include_router(user_handlers.router)
    dp.include_router(user_booking_handlers.router)
    dp.include_router(user_account_handlers.router)
    dp.include_router(other_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


# Запускаем поллинг
if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
