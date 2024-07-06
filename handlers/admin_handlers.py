from specialists.spetc import masters, change_and_add_master_field, search_master_to_id, delete_master, Master
from lexicon.lexicon import LEXICON_MASTER_FIELD
from state.states import FSMEditMaster
from keyboards.keyboards_mas import add_keyboard

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state


router = Router()

mast = Master()

kb_builder = InlineKeyboardBuilder()

flag = False

@router.callback_query(F.data.startswith('edit_mast'))
async def press_master_edit(callback: CallbackQuery, state: FSMContext):
    global flag
    flag = True
    master = search_master_to_id(int(callback.data.split()[-1]))
    markup = add_keyboard(3, ('Имя', f' {master.id}'), ('Фамилию', f' {master.id}'), ('Дату рождения', f' {master.id}'), ('О мастере', f' {master.id}'), ('Пол', f' {master.id}'))
    await callback.message.answer(
        text='Что Вы хотите редактировать?',
        reply_markup=markup
    )
    await state.update_data(id=master.id)
    
 
@router.callback_query(F.data.startswith('edit_field name'))
@router.callback_query(F.data.contains('add mast'))
async def add_or_edit_name(callback: CallbackQuery, state: FSMContext):
    print(callback.data)
    await callback.message.delete()
    if flag:
        field = callback.data.split()[1]
        await state.update_data(field=field)
        await callback.message.answer(
            text=f'Введите новое имя:'
        )
        await state.set_state(FSMEditMaster.edit_field)
    else:
        await callback.message.answer(
            text='Введите имя:'
        )
        await state.set_state(FSMEditMaster.fill_name)
 
@router.callback_query(F.data.startswith('edit_field last_name'))       
@router.message(StateFilter(FSMEditMaster.fill_name))
async def add_or_edit_last_name(message: Message or CallbackQuery, state: FSMContext):
    if flag:
        field = message.data.split()[1]
        await state.update_data(field=field)
        await message.message.answer(
            text=f'Введите новую фамилию:'
        )
        await state.set_state(FSMEditMaster.edit_field)
    else:
        await state.update_data(name=message.text)
        await message.answer(
            text='Введите фамилию:'
        )
        await state.set_state(FSMEditMaster.fill_last_name)

@router.callback_query(F.data.startswith('edit_field date_of_birth'))     
@router.message(StateFilter(FSMEditMaster.fill_last_name))
async def add_or_edit_date_of_birth(message: Message or CallbackQuery, state: FSMContext):
    if flag:
        field = message.data.split()[1]
        await state.update_data(field=field)
        await message.message.answer(
            text=f'Введите новый год рождения:'
        )
        await state.set_state(FSMEditMaster.edit_field)
    else:
        await state.update_data(last_name=message.text)
        await message.answer(
            text='Введите год рождения:'
        )
        await state.set_state(FSMEditMaster.fill_date_of_birth)
        
@router.callback_query(F.data.startswith('edit_field about_master'))      
@router.message(StateFilter(FSMEditMaster.fill_date_of_birth))
async def add_or_edit_date_of_birth(message: Message or CallbackQuery, state: FSMContext):
    if flag:
        field = message.data.split()[1]
        await state.update_data(field=field)
        await message.message.answer(
            text=f'Введите новое описание:'
        )
        await state.set_state(FSMEditMaster.edit_field)
    else:
        await state.update_data(date_of_birth=message.text)
        await message.answer(
            text='Введите описание:'
        )
        await state.set_state(FSMEditMaster.fill_about_master)

@router.callback_query(F.data.startswith('edit_field sex'))        
@router.message(StateFilter(FSMEditMaster.fill_about_master))
async def add_or_edit_description(message: Message or CallbackQuery, state: FSMContext):
    markup = add_keyboard(2, 'Женский', 'Мужской')
    if flag:
        field = message.data.split()[1]
        await state.update_data(field=field)
        await message.message.answer(
            text=f'Выберите новый пол:',
            reply_markup=markup
        )
        await state.set_state(FSMEditMaster.edit_field)
    else:
        await state.update_data(description=message.text)
        await message.answer(
            text='Выберите пол:',
            reply_markup=markup
        )
        await state.set_state(FSMEditMaster.fill_sex)
        
@router.callback_query(StateFilter(FSMEditMaster.fill_sex), F.data.in_(['Мужской', 'Женский']))
async def view_master(callback: CallbackQuery, state:FSMContext):
   
    markup = add_keyboard(2, ' Да ', 'Нет')
    
    await state.update_data(sex=callback.data)
    master = await state.get_data()
    await callback.message.delete()
    
    await callback.message.answer(
        text=f'Вот результат: \n\n имя: {master["name"]}\nфамилия: {master["last_name"]}\nдата рождения: {master["date_of_birth"]}\nо мастере: {master["about_master"]}\nпол: {master["sex"]}\n\nСохраняем?',
        reply_markup=markup
    )
    await state.set_state(FSMEditMaster.upload)
    
@router.callback_query(StateFilter(FSMEditMaster.upload), F.data=='yes')
async def save_master(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    master = await state.get_data()
    Master().add_master(master['name'], master['last_name'], master['date_of_birth'], master['about_master'], master['sex'])
    await callback.message.answer(
        text=f'Мастер {master["name"]} успешно сохранён!'
    )
    await state.clear()
    
@router.callback_query(StateFilter(FSMEditMaster.upload), F.data=='no')
async def cancel_add_master(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    markup = add_keyboard(2, (' Да ', ' add mast'), ('Нет', ' not_again'))
    await callback.message.answer(
        text='Начать добабление мастера сначала?',
        reply_markup=markup
    )
    
@router.callback_query(F.data.contains('not_again'))
async def add_master_again(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()
    
@router.message(StateFilter(FSMEditMaster.edit_field))
async def update_field(message: Message, state: FSMContext):
    await state.update_data(value=message.text)
    new_field = await state.get_data()
    
    change_and_add_master_field(new_field['id'], new_field['field'], new_field['value'])
    await message.answer(
        text='Редактирование прошло успешно!'
    )
    global flag
    flag = False
    await state.clear()
    
@router.callback_query(F.data.startswith('del mast'))
async def confirm_del_master(callback: CallbackQuery, state: FSMContext):
    await state.update_data(id=int(callback.data.split()[-1]))
    await callback.message.answer(
        text='Вы удаляете мастера. Если Вы уверены в своих действиях, напишите "да", для отмены напишите "нет".'
    )
    await state.set_state(FSMEditMaster.del_master)
      
@router.message(StateFilter(FSMEditMaster.del_master), F.text.lower() == 'да')
async def del_master(message: Message, state: FSMContext):
    id = await state.get_data()
    if message.from_user.id in admin_ids:
        name = delete_master(id['id'])
        await message.answer(
            text=f'Мастер {name} успешно удалён!'
        )
        await state.clear()
        
@router.message(StateFilter(FSMEditMaster.del_master), F.text.lower() == 'нет')
async def cancel_del_master(message: Message, state: FSMContext):
    await message.answer(
        text='Удаление отмененно.'
        )
    await state.clear()
        
@router.message(StateFilter(FSMEditMaster.del_master))
async def warning_del_master(message: Message):
    await message.answer(
        text='Я Вас не понял. Напишите ещё раз, только "да" или "нет".'
        )
        
    
