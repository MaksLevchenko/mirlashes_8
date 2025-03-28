from aiogram import Bot
from aiogram.types import BotCommand

from lexicon.lexicon import LEXICON_COMMANDS_MENU_REG


# Функция для настройки кнопки Menu бота
async def set_main_menu(bot: Bot):
    """
    Создаёт кнопки для меню бота
    """

    main_menu_commands = [
        BotCommand(command=command, description=description)
        for command, description in LEXICON_COMMANDS_MENU_REG.items()
    ]
    await bot.set_my_commands(main_menu_commands)
