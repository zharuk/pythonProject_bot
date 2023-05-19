from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from keyboards.for_product_show import create_products_kb
from services.product import format_variants_message
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
    # формируем основную информацию о товаре
    response_text = f"➡ Название товара: {json_value['name']}\n" \
                    f"➡ Описание товара: {json_value['description']}\n" \
                    f"➡ Артикул товара: {json_value['sku']}\n" \
                    f"➡ Цвета товара: {', '.join(json_value['colors'])}\n" \
                    f"➡ Размеры товара: {', '.join(json_value['sizes'])}\n" \
                    f"➡ Цена товара: {json_value['price']}\n" \
        # Отправляем значение пользователю
    await callback_query.message.answer(response_text, parse_mode='HTML')

    # вывод комплектаций товара
    value_variants = json_value['variants']
    formatted_variants = format_variants_message(value_variants)
    await callback_query.message.answer(formatted_variants, parse_mode='HTML')

    # Создаем список фотографий
    if 'photo_ids' in json_value:
        photo_ids = json_value['photo_ids']
        photos = [photo_id['id'] for photo_id in photo_ids]

        # Отправляем все фотографии одним сообщением
        await callback_query.message.answer_media_group(
            media=[InputMediaPhoto(media=photo_id) for photo_id in photos]
        )
    else:
        await callback_query.message.answer('Фото нет')

    await callback_query.answer()