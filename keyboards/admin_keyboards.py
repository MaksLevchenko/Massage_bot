from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON_MASSAGES
from specialists.spetc import masters


kb_builder = InlineKeyboardBuilder()

edit_mast_keyb = []
for master in masters.values():
    edit_mast = InlineKeyboardButton(
                text='Редактировать',
                callback_data=f'edit_mast {master.id}'
            )
    edit_mast_keyb.append(edit_mast)
            