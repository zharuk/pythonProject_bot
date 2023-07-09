
from aiogram import Router
from aiogram.types import Message

router: Router = Router()


# Обработчик, который отвечает за все остальные команды
# все команды которые не вошли в другие обработчики
# по умолчанию отправляет сообщение о том что команда не найдена

@router.message()
async def process_all_commands(message: Message):
    await message.answer(text='Команда не обработана не одним из обработчиков')
