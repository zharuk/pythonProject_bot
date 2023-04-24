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