from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from FSM.fsm import SellItemStates, ReturnItemStates, FSMEditProduct
from keyboards.keyboards import create_sku_kb, create_options_kb, create_variants_kb, create_cancel_kb, create_edit_kb, \
    create_edit_color_kb, create_edit_size_kb
from services.edit import edit_name, edit_description, edit_sku, edit_color, edit_size, check_color, check_size, \
    edit_price, check_price, get_stock, check_stock, edit_stock
from services.product import format_variants_message, generate_photos, format_main_info, return_product
import json
from services.redis_server import create_redis_client
from services.product import sell_product

router: Router = Router()
r = create_redis_client()


# Обработчик команды /show для вывода списка товаров с помощью инлайн-клавиатуры с артикулами товаров
@router.message(Command(commands='show'))
async def process_show_command(message: Message):
    # Создаем инлайн-клавиатуру с артикулами товаров
    kb = await create_sku_kb()
    # Отправляем сообщение пользователю
    await message.answer(text='Выберите товар или нажмите <b>отмена</b>', reply_markup=kb)


# Обработчик для кнопок с артикулами товаров в которых callback_data = артикулу товара
@router.callback_query(lambda callback_query: callback_query.data.isdigit())
async def process_callback_query(callback_query: CallbackQuery):
    # Получаем значение артикула товара из callback_data
    article = callback_query.data
    # Получаем значение из Redis по артикулу
    value = r.get(article)
    # Преобразуем значение в словарь json
    json_value = json.loads(value)
    # формируем основную информацию о товаре с помощью функции
    main_info = format_main_info(json_value)
    # формируем клавиатуру с 2 кнопками "Модификации товара" и "Показать фото" с помощью функции create_kb
    kb = await create_options_kb(article)
    # Отправляем значение пользователю
    await callback_query.message.answer(main_info, reply_markup=kb)
    await callback_query.answer()


