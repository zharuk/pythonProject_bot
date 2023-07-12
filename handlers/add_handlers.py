from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from FSM.fsm import FSMAddProduct, FSMAddProductOne
from aiogram.types import Message
from keyboards.keyboards import create_cancel_kb
from services.product import Product
import json
from services.redis_server import create_redis_client

router: Router = Router()
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
    # Создаем клавиатуру для отмены
    kb = await create_cancel_kb()
    # Проверяем нет ли введенного артикула пользователя в базе данных и если есть, то сообщаем что такой товар уже есть
    if r.get(message.text):
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
    # Создаем клавиатуру для отмены
    kb = await create_cancel_kb()
    # Cохраняем введенную цену в хранилище по ключу "price"
    await state.update_data(price=message.text)
    await message.answer(text='Спасибо!\n\nА теперь загрузите фото товара', reply_markup=kb)
    # Устанавливаем состояние ожидания ввода загрузки фото товаров товара
    await state.set_state(FSMAddProduct.fill_photo)


# Этот хэндлер будет срабатывать, если отправлено фото
# и завершать создание товара
@router.message(StateFilter(FSMAddProduct.fill_photo))
async def process_photo_sent(message: Message, state: FSMContext):
    # Получаем текущий список идентификаторов фото из состояния
    data = await state.get_data()
    photo_ids = data.get("photo_ids", [])
    print(photo_ids)
    # Получаем информацию о текущем фото и сохраняем его идентификатор в список
    largest_photo = message.photo[-1]
    photo_ids.append({"unique_id": largest_photo.file_unique_id, "id": largest_photo.file_id})
    print(photo_ids)
    # Сохраняем список идентификаторов фото в состояние
    await state.update_data(photo_ids=photo_ids)
    # Формируем товар и добавляем в БД redis
    data = await state.get_data()
    product = Product(data['name'], data['description'], data['sku'], data['colors'], data['sizes'], data['price'])
    product.generate_variants()
    product.__dict__['photo_ids'] = data['photo_ids']
    product_json = json.dumps(product.__dict__)
    r.set(product.sku, product_json)
    # Завершающее сообщение и очистка FSM
    await message.answer(text='Спасибо!\n\nТовар создан!')
    await state.clear()


# Хендлер который срабатывает на команду /add_one. Отправляет сообщение с просьбой ввести данные с новой строки:
# название товара
# описание товара
# артикул товара
# цвета товара
# размеры товара
# цена товара
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
    await state.set_state(FSMAddProductOne.fill_data)


# Этот хэндлер будет срабатывать, если введено корректное имя
# и переводить в состояние ожидания ввода описания товара
@router.message(StateFilter(FSMAddProductOne.fill_data))
async def process_data_send(message: Message, state: FSMContext):
    print(message.text.split('\n'))
    # Создаем клавиатуру для отмены
    kb = await create_cancel_kb()
    # Cохраняем введенное имя в хранилище по ключу "name"
    await state.update_data(fill_data=message.text.split('\n'))
    # Считываем из хранилища data
    data = await state.get_data()
    # Благодарим за введенную информацию и просим добавить фото, если оно есть
    await message.answer(text='Спасибо!\n\nА теперь загрузите фото товара', reply_markup=kb)
    # Переходим в состояние ожидания ввода фото
    await state.set_state(FSMAddProductOne.fill_photo)


# Этот хэндлер будет срабатывать, когда отправлены фото, а также создавать товар и добавлять его в базу данных.
@router.message(StateFilter(FSMAddProductOne.fill_photo), F.photo)
async def process_photo_sent(message: Message, state: FSMContext):
    # Получаем текущий список идентификаторов фото из состояния
    data = await state.get_data()
    photo_ids = data.get("photo_ids", [])
    print(photo_ids)
    # Получаем информацию о текущем фото и сохраняем его идентификатор в список
    largest_photo = message.photo[-1]
    photo_ids.append({"unique_id": largest_photo.file_unique_id, "id": largest_photo.file_id})
    print(photo_ids)
    # Сохраняем список идентификаторов фото в состояние
    await state.update_data(photo_ids=photo_ids)
    # Формируем товар и добавляем в БД redis
    data = await state.get_data()
    product = Product(data['fill_data'][0], data['fill_data'][1], data['fill_data'][2], data['fill_data'][3],
                      data['fill_data'][4], data['fill_data'][5])
    product.generate_variants()
    product.__dict__['photo_ids'] = data['photo_ids']
    product_json = json.dumps(product.__dict__)
    r.set(product.sku, product_json)
    # Завершающее сообщение и очистка FSM
    await message.answer(text='Спасибо!\n\nТовар создан!')
    await state.clear()
