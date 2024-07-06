from sqlalchemy import Integer, String
from handlers import user_handlers, user_booking_handlers, user_accaunt_handlers, other_handlers
from keyboards.set_menu import set_main_menu
from config.config import load_config

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from asyncpg_lite import DatabaseManager


config = load_config()
# Вместо BOT TOKEN HERE нужно вставить токен вашего бота,
# полученный у @BotFather
BOT_TOKEN = config.tg_bot.token

#Подключаемся к базе данных 

async def main():
    
    #Создаём базу данных клиентов
    async with DatabaseManager(
        db_url=f'postgresql://{config.db.db_user}:{config.db.db_password}@{config.db.db_host}:5432/{config.db.database}',
        deletion_password=config.db.db_password,
    ) as pg_manager:
        columns = [
                {"name": "user_id", "type": Integer, "options": {"primary_key": True, "autoincrement": False}},
                {"name": "name", "type": String},
                {"name": "phone", "type": String},
                {"name": "comment", "type": String},]
        
        await pg_manager.create_table(table_name='users_reg', columns=columns)
        

    # Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
    storage = MemoryStorage()

    # Создаем объекты бота и диспетчера
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    await set_main_menu(bot)

    dp.include_router(user_handlers.router)
    dp.include_router(user_booking_handlers.router)
    dp.include_router(user_accaunt_handlers.router)
    dp.include_router(other_handlers.router)

    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

# Запускаем поллинг
if __name__ == '__main__':
    asyncio.run(main())
    