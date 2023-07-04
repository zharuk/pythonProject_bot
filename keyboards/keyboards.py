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
        # Пропускаем ключ с названием 'reports'
        if key_sku == 'reports':
            continue  # Пропустить добавление кнопки
        buttons.append(InlineKeyboardButton(text=key_sku, callback_data=key_sku))

    # Сортируем кнопки по возрастанию
    buttons.sort(key=lambda x: x.text)

    # Создаем список списков кнопок
    inline_keyboard = [buttons]
    # Создаем кнопку "Отмена"
    cancel_button = InlineKeyboardButton(text='Отмена', callback_data='cancel')
    # Добавляем кнопку "Отмена" в список кнопок
    inline_keyboard.append([cancel_button])

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# Функция для формирования клавиатуры с кнопками названия которых будут все модификации товара.
# Название кнопок формируется из списка словарей 'variants' по ключам 'sku', 'color' и 'size.
# Например, название кнопки: sku = '121-1', 'color': 'черный', 'size': 'S' -> '121-1 черный S'.
# В callback_data кнопки записывается артикул модификация товара sku в словаре 'variants'.
# На вход функция принимает артикул товара и список словарей 'variants' и формирует клавиатуру.
def create_variants_kb(article, variants):
    # Инициализируем список для кнопок
    buttons = []

    # Создаем кнопки на основе ключей из Redis
    for variant in variants:
        # Формируем название кнопки
        button_name = f"Арт:{variant['sku']} ({variant['color']}-{variant['size']}) На складе - {str(variant['stock']) + 'шт.' if variant['stock'] > 0 else 'Нет в наличии'}"

        # Формируем callback_data кнопки
        button_callback_data = f"{variant['sku']}"
        # Создаем кнопку
        buttons.append([InlineKeyboardButton(text=button_name, callback_data=button_callback_data)])

    # Добавляем кнопку "Отмена"
    buttons.append([InlineKeyboardButton(text='Отмена', callback_data='cancel')])

    # Создаем список списков кнопок
    inline_keyboard = buttons

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# Функция создающая клавиатуру с 2 кнопками "Модификации товара" и "Показать фото"
def create_options_kb(article):
    # Создаем кнопку "Модификации товара"
    button_variants = InlineKeyboardButton(text='Модификации и остатки товара', callback_data=str(article) + '_variants')
    # Создаем кнопку "Показать фото"
    button_photo = InlineKeyboardButton(text='Показать фото', callback_data=str(article) + '_photo')
    # Создаем кнопку "Продать товар"
    button_sell = InlineKeyboardButton(text='Продать товар', callback_data=str(article) + '_sell')
    # Создаем кнопку отмены и сброса состояния, что бы сработал обработчик '/cancel'. Кнопка должна писать в чат
    # '/cancel'
    button_cancel = InlineKeyboardButton(text='Отмена', callback_data='cancel')

    # Создаем список списков кнопок
    inline_keyboard = [[button_variants], [button_photo], [button_sell], [button_cancel]]

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# Функция создающая клавиатуру с 1 кнопкой "Отмена"
def create_cancel_kb():
    # Создаем кнопку отмены и сброса состояния, что бы сработал обработчик '/cancel'. Кнопка должна писать в чат
    # '/cancel'
    button_cancel = InlineKeyboardButton(text='Отмена', callback_data='cancel')

    # Создаем список списков кнопок
    inline_keyboard = [[button_cancel]]

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# Функция создания клавиатуры для обработчиков /report.