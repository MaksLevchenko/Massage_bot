from logic.logic import pars_master, search_master_to_id, search_massge_to_id
from state.states import FSMBooking
from keyboards.keyboards_mas import add_keyboard, get_massage_keyboard
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
    
    markup = add_keyboard(2, 'Виды массажа', 'Наши специалисты', 'Запись на массаж')
    await message.answer(
        text='Этот бот для ознакомления с видами массажа и возможностью записи на сеанс \n\n'
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
@router.message(Command(commands='accaunt'))
async def accaunt(message: Message, state: FSMContext):
    id = int(message.from_user.id)
    user = {}
    async with pg_manager:
        for row in await pg_manager.select_data('users_reg'):
            if row['user_id'] == id:
                user = row
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
    user = {}
    async with pg_manager:
        for row in await pg_manager.select_data('users_reg'):
            if message.from_user.id == row['user_id']:
                user = row

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

    user = {}
    async with pg_manager:
        for row in await pg_manager.select_data('users_reg'):
            if callback.from_user.id == row['user_id']:
                user = row
    
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
@router.callback_query(F.data == 'massages')
async def process_massages_pres(callback: CallbackQuery):
    
    markup =  get_massage_keyboard()
        
    await callback.message.answer(
        text=f'\n\nНаши массажи:\n',
        reply_markup=markup
        )
        
# Этот хэндлер будет срабатывать на команду "/massages" в любых состояниях
@router.message(Command(commands = 'massages'))
async def process_massages_command(message: Message):
        
    markup =  get_massage_keyboard()
        
    await message.answer(
        text=f'\n\nНаши массажи:\n',
        reply_markup=markup
        )

# Этот хэндлер будет срабатывать на нажатие кнопки "Наши массажи" в любых состояниях
@router.callback_query(Command(commands = 'massages'))
async def process_massages_command(callback: CallbackQuery):
        
    markup =  get_massage_keyboard()
        
    await callback.message.answer(
        text=f'\n\nНаши массажи:\n',
        reply_markup=markup
        )

# Этот хэндлер будет срабатывать на нажатие кнопки на массаж в любых состояниях
@router.callback_query(F.data.startswith('mass'))
async def about_massege(callback: CallbackQuery, state: FSMContext):
    massage_id = int(callback.data.split()[-1])

    massage = search_massge_to_id(massage_id)

    markup = add_keyboard(1, (f'Записатьcя', f' {massage_id}'))

    if massage.foto:
        await callback.message.answer_photo(
                photo=massage.foto,
                caption=f'{massage.name}\n\n{massage.description}\n\nЦена: {massage.price} Р.',
                reply_markup=markup
                )
        if await state.get_data():
            # print(await state.get_data())
            await state.set_state(FSMBooking.book_select_date)
        else:
            await state.set_state(FSMBooking.book_select_mast)
    else:
        await callback.message.answer(
            text=f'{massage.name}\n\n{massage.description}\n\nЦена: {massage.price} Р.',
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
    user = {}
    async with pg_manager:
        for row in await pg_manager.select_data('users_reg'):
            if message.from_user.id == row['user_id']:
                user = row
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

# Этот хэндлер будет срабатывать на нажатие кнопки  "Записаться" в любых состояниях
@router.callback_query(F.data == 'booking', StateFilter(default_state))
async def booking(callback: CallbackQuery, state: FSMContext):
    user = {}
    async with pg_manager:
        for row in await pg_manager.select_data('users_reg'):
            if callback.from_user.id == row['user_id']:
                user = row
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

# Этот хэндлер будет срабатывать на нажатие кнопки "Выбрать мастера"
@router.callback_query(StateFilter(FSMBooking.book_select_mast))
async def press_booking(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.update_data(massage_id=callback.data.split()[-1])
    user = {}
    async with pg_manager:
        for row in await pg_manager.select_data('users_reg'):
            if callback.from_user.id == row['user_id']:
                user = row
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
    