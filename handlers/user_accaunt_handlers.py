# from specialists.spetc import masters
# from keyboards import keyboards_mas, admin_keyboards
from keyboards.keyboards_mas import add_keyboard
# from lexicon.lexicon import LEXICON_MASSAGES
from config.config import load_config, pg_manager
# from clients.clients import clients
from state.states import FSMEditUser

import datetime
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import default_state, State, StatesGroup


router = Router()

year = datetime.datetime.today().year

config = load_config()

admin_ids = config.tg_bot.admin_ids


# Этот хэндлер будет срабатывать после нажтия на кнопку "Заполнить анкету"
@router.callback_query(F.data.contains('start_anketa'))
async def start_anketa(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        text='Введите свой номер телефона в формате: "89123456789"'
    )
    await state.set_state(FSMEditUser.fill_phone)

# Этот хэндлер будет срабатывать ввода номер телефона      
@router.message(StateFilter(FSMEditUser.fill_phone),
                F.text.replace('-', '').replace(' ', '').isdigit()
                and F.text.replace('-', '').replace(' ', '').replace('+', '').len() >= 11)
async def process_phone_sent(message: Message, state: FSMContext):
        phone = message.text.replace('-', '').replace(' ', '')
        if phone.startswith('+7'):
            await state.update_data(phone=phone)
        else:
            await state.update_data(phone='+7'+phone[1:])
        await message.answer(
            text='Спасибо, а теперь введите Ваше имя:'
        )
        await state.set_state(FSMEditUser.fill_name)

# Этот хэндлер будет срабатывать если введено что-то непохожее на номер телефона       
@router.message(StateFilter(FSMEditUser.fill_phone))
async def warning_not_phone(message: Message):
    await message.answer(
        text='То, что Вы отправили не похоже на номер телефона\n\n'
             'Пожалуйста, введите Ваш номер телефона в формате: "89123456789"\n\n'
             'Если Вы хотите прервать заполнение анкеты - '
             'нажмите "отмена" в меню'
    )

# Этот хэндлер будет срабатывать после ввода номера телефона и предложит написать коментарий  
@router.message(StateFilter(FSMEditUser.fill_name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    markup = add_keyboard(1, 'Пропустить комментарий')
    await message.answer(
        text='Спасибо. Теперь можете написать какой-нибудь комментарий. Но это не обязательно.',
        reply_markup=markup
    )
    await state.set_state(FSMEditUser.save_anketa)

# Этот хэндлер будет срабатывать если введено что-то непохожее на имя
@router.message(StateFilter(FSMEditUser.fill_name))
async def warning_not_name(message: Message):
    await message.answer(
        text='То, что Вы отправили не похоже на имя\n\n'
             'Пожалуйста, введите Ваше имя\n\n'
             'Если Вы хотите прервать заполнение анкеты - '
             'нажмите "отмена" в меню')

# Этот хэндлер будет срабатывать если нажать "пропустить коментарий"  
@router.callback_query(StateFilter(FSMEditUser.save_anketa), F.data=='skip_comment')
async def skip_comment(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    user = await state.get_data()
    markup = add_keyboard(2, ' Да ',  'Нет')
    await callback.message.answer(
        text=f'Ваше имя: {user["name"]}\n\nВаш номер телефона: {user["phone"]}\n\nСохраняем?',
        reply_markup=markup
    )
    await state.set_state(FSMEditUser.upload)

# Этот хэндлер будет срабатывать когда всё введено и предложит проверить данные
@router.message(StateFilter(FSMEditUser.save_anketa))
async def view_user(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(comment=message.text)
    user = await state.get_data()
    markup = add_keyboard(2, ' Да ',  'Нет')
    
    await message.answer(
        text=f'Ваше имя: {user["name"]}\n\nВаш номер телефона: {user["phone"]}\nКомментарий: {user["comment"]}\n\nСохраняем?',
        reply_markup=markup
    )
    await state.set_state(FSMEditUser.upload)

# Этот хэндлер будет срабатывать если нажать на "да" и сохранит данные в базу данных 
@router.callback_query(StateFilter(FSMEditUser.upload), F.data=='yes')
async def upload_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    user = await state.get_data()
    id = callback.from_user.id
    name = user['name']
    phone = user['phone']
    if len(user) >= 3:
        comment = user['comment']
        #Client().add_client(id, name, phone, comment)
        user_info = {"user_id": id, "name": name, "phone": phone, "comment": comment}
        async with pg_manager:
            await pg_manager.insert_data_with_update(table_name='users_reg',
                                         records_data=user_info,
                                         conflict_column='user_id',
                                         update_on_conflict=True)
    else:
        user_info = {"user_id": id, "name": name, "phone": phone, "comment": 'comment'}
        async with pg_manager:
            await pg_manager.insert_data_with_update(table_name='users_reg',
                                         records_data=user_info,
                                         conflict_column='user_id',
                                         update_on_conflict=True)
    await callback.message.answer(
        text='Спасибо за уделённое время!\n\nТеперь можете записаться на сеанс!'
    )
    await state.clear()

# Этот хэндлер будет срабатывать если нажать на "нет" и не сохранит данные в базу данных   
@router.callback_query(StateFilter(FSMEditUser.upload), F.data=='no')
async def cancel_snketa(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    markup = add_keyboard(2, (' Да ', ' start_anketa'), ('Нет', ' not_again'))
    await callback.message.answer(
        text='Начать заполнение анкеты сначала?',
        reply_markup=markup
    )

# Этот хэндлер будет срабатывать если нажать на "нет" и не начинать заполнение анкеты снова  
@router.callback_query(F.data.contains('not_again'))
async def cancel_anketa(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()
