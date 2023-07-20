import ast
import asyncio
import json
import redis
from config_data.config import Config, load_config
import datetime


# Создание подключения к базе данных Redis
def create_redis_client() -> redis.Redis:
    # Загружаем конфиг в переменную config
    config: Config = load_config()
    # Подключение к серверу Redis
    r = redis.Redis(host=config.redis.host, port=config.redis.port)
    return r


# Проверка id пользователя в Redis
async def check_user_id_in_redis(user_id):
    # Подключение к базе данных Redis
    r = create_redis_client()
    # Проверка наличия ключа с id пользователя в Redis
    if r.exists(user_id):
        return True
    else:
        return False


# Функция проверки id пользователя в Redis и если нет - добавление в Redis ключа с id пользователя
async def create_company(user_id: str, company: str, currency: str):
    # Подключение к базе данных Redis
    r = create_redis_client()
    # Проверка наличия ключа с id пользователя в Redis
    if not r.exists(user_id):
        # Добавление ключа с id пользователя в Redis а значением будет словарь с ключами "admins" и "users" и
        # "products" и "company", в "admins" сразу добавляем id пользователя
        r.set(user_id,
              json.dumps({"admins": [user_id], "users": [], "currency": currency, "company": company, "products": []}))


# Функция принимающая id пользователя и возвращающая data из Redis
def get_data_from_redis(user_id: str | int) -> dict or bool:
    # Подключение к базе данных Redis
    r = create_redis_client()
    # Получение данных из Redis
    if r.exists(user_id):
        data = r.get(user_id)
        return json.loads(data)
    else:
        return False


# Функция сохраняющая data в Redis по id пользователя
def save_data_to_redis(user_id: int | str, data: dict) -> None:
    # Подключение к базе данных Redis
    r = create_redis_client()
    # Сохранение данных в Redis
    r.set(user_id, json.dumps(data))


# Функция проверка наличия ключа "reports" и далее полную структуру отчетов в Redis
def check_and_create_structure_reports():
    # Подключение к базе данных Redis
    r = create_redis_client()

    # Проверка наличия ключа "reports"
    if r.exists('reports'):
        # Получение значения ключа "reports"
        reports_data = r.get('reports')
        reports = json.loads(reports_data)
    else:
        # Создание пустой структуры, если ключ "reports" отсутствует
        reports = {}

    # Получение сегодняшней даты
    today = datetime.datetime.today().strftime("%d.%m.%Y")

    # Проверка наличия ключа "sold_products" в структуре "reports"
    if 'sold_products' not in reports:
        reports['sold_products'] = {}

    # Проверка наличия ключа сегодняшней даты в структуре "today"
    if today not in reports['sold_products']:
        reports['sold_products'][today] = []

    # Проверка наличия ключа "return_products" в структуре "reports"
    if 'return_products' not in reports:
        reports['return_products'] = {}

    # Проверка наличия ключа сегодняшней даты в структуре "today"
    if today not in reports['return_products']:
        reports['return_products'][today] = []

    # Кодирование и сохранение структуры "reports" в базе данных Redis
    r.set('reports', json.dumps(reports))

    return True
