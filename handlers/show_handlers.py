from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from FSM.fsm import SellItemStates, ReturnItemStates, FSMEditProduct
from keyboards.keyboards import create_sku_kb, create_options_kb, create_variants_kb, create_cancel_kb, create_edit_kb, \
    create_edit_color_kb, create_edit_size_kb
from middlewares.check_user import CheckUserMessageMiddleware
from services.edit import edit_name, edit_description, edit_sku, edit_color, edit_size, check_color, check_size, \
    edit_price, check_price, get_stock, check_stock, edit_stock
from services.product import format_variants_message, generate_photos, format_main_info, return_product, \
    get_product_from_data
import json
from services.product import sell_product
from services.redis_server import get_data_from_redis
from services.sell import check_int

router: Router = Router()
router.message.middleware(CheckUserMessageMiddleware())
#r = create_redis_client()


# Обработчик команды /show для вывода списка товаров с помощью инлайн-клавиатуры с артикулами товаров
@router.message(Command(commands='show'))
async def process_show_command(message: Message):
    # Получаем id пользователя
    user_id = message.from_user.id
    # Создаем клавиатуру с артикулами товаров
    kb = await create_sku_kb(user_id)
    # Отправляем сообщение пользователю
    await message.answer(text='Выберите товар или добавьте новый /add', reply_markup=kb)


# Обработчик срабатывающий на callback_data = 'show'. Функционал такой же как и у команды /show
@router.callback_query(lambda callback_query: callback_query.data == 'show')
async def process_show_callback(callback_query: CallbackQuery):
    # Получаем id пользователя
    user_id = callback_query.from_user.id
    # Создаем клавиатуру с артикулами товаров
    kb = await create_sku_kb(user_id)
    # Отправляем сообщение пользователю
    await callback_query.answer(text='Выберите товар или добавьте новый /add', reply_markup=kb)


