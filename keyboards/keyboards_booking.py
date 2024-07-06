from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON_MASSAGES, LEXICON_BUTTONS
from logic.logic import pars_date, pars_time


def get_date_keyboard(master_id: str, massage_id: str, month: str):
    
    kb_builder = InlineKeyboardBuilder()

    dates = pars_date(master_id=master_id, massage_id=massage_id)

    dates_keyboards = []
    for date in dates['working_dates']:
        if date.split('-')[1] == month:
            dat = InlineKeyboardButton(
                text=f"{date.split('-')[-1]}",
                callback_data=f"{date}"
                )
            dates_keyboards.append(dat)
    dates = kb_builder.row(*dates_keyboards,     width=5)
    return dates.as_markup()

def get_time_keyboard(master_id: str, massage_id: str, date: str):
    
    kb_builder = InlineKeyboardBuilder()

    times = pars_time(master_id=master_id, massage_id=massage_id, date=date)

    times_keyboards = []
    for time in times:
        tim = InlineKeyboardButton(
            text=f"{time['time']}",
            callback_data=f"{time['time'], time['datetime']}"
            )
        times_keyboards.append(tim)
    dates = kb_builder.row(*times_keyboards,     width=5)
    return dates.as_markup()
