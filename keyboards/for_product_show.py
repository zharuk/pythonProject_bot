from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config_data.config import load_config
import redis

# Загрузка конфигурации
config = load_config()

# Подключение к серверу Redis
r = redis.Redis(host=config.redis.host, port=config.redis.port)


# Функция для формирования инлайн-клавиатуры на лету на основе ключей из Redis
def create_products_kb():
    # Получаем ключи из Redis
    keys = r.keys()

    # Инициализируем список для кнопок
    buttons = []

    # Создаем кнопки на основе ключей из Redis
    for key in keys:
        # Преобразуем ключ из байтов в строку
        key_sku = key.decode('utf-8')
        buttons.append(InlineKeyboardButton(text=key_sku, callback_data=key_sku))

    # Создаем список списков кнопок
    inline_keyboard = [buttons]

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

