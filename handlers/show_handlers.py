from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from keyboards.keyboards import create_sku_kb, create_options_kb
from services.product import format_variants_message, generate_photos, format_main_info
import json
from services.redis_server import create_redis_client

router: Router = Router()
r = create_redis_client()


@router.message(Command(commands='show'))
async def process_show_command(message: Message):
    keyboard = create_sku_kb()
    await message.answer(text='Список товаров:',
                         reply_markup=keyboard)


@router.callback_query(lambda callback_query: len(callback_query.data) < 4)
async def process_callback_query(callback_query: CallbackQuery):
    # Получаем значение артикула товара из callback_data
    article = callback_query.data
    # Получаем значение из Redis по артикулу
    value = r.get(article)
    # Преобразуем значение в словарь json
    json_value = json.loads(value)
    # формируем основную информацию о товаре с помощью функции
    main_info = format_main_info(json_value)
    # формируем клавиатуру с 2 кнопками "Модификации товара" и "Показать фото" с помощью функции create_kb
    kb = create_options_kb(article)
    # Отправляем значение пользователю
    await callback_query.message.answer(main_info, parse_mode='HTML', reply_markup=kb)
    await callback_query.answer()


# Обработчик для кнопки "Модификации товара" в которой callback_data = '_variants'
@router.callback_query(lambda callback_query: '_variants' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # Получаем значение артикула товара из callback_data
    article = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    value = r.get(article)
    json_value = json.loads(value)
    # вывод комплектаций товара
    value_variants = json_value['variants']
    formatted_variants = format_variants_message(value_variants)
    # Отправляем значение пользователю
    await callback_query.message.answer(formatted_variants, parse_mode='HTML')
    await callback_query.answer()


# Обработчик для кнопки "Модификации товара" в которой callback_data = '_photo'
@router.callback_query(lambda callback_query: '_photo' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # Получаем значение артикула товара из callback_data
    article = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    value = r.get(article)
    json_value = json.loads(value)
    # Создаем список фотографий
    if 'photo_ids' in json_value:
        photo_ids = json_value['photo_ids']
        # Отправляем все фотографии одним сообщением
        await callback_query.message.answer_media_group(generate_photos(photo_ids))
    else:
        await callback_query.message.answer('Фото нет')
    await callback_query.answer()