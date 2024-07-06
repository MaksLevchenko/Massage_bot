from models.models import Master, Massage
from config.config import load_config

import requests
import re


# Загружаем файлы конфига
config = load_config()

# Инициализируем url и headers
url = "https://n80669.yclients.com/api/v1/book_staff/95440?datetime=&without_seances=1"
headers = {"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "Authorization": f"{config.yc.token}"
        }

# Выполняем гет запрос
r = requests.get(url=url, headers=headers)

# Функция парсинга мастеров
def pars_master() -> dict:
    masters: dict[int: Master()] = {}
    for i in r.json():
        master = Master()
        if i['bookable']:
            master.id = i['id']
            master.name = i['name']
            master.title = re.sub('<[^<]+?>', '', i['information']).replace('&nbsp', ' ').replace('&quot;', ' ')
            master.foto = i['avatar']
            master.rating = i['rating']
            master.massages_ids = pars_massages_mast(i['id'])
            masters.update({master.id: master})

    return dict(sorted(masters.items(), key=lambda x: x[1].rating))

# Функция парсинга массажей для конкретного мастера
def pars_massages_mast(master_id: str) -> dict:
    url = f"https://n80669.yclients.com/api/v1/booking/locations/95440/search/services?staff_id={master_id}"

    r = requests.get(url=url, headers=headers)
    massages_id = []
    for i in r.json()['data']:
        if i['attributes']['is_bookable']:
            massages_id.append(i['id'])
    return massages_id

# Функция парсинга массажей
def pars_massages() -> dict:
    url = "https://n80669.yclients.com/api/v1/book_services/95440"
    r = requests.get(url=url, headers=headers)

    massages: dict[int: Massage()] = {}
    for mass in r.json()['services']:
        massage = Massage()
        massage.id = mass['id']
        massage.name = mass['title']
        massage.description = mass['comment']
        massage.price = mass['price_min']
        massage.foto = mass['image']
        massages.update({massage.id: massage})
        
    return massages

# Функция парсинга времени для записи
def pars_time(master_id: str, massage_id: str, date: str) -> dict:
    url = f"https://n80669.yclients.com/api/v1/book_times/95440/{master_id}/{date}?&service_ids%5B%5D={massage_id}"
    
    r = requests.get(url=url, headers=headers)
    return r.json()

# Функция парсинга даты для записи
def pars_date(master_id: str, massage_id: str) -> dict:
    url = f"https://n80669.yclients.com/api/v1/book_dates/95440?staff_id={master_id}&date=&date_from=2024-07-01&date_to=9999-01-01&service_ids%5B%5D={massage_id}"
    r = requests.get(url=url, headers=headers)

    return r.json()

# Функция записи на массаж
def to_booking(json: dict):
    r = requests.post(url="https://api.yclients.com/api/v1/book_record/95440", json=json, headers=headers)
    return r.status_code

massages = pars_massages()

masters = pars_master()

# Функция поиска мастера по id
def search_master_to_id(id: int):
    
    for master in masters.values():
        if master.id == id:
            return master

# Функция поиска массажа по id  
def search_massge_to_id(id: int):
    
    for massage in massages.values():
        if massage.id == id:
            return massage
