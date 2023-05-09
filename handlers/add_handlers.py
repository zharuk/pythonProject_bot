from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from FSM.fsm import FSMAddProduct
from aiogram.types import Message, PhotoSize
from lexicon.lexicon import LEXICON_RU

# Инициализируем роутер уровня модуля
router: Router = Router()
user_dict: dict[int, dict[str, str | int | bool]] = {}

# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=LEXICON_RU['/start'])


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])


# Этот хэндлер будет срабатывать на команду /add
# и переводить бота в состояние ожидания ввода имени
@router.message(Command(commands='add'), StateFilter(default_state))
async def process_add_command(message: Message, state: FSMContext):
    await message.answer(text='Пожалуйста, название товара')
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


# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@router.message(StateFilter(FSMAddProduct.fill_name))
async def warning_not_name(message: Message):
    await message.answer(text='Что то пошло не так (fill_name)')


# Этот хэндлер будет срабатывать, если введено корректное описание товара
# и переводить в состояние ожидания ввода артикула товара
@router.message(StateFilter(FSMAddProduct.fill_description))
async def process_desc_sent(message: Message, state: FSMContext):
    # Cохраняем введенное описание в хранилище по ключу "description"
    await state.update_data(description=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите артикул товара')
    # Устанавливаем состояние ожидания ввода описания товара
    await state.set_state(FSMAddProduct.fill_sku)


# Этот хэндлер будет срабатывать, если во время ввода описания товара
# будет введено что-то некорректное
@router.message(StateFilter(FSMAddProduct.fill_description))
async def warning_not_desc(message: Message):
    await message.answer(text='Что то пошло не так (fill_description)')


# Этот хэндлер будет срабатывать, если введено корректный артикул товара
# и переводить в состояние ожидания ввода цветов товара
@router.message(StateFilter(FSMAddProduct.fill_sku))
async def process_sku_sent(message: Message, state: FSMContext):
    # Cохраняем введенный артикул в хранилище по ключу "sku"
    await state.update_data(sku=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите цвета товаров через пробел')
    # Устанавливаем состояние ожидания ввода цветов товара
    await state.set_state(FSMAddProduct.fill_colors)


# Этот хэндлер будет срабатывать, если во время ввода артикула товара
# будет введено что-то некорректное
@router.message(StateFilter(FSMAddProduct.fill_sku))
async def warning_not_sku(message: Message):
    await message.answer(text='Что то пошло не так (fill_sku)')


# Этот хэндлер будет срабатывать, если введены корректный артикул товара
# и переводить в состояние ожидания ввода цветов товара
@router.message(StateFilter(FSMAddProduct.fill_colors))
async def process_colors_sent(message: Message, state: FSMContext):
    # Cохраняем введенные цвета в хранилище по ключу "colors"
    await state.update_data(colors=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите размеры товаров через пробел')
    # Устанавливаем состояние ожидания ввода размеров товара
    await state.set_state(FSMAddProduct.fill_sizes)


# Этот хэндлер будет срабатывать, если во время ввода цветов товара
# будет введено что-то некорректное
@router.message(StateFilter(FSMAddProduct.fill_colors))
async def warning_not_colors(message: Message):
    await message.answer(text='Что то пошло не так (fill_colors)')


# Этот хэндлер будет срабатывать, если введены корректный артикул товара
# и переводить в состояние ожидания ввода цветов товара
@router.message(StateFilter(FSMAddProduct.fill_colors))
async def process_colors_sent(message: Message, state: FSMContext):
    # Cохраняем введенные цвета в хранилище по ключу "colors"
    await state.update_data(colors=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите размеры товаров через пробел')
    # Устанавливаем состояние ожидания ввода размеров товара
    await state.set_state(FSMAddProduct.fill_sizes)


# Этот хэндлер будет срабатывать, если во время ввода цветов товара
# будет введено что-то некорректное
@router.message(StateFilter(FSMAddProduct.fill_colors))
async def warning_not_colors(message: Message):
    await message.answer(text='Что то пошло не так (fill_colors)')


# Этот хэндлер будет срабатывать, если введены корректно цвета товаров
# и переводить в состояние ожидания ввода цены товара
@router.message(StateFilter(FSMAddProduct.fill_sizes))
async def process_sizes_sent(message: Message, state: FSMContext):
    # Cохраняем введенные размеры в хранилище по ключу "sizes"
    await state.update_data(sizes=message.text)
    await message.answer(text='Спасибо!\n\nА теперь введите цену товара')
    # Устанавливаем состояние ожидания ввода размеров товара
    await state.set_state(FSMAddProduct.fill_price)


# Этот хэндлер будет срабатывать, если во время ввода цветов товара
# будет введено что-то некорректное
@router.message(StateFilter(FSMAddProduct.fill_sizes))
async def warning_not_sizes(message: Message):
    await message.answer(text='Что то пошло не так (fill_sizes)')


# Этот хэндлер будет срабатывать, если введен корректно артикул товара
# и переходить к загрузке фото
@router.message(StateFilter(FSMAddProduct.fill_price))
async def process_price_sent(message: Message, state: FSMContext):
    # Cохраняем введенную цену в хранилище по ключу "price"
    await state.update_data(price=message.text)
    await message.answer(text='Спасибо!\n\nА теперь загрузите фото товара')
    # Устанавливаем состояние ожидания ввода загрузки фото товаров товара
    await state.set_state(FSMAddProduct.fill_photo)


# Этот хэндлер будет срабатывать, если во время ввода цены товара
# будет введено что-то некорректное
@router.message(StateFilter(FSMAddProduct.fill_sizes))
async def warning_not_price(message: Message):
    await message.answer(text='Что то пошло не так (fill_price)')


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

    # Если это была последняя отправленная фотография, завершаем машину состояний
    data = await state.get_data()
    print(data)

    await message.answer(text='Спасибо!\n\nТовар создан!')
    await state.clear()


