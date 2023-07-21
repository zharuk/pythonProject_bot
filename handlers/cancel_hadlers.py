from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from middlewares.check_user import CheckUserMessageMiddleware

router: Router = Router()
router.message.middleware(CheckUserMessageMiddleware())


# Обработчик команды /cancel на сообщение в чат команды /cancel
@router.message(Command(commands='cancel'))
async def cancel_handler(message: Message, state: FSMContext):
    # Сбрасываем состояние
    await state.clear()
    # Сообщаем пользователю, что состояние успешно сброшено
    await message.answer('Вы отменили текущую операцию. \n\nНажмите /start для выхода в главное меню\nНажмите /show для'
                         'просмотра товаров \nнажмите /add для добавления товара\n нажимте /report для отчета по '
                         'продажам')


# Обработчик команды /cancel на callback_data='/cancel'
@router.callback_query(lambda callback_query: 'cancel' in callback_query.data)
async def cancel_handler(callback_query: Message, state: FSMContext):
    # Сбрасываем состояние
    await state.clear()
    # Сообщаем пользователю, что состояние успешно сброшено
    await callback_query.message.answer('Вы отменили текущую операцию. \n\nНажмите /start для выхода в главное '
                                        'меню\nНажмите /show для'
                                        'просмотра товаров \nнажмите /add для добавления товара\n нажимте /report для '
                                        'отчета по'
                                        'продажам')
    await callback_query.answer()
