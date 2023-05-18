from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from keyboards.for_product_show import create_inline_kb
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
    keyboard = create_inline_kb()
    await message.answer(text='Список товаров:',
                         reply_markup=keyboard)


@router.callback_query()
async def process_callback_query(callback_query: CallbackQuery):
    # Получаем значение артикула товара из callback_data
    article = callback_query.data
    # Получаем значение из Redis по артикулу
    value = r.get(article)
    json_value = json.loads(value)
    print(json_value)
    response_text = f"➡ Название товара: {json_value['name']}\n" \
                    f"➡ Описание товара: {json_value['description']}\n" \
                    f"➡ Артикул товара: {json_value['sku']}\n" \
                    f"➡ Цвета товара: {', '.join(json_value['colors'])}\n" \
                    f"➡ Размеры товара: {', '.join(json_value['sizes'])}\n" \
                    f"➡ Цена товара: {json_value['price']}\n" \
        # Отправляем значение пользователю
    await callback_query.message.answer(response_text)
