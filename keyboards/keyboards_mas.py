from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon import LEXICON_BUTTONS
from logic.logic import pars_massages, pars_massages_mast, massages


mast_keyboard = []

massages = pars_massages()
def create_button(text: str, callback_data: str | int) -> InlineKeyboardButton:
    button = InlineKeyboardButton(
        text=text,
        callback_data=callback_data
    )
    return button
    
def create_keyboard(*args):
    keyboard = []
    for button in args:
        keyboard.append(button)
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    return markup
  
def add_keyboard(width: int, *args: str | tuple[str], **kwargs: str) -> InlineKeyboardMarkup:
        
    kb_builder = InlineKeyboardBuilder()
        
    buttons: list[InlineKeyboardButton] = []
        
    if args:
        for button in args:
              if type(button) is tuple:
                  for text, callback in LEXICON_BUTTONS.items():
                      if text in button[0]:
                          buttons.append(InlineKeyboardButton(
                          text=button[0],
                          callback_data=callback+button[1]
                          ))
              else:
                  for text, callback in LEXICON_BUTTONS.items():
                      if button in text:
                          
                          buttons.append(InlineKeyboardButton(
                          text=button,
                          callback_data=callback))
    if kwargs:
        for callback, text in kwargs.items():
            for t, c in LEXICON_BUTTONS.items():
                if text in t:
                    buttons.append(InlineKeyboardButton(
                        text=text,
                        callback_data=c+callback))
    
    kb_builder.row(*buttons, width=width)
    
    return kb_builder.as_markup()
    
def get_massage_keyboard():
    
    kb_builder = InlineKeyboardBuilder()
    
    mas_keyboard = []
    for massage in massages.values():
            mas = InlineKeyboardButton(
                text=f'{massage.name}',
                callback_data=f'mass {massage.id}'
                )
            mas_keyboard.append(mas)
    
    massageses = kb_builder.row(*mas_keyboard,     width=1)
    return massageses.as_markup()

def get_mast_massage_keyboard(master_id: str):
    
    kb_builder = InlineKeyboardBuilder()
    
    mas_keyboard = []
    massages_to_mast = pars_massages_mast(master_id=master_id)
    for massage in massages.values():
        if str(massage.id) in massages_to_mast:
            mas = InlineKeyboardButton(
                text=f'{massage.name}',
                callback_data=f'mass {massage.id}'
                )
            mas_keyboard.append(mas)
    
    massageses = kb_builder.row(*mas_keyboard,     width=1)
    return massageses.as_markup()
        