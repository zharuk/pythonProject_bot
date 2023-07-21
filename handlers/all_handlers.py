from aiogram import Router
from aiogram.types import Message, CallbackQuery
from middlewares.check_user import CheckUserMessageMiddleware

router: Router = Router()
router.message.middleware(CheckUserMessageMiddleware())

# Обработчик, отвечает за все остальные команды которые не вошли в другие обработчики по
# умолчанию отправляет сообщение о том что команда не найдена

@router.message()
async def process_all_commands(message: Message):
    await message.answer('хендлер не обслужен')


@router.callback_query()
async def callback_query(callback_query: CallbackQuery):
    await callback_query.message.answer('хендлер не обслужен')