# Обработчик для кнопки "Модификации товара" в которой callback_data = '_variants'
@router.callback_query(lambda callback_query: '_variants' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # Получаем значение артикула товара из callback_data
    article = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    value = r.get(article)
    json_value = json.loads(value)
    # вывод комплектаций товара
    value_variants = json_value['variants']
    formatted_variants = format_variants_message(value_variants)
    # Создаем клавиатуру с всеми товарами create_sku_kb()
    kb = await create_options_kb(article)
    # Отправляем значение пользователю
    await callback_query.message.answer(formatted_variants)
    await callback_query.message.answer(text='Выберите действие 👇', reply_markup=kb)
    await callback_query.answer()


# Обработчик для кнопки "Модификации товара" в которой callback_data = '_photo'
@router.callback_query(lambda callback_query: '_photo' in callback_query.data and '_edit' not in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # Получаем значение артикула товара из callback_data
    article = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    value = r.get(article)
    json_value = json.loads(value)
    # Создаем клавиатуру с всеми товарами create_sku_kb()
    kb = await create_options_kb(article)
    # Создаем список фотографий
    if 'photo_ids' in json_value:
        photo_ids = json_value['photo_ids']
        # Отправляем все фотографии одним сообщением
        await callback_query.message.answer_media_group(generate_photos(photo_ids))
        # Отправляем клавиатуру пользователю
        await callback_query.message.answer(text='Выберите действие 👇', reply_markup=kb)
    else:
        await callback_query.message.answer('Фото нет')
    await callback_query.answer()


# Обработчик для кнопки "Продать товар" в которой callback_data = '_sell', выводит список товаров
@router.callback_query(lambda callback_query: '_sell_button' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # Получаем значение артикула товара из callback_data
    main_article = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    value = r.get(main_article)
    # Преобразуем значение в словарь json
    json_value = json.loads(value)
    # Получаем значение variants из json_value
    json_value_variants = json_value['variants']
    # Создаем клавиатуру с вариантами товара
    kb = await create_variants_kb(json_value_variants, for_what='_sell_variant')
    # Отправляем клавиатуру пользователю
    await callback_query.message.answer(text='Выберите товар или нажмите отмена 👇', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который срабатывает при нажатии на кнопку с вариантом товара и просит ввести количество продаваемого
# товара сообщением "Введите количество:"
@router.callback_query(lambda callback_query: '_sell_variant' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение артикула товара из callback_data
    article_variant = callback_query.data.split('_')[0]
    # Устанавливаем FSM SellItemStates article
    await state.update_data(article_variant=article_variant)
    # Переводим в состояние SellItemStates.quantity
    await state.set_state(SellItemStates.quantity)
    # Создаем клавиатуру с кнопкой "Отмена"
    kb = await create_cancel_kb()
    # Отвечаем пользователю сообщением "Введите количество:"
    await callback_query.message.answer(text='Введите количество или нажмите <b>отмена</b>', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который обрабатывает введенное число пользователем
@router.message(StateFilter(SellItemStates.quantity), lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def process_quantity(message: Message, state: FSMContext):
    # Получаем значение введенное пользователем
    quantity = int(message.text)
    # Получаем значение article_variant из FSM
    data = await state.get_data()
    article_variant = data.get("article_variant")
    # Получаем значение из Redis по артикулу
    value = r.get(article_variant.split('-')[0])
    # Преобразуем значение в словарь json
    json_value = json.loads(value)
    # вывод комплектаций товара
    value_variants = json_value['variants']
    # Получаем название товара
    name = ''
    for i in value_variants:
        if i['sku'] == article_variant:
            name = i['name']
            break
    # вызываем функцию sell_product
    if sell_product(article_variant, quantity) is True:
        # Пишем сообщение пользователю, что товар продан в количестве quantity штук
        await message.answer(text=f'Товар {name} продан в количестве {quantity} шт.')
        # Выводим список товаров
        await message.answer(text='Перейти к списку товаров /show')
        # Переводим в состояние default
        await state.clear()
    else:
        # Пишем сообщение пользователю, что товара не хватает на складе
        await message.answer(text=f'Товара {name} <b>не хватает на складе</b>. Выберете другой товар или нажмите '
                                  f'"Отмена"')


# Обработчик, если было введено не число от 1 до 100
@router.message(StateFilter(SellItemStates.quantity), lambda x: x.text and not x.text.isdigit() or int(x.text) < 1 or int(x.text) > 100)
async def process_quantity(message: Message, state: FSMContext):
    # Делаем клавиатуру с одной кнопкой "Отмена"
    kb = await create_cancel_kb()
    # Пишем сообщение пользователю, что было введено не число от 1 до 100
    await message.answer(text='Введите число от 1 до 100 или нажмите <b>отмена</b>', reply_markup=kb)


# Обработчик кнопки вернуть товар
@router.callback_query(lambda callback_query: '_return_button' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # Получаем значение артикула товара из callback_data
    main_article = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    value = r.get(main_article)
    # Преобразуем значение в словарь json
    json_value = json.loads(value)
    # Получаем значение variants из json_value
    json_value_variants = json_value['variants']
    # Создаем клавиатуру с вариантами товара
    kb = await create_variants_kb(json_value_variants, for_what='_return_variant')
    # Отправляем клавиатуру пользователю
    await callback_query.message.answer(text='Выберите товар для возврата или нажмите отмена 👇', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который срабатывает при нажатии на кнопку с вариантом товара и просит ввести количество возвращаемого
# товара сообщением "Введите количество:"
@router.callback_query(lambda callback_query: '_return_variant' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение артикула товара из callback_data
    article_variant = callback_query.data.split('_')[0]
    # Устанавливаем FSM SellItemStates article
    await state.update_data(article_variant=article_variant)
    # Переводим в состояние SellItemStates.quantity
    await state.set_state(ReturnItemStates.quantity)
    # Создаем клавиатуру с кнопкой "Отмена"
    kb = await create_cancel_kb()
    # Отвечаем пользователю сообщением "Введите количество:"
    await callback_query.message.answer(text='Введите количество или нажмите <b>отмена</b>', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который обрабатывает введенное число пользователем
@router.message(StateFilter(ReturnItemStates.quantity), lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def process_quantity(message: Message, state: FSMContext):
    # Получаем значение введенное пользователем
    quantity = int(message.text)
    # Получаем значение article_variant из FSM
    data = await state.get_data()
    article_variant = data.get("article_variant")
    # Получаем значение из Redis по артикулу
    value = r.get(article_variant.split('-')[0])
    # Преобразуем значение в словарь json
    json_value = json.loads(value)
    # вывод комплектаций товара
    value_variants = json_value['variants']
    # Получаем название товара
    name = ''
    for i in value_variants:
        if i['sku'] == article_variant:
            name = i['name']
            break
    # вызываем функцию return_product
    if return_product(article_variant, quantity) is True:
        # Пишем сообщение пользователю, что товар продан в количестве quantity штук
        await message.answer(text=f'Товар {name} возвращен в количестве {quantity} шт.')
        # Выводим список товаров
        await message.answer(text='Перейти к списку товаров /show')
        # Переводим в состояние default
        await state.clear()
    else:
        # Пишем сообщение пользователю, что товара не хватает на складе
        await message.answer(text='При возврате товара произошла ошибка. Попробуйте еще раз или нажмите "Отмена"')


# Обработчик, если было введено не число от 1 до 100
@router.message(StateFilter(ReturnItemStates.quantity), lambda x: x.text and not x.text.isdigit() or int(x.text) < 1 or int(x.text) > 100)
async def process_quantity(message: Message, state: FSMContext):
    # Делаем клавиатуру с одной кнопкой "Отмена"
    kb = await create_cancel_kb()
    # Пишем сообщение пользователю, что было введено не число от 1 до 100
    await message.answer(text='Введите число от 1 до 100 или нажмите <b>отмена</b>', reply_markup=kb)


# Обработчик кнопки редактировать товар
@router.callback_query(lambda callback_query: '_edit_button' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # Получаем значение артикула товара из callback_data
    main_article = callback_query.data.split('_')[0]
    # создаем клавиатуру с кнопками с помощью функции create_edit_kb
    kb = await create_edit_kb(main_article)
    # Отправляем клавиатуру пользователю
    await callback_query.message.answer(text='Выберите что хотите отредактировать 👇', reply_markup=kb)


# Обработчик кнопки редактировать наименование товара
@router.callback_query(lambda callback_query: '_edit_name' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение артикула товара из callback_data
    main_article = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    value = r.get(main_article)
    # Преобразуем значение в словарь json
    json_value = json.loads(value)
    # Создаем клавиатуру с кнопкой "Отмена"
    kb = await create_cancel_kb()
    # Устанавливаем FSMEditProduct edit_name
    await state.set_state(FSMEditProduct.edit_name)
    # Сохраняем артикул товара в FSM
    await state.update_data(main_article=main_article)
    # Отправляем пользователю сообщение с названием товара на данный момент и просим ввести новое название или отменить
    await callback_query.message.answer(text=f'Текущее название товара: <b>{json_value["name"]}\n</b> Введите новое '
                                             'название товара или нажмите <b>отмена</b>', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который обрабатывает введенное название товара пользователем
@router.message(StateFilter(FSMEditProduct.edit_name))
async def process_name(message: Message, state: FSMContext):
    # Получаем значение введенное пользователем
    name = message.text
    # Получаем значение main_article из FSM
    data = await state.get_data()
    main_article = data.get("main_article")
    # Получаем значение из Redis по артикулу
    value = r.get(main_article)
    # Преобразуем значение в словарь json
    json_value = json.loads(value)
    # Применяем функцию edit_name
    new_name = edit_name(json_value, name)
    # Конвертируем словарь в json
    new_name = json.dumps(new_name)
    # Перезаписываем значение в Redis
    r.set(main_article, new_name)
    # Создаем клавиатуру с действия по редактированию товара
    kb = await create_edit_kb(main_article)
    # Пишем сообщение пользователю, что товар отредактирован и теперь его название name
    await message.answer(text=f'Товар отредактирован и теперь его название: <b>{name}</b>', reply_markup=kb)
    # Сбрасываем состояние
    await state.clear()


# Обработчик кнопки редактировать описание товара
@router.callback_query(lambda callback_query: '_edit_description' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение артикула товара из callback_data
    main_article = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    value = r.get(main_article)
    # Преобразуем значение в словарь json
    json_value = json.loads(value)
    # Создаем клавиатуру с кнопкой "Отмена"
    kb = await create_cancel_kb()
    # Устанавливаем FSMEditProduct edit_description
    await state.set_state(FSMEditProduct.edit_description)
    # Сохраняем артикул товара в FSM
    await state.update_data(main_article=main_article)
    # Отправляем пользователю сообщение с описанием товара на данный момент и просим ввести новое описание или отменить
    await callback_query.message.answer(text=f'Текущее описание товара: <b>{json_value["description"]}\n</b> Введите '
                                             f'новое описание товара или нажмите <b>отмена</b>', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который обрабатывает введенное описание товара пользователем
@router.message(StateFilter(FSMEditProduct.edit_description))
async def process_description(message: Message, state: FSMContext):
    # Получаем значение введенное пользователем
    description = message.text
    # Получаем значение main_article из FSM
    data = await state.get_data()
    main_article = data.get("main_article")
    # Получаем значение из Redis по артикулу
    value = r.get(main_article)
    # Преобразуем значение в словарь json
    json_value = json.loads(value)
    # Применяем функцию edit_description
    new_description = edit_description(json_value, description)
    # Конвертируем словарь в json
    new_description = json.dumps(new_description)
    # Перезаписываем значение в Redis
    r.set(main_article, new_description)
    # Создаем клавиатуру с действия по редактированию товара
    kb = await create_edit_kb(main_article)
    # Пишем сообщение пользователю, что товар отредактирован и теперь его описание description
    await message.answer(text=f'Товар отредактирован и теперь его описание: <b>{description}</b>', reply_markup=kb)
    # Сбрасываем состояние
    await state.clear()


# Обработчик кнопки редактировать артикул товара
@router.callback_query(lambda callback_query: '_edit_sku' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение артикула товара из callback_data
    main_article = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    value = r.get(main_article)
    # Преобразуем значение в словарь json
    json_value = json.loads(value)
    # Создаем клавиатуру с кнопкой "Отмена"
    kb = await create_cancel_kb()
    # Устанавливаем FSMEditProduct edit_article
    await state.set_state(FSMEditProduct.edit_sku)
    # Сохраняем артикул товара в FSM
    await state.update_data(main_article=main_article)
    # Отправляем пользователю сообщение с артикулом товара на данный момент и просим ввести новый артикул или отменить
    await callback_query.message.answer(text=f'Текущий артикул товара: <b>{json_value["sku"]}\n</b> Введите новый '
                                             f'артикул товара или нажмите <b>отмена</b>', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который обрабатывает введенный артикул товара пользователем
@router.message(StateFilter(FSMEditProduct.edit_sku))
async def process_sku(message: Message, state: FSMContext):
    # Получаем значение введенное пользователем
    sku = message.text
    # Проверяем введенный артикул на уникальность в Redis
    if r.get(sku):
        await message.answer(text=f'Товар с артикулом <b>{sku}</b> уже существует. Введите другой артикул или нажмите '
                                  f'<b>отмена</b>')
        return
    else:
        # Получаем значение main_article из FSM
        data = await state.get_data()
        main_article = data.get("main_article")
        # Получаем значение из Redis по артикулу
        value = r.get(main_article)
        # Преобразуем значение в словарь json
        json_value = json.loads(value)
        # Применяем функцию edit_sku
        new_sku = edit_sku(json_value, sku)
        # Конвертируем словарь в json
        new_sku = json.dumps(new_sku)
        # Перезаписываем значение в Redis
        r.set(sku, new_sku)
        # Удаляем старый артикул
        r.delete(main_article)
        # Создаем клавиатуру с действия по редактированию товара
        kb = await create_edit_kb(sku)
        # Пишем сообщение пользователю, что товар отредактирован и теперь его артикул sku
        await message.answer(text=f'Товар отредактирован и теперь его артикул: <b>{sku}</b>', reply_markup=kb)
        # Сбрасываем состояние
        await state.clear()


# Обработчик кнопки редактировать цвет товара
@router.callback_query(lambda callback_query: '_edit_color' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение артикула товара из callback_data
    main_article = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    value = r.get(main_article)
    # Преобразуем значение в словарь json
    json_value = json.loads(value)
    # Получаем список цветов товара
    colors = json_value['colors']
    # Создаем клавиатуру с кнопками цветов товара и кнопкой "Отмена"
    kb = await create_edit_color_kb(colors)
    # Устанавливаем FSMEditProduct edit_color
    await state.set_state(FSMEditProduct.edit_color)
    # Сохраняем артикул товара в FSM
    await state.update_data(main_article=main_article)
    # Отправляем пользователю сообщение с цветами товара на данный момент и просим выбрать новый цвет или отменить
    await callback_query.message.answer(text=f'Текущие цвета товара: <b>{colors}\n</b> Выберите цвет или '
                                             f'нажмите <b>отмена</b>', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который обрабатывает выбранный цвет товара пользователем
@router.callback_query(lambda callback_query: '_show_color' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Записываем в FSM выбранный цвет
    await state.update_data(selected_color=callback_query.data.split("_")[0].lower())
    # Создаем клавиатуру с кнопкой "Отмена"
    kb = await create_cancel_kb()
    # Пишем пользователю какой цвет он выбрал и просим ввести новый цвет или отменить
    await callback_query.message.answer(
        text=f'Вы выбрали цвет для редактирования: <b>{callback_query.data.split("_")[0]}</b>\n'
             f'Введите новый цвет или нажмите <b>отмена</b>', reply_markup=kb)


# Обработчик, который обрабатывает введенный цвет товара пользователем.
@router.message(StateFilter(FSMEditProduct.edit_color))
async def process_color(message: Message, state: FSMContext):
    # Создаем клавиатуру с кнопкой "Отмена"
    kb = await create_cancel_kb()
    # Проверяем цвет на валидность
    if check_color(message.text.lower()):
        # Сохраняем введенный пользователем цвет в FSM
        await state.update_data(desired_color=message.text.lower())
        # Получаем значение из FSM выбранного цвета для замены и желаемого цвета
        data = await state.get_data()
        selected_color = data.get("selected_color")
        desired_color = data.get("desired_color")
        # Получаем значение main_article из FSM
        data = await state.get_data()
        main_article = data.get("main_article")
        # Получаем значение из Redis по артикулу
        value = r.get(main_article)
        # Преобразуем значение в словарь json
        json_value = json.loads(value)
        # Применяем функцию edit_color
        new_color = edit_color(json_value, selected_color, desired_color)
        # Конвертируем словарь в json
        new_color_dump = json.dumps(new_color)
        # Перезаписываем значение в Redis
        r.set(main_article, new_color_dump)
        # Очищаем состояние
        await state.clear()
        # Выводим пользователю сообщение, что цвет товара отредактирован и теперь его цвет desired_color, а также
        # выводим, что все цвета товара теперь new_color['colors']
        await message.answer(text=f'Цвет товара отредактирован и теперь его цвет: <b>{desired_color}</b>\n'
                                  f'Все цвета товара: <b>{new_color["colors"]}</b>')
    else:
        # Если цвет не валидный, то выводим сообщение об ошибке и просим ввести новый цвет или отменить
        await message.answer(text=f'Цвет введен неверно, попробуйте еще раз или нажмите <b>отмена</b>', reply_markup=kb)


# Обработчик кнопки редактировать размер товара. Работает аналогично кнопке редактировать цвет товара.
@router.callback_query(lambda callback_query: '_edit_size' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    main_article = callback_query.data.split('_')[0]
    value = r.get(main_article)
    json_value = json.loads(value)
    sizes = json_value['sizes']
    kb = await create_edit_size_kb(sizes)
    await state.set_state(FSMEditProduct.edit_size)
    await state.update_data(main_article=main_article)
    await callback_query.message.answer(text=f'Текущие размеры товара: <b>{sizes}\n</b> Выберите размер или '
                                             f'нажмите <b>отмена</b>', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который обрабатывает выбранный размер товара пользователем
@router.callback_query(lambda callback_query: '_show_size' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    await state.update_data(selected_size=callback_query.data.split("_")[0].lower())
    kb = await create_cancel_kb()
    await callback_query.message.answer(
        text=f'Вы выбрали размер для редактирования: <b>{callback_query.data.split("_")[0]}</b>\n'
             f'Введите новый размер или нажмите <b>отмена</b>', reply_markup=kb)


# Обработчик, который обрабатывает введенный размер товара пользователем.
@router.message(StateFilter(FSMEditProduct.edit_size))
async def process_size(message: Message, state: FSMContext):
    kb = await create_cancel_kb()
    if check_size(message.text.lower()):
        await state.update_data(desired_size=message.text.lower())
        data = await state.get_data()
        selected_size = data.get("selected_size")
        desired_size = data.get("desired_size")
        data = await state.get_data()
        main_article = data.get("main_article")
        value = r.get(main_article)
        json_value = json.loads(value)
        new_size = edit_size(json_value, selected_size, desired_size)
        new_size_dump = json.dumps(new_size)
        r.set(main_article, new_size_dump)
        await state.clear()
        await message.answer(text=f'Размер товара отредактирован и теперь его размер: <b>{desired_size}</b>\n'
                                  f'Все размеры товара: <b>{new_size["sizes"]}</b>')
    else:
        await message.answer(text=f'Размер введен неверно, попробуйте еще раз или нажмите <b>отмена</b>',
                             reply_markup=kb)


# Обработчик кнопки редактировать цену товара. Работает аналогично кнопке редактировать цвет товара.
@router.callback_query(lambda callback_query: '_edit_price' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение main_article из callback_query
    main_article = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    value = r.get(main_article)
    # Преобразуем значение в словарь json
    json_value = json.loads(value)
    # Получаем значение цены товара
    price = json_value['price']
    # Создаем клавиатуру с кнопками для ввода цены или отмены
    kb = await create_cancel_kb()
    # Устанавливаем состояние edit_price
    await state.set_state(FSMEditProduct.edit_price)
    # Обновляем данные в состоянии
    await state.update_data(main_article=main_article)
    # Отправляем пользователю сообщение с текущей ценой товара и клавиатурой
    await callback_query.message.answer(text=f'Текущая цена товара: <b>{price}\n</b> Введите новую цену или '
                                             f'нажмите <b>отмена</b>', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который обрабатывает введенную цену товара пользователем.
@router.message(StateFilter(FSMEditProduct.edit_price))
async def process_price(message: Message, state: FSMContext):
    # Создаем клавиатуру с кнопками для отмены
    kb = await create_cancel_kb()
    # Проверяем, что цена введена корректно
    if check_price(message.text):
        # Если цена введена корректно, то обновляем данные в состоянии
        await state.update_data(desired_price=message.text)
        # Получаем данные из состояния
        data = await state.get_data()
        # Получаем значение main_article из состояния
        main_article = data.get("main_article")
        # Получаем значение desired_price из состояния
        desired_price = data.get("desired_price")
        # Получаем значение из Redis по артикулу
        value = r.get(main_article)
        # Преобразуем значение в словарь json
        json_value = json.loads(value)
        # Обновляем значение цены товара c помощью функции edit_price
        new_price = edit_price(json_value, desired_price)
        # Преобразуем значение в словарь json
        new_price_dump = json.dumps(new_price)
        # Обновляем значение в Redis
        r.set(main_article, new_price_dump)
        # Очищаем состояние
        await state.clear()
        # Выводим пользователю сообщение, что цена товара отредактирована и теперь его цена desired_price
        await message.answer(text=f'Цена товара отредактирована и теперь его цена: <b>{desired_price}</b>')
    else:
        # Если цена введена некорректно, то выводим пользователю сообщение, что цена введена некорректно
        await message.answer(text=f'Цена введена некорректно, попробуйте еще раз или нажмите <b>отмена</b>',
                             reply_markup=kb)


# Обработчик кнопки 'Изменить остатки комплектации'. Выводит список комплектаций товара в виде кнопок.
@router.callback_query(lambda callback_query: '_edit_stock' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение main_article из callback_query
    main_article = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    value = r.get(main_article)
    # Преобразуем значение в словарь json
    json_value = json.loads(value)
    # Отсекаем в словаре все кроме variants
    variants = json_value['variants']
    # Создаем клавиатуру с вариантами комплектаций товара
    kb = await create_variants_kb(variants, for_what='_stock')
    # Устанавливаем состояние edit_stock
    await state.set_state(FSMEditProduct.edit_stock)
    # Обновляем данные в состоянии
    await state.update_data(main_article=main_article)
    # Отправляем пользователю сообщение с вариантами комплектаций товара и клавиатурой
    await callback_query.message.answer(text=f'Выберите комплектацию товара, остатки которой хотите изменить или '
                                             f'нажмите <b>отмена</b>',
                                        reply_markup=kb)


# Обработчик, который обрабатывает кнопку выбранной комплектации товара пользователем. Выводит сообщение с текущим
# остатком товара и просит ввести новый остаток либо нажать отмена.
@router.callback_query(lambda callback_query: '_stock' in callback_query.data and '-' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение main_article из callback_query
    main_article = callback_query.data.split('-')[0]
    variant_article = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    value = r.get(main_article)
    # Преобразуем значение в словарь json
    json_value = json.loads(value)
    print(json_value)
    # Получаем значение остатка комплектации товара c помощью функции get_stock
    stock = get_stock(json_value, variant_article)
    # Создаем клавиатуру с кнопкой отмена
    kb = await create_cancel_kb()
    # Устанавливаем состояние edit_stock
    await state.set_state(FSMEditProduct.edit_stock)
    # Обновляем данные в состоянии
    await state.update_data(main_article=main_article, variant_article=variant_article, stock=stock)
    # Отправляем пользователю сообщение с текущим остатком товара и клавиатурой
    await callback_query.message.answer(text=f'Текущий остаток товара: <b>{stock}\n</b> Введите новый остаток или '
                                                f'нажмите <b>отмена</b>', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который обрабатывает введенный остаток товара пользователем.
@router.message(StateFilter(FSMEditProduct.edit_stock))
async def process_stock(message: Message, state: FSMContext):
    # Создаем клавиатуру с кнопками для отмены
    kb = await create_cancel_kb()
    # Проверяем, что остаток введен корректно
    if check_stock(message.text):
        # Если остаток введен корректно, то обновляем данные в состоянии
        await state.update_data(desired_stock=message.text)
        # Получаем данные из состояния
        data = await state.get_data()
        # Получаем значение main_article из состояния
        main_article = data.get("main_article")
        # Получаем значение variant_article из состояния
        variant_article = data.get("variant_article")
        # Получаем значение desired_stock из состояния
        desired_stock = data.get("desired_stock")
        # Получаем значение из Redis по артикулу
        value = r.get(main_article)
        # Преобразуем значение в словарь json
        json_value = json.loads(value)
        # Обновляем значение остатка комплектации товара c помощью функции edit_stock
        new_stock = edit_stock(json_value, variant_article, desired_stock)
        # Преобразуем значение в словарь json
        new_stock_dump = json.dumps(new_stock)
        # Обновляем значение в Redis
        r.set(main_article, new_stock_dump)
        # Очищаем состояние
        await state.clear()
        # Выводим пользователю сообщение, что остаток товара отредактирован и теперь его остаток desired_stock
        await message.answer(text=f'Остаток товара отредактирован и теперь его остаток: <b>{desired_stock}</b>')
    else:
        # Если остаток введен некорректно, то выводим пользователю сообщение, что остаток введен некорректно
        await message.answer(text=f'Остаток введен некорректно, попробуйте еще раз или нажмите <b>отмена</b>',
                             reply_markup=kb)


# Обработчик кнопки "обновить фото" в меню редактирования товара. Выводит все фото товара и спрашивает следует ли их
# заменить
@router.callback_query(lambda callback_query: '_edit_photo' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # Получаем значение артикула товара из callback_data
    article = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    value = r.get(article)
    json_value = json.loads(value)
    # Создаем клавиатуру с кнопкой отмена
    kb = await create_cancel_kb()
    # Создаем список фотографий
    if 'photo_ids' in json_value:
        photo_ids = json_value['photo_ids']
        # Отправляем все фотографии одним сообщением
        await callback_query.message.answer_media_group(generate_photos(photo_ids))
        # Отправляем клавиатуру пользователю
        await callback_query.message.answer(text='Фото данного товара 👆🏼')
        await callback_query.message.answer(text='Хотите обновить фото?\n все предыдущие фото будут удалены.', reply_markup=kb)
    else:
        await callback_query.message.answer('Фото нет')
    await callback_query.answer()


# Обработчик, который сохранит загруженные фото, если пользователь не нажмет отмена и загрузит новые фото
@router.message(F.photo)
async def process_photo_sent(message: Message):
    print(message.photo)




