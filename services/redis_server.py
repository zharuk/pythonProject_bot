import json
import redis
from config_data.config import Config, load_config
import datetime


def create_redis_client():
    # Загружаем конфиг в переменную config
    config: Config = load_config()
    # Подключение к серверу Redis
    r = redis.Redis(host=config.redis.host, port=config.redis.port)
    return r


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

