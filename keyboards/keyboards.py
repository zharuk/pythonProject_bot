from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from services.redis_server import get_data_from_redis


# Функция для формирования клавиатуры с кнопкой "Создать компанию"
async def create_company_kb():
    # Создаем кнопку "Создать компанию"
    create_company_button = InlineKeyboardButton(text='Создать компанию', callback_data='create_company')
    # Создаем список кнопок
    inline_keyboard = [[create_company_button]]
    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# Функция для формирования клавиатуры основной клавиатуры с кнопками "Список товаров", "Добавить товар",
# "Добавить товар одной строкой", "Статистика", "Меню"
async def create_main_kb():
    # Создаем кнопки "Список товаров", "Добавить товар", "Добавить товар одной строкой", "Статистика"
    show_button = InlineKeyboardButton(text='📋 Список товаров', callback_data='show')
    add_button = InlineKeyboardButton(text='➕ Добавить товар', callback_data='add')
    add_one_button = InlineKeyboardButton(text='➕ Добавить товар одной строкой', callback_data='add_one')
    report_button = InlineKeyboardButton(text='📊 Статистика', callback_data='report')
    # Создаем список кнопок
    inline_keyboard = [show_button], [add_button], [add_one_button], [report_button]
    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# Функция для формирования клавиатуры с кнопками "Вернутся в меню" , где callback_data = 'start' а также "вернутся к
# списку товаров" с callback_data = 'show'
async def create_back_kb():
    # Создаем кнопку "Вернутся в меню"
    back_button = InlineKeyboardButton(text='↩️ Вернуться в меню', callback_data='start')
    # Создаем кнопку "Вернутся к списку товаров"
    show_button = InlineKeyboardButton(text='↩️ Вернуться к списку товаров', callback_data='show')
    # Создаем список кнопок
    inline_keyboard = [[back_button], [show_button]]
    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# Функция для формирования клавиатуры, где кнопки являются артикулы товаров
