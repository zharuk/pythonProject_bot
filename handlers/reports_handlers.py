# Этот модуль содержит обработчики команд связанных с отчетами
from aiogram.dispatcher import router
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from keyboards.keyboards import create_report_kb
from services.reports import get_sales_today_report

router: router = router.Router()


# Обработчик команды /report
@router.message(Command(commands='report'))
async def report_handler(message):
    # Формируем клавиатуру с выбором отчета
    kb = await create_report_kb()
    # Отправляем сообщение пользователю
    await message.answer('Выберите отчет', reply_markup=kb)


# Обработчик для кнопки "Продажи за сегодня" в которой callback_data = 'today'
@router.callback_query(lambda callback_query: 'today' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # Получаем значение из Redis по артикулу
    value = get_sales_today_report()
    # Отправляем значение пользователю
    await callback_query.message.answer(value)
    await callback_query.answer()


# Обработчик для кнопки "Продажи за неделю" в которой callback_data = 'week'
@router.callback_query(lambda callback_query: 'week' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # Отправляем значение пользователю
    await callback_query.message.answer('Функция пока в разработке')
    await callback_query.answer()


# Обработчик для кнопки "Продажи за месяц" в которой callback_data = 'month'
@router.callback_query(lambda callback_query: 'month' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # Отправляем значение пользователю
    await callback_query.message.answer('Функция пока в разработке')
    await callback_query.answer()


# Обработчик для кнопки "Продажи за год" в которой callback_data = 'year'
@router.callback_query(lambda callback_query: 'year' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # Отправляем значение пользователю
    await callback_query.message.answer('Функция пока в разработке')
    await callback_query.answer()


# Обработчик для кнопки "Выбрать период" в которой callback_data = 'period'
@router.callback_query(lambda callback_query: 'period' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # Отправляем значение пользователю
    await callback_query.message.answer('Функция пока в разработке')
    await callback_query.answer()
