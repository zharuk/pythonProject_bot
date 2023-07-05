from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from FSM.fsm import FSMAddProduct
from aiogram.types import Message
from services.product import Product
import json
from services.redis_server import create_redis_client

router: Router = Router()
r = create_redis_client()


# Этот хэндлер будет срабатывать на команду /add
# и переводить бота в состояние ожидания ввода имени
@router.message(Command(commands='add'), StateFilter(default_state))
async def process_add_command(message: Message, state: FSMContext):
    await message.answer(text='Введите имя товара или для отмены введите /cancel')
    # Устанавливаем состояние ожидания ввода имени
    await state.set_state(FSMAddProduct.fill_name)


# Этот хэндлер будет срабатывать, если введено корректное имя
# и переводить в состояние ожидания ввода описания товара
@router.message(StateFilter(FSMAddProduct.fill_name))
async def process_name_sent(message: Message, state: FSMContext):
    # Cохраняем введенное имя в хранилище по ключу "name"
    await state.update_data(name=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите описание товара')
    # Устанавливаем состояние ожидания ввода описания товара
    await state.set_state(FSMAddProduct.fill_description)


# Этот хендлер будет срабатывать, если введено корректное описание товара
# и переводить в состояние ожидания ввода артикула товара
@router.message(StateFilter(FSMAddProduct.fill_description))
async def process_desc_sent(message: Message, state: FSMContext):
    # Cохраняем введенное описание в хранилище по ключу "description"
    await state.update_data(description=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите артикул товара')
    # Устанавливаем состояние ожидания ввода описания товара
    await state.set_state(FSMAddProduct.fill_sku)


# Этот хэндлер будет срабатывать, если введено корректный артикул товара
# и переводить в состояние ожидания ввода цветов товара
@router.message(StateFilter(FSMAddProduct.fill_sku))
async def process_sku_sent(message: Message, state: FSMContext):
    # Cохраняем введенный артикул в хранилище по ключу "sku"
    await state.update_data(sku=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите цвета товаров через пробел')
    # Устанавливаем состояние ожидания ввода цветов товара
    await state.set_state(FSMAddProduct.fill_colors)


# Этот хэндлер будет срабатывать, если введены корректный артикул товара
# и переводить в состояние ожидания ввода цветов товара
@router.message(StateFilter(FSMAddProduct.fill_colors))
async def process_colors_sent(message: Message, state: FSMContext):
    # Cохраняем введенные цвета в хранилище по ключу "colors"
    await state.update_data(colors=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите размеры товаров через пробел')
    # Устанавливаем состояние ожидания ввода размеров товара
    await state.set_state(FSMAddProduct.fill_sizes)


# Этот хэндлер будет срабатывать, если введены корректный артикул товара
# и переводить в состояние ожидания ввода цветов товара
@router.message(StateFilter(FSMAddProduct.fill_colors))
async def process_colors_sent(message: Message, state: FSMContext):
    # Cохраняем введенные цвета в хранилище по ключу "colors"
    await state.update_data(colors=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите размеры товаров через пробел')
    # Устанавливаем состояние ожидания ввода размеров товара
    await state.set_state(FSMAddProduct.fill_sizes)


# Этот хэндлер будет срабатывать, если введены корректно цвета товаров
# и переводить в состояние ожидания ввода цены товара
@router.message(StateFilter(FSMAddProduct.fill_sizes))
async def process_sizes_sent(message: Message, state: FSMContext):
    # Cохраняем введенные размеры в хранилище по ключу "sizes"
    await state.update_data(sizes=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите цену товара')
    # Устанавливаем состояние ожидания ввода размеров товара
    await state.set_state(FSMAddProduct.fill_price)


# Этот хэндлер будет срабатывать, если введен корректно артикул товара
# и переходить к загрузке фото
@router.message(StateFilter(FSMAddProduct.fill_price))
async def process_price_sent(message: Message, state: FSMContext):
    # Cохраняем введенную цену в хранилище по ключу "price"
    await state.update_data(price=message.text)
    await message.answer(text='Спасибо!\n\nА теперь загрузите фото товара')
    # Устанавливаем состояние ожидания ввода загрузки фото товаров товара
    await state.set_state(FSMAddProduct.fill_photo)


# Этот хэндлер будет срабатывать, если отправлено фото
# и завершать создание товара
@router.message(StateFilter(FSMAddProduct.fill_photo))
async def process_photo_sent(message: Message, state: FSMContext):
    # Получаем текущий список идентификаторов фото из состояния
    data = await state.get_data()
    photo_ids = data.get("photo_ids", [])
    # Получаем информацию о текущем фото и сохраняем его идентификатор в список
    largest_photo = message.photo[-1]
    photo_ids.append({"unique_id": largest_photo.file_unique_id, "id": largest_photo.file_id})
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
