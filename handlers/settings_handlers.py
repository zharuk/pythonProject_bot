# Данный модуль отвечает за обработку команд, связанных с настройками бота
from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from FSM.fsm import FSMEditCompany
from keyboards.keyboards import create_settings_kb
from middlewares.check_user import CheckUserMessageMiddleware
from services.redis_server import get_data_from_redis, edit_company_name, edit_currency

router: Router = Router()
router.message.middleware(CheckUserMessageMiddleware())


# Обработчик команды /settings
# Выводит список настроек в виде кнопок и ожидает выбора пользователя
@router.message(Command(commands='settings'))
async def settings(message):
    kb = await create_settings_kb()
    # Получаем id пользователя
    user_id = message.from_user.id
    # Получаем данные из Redis
    data = await get_data_from_redis(user_id)
    # Получаем название компании
    company_name = data['company']
    # Получаем валюту
    currency = data['currency']
    # Получаем список администраторов
    admins = data['admins']
    # Получаем список пользователей
    users = data['users']
    kb = await create_settings_kb()
    await message.answer(text=f'Название компании: {company_name}\n'
                              f'Валюта: {currency}\n'
                              f'Список администраторов: {admins}\n'
                              f'Список пользователей: {users}', reply_markup=kb)


# Обработчик команды /settings, но с callback query = 'settings'
# Выводит список настроек в виде кнопок и ожидает выбора пользователя
@router.callback_query(lambda callback_query: callback_query.data == 'settings')
async def process_show_callback(callback_query: CallbackQuery):
    kb = await create_settings_kb()
    # Получаем id пользователя
    user_id = callback_query.from_user.id
    # Получаем данные из Redis
    data = await get_data_from_redis(user_id)
    # Получаем название компании
    company_name = data['company']
    # Получаем валюту
    currency = data['currency']
    # Получаем список администраторов
    admins = data['admins']
    # Получаем список пользователей
    users = data['users']
    # Выводим сообщение с названием компании, валютой, списком администраторов и пользователей
    await callback_query.message.answer(text=f'Название компании: {company_name}\n'
                                             f'Валюта: {currency}\n'
                                             f'Список администраторов: {admins}\n'
                                             f'Список пользователей: {users}', reply_markup=kb)


# Обработчик callback query с data = 'edit_company_name'
# Выводит сообщение с текущим названием компании а также с просьбой ввести новое название компании
@router.callback_query(lambda callback_query: callback_query.data == 'edit_company_name')
async def process_show_callback(callback_query: CallbackQuery, state: FSMContext):
    # Получаем название компании из Redis
    data = await get_data_from_redis(callback_query.from_user.id)
    company_name = data['company']
    # Выводим сообщение с текущим названием компании, а также с просьбой ввести новое название компании
    await callback_query.message.answer(text=f'Текущее название компании: {company_name}\n\n'
                                             f'<b>Введите новое название компании:</b>')
    # Переходим в состояние edit_company_name
    await state.set_state(FSMEditCompany.name)
    await callback_query.answer()


# Обрабатываем введенное пользователем новое название компании и сохраняем его в Redis
@router.message(StateFilter(FSMEditCompany.name))
async def process_edit_company_name(message, state: FSMContext):
    # Получаем новое название компании
    new_company_name = message.text
    # Получаем id пользователя
    user_id = message.from_user.id
    # Сохраняем новое название компании в Redis
    await edit_company_name(user_id, new_company_name)
    # Создаем клавиатуру с настройками
    kb = await create_settings_kb()
    # Выводим сообщение с новым названием компании
    await message.answer(f'Название компании успешно изменено на: {new_company_name}', reply_markup=kb)
    # Скидываем состояние
    await state.clear()


# Обработчик callback query с data = 'edit_currency'
# Выводит сообщение с текущей валютой а также с просьбой ввести новую валюту
@router.callback_query(lambda callback_query: callback_query.data == 'edit_currency')
async def process_show_callback(callback_query: CallbackQuery, state: FSMContext):
    # Получаем id пользователя
    user_id = callback_query.from_user.id
    # Получаем данные из Redis
    data = await get_data_from_redis(user_id)
    currency = data['currency']
    # Выводим сообщение с текущей валютой, а также с просьбой ввести новую валюту
    await callback_query.message.answer(text=f'Текущая валюта: {currency}\n\n'
                                             f'<b>Введите новую валюту:</b>')
    # Переходим в состояние edit_currency
    await state.set_state(FSMEditCompany.currency)
    await callback_query.answer()


# Обрабатываем введенную пользователем новую валюту и сохраняем ее в Redis
@router.message(StateFilter(FSMEditCompany.currency))
async def process_edit_currency(message, state: FSMContext):
    # Получаем новую валюту
    new_currency = message.text
    # Получаем id пользователя
    user_id = message.from_user.id
    # Сохраняем новую валюту в Redis
    await edit_currency(user_id, new_currency)
    # Создаем клавиатуру с настройками
    kb = await create_settings_kb()
    # Выводим сообщение с новой валютой
    await message.answer(f'Валюта успешно изменена на: {new_currency}', reply_markup=kb)
    # Скидываем состояние
    await state.clear()


# Обработчик callback query с data = 'add_admin'
# Выводит сообщение с просьбой ввести данные нового пользователя