# Этот модуль содержит обработчики команд связанных с отчетами
from aiogram.dispatcher import router
from aiogram.filters import Command

from services.reports import get_sales_today_report

router: router = router.Router()


# Обработчик команды /report
@router.message(Command(commands='report'))
async def report_handler(message):
    # Формируем дневной отчет
    data = get_sales_today_report()
    await message.answer(data)
