from sqlalchemy import Integer, String
from handlers import (
    user_handlers,
    user_booking_handlers,
    other_handlers,
    user_account_handlers,
)
from keyboards.set_menu import set_main_menu
from config.config import load_config, pg_manager

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from asyncpg_lite import DatabaseManager


config = load_config()
# Вместо BOT TOKEN HERE нужно вставить токен вашего бота,
# полученный у @BotFather
BOT_TOKEN = config.tg_bot.token


async def main():

    # Создаём базу данных клиентов
    async with pg_manager:
        columns = [
            {
                "name": "user_id",
                "type": Integer,
                "options": {"primary_key": True, "autoincrement": False},
            },
            {"name": "name", "type": String},
            {"name": "phone", "type": String},
            {"name": "comment", "type": String},
        ]
        await pg_manager.create_table(table_name="rachat_client", columns=columns)

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
    asyncio.run(main())
