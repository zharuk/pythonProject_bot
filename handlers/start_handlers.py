from aiogram import Router
from aiogram.filters import Command


router: Router = Router()


# Обработчик команды /start
@router.message(Command(commands='start'))
async def start_handler(message):
    # Отправляем приветственное сообщение пользователю и клавиатуру с основными действиями
    await message.answer('Добро пожаловать в бота магазин!\n\n'
                         '<b>Основные команды бота🤖:</b>\n\n'
                         'Нажмите <b>/start</b> что бы попасть в это меню\n'
                         'Нажмите <b>/show</b> для просмотра всех товаров\n'
                         'Нажмите <b>/add</b> для добавления новых товара\n'
                         'Нажмите <b>/cancel</b> для отмены\n\n'
                         'или воспользуйтесь кнопкой "Меню" ↙️ слева внизу экрана')


