import asyncio
from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from handlers import add_handlers, show_handlers, cancel_hadlers, start_handlers, reports_handlers, all_handlers, \
    settings_handlers
from keyboards.set_menu import set_main_menu
import logging
from aiogram.fsm.storage.redis import RedisStorage, Redis

from middlewares.check_user import CheckUserCallbackMiddleware

# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция конфигурирования и запуска бота
async def main():
    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')
    # Загружаем конфиг в переменную config
    config: Config = load_config()
    # Создаем подключение к Redis состояний и хранилищу
    redis: Redis = Redis(host='localhost')
    # Инициализируем хранилище (создаем экземпляр класса RedisStorage)
    storage: RedisStorage = RedisStorage(redis=redis)

    # Инициализируем бот и диспетчер и сервер
    bot: Bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp: Dispatcher = Dispatcher(storage=storage, bot=bot)

    # Настраиваем меню
    await set_main_menu(bot)

    # Регистрируем роутеры в диспетчере
    dp.callback_query.outer_middleware(CheckUserCallbackMiddleware())
    dp.include_router(start_handlers.router)
    dp.include_router(cancel_hadlers.router)
    dp.include_router(add_handlers.router)
    dp.include_router(show_handlers.router)
    dp.include_router(reports_handlers.router)
    dp.include_router(settings_handlers.router)
    dp.include_router(all_handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
