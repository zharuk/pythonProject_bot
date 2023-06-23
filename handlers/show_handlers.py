from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from keyboards.for_product_show import create_products_kb
from services.product import format_variants_message, generate_photos, format_main_info
from config_data.config import load_config
import redis
import json

# Загрузка конфигурации
config = load_config()

# Подключение к серверу Redis
r = redis.Redis(host=config.redis.host, port=config.redis.port)

router: Router = Router()


@router.message(Command(commands='show'))
async def process_show_command(message: Message):
    keyboard = create_products_kb()
    await message.answer(text='Список товаров:',
                         reply_markup=keyboard)


@router.callback_query()
async def process_callback_query(callback_query: CallbackQuery):
    # Получаем значение артикула товара из callback_data
    article = callback_query.data
    # Получаем значение из Redis по артикулу
    value = r.get(article)
    json_value = json.loads(value)

    # формируем основную информацию о товаре с помощью функции
    main_info = format_main_info(json_value)
    # Отправляем значение пользователю
    await callback_query.message.answer(main_info, parse_mode='HTML')

    # вывод комплектаций товара
    value_variants = json_value['variants']
    formatted_variants = format_variants_message(value_variants)
    # Отправляем значение пользователю
    await callback_query.message.answer(formatted_variants, parse_mode='HTML')

    # Создаем список фотографий
    if 'photo_ids' in json_value:
        photo_ids = json_value['photo_ids']
        # Отправляем все фотографии одним сообщением
        await callback_query.message.answer_media_group(generate_photos(photo_ids))
    else:
        await callback_query.message.answer('Фото нет')

    await callback_query.answer()