async def create_sku_kb(user_id):
    # получаем данные из Redis по id пользователя
    data_user = await get_data_from_redis(user_id)
    # Инициализируем список для кнопок
    buttons = []
    # Создаем кнопки на основе ключей из data_user > products
    for key in data_user['products']:
        # Преобразуем ключ из байтов в строку
        key_sku = list(key.keys())[0]
        # Пропускаем ключ с названием 'reports'
        buttons.append(InlineKeyboardButton(text=key_sku, callback_data=key_sku + '_main_sku'))
    # Сортируем кнопки по возрастанию
    buttons.sort(key=lambda x: int(x.text))

    # Задаем количество кнопок в каждом ряду (здесь используется 8)
    buttons_per_row = 8
    # Разбиваем список кнопок на ряды
    rows = [buttons[i:i + buttons_per_row] for i in range(0, len(buttons), buttons_per_row)]

    # Добавляем кнопку "Добавить товар" с callback_data='add' в отдельный ряд
    buttons_add = InlineKeyboardButton(text='📁 Создать товар', callback_data='add')
    rows.append([buttons_add])

    # Добавляем кнопку "Вернутся в меню" с callback_data='start' в отдельный ряд
    buttons_back = InlineKeyboardButton(text='↩️ Вернуться в меню', callback_data='start')
    rows.append([buttons_back])

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Создаем клавиатуру с 2 кнопками отмена и готово
async def cancel_and_done_kb():
    # Создаем кнопки "Отмена" и "Готово"
    cancel_button = InlineKeyboardButton(text='⛔️ Отмена', callback_data='cancel')
    done_button = InlineKeyboardButton(text='✅ Готово', callback_data='done')
    # Создаем список кнопок
    inline_keyboard = [[cancel_button, done_button]]
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

    # Добавляем кнопку к списку товаров
    buttons.append([InlineKeyboardButton(text='↩️ Вернуться к списку товаров', callback_data='show')])
    # Добавляем кнопку "Отмена"
    buttons.append([InlineKeyboardButton(text='⛔️ Отмена', callback_data='cancel')])

    # Создаем список списков кнопок
    inline_keyboard = buttons

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# Функция создающая клавиатуру с 2 кнопками "Модификации товара" и "Показать фото"
async def create_options_kb(main_sku):
    # Создаем кнопку "Модификации товара"
    button_variants = InlineKeyboardButton(text='📦 Модификации и остатки товара',
                                           callback_data=str(main_sku) + '_variants')
    # Создаем кнопку "Показать фото"
    button_photo = InlineKeyboardButton(text='👀 Показать фото', callback_data=str(main_sku) + '_photo')
    # Создаем кнопку "Продать товар"
    button_sell = InlineKeyboardButton(text='💵 Продать товар', callback_data=str(main_sku) + '_sell_button')
    # Создаем кнопку вернуть товар
    button_return = InlineKeyboardButton(text='♻️ Вернуть товар', callback_data=str(main_sku) + '_return_button')
    # Создаем кнопку редактировать товар
    button_edit = InlineKeyboardButton(text='✍️ Редактировать товар', callback_data=str(main_sku) + '_edit_button')
    # Создаем кнопку вернутся к списку товаров
    button_show = InlineKeyboardButton(text='↩️ Вернуться к списку товаров', callback_data='show')
    # Создаем кнопку отмены и сброса состояния, что бы сработал обработчик '/cancel'.
    button_cancel = InlineKeyboardButton(text='⛔️ Отмена', callback_data='cancel')

    # Создаем список списков кнопок
    inline_keyboard = [[button_variants], [button_photo], [button_sell], [button_return], [button_edit], [button_show],
                       [button_cancel]]

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# Функция создающая клавиатуру с 1 кнопкой "Отмена"
async def create_cancel_kb():
    # Создаем кнопку 'возврат к списку товаров'
    button_show = InlineKeyboardButton(text='↩️ Вернуться к списку товаров', callback_data='show')
    # Создаем кнопку отмены и сброса состояния, что бы сработал обработчик '/cancel'. Кнопка должна писать в чат
    # '/cancel'
    button_cancel = InlineKeyboardButton(text='⛔️ Отмена', callback_data='cancel')

    # Создаем список списков кнопок
    inline_keyboard = [[button_show], [button_cancel]]

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
    button_cancel = InlineKeyboardButton(text='⛔️ Отмена', callback_data='cancel')

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
    button_delete = InlineKeyboardButton(text='💀 Удалить товар', callback_data=f'{sku}_edit_delete')
    # Создаем кнопку возврата к списку товаров
    button_show = InlineKeyboardButton(text='↩️ Вернуться назад', callback_data=f'{sku}_main_sku')
    # Создаем кнопку отмены и сброса состояния, что бы сработал обработчик '/cancel'. Кнопка должна писать в чат
    # '/cancel'
    button_cancel = InlineKeyboardButton(text='⛔️ Отмена', callback_data='cancel')

    # Создаем список списков кнопок
    inline_keyboard = [[button_name, button_description], [button_article, button_color], [button_size, button_price],
                       [button_variants, button_photo], [button_delete], [button_show], [button_cancel]]

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
    button_cancel = InlineKeyboardButton(text='⛔️ Отмена', callback_data='cancel')

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
    button_cancel = InlineKeyboardButton(text='⛔️ Отмена', callback_data='cancel')

    # Создаем список списков кнопок
    inline_keyboard = [buttons, [button_cancel]]

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# Функция создания клавиатуры для обработчиков /settings. Функция формирует такие кнопки: "Изменить имя компании",
# "Изменить валюту", "Добавить админа", "Добавить пользователя", "Удалить админа", "Удалить пользователя"
# "Удалить компанию", "Вернуться в меню"
async def create_settings_kb():
    # Создаем кнопку "Изменить имя компании"
    button_name = InlineKeyboardButton(text='Изменить имя компании', callback_data='edit_company_name')
    # Создаем кнопку "Изменить валюту"
    button_currency = InlineKeyboardButton(text='Изменить валюту', callback_data='edit_currency')
    # Создаем кнопку "Добавить админа"
    button_add_admin = InlineKeyboardButton(text='Добавить админа', callback_data='add_admin')
    # Создаем кнопку "Добавить пользователя"
    button_add_user = InlineKeyboardButton(text='Добавить пользователя', callback_data='add_user')
    # Создаем кнопку "Удалить админа"
    button_del_admin = InlineKeyboardButton(text='Удалить админа', callback_data='del_admin')
    # Создаем кнопку "Удалить пользователя"
    button_del_user = InlineKeyboardButton(text='Удалить пользователя', callback_data='del_user')
    # Создаем кнопку "Удалить компанию"
    button_del_company = InlineKeyboardButton(text='Удалить компанию', callback_data='del_company')
    # Создаем кнопку "Вернуться в меню"
    button_show = InlineKeyboardButton(text='↩️ Вернуться в меню', callback_data='start')

    # Создаем список списков кнопок
    inline_keyboard = [[button_name, button_currency], [button_add_admin, button_add_user],
                       [button_del_admin, button_del_user], [button_del_company], [button_show]]

    # Возвращаем объект инлайн-клавиатуры
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
