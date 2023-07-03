from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router: Router = Router()


# Обработчик команды /cancel
@router.message(Command(commands='cancel'))
async def cancel_handler(message: Message, state: FSMContext):
    # Сбрасываем состояние
    await state.clear()
    # Сообщаем пользователю, что состояние успешно сброшено
    await message.answer('Вы отменили текущую операцию. \nНажмите /show для просмотра товаров \nнажмите /add для '
                         'добавления товара')
