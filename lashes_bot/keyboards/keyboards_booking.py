from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON_BUTTONS
from logic.logic import pars_date, pars_time


# Добавление клавиатуры с датами
def get_date_keyboard(
    master_id: str, service_id: str, month: str
) -> InlineKeyboardBuilder:
    """Функция принимает id мастера, id услуги и месяц и возвращает клавиатуру с доступными датами для записи"""

    kb_builder = InlineKeyboardBuilder()

    dates = pars_date(master_id=master_id, service_id=service_id)

    dates_keyboards = []
    for date in dates["working_dates"]:
        if date.split("-")[1] == month:
            dat = InlineKeyboardButton(
                text=f"{date.split('-')[-1]}", callback_data=f"{date}"
            )
            dates_keyboards.append(dat)
    dates = kb_builder.row(*dates_keyboards, width=5)
    return dates.as_markup()


# Добавление клавиатуры с временем
def get_time_keyboard(
    master_id: str, service_id: str, date: str
) -> InlineKeyboardBuilder:
    """Функция принимает id мастера, id услуги и дату и возвращает клавиатуру с доступным временем для записи"""

    kb_builder = InlineKeyboardBuilder()

    times = pars_time(master_id=master_id, service_id=service_id, date=date)
    times_keyboards = []
    for time in times:
        tim = InlineKeyboardButton(
            text=f"{time['time']}", callback_data=f"{time['time'], time['datetime']}"
        )
        times_keyboards.append(tim)
    dates = kb_builder.row(*times_keyboards, width=5)
    return dates.as_markup()
