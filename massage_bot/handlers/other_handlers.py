from aiogram import Router
from aiogram.fsm.state import default_state
from aiogram.types import Message
from aiogram.filters import StateFilter


router = Router()

# Этот хэндлер будет срабатывать если вводить что-то не тогда, когда просят
@router.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.reply(text='Извините, моя твоя не понимать')
    