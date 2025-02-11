from logic.logic import get_user_to_id, pars_master, search_master_to_id, search_service_to_id
from state.states import FSMBooking
from keyboards.keyboards_mas import add_keyboard, get_services_keyboard
from config.config import load_config, pg_manager

import datetime
from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state


router = Router()

year = datetime.datetime.today().year

config = load_config()

masters = pars_master()

# Этот хэндлер будет срабатывать на команду /start вне состояний
# и предлагать перейти к заполнению анкеты, отправив команду /fillform
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    
    markup = add_keyboard(1, 'Услуги', 'Записаться')
    await message.answer(
        text='Этот бот для ознакомления с нашими услугами и возможностью записи на сеанс \n\n'
             'Выберите что бы Вы хотели:',
         reply_markup=markup
    )


# Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
# по умолчанию и сообщать, что эта команда работает внутри машины состояний
@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Отменять нечего.'
    )


# Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
# кроме состояния по умолчанию, и отключать машину состояний
@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Всё успешно отменено!'
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()
    
# Этот хэндлер будет срабатывать на команду "/accaunt" в любых состояниях
@router.message(Command(commands='account'))
async def account(message: Message, state: FSMContext):
    id = message.from_user.id
    user = await get_user_to_id(id=id)
    if user:
        markup = add_keyboard(1, ("Редактировать"))
        if user['comment']:
            await message.answer(
            text=f"Имя: {user['name']}\n Телефон: {user['phone']}\nКомментарий к записи: {user['comment']}",
            reply_markup=markup
                )
        else:
            await message.answer(
                text=f"Имя: {user['name']}\n Телефон: {user['phone']}",
                reply_markup=markup
                    )
    else:
        await message.answer(
            text=f"К сожалению у Вас ещё нет аккаунта.",
            )

# Этот хэндлер будет срабатывать на вызов мастеров в любых состояниях
@router.callback_query(F.data == 'masters')
async def process_masters_pres(callback: CallbackQuery | Message):
    await callback.message.delete()
    for master in masters.values():
        spec = master.name
        
        markup = add_keyboard(1, (f'Записаться к {spec}', f' {master.id}'))
            
        await callback.message.answer(
            protect_content=f'{master.foto}\n',
            text=f'{master.name}\n\n{master.title}',
            reply_markup=markup
            )
                
# Этот хэндлер будет срабатывать на команду "/masters" в любых состояниях
@router.message(Command(commands='masters'))
async def process_masters_command_pres(message: Message, state: FSMContext):
    id = message.from_user.id
    user = await get_user_to_id(id=id)
    for master in masters.values():
        if master.name=='Максим Л.':
            spec = master.name[:-3] + 'у'
        else:
            spec = master.name[:-1] + 'е'

        markup = add_keyboard(1, ('Подробнее о мастере', f' {master.id}'), (f'Записаться к {spec}', f' {master.id}'))

        await message.answer_photo(
            photo=master.foto,
            caption=f'{master.name}\n\n{master.title[:30]}...\n\nРэйтинг: {master.rating}',
            reply_markup=markup
                )
        if user:
            await state.set_state(FSMBooking.book_select_mass)
        else:
            markup = add_keyboard(1, ('Начать', f'_anketa'))
            await message.answer(
                text='Вы впервые записываетесь через телеграмм-бота, поэтому Вам необходимо заполнить небольшую анкету. Нажмите "Начать" для продолжения, либо нажмите "отмена" в меню.',
                reply_markup=markup
                )

# Этот хэндлер будет срабатывать на нажатие кнопки "Подробнее о мастере" в любых состояниях
@router.callback_query(F.data.startswith('about_master'))
async def about_master(callback: CallbackQuery, state: FSMContext):
    master_id = int(callback.data.split()[-1])

    master = search_master_to_id(master_id)

    id = callback.from_user.id
    user = await get_user_to_id(id=id)
    
    if master.name=='Максим Л.':
        spec = master.name[:-3] + 'у'
    else:
        spec = master.name[:-1] + 'е'

    markup = add_keyboard(1, (f'Записаться к {spec}', f' {master.id}'))

    await callback.message.answer_photo(
            photo=master.foto,
            caption=f'{master.name}\n\n{master.title}\n\nРэйтинг: {master.rating}',
            reply_markup=markup
                )
    if user:
        await state.set_state(FSMBooking.book_select_mass)
    else:
        markup = add_keyboard(1, ('Начать', f'_anketa'))
        await callback.message.answer(
            text='Вы впервые записываетесь через телеграмм-бота, поэтому Вам необходимо заполнить небольшую анкету. Нажмите "Начать" для продолжения, либо нажмите "отмена" в меню.',
            reply_markup=markup
            )

# Этот хэндлер будет срабатывать на нажатие кнопки "Наши массажи" в любых состояниях
@router.callback_query(F.data == 'services')
async def process_services_pres(callback: CallbackQuery):
    
    markup =  get_services_keyboard()
        
    await callback.message.answer(
        text=f'\n\nНаши Услуги:\n',
        reply_markup=markup
        )
        
