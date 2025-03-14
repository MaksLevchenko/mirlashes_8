from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON_BUTTONS
from logic.logic import pars_services, pars_services_mast


mast_keyboard = []

services = pars_services()


# Создание кнопок
def create_button(text: str, callback_data: str | int) -> InlineKeyboardButton:
    button = InlineKeyboardButton(text=text, callback_data=callback_data)
    return button


# Добавление клавиатуры
def add_keyboard(
    width: int, *args: str | tuple[str], **kwargs: str
) -> InlineKeyboardMarkup:

    kb_builder = InlineKeyboardBuilder()

    buttons: list[InlineKeyboardButton] = []

    if args:
        for button in args:
            if type(button) is tuple:
                for text, callback in LEXICON_BUTTONS.items():
                    if text in button[0]:
                        buttons.append(
                            InlineKeyboardButton(
                                text=button[0], callback_data=callback + button[1]
                            )
                        )
            else:
                for text, callback in LEXICON_BUTTONS.items():
                    if button in text:

                        buttons.append(
                            InlineKeyboardButton(text=button, callback_data=callback)
                        )
    if kwargs:
        for callback, text in kwargs.items():
            for t, c in LEXICON_BUTTONS.items():
                if text in t:
                    buttons.append(
                        InlineKeyboardButton(text=text, callback_data=c + callback)
                    )

    kb_builder.row(*buttons, width=width)

    return kb_builder.as_markup()


# Добавление клавиатуры с услугами
def get_services_keyboard():

    kb_builder = InlineKeyboardBuilder()
    services = pars_services()

    mas_keyboard = []
    for service in services.values():
        mas = InlineKeyboardButton(
            text=f"{service.name}", callback_data=f"serv_{service.id}"
        )
        mas_keyboard.append(mas)

    services = kb_builder.row(*mas_keyboard, width=1)
    return services.as_markup()


# Добавление клавиатуры с услугами для конкретного мастера
def get_mast_services_keyboard(master_id: str):

    kb_builder = InlineKeyboardBuilder()
    services = pars_services()
    mas_keyboard = []
    services_to_mast = pars_services_mast(master_id=master_id)
    for service in services.values():
        if service.id in services_to_mast:
            mas = InlineKeyboardButton(
                text=f"{service.name}", callback_data=f"mass {service.id}"
            )
            mas_keyboard.append(mas)

    services = kb_builder.row(*mas_keyboard, width=1)
    return services.as_markup()
