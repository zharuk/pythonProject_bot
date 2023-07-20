from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from FSM.fsm import FSMCreateCompany
from keyboards.keyboards import create_company_kb
from services.redis_server import check_user_id_in_redis, create_company

router: Router = Router()


# Обработчик команды /start
@router.message(Command(commands='start'))
async def start_handler(message: Message):
    # Сохраняем id пользователя в переменную user_id
    user_id = message.from_user.id
    # Проверяем, есть ли пользователь в базе данных
    if not await check_user_id_in_redis(user_id):
        # Создаем клавиатуру с create_company_kb
        kb = await create_company_kb()
        # Отправляем приветственное сообщение пользователю и клавиатуру с основными действиями
        await message.answer('Добро пожаловать в бота для работы с остатками товара!\n'
                             'для начала работы нажмите на кнопку "Создать компанию"', reply_markup=kb)
    else:
        await message.answer('Добро пожаловать!\n\n'
                             'основные команды:\n'
                             '<b>/show</b> - список товаров\n'
                             '<b>/add</b> - добавить товар\n'
                             '<b>/add_one</b> - добавить товар одной строкой\n'
                             '<b>/report</b> - статистика\n'
                             '<b>/cancel</b> - отменить текущее действие\n\n'
                             'или нажмите "Меню" для вызова основного меню')


# Обработчик кнопки "Создать компанию"
@router.callback_query(lambda callback_query: 'create_company' in callback_query.data)
async def create_company_handler(callback_query: CallbackQuery, state: FSMContext):
    # Устанавливаем состояние ввода названия компании FSM
    await state.set_state(FSMCreateCompany.name)
    # Просим ввести название компании и сохраняем в переменную company_name
    await callback_query.message.answer('Введите название компании')
    await callback_query.answer()


# Обработчик введенного названия компании
@router.message(FSMCreateCompany.name)
async def create_company_name_handler(message: Message, state: FSMContext):
    # Сохраняем введенное название компании в переменную company_name
    company_name = message.text
    # Сохраняем название компании в базу данных
    await state.update_data(company_name=company_name)
    # Переводим в состояние ввода валюты компании
    await state.set_state(FSMCreateCompany.currency)
    # Просим ввести валюту компании и сохраняем в переменную currency
    await message.answer('Введите валюту компании\n\n'
                         'Например: <b>грн</b>, <b>дол</b>, <b>евро</b> и т.д.\n'
                         'или <b>₴</b>, <b>$</b>, <b>€</b>')


# Обработчик введенной валюты компании
@router.message(FSMCreateCompany.currency)
async def create_company_currency_handler(message: Message, state: FSMContext):
    # Сохраняем введенную валюту компании в состояние FSM
    await state.update_data(currency=message.text)
    # Получаем данные из состояния FSM и присваиваем переменным company_name и currency
    data = await state.get_data()
    company_name = data.get('company_name')
    currency = data.get('currency')
    # Сохраняем id пользователя в переменную user_id
    user_id = message.from_user.id
    # Вызываем функцию для создания компании в базе данных
    await create_company(user_id, company_name, currency)
    # Сбрасываем состояние FSM
    await state.clear()
    # Отправляем сообщение пользователю и клавиатуру с основными действиями
    await message.answer('Компания успешно создана!\n\n'
                         'основные команды:\n'
                         '<b>/show</b> - список товаров\n'
                         '<b>/add</b> - добавить товар\n'
                         '<b>/add_one</b> - добавить товар одной строкой\n'
                         '<b>/report</b> - статистика\n'
                         '<b>/cancel</b> - отменить текущее действие\n\n'
                         'или нажмите "Меню" для вызова основного меню')
