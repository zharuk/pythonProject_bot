import json
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from services.redis_server import create_redis_client

# Подключение к серверу Redis
r = create_redis_client()


# Функция для формирования инлайн-клавиатуры, где кнопки являются ключами из Redis т.е артикулами товаров
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


# Функция для формирования клавиатуры с кнопками названия которых будут все модификации товара т.е 001-1, 001-2 и т.д
def create_variants_kb(article):
    # Получаем значение из Redis по артикулу
    value = r.get(article)
    # Преобразуем значение в словарь json
    json_value = json.loads(value)
    # Получаем список модификаций товара
    value_variants = json_value['variants']

    # Инициализируем список для кнопок
    buttons = []

    # Создаем кнопки на основе списка модификаций товара
    for variant in value_variants:
        buttons.append(InlineKeyboardButton(text=variant, callback_data=variant))

    # Создаем список списков кнопок
    inline_keyboard = [buttons]

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# Функция создающая клавиатуру с 2 кнопками "Модификации товара" и "Показать фото"
def create_options_kb(article):
    # Создаем кнопку "Модификации товара"
    button_variants = InlineKeyboardButton(text='Модификации товара', callback_data=str(article) + '_variants')
    # Создаем кнопку "Показать фото"
    button_photo = InlineKeyboardButton(text='Показать фото', callback_data=str(article) + '_photo')
    # Создаем кнопку "Продать товар"
    button_sell = InlineKeyboardButton(text='Продать товар', callback_data=str(article) + '_sell')

    # Создаем список списков кнопок
    inline_keyboard = [[button_variants], [button_photo], [button_sell]]

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
