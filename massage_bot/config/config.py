from dataclasses import dataclass
import os
import dotenv
from asyncpg_lite import DatabaseManager


#dotenv.load_dotenv()

@dataclass
class DatabaseConfig:
    database: str
    db_host: str
    db_user: str
    db_password: str
    
@dataclass
class TgBot:
    token: str

@dataclass
class Yclients:
    token: str
    
@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig
    yc: Yclients

def load_config() -> Config:
    dotenv.load_dotenv()
    return Config(
        tg_bot=TgBot(
            token=os.getenv('BOT_TOKEN'),
        ),
        db=DatabaseConfig(
            database=os.getenv('NAME_DB'),
            db_host=os.getenv('HOST_DB'),
            db_user=os.getenv('USER_DB'),
            db_password=os.getenv('PASS_DB'),
            ),
        yc=Yclients(
            token=os.getenv('YCLIENTS_TOKEN')
        )
        )
        

config = load_config()

pg_manager = DatabaseManager(
        # db_url=f'postgresql://{config.db.db_user}:{config.db.db_password}@database:5432/{config.db.database}',
        db_url=f'postgresql://{config.db.db_user}:{config.db.db_password}@{config.db.db_host}:5432/{config.db.database}',
        deletion_password=config.db.db_password,
    )
