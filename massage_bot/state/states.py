from aiogram.fsm.state import State, StatesGroup


# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM 
class FSMEditUser(StatesGroup):
    fill_phone = State()  # Состояние ожидания ввода номера телефона
    fill_name = State()   # Состояние ожидания ввода имени
    save_anketa = State() # Состояние ожидания сохраняем ли анкету
    upload = State()      # Состояние ожидания сохранения анкеты
    
# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMBooking(StatesGroup):
    book_select_mast = State() # Состояние ожидания выбора мастера
    book_select_mass = State() # Состояние ожидания выбора массажа
    book_select_date = State() # Состояние ожидания выбора даты
    book_select_time = State() # Состояние ожидания выбора времени
    book_confirmation = State() # Состояние ожидания подтверждения
    book_upload = State()      # Состояние запись на услугу

 # Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMEditAccaunt(StatesGroup):
    edit = State() # Состояние ожидания выбора, что изменить
    edit_name = State() # Состояние ожидания изменения имени
    edit_phone = State() # Состояние ожидания изменения номера телефона
    edit_comment = State() # Состояние ожидания изменения комментария