# Обработчик для кнопок с артикулами товаров в которых callback_data = артикулу товара
@router.callback_query(lambda callback_query: '_main_sku' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # получаем id пользователя
    user_id = callback_query.from_user.id
    # Получаем все данные пользователя из Redis
    user_data = get_data_from_redis(user_id)
    # Получаем значение артикула товара из callback_data
    main_sku = callback_query.data.split('_')[0]
    # Ищем товар в словаре пользователя список products = user_data['products']
    product = get_product_from_data(main_sku, user_data)
    # формируем основную информацию о товаре с помощью функции
    main_info = format_main_info(product)
    # формируем клавиатуру с помощью функции create_kb
    kb = await create_options_kb(main_sku)
    # Отправляем значение пользователю
    await callback_query.message.answer(main_info, reply_markup=kb)
    await callback_query.answer()


# Обработчик для кнопки "Остатки и модификации товара" в которой callback_data = '_variants'
@router.callback_query(lambda callback_query: '_variants' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение артикула товара из callback_data
    main_sku = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    product = r.get(main_sku)
    product = json.loads(product)
    # вывод комплектаций товара
    products_variants = product['variants']
    products_variants = format_variants_message(products_variants)
    # Создаем клавиатуру с всеми товарами create_sku_kb()
    kb = await create_options_kb(main_sku)
    # Отправляем значение пользователю
    await callback_query.message.answer(products_variants)
    await callback_query.message.answer(text='Выберите действие 👇', reply_markup=kb)
    await callback_query.answer()


# Обработчик для кнопки "Показать фото" в которой callback_data = '_photo'
@router.callback_query(lambda callback_query: '_photo' in callback_query.data and '_edit' not in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # Получаем значение артикула товара из callback_data
    main_sku = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    product = r.get(main_sku)
    product = json.loads(product)
    # Создаем клавиатуру с всеми товарами create_sku_kb()
    kb = await create_options_kb(main_sku)
    # Создаем список фотографий
    if 'photo_ids' in product:
        photo_ids = product['photo_ids']
        # Отправляем все фотографии одним сообщением
        await callback_query.message.answer_media_group(generate_photos(photo_ids))
        # Отправляем клавиатуру пользователю
        await callback_query.message.answer(text='Выберите действие с товаром👇', reply_markup=kb)
    else:
        await callback_query.message.answer('Фото нет')
    await callback_query.answer()


# Обработчик для кнопки "Продать товар" в которой callback_data = '_sell_button', выводит список модификаций товаров для
# продажи
@router.callback_query(lambda callback_query: '_sell_button' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # Получаем значение артикула товара из callback_data
    main_sku = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    product = r.get(main_sku)
    # Преобразуем значение в словарь json
    product = json.loads(product)
    # Получаем значение variants из json_value
    product_variant = product['variants']
    # Создаем клавиатуру с вариантами товара
    kb = await create_variants_kb(product_variant, for_what='_sell_variant')
    # Отправляем клавиатуру пользователю
    await callback_query.message.answer(text='Выберите товар или нажмите отмена 👇', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который срабатывает при нажатии на кнопку с вариантом товара и просит ввести количество продаваемого
# товара сообщением "Введите количество:"
@router.callback_query(lambda callback_query: '_sell_variant' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Переводим в состояние SellItemStates.quantity
    await state.set_state(SellItemStates.quantity)
    # Получаем значение артикула товара из callback_data
    variant_sku = callback_query.data.split('_')[0]
    # Устанавливаем FSM SellItemStates article
    await state.update_data(variant_sku=variant_sku)
    # Создаем клавиатуру с кнопкой "Отмена"
    kb = await create_cancel_kb()
    # Отвечаем пользователю сообщением "Введите количество:"
    await callback_query.message.answer(text='Введите количество или нажмите <b>отмена</b>', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который обрабатывает введенное число пользователем для продажи товара
@router.message(StateFilter(SellItemStates.quantity))
async def process_quantity(message: Message, state: FSMContext):
    # Проверяем является ли введенное значение числом от 1 до 100
    if check_int(message.text):
        # Получаем значение введенное пользователем
        quantity = int(message.text)
        # Получаем значение article_variant из FSM
        data = await state.get_data()
        variant_sku = data.get("variant_sku")
        # Получаем значение из Redis по артикулу
        product = r.get(variant_sku.split('-')[0])
        # Преобразуем значение в словарь json
        product = json.loads(product)
        # вывод комплектаций товара
        product_variants = product['variants']
        # Получаем название товара
        name = ''
        for i in product_variants:
            if i['sku'] == variant_sku:
                name = i['name']
                break
        # вызываем функцию sell_product
        if sell_product(variant_sku, quantity) is True:
            # Создаем клавиатуру с возврата к списку товаров и отменой
            kb = await create_cancel_kb()
            # Пишем сообщение пользователю, что товар продан в количестве quantity штук
            await message.answer(text=f'Товар {name} продан в количестве {quantity} шт.')
            # Выводим кнопку клавиатуру с кнопками "Вернуться к списку товаров" и "Отмена"
            await message.answer(text='Посмотреть отчет /report', reply_markup=kb)
            # Переводим в состояние default
            await state.clear()
        else:
            # Создаем клавиатуру с кнопкой "модификация товара для продажи"
            kb = await create_variants_kb(product_variants, for_what='_sell_variant')
            # Пишем сообщение пользователю, что товара не хватает на складе
            await message.answer(text=f'Товара {name} <b>не хватает на складе</b>. Выберете другой товар или нажмите '
                                      f'"Отмена"', reply_markup=kb)
    else:
        # Создаем клавиатуру с кнопкой "Отмена"
        kb = await create_cancel_kb()
        # Пишем сообщение пользователю, что было введено не число от 1 до 100
        await message.answer(text='Введите число от 1 до 100 или нажмите <b>отмена</b>', reply_markup=kb)


# Обработчик для кнопки "Вернуть товар" в которой callback_data = '_return_button', выводит список модификаций
# товаров для возврата
@router.callback_query(lambda callback_query: '_return_button' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # Получаем значение артикула товара из callback_data
    main_sku = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    product = r.get(main_sku)
    # Преобразуем значение в словарь json
    product = json.loads(product)
    # Получаем значение variants из json_value
    product_variants = product['variants']
    # Создаем клавиатуру с вариантами товара
    kb = await create_variants_kb(product_variants, for_what='_return_variant')
    # Отправляем клавиатуру пользователю
    await callback_query.message.answer(text='Выберите товар для возврата или нажмите отмена 👇', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который срабатывает при нажатии на кнопку с вариантом товара и просит ввести количество возвращаемого
# товара сообщением "Введите количество:"
@router.callback_query(lambda callback_query: '_return_variant' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение артикула товара из callback_data
    variant_sku = callback_query.data.split('_')[0]
    # Устанавливаем FSM SellItemStates article
    await state.update_data(variant_sku=variant_sku)
    # Переводим в состояние SellItemStates.quantity
    await state.set_state(ReturnItemStates.quantity)
    # Создаем клавиатуру с кнопкой "Отмена"
    kb = await create_cancel_kb()
    # Отвечаем пользователю сообщением "Введите количество:"
    await callback_query.message.answer(text='Введите количество или нажмите <b>отмена</b>', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который обрабатывает введенное число пользователем для возврата товара
@router.message(StateFilter(ReturnItemStates.quantity))
async def process_quantity(message: Message, state: FSMContext):
    if check_int(message.text):
        # Получаем значение введенное пользователем
        quantity = int(message.text)
        # Получаем значение article_variant из FSM
        data = await state.get_data()
        sku_variant = data.get("variant_sku")
        # Получаем значение из Redis по артикулу
        product = r.get(sku_variant.split('-')[0])
        # Преобразуем значение в словарь json
        product = json.loads(product)
        # вывод комплектаций товара
        product_variants = product['variants']
        # Получаем название товара
        name = ''
        for i in product_variants:
            if i['sku'] == sku_variant:
                name = i['name']
                break
        # вызываем функцию return_product
        if return_product(sku_variant, quantity) is True:
            # Создаем клавиатуру с возврата к списку товаров и отменой
            kb = await create_cancel_kb()
            # Пишем сообщение пользователю, что товар продан в количестве quantity штук
            await message.answer(text=f'Товар {name} возвращен в количестве {quantity} шт.')
            # Выводим список товаров
            await message.answer(text='Посмотреть отчет /report', reply_markup=kb)
            # Переводим в состояние default
            await state.clear()
        else:
            # Создаем клавиатуру с кнопкой "модификация товара для возврата"
            kb = await create_variants_kb(product_variants, for_what='_return_variant')
            # Пишем сообщение пользователю, что товара не хватает на складе
            await message.answer(text=f'Товара {name} <b>не хватает на складе</b>. Выберете другой товар или нажмите '
                                      f'"Отмена"', reply_markup=kb)
    else:
        # Создаем клавиатуру с кнопкой "Отмена"
        kb = await create_cancel_kb()
        # Пишем сообщение пользователю, что было введено не число от 1 до 100
        await message.answer(text='Введите число от 1 до 100 или нажмите <b>отмена</b>', reply_markup=kb)


# Обработчик кнопки редактировать товар
@router.callback_query(lambda callback_query: '_edit_button' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # Получаем значение артикула товара из callback_data
    main_sku = callback_query.data.split('_')[0]
    # создаем клавиатуру с кнопками с помощью функции create_edit_kb
    kb = await create_edit_kb(main_sku)
    # Отправляем клавиатуру пользователю
    await callback_query.message.answer(text='Выберите что хотите отредактировать 👇', reply_markup=kb)
    await callback_query.answer()


# Обработчик кнопки редактировать наименование товара
@router.callback_query(lambda callback_query: '_edit_name' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение артикула товара из callback_data
    main_sku = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    product = r.get(main_sku)
    # Преобразуем значение в словарь json
    product = json.loads(product)
    # Создаем клавиатуру с кнопкой "Отмена"
    kb = await create_cancel_kb()
    # Устанавливаем FSMEditProduct edit_name
    await state.set_state(FSMEditProduct.edit_name)
    # Сохраняем артикул товара в FSM
    await state.update_data(main_sku=main_sku)
    # Отправляем пользователю сообщение с названием товара на данный момент и просим ввести новое название или отменить
    await callback_query.message.answer(text=f'Текущее название товара: <b>{product["name"]}\n</b> Введите новое '
                                             'название товара или нажмите <b>отмена</b>', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который обрабатывает введенное название товара пользователем
@router.message(StateFilter(FSMEditProduct.edit_name))
async def process_name(message: Message, state: FSMContext):
    # Получаем значение введенное пользователем
    name = message.text
    # Получаем значение main_article из FSM
    data = await state.get_data()
    main_sku = data.get("main_sku")
    # Получаем значение из Redis по артикулу
    product = r.get(main_sku)
    # Преобразуем значение в словарь json
    product = json.loads(product)
    # Применяем функцию edit_name
    new_name = edit_name(product, name)
    # Конвертируем словарь в json
    new_name = json.dumps(new_name)
    # Перезаписываем значение в Redis
    r.set(main_sku, new_name)
    # Создаем клавиатуру с действия по редактированию товара
    kb = await create_edit_kb(main_sku)
    # Пишем сообщение пользователю, что товар отредактирован и теперь его название name
    await message.answer(text=f'Товар отредактирован и теперь его название: <b>{name}</b>', reply_markup=kb)
    # Сбрасываем состояние
    await state.clear()


# Обработчик кнопки редактировать описание товара
@router.callback_query(lambda callback_query: '_edit_description' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение артикула товара из callback_data
    main_sku = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    product = r.get(main_sku)
    # Преобразуем значение в словарь json
    product = json.loads(product)
    # Создаем клавиатуру с кнопкой "Отмена"
    kb = await create_cancel_kb()
    # Устанавливаем FSMEditProduct edit_description
    await state.set_state(FSMEditProduct.edit_description)
    # Сохраняем артикул товара в FSM
    await state.update_data(main_sku=main_sku)
    # Отправляем пользователю сообщение с описанием товара на данный момент и просим ввести новое описание или отменить
    await callback_query.message.answer(text=f'Текущее описание товара: <b>{product["description"]}\n</b> Введите '
                                             f'новое описание товара или нажмите <b>отмена</b>', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который обрабатывает введенное описание товара пользователем
@router.message(StateFilter(FSMEditProduct.edit_description))
async def process_description(message: Message, state: FSMContext):
    # Получаем значение введенное пользователем
    description = message.text
    # Получаем значение main_article из FSM
    data = await state.get_data()
    main_sku = data.get("main_sku")
    # Получаем значение из Redis по артикулу
    product = r.get(main_sku)
    # Преобразуем значение в словарь json
    product = json.loads(product)
    # Применяем функцию edit_description
    new_description = edit_description(product, description)
    # Конвертируем словарь в json
    new_description = json.dumps(new_description)
    # Перезаписываем значение в Redis
    r.set(main_sku, new_description)
    # Создаем клавиатуру с действия по редактированию товара
    kb = await create_edit_kb(main_sku)
    # Пишем сообщение пользователю, что товар отредактирован и теперь его описание description
    await message.answer(text=f'Товар отредактирован и теперь его описание: <b>{description}</b>', reply_markup=kb)
    # Сбрасываем состояние
    await state.clear()


# Обработчик кнопки редактировать артикул товара
@router.callback_query(lambda callback_query: '_edit_sku' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение артикула товара из callback_data
    main_sku = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    product = r.get(main_sku)
    # Преобразуем значение в словарь json
    product = json.loads(product)
    # Создаем клавиатуру с кнопкой "Отмена"
    kb = await create_cancel_kb()
    # Устанавливаем FSMEditProduct edit_article
    await state.set_state(FSMEditProduct.edit_sku)
    # Сохраняем артикул товара в FSM
    await state.update_data(main_sku=main_sku)
    # Отправляем пользователю сообщение с артикулом товара на данный момент и просим ввести новый артикул или отменить
    await callback_query.message.answer(text=f'Текущий артикул товара: <b>{product["sku"]}\n</b> Введите новый '
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
        main_sku = data.get("main_sku")
        # Получаем значение из Redis по артикулу
        product = r.get(main_sku)
        # Преобразуем значение в словарь json
        product = json.loads(product)
        # Применяем функцию edit_sku
        new_sku = edit_sku(product, sku)
        # Конвертируем словарь в json
        new_sku = json.dumps(new_sku)
        # Перезаписываем значение в Redis
        r.set(sku, new_sku)
        # Удаляем старый артикул
        r.delete(main_sku)
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
    main_sku = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    product = r.get(main_sku)
    # Преобразуем значение в словарь json
    product = json.loads(product)
    # Получаем список цветов товара
    colors = product['colors']
    # Создаем клавиатуру с кнопками цветов товара и кнопкой "Отмена"
    kb = await create_edit_color_kb(colors)
    # Устанавливаем FSMEditProduct edit_color
    await state.set_state(FSMEditProduct.edit_color)
    # Сохраняем артикул товара в FSM
    await state.update_data(main_sku=main_sku)
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
    await callback_query.answer()


# Обработчик, который обрабатывает введенный цвет товара пользователем.
@router.message(StateFilter(FSMEditProduct.edit_color))
async def process_color(message: Message, state: FSMContext):
    # Проверяем цвет на валидность
    if check_color(message.text.lower()):
        # Сохраняем введенный пользователем цвет в FSM
        await state.update_data(desired_color=message.text.lower())
        # Получаем значение из FSM выбранного цвета для замены и желаемого цвета
        data = await state.get_data()
        selected_color = data.get("selected_color")
        desired_color = data.get("desired_color")
        # Получаем значение main_article из FSM
        main_sku = data.get("main_sku")
        # Получаем значение из Redis по артикулу
        product = r.get(main_sku)
        # Преобразуем значение в словарь json
        product = json.loads(product)
        # Применяем функцию edit_color
        new_color = edit_color(product, selected_color, desired_color)
        # Конвертируем словарь в json
        new_color_dump = json.dumps(new_color)
        # Перезаписываем значение в Redis
        r.set(main_sku, new_color_dump)
        # Очищаем состояние
        await state.clear()
        # Создаем клавиатуру с действиями по редактированию товара
        kb = await create_edit_kb(main_sku)
        # Выводим пользователю сообщение, что цвет товара отредактирован и теперь его цвет desired_color, а также
        # выводим, что все цвета товара теперь new_color['colors']
        await message.answer(text=f'Цвет товара отредактирован и теперь его цвет: <b>{desired_color}</b>\n'
                                  f'Все цвета товара: <b>{new_color["colors"]}</b>', reply_markup=kb)
    else:
        # Создаем клавиатуру с кнопкой "Отмена"
        kb = await create_cancel_kb()
        # Если цвет не валидный, то выводим сообщение об ошибке и просим ввести новый цвет или отменить
        await message.answer(text=f'Цвет введен неверно, попробуйте еще раз или нажмите <b>отмена</b>', reply_markup=kb)


# Обработчик кнопки редактировать размер товара. Работает аналогично кнопке редактировать цвет товара.
@router.callback_query(lambda callback_query: '_edit_size' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    main_sku = callback_query.data.split('_')[0]
    product = r.get(main_sku)
    product = json.loads(product)
    sizes = product['sizes']
    kb = await create_edit_size_kb(sizes)
    await state.set_state(FSMEditProduct.edit_size)
    await state.update_data(main_sku=main_sku)
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
    await callback_query.answer()


# Обработчик, который обрабатывает введенный размер товара пользователем.
@router.message(StateFilter(FSMEditProduct.edit_size))
async def process_size(message: Message, state: FSMContext):
    if check_size(message.text.lower()):
        # Сохраняем введенный пользователем размер в FSM
        await state.update_data(desired_size=message.text.lower())
        # Получаем значение из FSM выбранного размера для замены и желаемого размера
        data = await state.get_data()
        # Получаем значение selected_size и desired_size из FSM
        selected_size = data.get("selected_size")
        desired_size = data.get("desired_size")
        # Получаем значение main_sku из FSM
        main_sku = data.get("main_sku")
        # Получаем значение из Redis по артикулу
        product = r.get(main_sku)
        product = json.loads(product)
        # Применяем функцию edit_size
        new_size = edit_size(product, selected_size, desired_size)
        # Конвертируем словарь в json
        new_size_dump = json.dumps(new_size)
        # Перезаписываем значение в Redis
        r.set(main_sku, new_size_dump)
        # Создаем клавиатуру с основными действиями по редактированию товара
        kb = await create_edit_kb(main_sku)
        await state.clear()
        await message.answer(text=f'Размер товара отредактирован и теперь его размер: <b>{desired_size}</b>\n'
                                  f'Все размеры товара: <b>{new_size["sizes"]}</b>', reply_markup=kb)
    else:
        kb = await create_cancel_kb()
        await message.answer(text=f'Размер введен неверно, попробуйте еще раз или нажмите <b>отмена</b>',
                             reply_markup=kb)


# Обработчик кнопки редактировать цену товара. Работает аналогично кнопке редактировать цвет товара.
@router.callback_query(lambda callback_query: '_edit_price' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение main_sku из callback_query
    main_sku = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    product = r.get(main_sku)
    # Преобразуем значение в словарь json
    product = json.loads(product)
    # Получаем значение цены товара
    price = product['price']
    # Создаем клавиатуру с кнопками для ввода цены или отмены
    kb = await create_cancel_kb()
    # Устанавливаем состояние edit_price
    await state.set_state(FSMEditProduct.edit_price)
    # Обновляем данные в состоянии
    await state.update_data(main_sku=main_sku)
    # Отправляем пользователю сообщение с текущей ценой товара и клавиатурой
    await callback_query.message.answer(text=f'Текущая цена товара: <b>{price}{currency}\n</b> Введите новую цену или '
                                             f'нажмите <b>отмена</b>', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который обрабатывает введенную цену товара пользователем при редактировании товара.
@router.message(StateFilter(FSMEditProduct.edit_price))
async def process_price(message: Message, state: FSMContext):
    # Проверяем, что цена введена корректно
    if check_price(message.text):
        # Если цена введена корректно, то обновляем данные в состоянии
        await state.update_data(desired_price=message.text)
        # Получаем данные из состояния
        data = await state.get_data()
        # Получаем значение main_sku из состояния
        main_sku = data.get("main_sku")
        # Получаем значение desired_price из состояния
        desired_price = data.get("desired_price")
        # Получаем значение из Redis по артикулу
        product = r.get(main_sku)
        # Преобразуем значение в словарь json
        product = json.loads(product)
        # Обновляем значение цены товара c помощью функции edit_price
        new_price = edit_price(product, desired_price)
        # Преобразуем значение в словарь json
        new_price_dump = json.dumps(new_price)
        # Обновляем значение в Redis
        r.set(main_sku, new_price_dump)
        # Очищаем состояние
        await state.clear()
        # Создаем клавиатуру с основными действиями по редактированию товара
        kb = await create_edit_kb(main_sku)
        # Выводим пользователю сообщение, что цена товара отредактирована и теперь его цена desired_price
        await message.answer(text=f'Цена товара отредактирована и теперь его цена: <b>{desired_price}</b>{currency}',
                             reply_markup=kb)
    else:
        # Создаем клавиатуру с кнопками для отмены
        kb = await create_cancel_kb()
        # Если цена введена некорректно, то выводим пользователю сообщение, что цена введена некорректно
        await message.answer(text=f'Цена введена некорректно, попробуйте еще раз или нажмите <b>отмена</b>',
                             reply_markup=kb)


# Обработчик кнопки 'Изменить остатки комплектации'. Выводит список комплектаций товара в виде кнопок.
@router.callback_query(lambda callback_query: '_edit_stock' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение main_article из callback_query
    main_sku = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    product = r.get(main_sku)
    # Преобразуем значение в словарь json
    product = json.loads(product)
    # Отсекаем в словаре все кроме variants
    product_variants = product['variants']
    # Создаем клавиатуру с вариантами комплектаций товара
    kb = await create_variants_kb(product_variants, for_what='_stock')
    # Устанавливаем состояние edit_stock
    await state.set_state(FSMEditProduct.edit_stock)
    # Обновляем данные в состоянии
    await state.update_data(main_sku=main_sku)
    # Отправляем пользователю сообщение с вариантами комплектаций товара и клавиатурой
    await callback_query.message.answer(text=f'Выберите комплектацию товара, остатки которой хотите изменить или '
                                             f'нажмите <b>отмена</b>',
                                        reply_markup=kb)
    await callback_query.answer()


# Обработчик, который обрабатывает кнопку выбранной комплектации товара пользователем. Выводит сообщение с текущим
# остатком товара и просит ввести новый остаток либо нажать отмена.
@router.callback_query(lambda callback_query: '_stock' in callback_query.data and '-' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение main_article из callback_query
    main_sku = callback_query.data.split('-')[0]
    variant_sku = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    product = r.get(main_sku)
    # Преобразуем значение в словарь json
    product = json.loads(product)
    # Получаем значение остатка комплектации товара c помощью функции get_stock
    stock = get_stock(product, variant_sku)
    # Создаем клавиатуру с кнопкой отмена
    kb = await create_cancel_kb()
    # Устанавливаем состояние edit_stock
    await state.set_state(FSMEditProduct.edit_stock)
    # Обновляем данные в состоянии
    await state.update_data(main_sku=main_sku, variant_sku=variant_sku, stock=stock)
    # Отправляем пользователю сообщение с текущим остатком товара и клавиатурой
    await callback_query.message.answer(text=f'Текущий остаток товара: <b>{stock}\n</b> Введите новый остаток или '
                                             f'нажмите <b>отмена</b>', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который обрабатывает введенный остаток товара пользователем.
@router.message(StateFilter(FSMEditProduct.edit_stock))
async def process_stock(message: Message, state: FSMContext):
    # Проверяем, что остаток введен корректно
    if check_stock(message.text):
        # Если остаток введен корректно, то обновляем данные в состоянии
        await state.update_data(desired_stock=message.text)
        # Получаем данные из состояния
        data = await state.get_data()
        # Получаем значение main_article из состояния
        main_sku = data.get("main_sku")
        # Получаем значение variant_article из состояния
        variant_sku = data.get("variant_sku")
        # Получаем значение desired_stock из состояния
        desired_stock = data.get("desired_stock")
        # Получаем значение из Redis по артикулу
        product = r.get(main_sku)
        # Преобразуем значение в словарь json
        product = json.loads(product)
        # Обновляем значение остатка комплектации товара c помощью функции edit_stock
        new_stock = edit_stock(product, variant_sku, desired_stock)
        # Преобразуем значение в словарь json
        new_stock_dump = json.dumps(new_stock)
        # Обновляем значение в Redis
        r.set(main_sku, new_stock_dump)
        # Очищаем состояние
        await state.clear()
        # Создаем клавиатуру с основными кнопками редактирования товара
        kb = await create_edit_kb(main_sku)
        # Выводим пользователю сообщение, что остаток товара отредактирован и теперь его остаток desired_stock
        await message.answer(text=f'Остаток товара отредактирован и теперь его остаток: <b>{desired_stock}</b>',
                             reply_markup=kb)
    else:
        # Создаем клавиатуру с кнопками для отмены
        kb = await create_cancel_kb()
        # Если остаток введен некорректно, то выводим пользователю сообщение, что остаток введен некорректно
        await message.answer(text=f'Остаток введен некорректно, попробуйте еще раз или нажмите <b>отмена</b>',
                             reply_markup=kb)


# Обработчик кнопки "обновить фото" в меню редактирования товара. Выводит все фото товара и спрашивает следует ли их
# заменить
@router.callback_query(lambda callback_query: '_edit_photo' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение артикула товара из callback_data
    main_sku = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    product = r.get(main_sku)
    product = json.loads(product)
    # Создаем клавиатуру с кнопкой отмена
    kb = await create_cancel_kb()
    # Устанавливаем состояние edit_photo
    await state.set_state(FSMEditProduct.edit_photo)
    # Передаем в состояние артикул товара
    await state.update_data(main_sku=main_sku)
    # Создаем список фотографий
    if 'photo_ids' in product:
        photo_ids = product['photo_ids']
        # Отправляем все фотографии одним сообщением
        await callback_query.message.answer_media_group(generate_photos(photo_ids))
        # Отправляем клавиатуру пользователю
        await callback_query.message.answer(text='Фото данного товара 👆🏼')
        await callback_query.message.answer(text='Хотите обновить фото?\n все предыдущие фото будут удалены.',
                                            reply_markup=kb)
    else:
        await callback_query.message.answer(text='Фото нет', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который сохранит загруженные фото, если пользователь не нажмет отмена и загрузит новые фото. Должен быть
# способ работы с media_group. Сохраняем все фото и выводим их на экран.
@router.message(StateFilter(FSMEditProduct.edit_photo))
async def process_photo_sent(message: Message, state: FSMContext):
    # Получаем текущий список идентификаторов фото из состояния и если его нет, то создаем пустой список
    data = await state.get_data()
    new_photos = data.get("photo_ids", [])
    # Получаем информацию о текущем фото и сохраняем его идентификатор в список
    largest_photo = message.photo[-1]
    new_photos.append({"unique_id": largest_photo.file_unique_id, "id": largest_photo.file_id})
    # Сохраняем список идентификаторов фото в состояние
    await state.update_data(photo_ids=new_photos)
    # Извлекаем артикул товара из состояния
    data = await state.get_data()
    main_sku = data.get("main_sku")
    # Получаем значение из Redis по артикулу
    product = r.get(main_sku)
    product = json.loads(product)
    # Заменяем список фото в товаре на новый
    product['photo_ids'] = new_photos
    # Преобразуем значение в словарь json
    product_dump = json.dumps(product)
    # Обновляем значение в Redis
    r.set(main_sku, product_dump)
    # Отправляем клавиатуру пользователю
    await message.answer(text='Фото обновлены 👆🏼')
    # Очищаем состояние
    await state.clear()

# Обработчик кнопки удалить товар в меню редактирования товара. Выводит сообщение с подтверждением удаления товара
# путем ввода артикула товара и слова "удалить"
@router.callback_query(lambda callback_query: '_edit_delete' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение артикула товара из callback_data
    main_sku = callback_query.data.split('_')[0]
    # Создаем клавиатуру с кнопкой отмена
    kb = await create_cancel_kb()
    # Устанавливаем состояние edit_delete
    await state.set_state(FSMEditProduct.edit_delete)
    # Передаем в состояние артикул товара
    await state.update_data(main_sku=main_sku)
    # Отправляем сообщение пользователю с просьбой ввести артикул товара и слово "удалить"
    await callback_query.message.answer(text=f'Введите артикул "{main_sku}" товара и слово "удалить" для подтверждения '
                                             f'удаления, <b>ТОВАР БУДЕТ УДАЛЕН НАВСЕГДА 💀</b>', reply_markup=kb)
    await callback_query.answer()


# Обработчик удаления товара в состоянии edit_delete. Если пользователь ввел артикул товара и слово "удалить", то
# удаляем товар из Redis и выводим сообщение об удалении товара. Если введен некорректный артикул товара или слово
# "удалить", то выводим сообщение об ошибке и предлагаем ввести артикул товара и слово "удалить" еще раз.
@router.message(StateFilter(FSMEditProduct.edit_delete))
async def process_delete_product(message: Message, state: FSMContext):
    # Получаем артикул товара из состояния
    data = await state.get_data()
    main_sku = data.get("main_sku")
    # Получаем значение из Redis по артикулу
    product = r.get(main_sku)
    product = json.loads(product)
    # Если артикул товара и слово "удалить" введены корректно, то удаляем товар из Redis, очищаем состояние и
    # выводим сообщение об удалении товара
    if product and message.text == f'{main_sku} удалить':
        # Создаем клавиатуру с кнопкой отмена
        kb = await create_cancel_kb()
        # Удаляем товар из Redis
        r.delete(main_sku)
        await state.clear()
        await message.answer(text=f'Товар {main_sku} удален', reply_markup=kb)
    else:
        # Создаем клавиатуру с кнопкой отмена
        kb = await create_cancel_kb()
        # Если артикул товара и слово "удалить" введены некорректно, то выводим сообщение об ошибке и предлагаем
        # ввести артикул товара и слово "удалить" еще раз.
        await message.answer(text=f'Артикул товара {main_sku} или слово "удалить" введены некорректно, попробуйте еще '
                                  f'раз', reply_markup=kb)





