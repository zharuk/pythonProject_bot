import json
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from services.redis_server import create_redis_client

# Подключение к серверу Redis
r = create_redis_client()


# Функция для формирования инлайн-клавиатуры на лету на основе ключей из Redis
def create_sku_kb():
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


# Функция создающая клавиатуру с 2 кнопками "Модификации товара" и "Показать фото"
def create_options_kb(article):
    # Создаем кнопки
    button_variants = InlineKeyboardButton(text='Модификации товара', callback_data=str(article) + '_variants')
    button_photo = InlineKeyboardButton(text='Показать фото', callback_data=str(article) + '_photo')

    # Создаем список списков кнопок
    inline_keyboard = [[button_variants, button_photo]]

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)