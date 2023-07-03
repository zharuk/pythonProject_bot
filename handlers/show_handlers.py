from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm import state
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from FSM.fsm import SellItemStates
from keyboards.keyboards import create_sku_kb, create_options_kb, create_variants_kb
from services.product import format_variants_message, generate_photos, format_main_info
import json
from services.redis_server import create_redis_client
from services.reports import sell_product

router: Router = Router()
r = create_redis_client()


# Обработчик команды /show для вывода списка товаров с помощью инлайн-клавиатуры с артикулами товаров
@router.message(Command(commands='show'))
async def process_show_command(message: Message):
    # Создаем инлайн-клавиатуру с артикулами товаров
    kb = create_sku_kb()
    # Отправляем сообщение пользователю
    await message.answer(text='Список товаров:', reply_markup=kb)


# Обработчик для кнопок с артикулами товаров в которых callback_data = артикулу товара
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
    await callback_query.message.answer(main_info, reply_markup=kb)
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
    await callback_query.message.answer(formatted_variants)
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


# Обработчик для кнопки "Продать товар" в которой callback_data = '_sell', выводит список товаров
@router.callback_query(lambda callback_query: '_sell' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery):
    # Получаем значение артикула товара из callback_data
    article = callback_query.data.split('_')[0]
    # Получаем значение из Redis по артикулу
    value = r.get(article)
    # Преобразуем значение в словарь json
    json_value = json.loads(value)
    # Получаем значение variants из json_value
    json_value_variants = json_value['variants']
    # Создаем клавиатуру с вариантами товара
    kb = create_variants_kb(article, json_value_variants)
    # Отправляем клавиатуру пользователю
    await callback_query.message.answer(text='Выберите товар:', reply_markup=kb)
    await callback_query.answer()


# Обработчик, который срабатывает при нажатии на кнопку с вариантом товара и просит ввести количество продаваемого
# товара сообщением "Введите количество:"
@router.callback_query(lambda callback_query: '-' in callback_query.data)
async def process_callback_query(callback_query: CallbackQuery, state: FSMContext):
    # Получаем значение артикула товара из callback_data
    article = callback_query.data.split('_')[0]
    article_variant = callback_query.data
    # Устанавливаем FSM SellItemStates article
    await state.update_data(article_variant=article_variant)
    data = await state.get_data()
    # Переводим в состояние SellItemStates.quantity
    await state.set_state(SellItemStates.quantity)
    # Отвечаем пользователю сообщением "Введите количество:"
    await callback_query.message.answer(text='Введите количество:')
    await callback_query.answer()


# Обработчик, который обрабатывает введенное число пользователем
@router.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100, SellItemStates.quantity)
async def process_quantity(message: Message, state: FSMContext):
    # Получаем значение введенное пользователем
    quantity = int(message.text)
    # Получаем значение article_variant из FSM
    data = await state.get_data()
    article_variant = data.get("article_variant")
    # Получаем значение из Redis по артикулу
    value = r.get(article_variant.split('-')[0])
    # Преобразуем значение в словарь json
    json_value = json.loads(value)
    # вывод комплектаций товара
    value_variants = json_value['variants']
    # Получаем название товара
    name = ''
    for i in value_variants:
        if i['sku'] == article_variant:
            name = i['name']
            break
    # вызываем функцию sell_product
    if sell_product(article_variant, quantity) is True:
        # Пишем сообщение пользователю, что товар продан в количестве quantity штук
        await message.answer(text=f'Товар {name} продан в количестве {quantity} шт.')
        # Переводим в состояние default
        await state.clear()
    else:
        # Пишем сообщение пользователю, что товара не хватает на складе
        await message.answer(text=f'Товара {name} <b>не хватает на складе</b>')


# Обработчик, если было введено не число от 1 до 100
@router.message(lambda x: x.text and not x.text.isdigit() or int(x.text) < 1 or int(x.text) > 100,
                SellItemStates.quantity)
async def process_quantity(message: Message, state: FSMContext):
    # Пишем сообщение пользователю, что было введено не число от 1 до 100
    await message.answer(text='Было введено не число от 1 до 100')

# @router.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100, SellItemStates.article)
# async def process_quantity(message: Message, state: FSMContext):