# Этот хэндлер будет срабатывать на команду "/services" в любых состояниях
@router.message(Command(commands = 'services'))
async def process_servicesmassages_command(message: Message):
        
    markup =  get_services_keyboard()
        
    await message.answer(
        text=f'\n\nНаши услуги:\n',
        reply_markup=markup
        )

# Этот хэндлер будет срабатывать на нажатие кнопки "Наши услуги" в любых состояниях
@router.callback_query(Command(commands = 'services'))
async def process_services_command(callback: CallbackQuery):
        
    markup =  get_services_keyboard()
    await callback.message.answer(
        text=f'\n\nНаши услуги:\n',
        reply_markup=markup
        )

# Этот хэндлер будет срабатывать на нажатие кнопки на массаж в любых состояниях
@router.callback_query(F.data.startswith('serv_'))
async def about_service(callback: CallbackQuery, state: FSMContext):
    services_id = int(callback.data.split('_')[-1])

    service = search_service_to_id(services_id)

    markup = add_keyboard(1, (f'Записатьcя', f' {services_id}'))
    if service.foto:
        await callback.message.answer_photo(
                photo=service.foto,
                caption=f'{service.name}\n\n{service.description}\n\nЦена: {service.price} Р.',
                reply_markup=markup
                )
        if await state.get_data():
            # print(await state.get_data())
            await state.set_state(FSMBooking.book_select_date)
        else:
            await state.set_state(FSMBooking.book_select_mast)
    else:
        await callback.message.answer(
            text=f'{service.name}\n\n{service.description}\n\nЦена: {service.price} Р.',
            reply_markup=markup
        )
        if await state.get_data():
            #print(await state.get_data())
            await state.set_state(FSMBooking.book_select_date)
        else:
            #print('net')
            await state.set_state(FSMBooking.book_select_mast)
        
# Этот хэндлер будет срабатывать на команду "/booking" в любых состояниях
@router.message(Command(commands='booking'), StateFilter(default_state))
async def press_booking(message: Message, state: FSMContext):
    id = message.from_user.id
    user = await get_user_to_id(id=id)
            
    if user:
        await message.answer(
            text='Выберите мастера:',
            )
        for master in masters.values():
            markup = add_keyboard(1, ('Выбрать мастера', f' {master.id}'))
        
            await message.answer(
                text=f'{master.name}\nРэйтинг: {master.rating}',
                reply_markup=markup,
                    )
            await state.set_state(FSMBooking.book_select_mass)
    else:
        markup = add_keyboard(1, ('Начать', f'_anketa'))
        await message.answer(
            text='Вы впервые записываетесь через телеграмм-бота, поэтому Вам необходимо заполнить небольшую анкету. Нажмите "Начать" для продолжения, либо нажмите "отмена" в меню.',
            reply_markup=markup
            )
        await state.clear()

# Этот хэндлер будет срабатывать на нажатие кнопки  "Записаться" в любых состояниях
@router.callback_query(F.data == 'booking', StateFilter(default_state))
async def booking(callback: CallbackQuery, state: FSMContext):
    id = callback.from_user.id
    user = await get_user_to_id(id=id)
    if user:
        await callback.message.answer(
            text='Выберите мастера:',
            )
        for master in masters.values():
            markup = add_keyboard(1, ('Выбрать мастера', f' {master.id}'))
        
            await callback.message.answer(
                text=f'{master.name}\nРэйтинг: {master.rating}',
                reply_markup=markup,
                    )
            await state.set_state(FSMBooking.book_select_mass)
    else:
        markup = add_keyboard(1, ('Начать', f'_anketa'))
        await callback.message.answer(
            text='Вы впервые записываетесь через телеграмм-бота, поэтому Вам необходимо заполнить небольшую анкету. Нажмите "Начать" для продолжения, либо нажмите "отмена" в меню.',
            reply_markup=markup
            )
        await state.clear()

# Этот хэндлер будет срабатывать на нажатие кнопки "Выбрать мастера"
@router.callback_query(StateFilter(FSMBooking.book_select_mast))
async def press_booking(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.update_data(service_id=callback.data.split()[-1])
    id = callback.from_user.id
    user = await get_user_to_id(id=id)
    if user:
        await callback.message.answer(
            text='Выберите мастера:',
            )
        for master in masters.values():
            if callback.data.split()[-1] in master.massages_ids:
                markup = add_keyboard(1, ('Выбрать мастера', f' {master.id}'))
            
                await callback.message.answer(
                    text=f'{master.name}\nРэйтинг: {master.rating}',
                    reply_markup=markup,
                        )
            if await state.get_data():
                await state.set_state(FSMBooking.book_select_date)
            else:
                await state.set_state(FSMBooking.book_select_mass)
    else:
        markup = add_keyboard(1, ('Начать', f'_anketa'))
        await callback.message.answer(
            text='Вы впервые записываетесь через телеграмм-бота, поэтому Вам необходимо заполнить небольшую анкету. Нажмите "Начать" для продолжения, либо нажмите "отмена" в меню.',
            reply_markup=markup
            )
        await state.clear()
    