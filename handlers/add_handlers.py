from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from FSM.fsm import FSMAddProduct, FSMAddProductOne
from aiogram.types import Message, CallbackQuery
from keyboards.keyboards import create_cancel_kb, cancel_and_done_kb
from middlewares.check_user import CheckUserMessageMiddleware
from services.product import Product
from services.redis_server import create_redis_client, get_data_from_redis, save_data_to_redis, check_product_in_redis

router: Router = Router()
router.message.middleware(CheckUserMessageMiddleware())
r = create_redis_client()


# Этот хэндлер будет срабатывать на команду /add
# и переводить бота в состояние ожидания ввода имени
@router.message(Command(commands='add'), StateFilter(default_state))
async def process_add_command(message: Message, state: FSMContext):
    # Создаем клавиатуру для отмены
    kb = await create_cancel_kb()
    # Отправляем сообщение с просьбой ввести имя товара
    await message.answer(text='Введите имя товара или нажмите отмена', reply_markup=kb)
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSMAddProduct.fill_name)


# Этот хэндлер будет срабатывать, если введено корректное имя
# и переводить в состояние ожидания ввода описания товара
@router.message(StateFilter(FSMAddProduct.fill_name))
async def process_name_sent(message: Message, state: FSMContext):
    # Создаем клавиатуру для отмены
    kb = await create_cancel_kb()
    # Cохраняем введенное имя в хранилище по ключу "name"
    await state.update_data(name=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите описание товара', reply_markup=kb)
    # Устанавливаем состояние ожидания ввода описания товара
    await state.set_state(FSMAddProduct.fill_description)


# Этот хендлер будет срабатывать, если введено корректное описание товара
# и переводить в состояние ожидания ввода артикула товара
@router.message(StateFilter(FSMAddProduct.fill_description))
async def process_desc_sent(message: Message, state: FSMContext):
    # Создаем клавиатуру для отмены
    kb = await create_cancel_kb()
    # Cохраняем введенное описание в хранилище по ключу "description"
    await state.update_data(description=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите артикул товара', reply_markup=kb)
    # Устанавливаем состояние ожидания ввода описания товара
    await state.set_state(FSMAddProduct.fill_sku)


# Этот хэндлер будет срабатывать, если введено корректный артикул товара
# и переводить в состояние ожидания ввода цветов товара
@router.message(StateFilter(FSMAddProduct.fill_sku))
async def process_sku_sent(message: Message, state: FSMContext):
    # Получаем user_id
    user_id = message.from_user.id
    # Создаем клавиатуру для отмены
    kb = await create_cancel_kb()
    # Проверяем нет ли введенного артикула пользователя в базе данных и если есть, то сообщаем что такой товар уже есть
    if check_product_in_redis(user_id, message.text):
        await message.answer(text='Товар с таким артикулом уже есть в базе данных!\n\n'
                                  'Введите другой артикул или для отмены введите /cancel', reply_markup=kb)
        return
    else:
        # Cохраняем введенный артикул в хранилище по ключу "sku"
        await state.update_data(sku=message.text)
        await message.answer(text='Спасибо!\n\nА теперь введите цвета товаров через пробел', reply_markup=kb)
        # Устанавливаем состояние ожидания ввода цветов товара
        await state.set_state(FSMAddProduct.fill_colors)


# Этот хэндлер будет срабатывать, если введены корректный артикул товара
# и переводить в состояние ожидания ввода цветов товара
@router.message(StateFilter(FSMAddProduct.fill_colors))
async def process_colors_sent(message: Message, state: FSMContext):
    # Создаем клавиатуру для отмены
    kb = await create_cancel_kb()
    # Cохраняем введенные цвета в хранилище по ключу "colors"
    await state.update_data(colors=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите размеры товаров через пробел', reply_markup=kb)
    # Устанавливаем состояние ожидания ввода размеров товара
    await state.set_state(FSMAddProduct.fill_sizes)


# Этот хэндлер будет срабатывать, если введены корректный артикул товара
# и переводить в состояние ожидания ввода цветов товара
@router.message(StateFilter(FSMAddProduct.fill_colors))
async def process_colors_sent(message: Message, state: FSMContext):
    # Создаем клавиатуру для отмены
    kb = await create_cancel_kb()
    # Cохраняем введенные цвета в хранилище по ключу "colors"
    await state.update_data(colors=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите размеры товаров через пробел', reply_markup=kb)
    # Устанавливаем состояние ожидания ввода размеров товара
    await state.set_state(FSMAddProduct.fill_sizes)


# Этот хэндлер будет срабатывать, если введены корректно цвета товаров
# и переводить в состояние ожидания ввода цены товара
@router.message(StateFilter(FSMAddProduct.fill_sizes))
async def process_sizes_sent(message: Message, state: FSMContext):
    # Создаем клавиатуру для отмены
    kb = await create_cancel_kb()
    # Cохраняем введенные размеры в хранилище по ключу "sizes"
    await state.update_data(sizes=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите цену товара', reply_markup=kb)
    # Устанавливаем состояние ожидания ввода размеров товара
    await state.set_state(FSMAddProduct.fill_price)


# Этот хэндлер будет срабатывать, если введен корректно артикул товара
# и переходить к загрузке фото
@router.message(StateFilter(FSMAddProduct.fill_price))
async def process_price_sent(message: Message, state: FSMContext):
    # Создаем клавиатуру с 2 кнопками для отмены и готово
    kb = await cancel_and_done_kb()
    # Cохраняем введенную цену в хранилище по ключу "price"
    await state.update_data(price=message.text)
    await message.answer(text='Спасибо!\n\nА теперь загрузите фото товара\n\n<b>После загрузки всех фото нажмите '
                              'кнопку "Готово👇"</b>', reply_markup=kb)
    # Устанавливаем состояние ожидания ввода загрузки фото товаров товара
    await state.set_state(FSMAddProduct.fill_photo)


# Этот хэндлер будет принимать фото и формировать список идентификаторов фото
lst = []  # Список идентификаторов фото


@router.message(StateFilter(FSMAddProduct.fill_photo), F.photo)
async def process_photo_sent(message: Message):
    largest_photo = message.photo[-1]
    lst.append({"unique_id": largest_photo.file_unique_id, "id": largest_photo.file_id})


# Хендлер который окончательно формирует товар и сохраняет его в базу данных
@router.callback_query(StateFilter(FSMAddProduct.fill_photo), lambda callback_query: 'done' in callback_query.data)
async def process_done_button(callback_query: CallbackQuery, state: FSMContext):
    # Получаем все данные из хранилища
    data = await state.get_data()
    data["photo_ids"] = lst
    # Создаем товар
    product = Product(
        name=data.get("name"),
        description=data.get("description"),
        sku=data.get("sku"),
        colors=data.get("colors"),
        sizes=data.get("sizes"),
        price=data.get("price"),
        photo_ids=data.get("photo_ids"),
    )
    product = {product.__dict__['sku']: product.__dict__}
    # получаем id пользователя
    user_id = callback_query.from_user.id
    # Получает данные о пользователе из базы данных по id
    user_data = get_data_from_redis(user_id)
    # Добавляем товар в базу данных
    user_data['products'].append(product)
    # записываем данные о пользователе в базу данных
    save_data_to_redis(user_id, user_data)
    # Отправляем сообщение о том, что товар успешно добавлен
    await callback_query.message.reply(text='Товар успешно Создан!')
    # очищаем хранилище
    await state.clear()


# Хендлер который срабатывает на команду /add_one. Отправляет сообщение с просьбой ввести данные с новой строки:
@router.message(Command(commands='add_one'), StateFilter(default_state))
async def process_add_command(message: Message, state: FSMContext):
    # Создаем клавиатуру для отмены
    kb = await create_cancel_kb()
    # Отправляем сообщение с просьбой ввести имя товара
    await message.answer(text='Вы добавляете товар одним стоблцом.\n\n'
                              '<b>Введите данные в таком формате (каждое с новой строки):</b>\n\n'
                              '👉 Имя товара\n'
                              '👉 Описание товара\n'
                              '👉 Артикул товара\n'
                              '👉 Цвета товара через пробел\n'
                              '👉 Размеры товара через пробел\n'
                              '👉 Цена товара (без валюты)', reply_markup=kb)

    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSMAddProductOne.data)


# Этот хэндлер будет срабатывать, если все строки введены корректно
@router.message(StateFilter(FSMAddProductOne.data))
async def process_data_send(message: Message, state: FSMContext):
    # Получаем id пользователя
    user_id = message.from_user.id
    # Создаем клавиатуру для отмены и готово
    kb = await cancel_and_done_kb()
    # Создаем клавитуру для отмены
    kb2 = await create_cancel_kb()
    # Cохраняем введенное имя в хранилище по ключу "name"
    data = message.text.split('\n')
    if len(data) == 6:
        if check_product_in_redis(user_id, data[2]):
            await message.answer(text='Товар с таким артикулом уже есть в базе данных!\n\n'
                                      'Заполните товар заново или для отмены нажмите "Отмена"', reply_markup=kb2)
        else:
            await state.update_data(name=data[0], description=data[1], sku=data[2], colors=data[3], sizes=data[4],
                                    price=data[5])
            # Благодарим за введенную информацию и просим добавить фото, если оно есть
            await message.answer(text='Спасибо!\n\nА теперь загрузите фото товара\n\n<b>После загрузки всех фото '
                                      'нажмите'
                                      'кнопку "Готово👇"</b>', reply_markup=kb)
            # Переходим в состояние ожидания ввода фото
            await state.set_state(FSMAddProductOne.photo)
    else:
        await message.answer(text='Неверный формат ввода!\n\n'
                                  '<b>Введите данные в таком формате (каждое с новой строки):</b>\n\n'
                                  '👉 Имя товара\n'
                                  '👉 Описание товара\n'
                                  '👉 Артикул товара\n'
                                  '👉 Цвета товара через пробел\n'
                                  '👉 Размеры товара через пробел\n'
                                  '👉 Цена товара (без валюты)\n\n'
                                  '<b>или нажмите "Отмена"</b>', reply_markup=kb2)


# Этот хэндлер будет принимать фото и формировать список идентификаторов фото
@router.message(StateFilter(FSMAddProductOne.photo), F.photo)
async def process_photo_sent(message: Message):
    largest_photo = message.photo[-1]
    lst.append({"unique_id": largest_photo.file_unique_id, "id": largest_photo.file_id})


# Хендлер который окончательно формирует товар и сохраняет его в базу данных
@router.callback_query(StateFilter(FSMAddProductOne.photo), lambda callback_query: 'done' in callback_query.data)
async def process_done_button(callback_query: CallbackQuery, state: FSMContext):
    # Получаем все данные из хранилища
    data = await state.get_data()
    data["photo_ids"] = lst
    # Создаем товар
    product = Product(
        name=data.get("name"),
        description=data.get("description"),
        sku=data.get("sku"),
        colors=data.get("colors"),
        sizes=data.get("sizes"),
        price=data.get("price"),
        photo_ids=data.get("photo_ids"),
    )
    product = {product.__dict__['sku']: product.__dict__}
    # получаем id пользователя
    user_id = callback_query.from_user.id
    # Получает данные о пользователе из базы данных по id
    user_data = get_data_from_redis(user_id)
    # Добавляем товар в базу данных
    user_data['products'].append(product)
    # записываем данные о пользователе в базу данных
    save_data_to_redis(user_id, user_data)
    # Отправляем сообщение о том, что товар успешно добавлен
    await callback_query.message.reply(text='Товар успешно Создан!')
    # очищаем хранилище
    await state.clear()

