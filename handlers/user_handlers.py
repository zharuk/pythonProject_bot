from aiogram import Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from FSM.fsm import FSMAddProduct
from aiogram.types import Message
from lexicon.lexicon import LEXICON_RU

# Инициализируем роутер уровня модуля
router: Router = Router()


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
@router.message(StateFilter(FSMAddProduct.fill_name))
async def warning_not_name(message: Message):
    await message.answer(text='Что то пошло не так (fill_description)')