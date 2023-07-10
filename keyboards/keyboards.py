import asyncio
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from services.redis_server import create_redis_client

# Подключение к серверу Redis
r = create_redis_client()


# Функция для формирования инлайн-клавиатуры, где кнопки являются ключами из Redis т.е артикулами товаров
async def create_sku_kb():
    # Получаем ключи из Redis
    keys = await asyncio.get_event_loop().run_in_executor(None, r.keys)

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
    buttons.sort(key=lambda x: int(x.text))

    # Разбиваем кнопки на строки по 8 кнопок в каждой
    rows = [buttons[i:i + 8] for i in range(0, len(buttons), 8)]

    # Создаем список списков кнопок
    inline_keyboard = rows
    # Создаем кнопку "Отмена"
    cancel_button = InlineKeyboardButton(text='Отмена', callback_data='cancel')
    # Добавляем кнопку "Отмена" в последнюю строку
    inline_keyboard.append([cancel_button])

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)



# Функция для формирования клавиатуры с кнопками названия которых будут все модификации товара.
# Название кнопок формируется из списка словарей 'variants' по ключам 'sku', 'color' и 'size.
# Например, название кнопки: sku = '121-1', 'color': 'черный', 'size': 'S' -> '121-1 черный S'.
# В callback_data кнопки записывается артикул модификация товара sku в словаре 'variants'.
# На вход функция принимает артикул товара и список словарей 'variants' и формирует клавиатуру.
async def create_variants_kb(variants, for_what=None):
    # Инициализируем список для кнопок
    buttons = []

    # Создаем кнопки на основе ключей из Redis
    for variant in variants:
        # Формируем название кнопки
        button_name = f"Арт:{variant['sku']} ({variant['color']}-{variant['size']}) На складе - {'✅ ' + str(variant['stock']) + 'шт.' if int(variant['stock']) > 0 else '❌ Нет в наличии'}"

        # Формируем callback_data кнопки
        button_callback_data = f"{variant['sku']}"
        # Создаем кнопку
        buttons.append([InlineKeyboardButton(text=button_name, callback_data=button_callback_data + for_what)])

    # Добавляем кнопку "Отмена"
    buttons.append([InlineKeyboardButton(text='Отмена', callback_data='cancel')])

    # Создаем список списков кнопок
    inline_keyboard = buttons

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# Функция создающая клавиатуру с 2 кнопками "Модификации товара" и "Показать фото"
async def create_options_kb(article):
    # Создаем кнопку "Модификации товара"
    button_variants = InlineKeyboardButton(text='Модификации и остатки товара',
                                           callback_data=str(article) + '_variants')
    # Создаем кнопку "Показать фото"
    button_photo = InlineKeyboardButton(text='Показать фото', callback_data=str(article) + '_photo')
    # Создаем кнопку "Продать товар"
    button_sell = InlineKeyboardButton(text='Продать товар', callback_data=str(article) + '_sell_button')
    # Создаем кнопку вернуть товар
    button_return = InlineKeyboardButton(text='Вернуть товар', callback_data=str(article) + '_return_button')
    # Создаем кнопку редактировать товар
    button_edit = InlineKeyboardButton(text='Редактировать товар', callback_data=str(article) + '_edit_button')
    # Создаем кнопку отмены и сброса состояния, что бы сработал обработчик '/cancel'.
    button_cancel = InlineKeyboardButton(text='Отмена', callback_data='cancel')

    # Создаем список списков кнопок
    inline_keyboard = [[button_variants], [button_photo], [button_sell], [button_return], [button_edit],
                       [button_cancel]]

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# Функция создающая клавиатуру с 1 кнопкой "Отмена"
async def create_cancel_kb():
    # Создаем кнопку отмены и сброса состояния, что бы сработал обработчик '/cancel'. Кнопка должна писать в чат
    # '/cancel'
    button_cancel = InlineKeyboardButton(text='Отмена', callback_data='cancel')

    # Создаем список списков кнопок
    inline_keyboard = [[button_cancel]]

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# Функция создания клавиатуры для обработчиков /report. Функция формирует 6 кнопки продажи за сегодня, продажи за
# неделю, продажи за месяц и продажи за год и выбрать период и кнопка отмены
async def create_report_kb():
    # Создаем кнопку "Продажи за сегодня"
    button_today = InlineKeyboardButton(text='Продажи за сегодня', callback_data='today')
    # Создаем кнопку "Продажи за неделю"
    button_week = InlineKeyboardButton(text='Продажи за неделю', callback_data='week')
    # Создаем кнопку "Продажи за месяц"
    button_month = InlineKeyboardButton(text='Продажи за месяц', callback_data='month')
    # Создаем кнопку "Продажи за год"
    button_year = InlineKeyboardButton(text='Продажи за год', callback_data='year')
    # Создаем кнопку "Выбрать период"
    button_period = InlineKeyboardButton(text='Выбрать период', callback_data='period')
    # Создаем кнопку отмены и сброса состояния, что бы сработал обработчик '/cancel'. Кнопка должна писать в чат
    # '/cancel'
    button_cancel = InlineKeyboardButton(text='Отмена', callback_data='cancel')

    # Создаем список списков кнопок
    inline_keyboard = [[button_today, button_week], [button_month, button_year], [button_period], [button_cancel]]

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# Создаем клавиатуру для редактирования товара которая бы состояла из кнопок изменить название, изменить
# описание, изменить артикул, изменить цвета, изменить размеры, изменить цену, изменить комплектацию товара,
# обновить фото, удалить товар, отмена
async def create_edit_kb(sku):
    # Создаем кнопку "Изменить название"
    button_name = InlineKeyboardButton(text='Изменить название', callback_data=f'{sku}_edit_name')
    # Создаем кнопку "Изменить описание"
    button_description = InlineKeyboardButton(text='Изменить описание', callback_data=f'{sku}_edit_description')
    # Создаем кнопку "Изменить артикул"
    button_article = InlineKeyboardButton(text='Изменить артикул', callback_data=f'{sku}_edit_sku')
    # Создаем кнопку "Изменить цвета"
    button_color = InlineKeyboardButton(text='Изменить цвета', callback_data=f'{sku}_edit_color')
    # Создаем кнопку "Изменить размеры"
    button_size = InlineKeyboardButton(text='Изменить размеры', callback_data=f'{sku}_edit_size')
    # Создаем кнопку "Изменить цену"
    button_price = InlineKeyboardButton(text='Изменить цену', callback_data=f'{sku}_edit_price')
    # Создаем кнопку "Изменить комплектацию"
    button_variants = InlineKeyboardButton(text='Изменить остатки', callback_data=f'{sku}_edit_stock')
    # Создаем кнопку "Обновить фото"
    button_photo = InlineKeyboardButton(text='Обновить фото', callback_data=f'{sku}_edit_photo')
    # Создаем кнопку "Удалить товар"
    button_delete = InlineKeyboardButton(text='Удалить товар', callback_data=f'{sku}_edit_delete')
    # Создаем кнопку отмены и сброса состояния, что бы сработал обработчик '/cancel'. Кнопка должна писать в чат
    # '/cancel'
    button_cancel = InlineKeyboardButton(text='Отмена', callback_data='cancel')

    # Создаем список списков кнопок
    inline_keyboard = [[button_name, button_description], [button_article, button_color], [button_size, button_price],
                       [button_variants, button_photo], [button_delete], [button_cancel]]

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# Функция создания клавиатуры для обработчиков /edit. Функция формирует кнопки с цветами товара и кнопку отмены. В
# качестве аргумента принимает список цветов товара. Кнопки цветов должны быть в одном ряду а кнопка отмены во втором
# отдельном ряду
async def create_edit_color_kb(colors):
    # Создаем список кнопок цветов
    buttons = []
    for color in colors:
        buttons.append(InlineKeyboardButton(text=color, callback_data=f'{color}_show_color'))

    # Создаем кнопку отмены и сброса состояния, что бы сработал обработчик '/cancel'. Кнопка должна писать в чат
    # '/cancel'
    button_cancel = InlineKeyboardButton(text='Отмена', callback_data='cancel')

    # Создаем список списков кнопок
    inline_keyboard = [buttons, [button_cancel]]

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# Функция создания клавиатуры для обработчиков /edit. Функция формирует кнопки с размерами товара и кнопку отмены. В
# качестве аргумента принимает список размеров товара. Кнопки размеров должны быть в одном ряду а кнопка отмены во
# втором отдельном ряду
async def create_edit_size_kb(sizes):
    # Создаем список кнопок размеров
    buttons = []
    for size in sizes:
        buttons.append(InlineKeyboardButton(text=size, callback_data=f'{size}_show_size'))

    # Создаем кнопку отмены и сброса состояния, что бы сработал обработчик '/cancel'. Кнопка должна писать в чат
    # '/cancel'
    button_cancel = InlineKeyboardButton(text='Отмена', callback_data='cancel')

    # Создаем список списков кнопок
    inline_keyboard = [buttons, [button_cancel]]

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

