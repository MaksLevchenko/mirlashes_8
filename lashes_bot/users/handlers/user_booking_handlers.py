from keyboards.keyboards_booking import get_date_keyboard, get_time_keyboard
from users.crud import get_user_to_telegram_id
from logic.logic import (
    pars_date,
    pars_services,
    search_service_to_id,
    search_master_to_id,
    to_booking,
)
from keyboards.keyboards_mas import add_keyboard, get_mast_services_keyboard
from lexicon.lexicon import LEXICON_MONTH

from state.states import FSMBooking

import datetime
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext


router = Router()

year = datetime.datetime.today().year


services = pars_services()


# Этот хэндлер будет срабатывать на нажатие кнопки "Выбрать мастера"
@router.callback_query(StateFilter(FSMBooking.book_select_mass))
async def press_select_services(callback: CallbackQuery, state: FSMContext):
    master_id = callback.data.split()[-1]
    markup = get_mast_services_keyboard(master_id=master_id)
    await callback.message.delete()
    await state.update_data(master_id=master_id)
    await callback.message.answer(text="Теперь выберите услугу:", reply_markup=markup)
    await state.set_state(FSMBooking.book_select_date)


# Этот хэндлер будет срабатывать после выбора услуги и предложит выбрать дату
@router.callback_query(
    StateFilter(FSMBooking.book_select_date) or StateFilter(FSMBooking.book_select_time)
)
async def booking_select_date(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()

    data = await state.get_data()

    if data.get("master_id"):
        if data.get("service_id"):
            pass
        else:
            await state.update_data(service_id=callback.data.split()[-1])
    else:
        await state.update_data(master_id=callback.data.split()[-1])

    data = await state.get_data()
    await callback.message.answer(
        text="А теперь выберите дату:",
    )
    for m in pars_date(master_id=data["master_id"], service_id=data["service_id"])[
        "working_days"
    ]:
        month = LEXICON_MONTH[m]
        if len(m) == 1:
            m = "0" + m
        markup = get_date_keyboard(data["master_id"], data["service_id"], m)

        await callback.message.answer(text=f"{month}:", reply_markup=markup)

    await state.set_state(FSMBooking.book_select_time)


# Этот хэндлер будет срабатывать после выбора даты и предложит выбрать время
@router.callback_query(StateFilter(FSMBooking.book_select_time))
async def booking_select_time(callback: CallbackQuery, state: FSMContext):

    await state.update_data(date=callback.data)
    data = await state.get_data()

    markup = get_time_keyboard(data["master_id"], data["service_id"], data["date"])
    if markup.inline_keyboard:
        await callback.message.answer(
            text="Доступное время для записи:", reply_markup=markup
        )
        await state.set_state(FSMBooking.book_confirmation)
    else:
        await callback.message.answer(
            text="К сожалению на выбранную дату нет свободных окошек!\n\nПожалуйста выберите другую дату.",
        )


# Этот хэндлер будет срабатывать после выбора времени и предложит подтвердить запись
@router.callback_query(StateFilter(FSMBooking.book_confirmation))
async def booking_confirmation(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    data = callback.data.replace("('", "").replace("'", "").replace(")", "")
    await state.update_data(
        time=data.split(",")[0], datetime=data.split(",")[1].strip()
    )
    booking_data = await state.get_data()
    service = search_service_to_id(int(booking_data["service_id"]))
    master = search_master_to_id(int(booking_data["master_id"]))
    markup = add_keyboard(2, " Да ", "Нет")

    await callback.message.answer(
        text=f"Вы выбрали:"
        f"\nУслуга: {service.name}"
        f"\nМастер: {master.name}"
        f"\nДата: {booking_data['date']}"
        f"\nВремя: {booking_data['time']}"
        f"\nСтоимость: {service.price} P"
        f"\n\nЗаписываемся?",
        reply_markup=markup,
    )
    await state.set_state(FSMBooking.book_upload)


# Этот хэндлер будет срабатывать после подтверждения данных и предложит записаться
@router.callback_query(StateFilter(FSMBooking.book_upload), F.data == "yes")
async def upload_booking(callback: CallbackQuery, state: FSMContext):
    booking_data = await state.get_data()
    id = int(callback.from_user.id)
    service = search_service_to_id(int(booking_data["service_id"]))
    master = search_master_to_id(int(booking_data["master_id"]))
    client = await get_user_to_telegram_id(tele_id=id)
    json = {
        "phone": client.phone,
        "fullname": client.name,
        "email": "",
        "code": "",
        "comment": client.comment + "\n\nЭта запись создана с помощью telegram",
        "type": "mobile",
        "notify_by_sms": 6,
        "notify_by_email": 24,
        "api_id": "",
        "custom_fields": {},
        "appointments": [
            {
                "id": 1,
                "services": [service.id],
                "staff_id": master.id,
                "datetime": booking_data["datetime"],
                "custom_fields": {},
            },
        ],
    }
    booking = to_booking(json)
    markup = add_keyboard(2, " Да ", "Нет")
    if booking == 201:
        await callback.message.answer(
            text="Спасибо за уделённое время!\n\nЖдём Вас по адресу: г.Москва ул.Костянский переулок, 14!",
        )
    else:
        await callback.message.answer(
            text="УПС, что-то пошло не так!\nПопробуем записаться снова?",
            reply_markup=markup,
        )
    await state.clear()


# Этот хэндлер будет срабатывать после нажатия на кнопку "Нет"
@router.callback_query(StateFilter(FSMBooking.book_upload), F.data == "no")
async def cancel_booking(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    markup = add_keyboard(2, ("Дa", "booking"), ("Нет", " not_again"))
    await callback.message.answer(text="Начать запись сначала?", reply_markup=markup)
    await state.clear()
