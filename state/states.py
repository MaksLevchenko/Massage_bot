from aiogram.fsm.state import State, StatesGroup

    
class FSMEditUser(StatesGroup):
    fill_phone = State()
    fill_name = State()
    save_anketa = State()
    upload = State()
    
# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMBooking(StatesGroup):
    book_select_mast = State() # Состояние ожидания выбора мастера
    book_select_mass = State() # Состояние ожидания выбора массажа
    book_select_date = State() # Состояние ожидания выбора даты
    book_select_time = State() # Состояние ожидания выбора времени
    book_confirmation = State() # Состояние ожидания подтверждения
    book_upload = State()      # Состояние запись на услугу
    
