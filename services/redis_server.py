import json
from pprint import pprint, pp
import redis
from config_data.config import Config, load_config
import datetime


# Создание подключения к базе данных Redis
async def create_redis_client() -> redis.Redis:
    # Загружаем конфиг в переменную config
    config: Config = load_config()
    # Подключение к серверу Redis
    r = redis.Redis(host=config.redis.host, port=config.redis.port)
    return r


# Проверка id пользователя в Redis
async def check_user_id_in_redis(user_id):
    # Подключение к базе данных Redis
    r = await create_redis_client()
    keys = r.keys()
    print(keys)
    decoded_a = [item.decode('utf-8') for item in keys]
    print(decoded_a)
    # Проверка наличия ключа с id пользователя в Redis
    if r.exists(user_id):
        return True
    else:
        return False


# Функция изменения названия компании
async def edit_company_name(user_id: int, new_company_name: str):
    # Получаем данные пользователя из Redis
    data = await get_data_from_redis(user_id)
    # Изменяем название компании
    data['company'] = new_company_name
    # Сохраняем данные в Redis
    await save_data_to_redis(user_id, data)
    return True


# Функция изменения валюты
async def edit_currency(user_id: int, new_currency: str):
    # Получаем данные пользователя из Redis
    data = await get_data_from_redis(user_id)
    # Изменяем валюту
    data['currency'] = new_currency
    # Сохраняем данные в Redis
    await save_data_to_redis(user_id, data)
    return True


# Функция проверки id пользователя в Redis и если нет - добавление в Redis ключа с id пользователя
async def create_company(user_id: str | int, user_name: str, company: str, currency: str):
    # Подключение к базе данных Redis
    r = await create_redis_client()
    # Проверка наличия ключа с id пользователя в Redis
    if not r.exists(user_id):
        # Добавление ключа с id пользователя в Redis а значением будет словарь с ключами "admins" и "users" и
        # "products" и "company", в "admins" сразу добавляем id пользователя
        r.set(user_id, json.dumps({"admins": {user_id: user_name}, "users": {}, "currency": currency, "company": company, "products": []}))


# Функция принимающая id пользователя и возвращающая data из Redis
async def get_data_from_redis(user_id: str | int) -> dict or bool:
    # Подключение к базе данных Redis
    r = await create_redis_client()
    # Получение данных из Redis
    if r.exists(user_id):
        data = r.get(user_id)
        return json.loads(data)
    else:
        return False


# a = get_data_from_redis('774411051')
# pp(a)


# Функция сохраняющая data в Redis по id пользователя
async def save_data_to_redis(user_id: int | str, data: dict) -> None:
    # Подключение к базе данных Redis
    r = await create_redis_client()
    # Сохранение данных в Redis
    r.set(user_id, json.dumps(data))


# Функция проверка наличия ключа "reports" и далее полную структуру отчетов в Redis
async def check_and_create_structure_reports(user_id: str | int):
    # Получаем данные пользователя из Redis
    data = await get_data_from_redis(user_id)
    # Получение сегодняшней даты
    today = datetime.datetime.today().strftime("%d.%m.%Y")

    # Проверка наличия ключа "reports" в структуре данных
    if 'reports' not in data:
        # Создание пустой структуры, если ключ "reports" отсутствует
        data['reports'] = {}

    # Проверка наличия ключа сегодняшней даты в структуре "reports"
    if today not in data['reports']:
        data['reports'][today] = {}

    # Проверка наличия ключа "sold_products" в структуре "today"
    if 'sold_products' not in data['reports'][today]:
        data['reports'][today]['sold_products'] = []

    # Проверка наличия ключа "return_products" в структуре "today"
    if 'return_products' not in data['reports'][today]:
        data['reports'][today]['return_products'] = []

    # Сохранение данных в Redis
    await save_data_to_redis(user_id, data)

    return True

