from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config_data.config import load_config
import redis

# Загрузка конфигурации
config = load_config()

# Подключение к серверу Redis
r = redis.Redis(host=config.redis.host, port=config.redis.port)

# Функция для формирования инлайн-клавиатуры на лету на основе ключей из Redis
def create_inline_kb():

    # Получаем ключи из Redis
    keys = r.keys()

    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Создаем кнопки на основе ключей из Redis
    for key in keys:
        # Преобразуем ключ из байтов в строку
        key_str = key.decode('utf-8')
        buttons.append(InlineKeyboardButton(text=key_str, callback_data=key_str))

    # Распаковываем список с кнопками в билдер методом row с параметром width
    kb_builder.row(*buttons)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup()
