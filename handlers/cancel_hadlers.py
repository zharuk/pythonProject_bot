from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from lexicon.lexicon import LEXICON_COMMANDS_MENU
from middlewares.check_user import CheckUserMessageMiddleware

router: Router = Router()
router.message.middleware(CheckUserMessageMiddleware())


# Обработчик команды /cancel на сообщение в чат команды /cancel
@router.message(Command(commands='cancel'))
async def cancel_handler(message: Message, state: FSMContext):
    # Сбрасываем состояние
    await state.clear()
    # Формируем строку доступных команд из словаря LEXICON_COMMANDS_MENU
    commands = '\n'.join([f'<b>{command}</b> - {description}' for command, description in LEXICON_COMMANDS_MENU.items()])
    # Сообщаем пользователю, что состояние успешно сброшено
    await message.answer(f' \n\n{commands}')


# Обработчик команды /cancel на callback_data='/cancel'
@router.callback_query(lambda callback_query: 'cancel' in callback_query.data)
async def cancel_handler(callback_query: CallbackQuery, state: FSMContext):
    # Сбрасываем состояние
    await state.clear()
    # Формируем строку доступных команд из словаря LEXICON_COMMANDS_MENU
    commands = '\n'.join([f'<b>{command}</b> - {description}' for command, description in LEXICON_COMMANDS_MENU.items()])
    # Сообщаем пользователю, что состояние успешно сброшено
    await callback_query.message.answer(text='Вы отменили текущее действие\n\n'
                                             'Доступные команды:\n'
                                             f'{commands}')
